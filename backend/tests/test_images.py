"""Image-contract checks using small pixel fixtures, not model predictions."""
import tempfile
import unittest
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from veyo.images import load_image


class LoadImageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def test_jpeg_accepts_string_path_and_returns_independent_image(self):
        path = self.root / "ad.jpg"
        Image.new("RGB", (7, 5), (90, 120, 150)).save(path)
        with Image.open(path) as source:
            expected = source.copy()
        result = load_image(str(path))
        path.unlink()
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (7, 5))
        self.assertEqual(result.mode, "RGB")
        self.assertEqual(result.tobytes(), expected.tobytes())

    def test_opaque_png_preserves_pixels_and_source_file(self):
        path = self.root / "ad.png"
        original = Image.new("RGB", (3, 2), (10, 20, 30))
        original.putpixel((2, 1), (200, 150, 100))
        original.save(path)
        before = path.read_bytes()
        result = load_image(path)
        self.assertEqual(result.tobytes(), original.tobytes())
        self.assertEqual(path.read_bytes(), before)

    def test_transparency_blends_over_white_instead_of_discarding_alpha(self):
        path = self.root / "transparent.png"
        image = Image.new("RGBA", (3, 1))
        image.putdata([(0, 0, 0, 0), (255, 0, 0, 128), (0, 0, 255, 255)])
        image.save(path)
        result = load_image(path)
        self.assertEqual(result.mode, "RGB")
        self.assertEqual(result.getpixel((0, 0)), (255, 255, 255))
        self.assertEqual(result.getpixel((1, 0)), (255, 127, 127))
        self.assertEqual(result.getpixel((2, 0)), (0, 0, 255))

    def test_palette_transparency_is_preserved_during_compositing(self):
        path = self.root / "palette.png"
        image = Image.new("P", (2, 1))
        image.putpalette([0, 0, 0, 0, 255, 0] + [0] * (768 - 6))
        image.putdata([0, 1])
        image.save(path, transparency=0)
        result = load_image(path)
        self.assertEqual(result.getpixel((0, 0)), (255, 255, 255))
        self.assertEqual(result.getpixel((1, 0)), (0, 255, 0))

    def test_grayscale_becomes_rgb(self):
        path = self.root / "gray.png"
        Image.new("L", (2, 3), 80).save(path)
        result = load_image(path)
        self.assertEqual(result.mode, "RGB")
        self.assertEqual(result.size, (2, 3))
        self.assertEqual(result.getpixel((0, 0)), (80, 80, 80))

    def test_exif_rotation_and_mirroring_map_pixels_correctly(self):
        # Red-channel IDs make every pixel's expected location unambiguous.
        cases = [(6, (3, 2), [5, 3, 1, 6, 4, 2]),
                 (2, (2, 3), [2, 1, 4, 3, 6, 5])]
        for orientation, expected_size, expected_ids in cases:
            with self.subTest(orientation=orientation):
                path = self.root / f"oriented-{orientation}.png"
                image = Image.new("RGB", (2, 3))
                image.putdata([(i, 0, 0) for i in range(1, 7)])
                exif = Image.Exif()
                exif[274] = orientation
                image.save(path, exif=exif)
                result = load_image(path)
                self.assertEqual(result.size, expected_size)
                pixels = [result.getpixel((x, y))[0]
                          for y in range(result.height)
                          for x in range(result.width)]
                self.assertEqual(pixels, expected_ids)
                self.assertNotIn(274, result.getexif())

    def test_content_determines_format_not_extension(self):
        disguised = self.root / "not-really-jpeg.jpg"
        Image.new("RGB", (2, 2)).save(disguised, format="GIF")
        with self.assertRaisesRegex(ValueError, "Unsupported image format: GIF"):
            load_image(disguised)
        valid = self.root / "valid-image.bin"
        Image.new("RGB", (2, 2)).save(valid, format="PNG")
        self.assertEqual(load_image(valid).size, (2, 2))

    def test_animated_png_is_rejected(self):
        path = self.root / "animated.png"
        Image.new("RGB", (2, 2), "red").save(
            path, save_all=True,
            append_images=[Image.new("RGB", (2, 2), "blue")], duration=100,
        )
        with self.assertRaisesRegex(ValueError, "Animated images"):
            load_image(path)

    def test_non_image_file_is_rejected(self):
        path = self.root / "invalid.png"
        path.write_bytes(b"This is not an image")
        with self.assertRaises(UnidentifiedImageError):
            load_image(path)

    def test_truncated_jpeg_is_rejected(self):
        path = self.root / "truncated.jpg"
        Image.new("RGB", (40, 40), "red").save(path)
        path.write_bytes(path.read_bytes()[:-20])
        with self.assertRaises(OSError):
            load_image(path)

    def test_missing_file_error_is_preserved(self):
        with self.assertRaises(FileNotFoundError):
            load_image(self.root / "missing.jpg")


if __name__ == "__main__":
    unittest.main()
