from pathlib import Path

from PIL import Image, ImageOps


def load_image(path: str | Path) -> Image.Image:
    """Load a static PNG/JPEG as an independent, oriented RGB image.

    Transparent pixels are composited onto white. No resizing or cropping is
    performed; EXIF orientation can swap width and height. Source bytes are
    unchanged. Unsupported formats and animation raise ValueError; file and
    decoding errors propagate from Pillow.
    """
    with Image.open(path) as image:
        # Check before transformations: copies may no longer retain format info.
        if image.format not in {"PNG", "JPEG"}:
            raise ValueError(
                f"Unsupported image format: {image.format}. Use PNG or JPEG."
            )
        if getattr(image, "is_animated", False):
            raise ValueError("Animated images are not supported. Use a static ad.")

        oriented = ImageOps.exif_transpose(image)
        foreground = oriented.convert("RGBA")
        background = Image.new("RGBA", foreground.size, (255, 255, 255, 255))
        return Image.alpha_composite(background, foreground).convert("RGB")
