"""Google Cloud Storage adapter: durable files and JSON, without a database."""
import json
from .store import safe_key


class CloudStore:
    def __init__(self, bucket_name: str):
        from google.cloud import storage
        self.bucket = storage.Client().bucket(bucket_name)

    def put(self, key: str, data: bytes, content_type="application/octet-stream"):
        self.bucket.blob(safe_key(key)).upload_from_string(data, content_type=content_type)

    def get(self, key: str) -> bytes:
        from google.api_core.exceptions import NotFound
        try:
            return self.bucket.blob(safe_key(key)).download_as_bytes()
        except NotFound as exc:
            raise FileNotFoundError(key) from exc

    def keys(self, prefix: str) -> list[str]:
        return sorted(b.name for b in self.bucket.list_blobs(prefix=safe_key(prefix).rstrip("/") + "/"))

    def delete(self, key: str):
        from google.api_core.exceptions import NotFound
        try:
            self.bucket.blob(safe_key(key)).delete()
        except NotFound:
            pass

    def json(self, key: str) -> dict:
        return json.loads(self.get(key))

    def put_json(self, key: str, value: dict):
        self.put(key, (json.dumps(value, allow_nan=False) + "\n").encode(), "application/json")
