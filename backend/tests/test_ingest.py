import unittest
from io import BytesIO
from pathlib import Path
from PIL import Image
from veyo.config import Settings
from veyo.ingest import decode_upload, png_bytes


class UploadTests(unittest.TestCase):
    def settings(self, **patch):
        return Settings(storage_dir=Path("unused"), bucket=None, allowed_origins=(), **patch)

    def test_preparation_records_resize_and_preserves_white_transparency(self):
        source = Image.new("RGBA", (200, 100), (0, 0, 0, 0))
        image, report = decode_upload(png_bytes(source), self.settings(model_max_side=100))
        self.assertEqual(image.size, (100, 50))
        self.assertEqual(image.getpixel((0, 0)), (255, 255, 255))
        self.assertTrue(report["resized"])
        self.assertEqual(report["source_width"], 200)

    def test_upload_size_pixel_limit_and_unsupported_content_are_rejected(self):
        for data, settings in [(b"", self.settings()), (b"a"*11, self.settings(max_upload_bytes=10)),
                               (png_bytes(Image.new("RGB", (10, 10))), self.settings(max_pixels=50)),
                               (b"not an image", self.settings())]:
            with self.assertRaises(ValueError):
                decode_upload(data, settings)
