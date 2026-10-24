"""Persistence and tenant-boundary tests; no inference or cloud calls."""
import json
from pathlib import Path
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from veyo.store import LocalStore, safe_key
from veyo.repository import Repository
from veyo.identity import workspace_id


class StoreTests(unittest.TestCase):
    def test_rejects_traversal_and_absolute_keys(self):
        for key in ["../secret", "/etc/passwd", "a/../../b", "a\\b", ""]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                safe_key(key)

    def test_atomic_records_remain_complete_under_competing_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            store = LocalStore(Path(directory))
            records = [{"writer": i, "payload": "x"*5000} for i in range(20)]
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(lambda record: store.put_json("records/example.json", record), records))
            self.assertIn(store.json("records/example.json"), records)
            self.assertEqual(store.keys("records"), ["records/example.json"])

    def test_workspaces_cannot_read_each_others_resources(self):
        with tempfile.TemporaryDirectory() as directory:
            store = LocalStore(Path(directory))
            one = Repository(store, workspace_id("a"*64))
            two = Repository(store, workspace_id("b"*64))
            project = one.create_project("Private creative")
            self.assertEqual(two.list("projects"), [])
            with self.assertRaises(FileNotFoundError):
                two.get("projects", project["id"])
            self.assertNotIn("a"*64, store.get(one.key("projects", project["id"])).decode())

    def test_metadata_never_serializes_nonfinite_numbers(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                LocalStore(Path(directory)).put_json("bad.json", {"score": float("nan")})
