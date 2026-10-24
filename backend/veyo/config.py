"""Environment-owned application configuration, with safe local defaults."""
from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    storage_dir: Path
    bucket: str | None
    allowed_origins: tuple[str, ...]
    max_upload_bytes: int = 12 * 1024 * 1024
    max_pixels: int = 12_000_000
    model_max_side: int = 1600
    threads: int = 4

    @classmethod
    def from_env(cls):
        return cls(
            storage_dir=Path(os.getenv("VEYO_STORAGE_DIR", "../storage")),
            bucket=os.getenv("VEYO_GCS_BUCKET") or None,
            allowed_origins=tuple(x.strip() for x in os.getenv(
                "VEYO_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
            ).split(",") if x.strip()),
            threads=int(os.getenv("VEYO_THREADS", "4")),
        )
