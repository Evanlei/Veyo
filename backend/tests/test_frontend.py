"""Production routing must serve deep links without hiding API or asset failures."""
from pathlib import Path
import tempfile
import unittest
from fastapi.testclient import TestClient
from veyo.app import create_app
from veyo.config import Settings


class FrontendTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        root = Path(self.directory.name)
        self.frontend = root / "dist"
        (self.frontend / "assets").mkdir(parents=True)
        (self.frontend / "index.html").write_text("<!doctype html><title>Veyo test shell</title>")
        (self.frontend / "assets" / "app-abc123.js").write_text("console.log('Veyo');")
        (root / "private.txt").write_text("must not be served")
        settings = Settings(root / "storage", None, (), frontend_dir=self.frontend)
        self.client = TestClient(create_app(settings))

    def tearDown(self):
        self.client.close()
        self.directory.cleanup()

    def test_shell_and_deep_links_are_refreshable(self):
        for path in ("/", "/index.html", "/guide", "/settings", "/creative/project-123", "/compare/project-123"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertIn("Veyo test shell", response.text)
            self.assertEqual(response.headers["cache-control"], "no-cache")
            self.assertIn("frame-ancestors 'none'", response.headers["content-security-policy"])
        self.assertEqual(self.client.head("/guide").status_code, 200)
        self.assertEqual(self.client.post("/guide").status_code, 405)

    def test_hashed_assets_are_cacheable_but_missing_assets_are_not_html(self):
        response = self.client.get("/assets/app-abc123.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn("immutable", response.headers["cache-control"])
        for path in ("/assets/missing.js", "/missing.png", "/.env", "/%2e%2e/private.txt"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 404, path)
            self.assertNotIn("Veyo test shell", response.text)
            self.assertNotIn("must not be served", response.text)

    def test_api_health_authentication_and_404s_keep_their_json_contract(self):
        # A build directory cannot shadow an unknown API endpoint.
        (self.frontend / "api").mkdir()
        (self.frontend / "api" / "missing").write_text("wrong content")
        for path, status in (("/api/health", 200), ("/api/projects", 401), ("/api/missing", 404), ("/api", 404)):
            response = self.client.get(path)
            self.assertEqual(response.status_code, status, path)
            self.assertIn("application/json", response.headers["content-type"])
            self.assertEqual(response.headers["cache-control"], "private, no-store")
