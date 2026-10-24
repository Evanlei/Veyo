"""HTTP integration with an explicitly injected test predictor, never a production fallback."""
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient
from veyo.app import create_app
from veyo.config import Settings
from veyo.engine import InferenceEngine
from veyo.ingest import png_bytes


class TestPredictor:
    def __init__(self):
        self.calls = 0
        self.fail = False

    def predict(self, image):
        self.calls += 1
        if self.fail:
            raise RuntimeError("Intentional test failure")
        values = np.arange(1, image.width*image.height+1, dtype=float).reshape(image.height, image.width)
        return values / values.sum()


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.settings = Settings(Path(self.directory.name), None, ("http://localhost:5173",))
        self.predictor = TestPredictor()
        engine = InferenceEngine(self.settings, predictor_factory=lambda: self.predictor)
        self.client = TestClient(create_app(self.settings, engine=engine), raise_server_exceptions=False)
        self.headers = {"X-Workspace-Key": "a"*64}

    def tearDown(self):
        self.client.close()
        self.directory.cleanup()

    def create(self):
        source = Image.fromarray(np.arange(40*30*3, dtype=np.uint8).reshape(30, 40, 3))
        response = self.client.post("/api/projects", headers=self.headers, data={"name": "API review"},
                                    files={"image": ("creative.png", png_bytes(source), "image/png")})
        self.assertEqual(response.status_code, 201, response.text)
        project = response.json()
        return project, project["assets"][0]

    def annotate(self, asset, box=None):
        response = self.client.put(f"/api/assets/{asset['id']}/targets", headers=self.headers,
            json={"targets": [{"id": "product", "label": "Product", "role": "product", "priority": 3,
                               "box": box or [2, 3, 24, 25]}], "confirmed": True})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def run_analysis(self, asset):
        response = self.client.post(f"/api/assets/{asset['id']}/analyze", headers=self.headers)
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def test_upload_annotation_analysis_cache_history_and_export(self):
        project, asset = self.create()
        self.assertEqual(self.client.post(f"/api/assets/{asset['id']}/analyze", headers=self.headers).status_code, 422)
        self.annotate(asset)
        first = self.run_analysis(asset)
        self.assertEqual(first["status"], "completed")
        self.assertFalse(first["cached"])
        self.annotate(asset, [1, 1, 10, 10])
        second = self.run_analysis(asset)
        self.assertTrue(second["cached"])
        self.assertEqual(self.predictor.calls, 1)
        saved_first = self.client.get(f"/api/runs/{first['id']}", headers=self.headers).json()
        self.assertEqual(saved_first["targets"][0]["box"], [2, 3, 24, 25])
        for artifact in ["heatmap.png", "overlay.png"]:
            response = self.client.get(f"/api/runs/{first['id']}/{artifact}", headers=self.headers)
            self.assertEqual(Image.open(BytesIO(response.content)).size, (40, 30))
            self.assertEqual(response.headers["cache-control"], "private, no-store")
        exported = self.client.get(f"/api/projects/{project['id']}/export", headers=self.headers)
        with ZipFile(BytesIO(exported.content)) as archive:
            self.assertIn("project.json", archive.namelist())
            self.assertEqual(len([n for n in archive.namelist() if n.endswith("overlay.png")]), 2)
        self.assertNotIn(b"a"*64, exported.content)

    def test_private_resources_reject_other_or_missing_workspace_keys(self):
        project, asset = self.create()
        for path in [f"/api/projects/{project['id']}", f"/api/assets/{asset['id']}/image"]:
            self.assertEqual(self.client.get(path).status_code, 401)
            self.assertEqual(self.client.get(path, headers={"X-Workspace-Key": "b"*64}).status_code, 404)

    def test_adjustment_becomes_a_separate_revision_and_can_be_compared(self):
        project, asset = self.create(); self.annotate(asset); before = self.run_analysis(asset)
        response = self.client.post(f"/api/assets/{asset['id']}/adjust", headers=self.headers,
                                    json={"label": "Brighter product", "brightness": 1.2, "target_id": "product"})
        self.assertEqual(response.status_code, 201, response.text)
        revision = response.json()
        self.assertNotEqual(revision["id"], asset["id"])
        self.assertFalse(revision["confirmed"])
        self.annotate(revision); after = self.run_analysis(revision)
        comparison = self.client.post("/api/comparisons", headers=self.headers,
                                      json={"before_run_id": before["id"], "after_run_id": after["id"]})
        self.assertEqual(comparison.status_code, 200, comparison.text)
        self.assertEqual(len(comparison.json()["targets"]), 1)

    def test_inference_failure_is_saved_without_a_heatmap(self):
        project, asset = self.create(); self.annotate(asset); self.predictor.fail = True
        response = self.client.post(f"/api/assets/{asset['id']}/analyze", headers=self.headers)
        self.assertEqual(response.status_code, 500)
        runs = self.client.get(f"/api/projects/{project['id']}", headers=self.headers).json()["runs"]
        self.assertEqual(runs[0]["status"], "failed")
        self.assertEqual(self.client.get(f"/api/runs/{runs[0]['id']}/heatmap.png", headers=self.headers).status_code, 404)

    def test_invalid_bounds_and_oversized_requests_are_rejected(self):
        _, asset = self.create()
        response = self.client.put(f"/api/assets/{asset['id']}/targets", headers=self.headers,
            json={"targets": [{"id": "bad", "label": "Bad bounds", "box": [0, 0, 1000, 1000]}]})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.post("/api/projects", headers={**self.headers, "Content-Length": str(15*1024*1024)}).status_code, 413)

    def test_sample_creates_an_annotated_project(self):
        response = self.client.post("/api/samples/forma", headers=self.headers)
        self.assertEqual(response.status_code, 201, response.text)
        self.assertTrue(response.json()["assets"][0]["confirmed"])
        self.assertEqual(len(response.json()["assets"][0]["targets"]), 3)

    def test_target_coordinates_reject_booleans_and_fractional_pixels(self):
        _, asset = self.create()
        for box in [[True, 0, 10, 10], [0, 0, 10.5, 10]]:
            response = self.client.put(f"/api/assets/{asset['id']}/targets", headers=self.headers,
                json={"targets": [{"id": "bad", "label": "Bad coordinate", "box": box}]})
            self.assertEqual(response.status_code, 422)
