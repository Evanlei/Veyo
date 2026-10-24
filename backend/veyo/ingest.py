"""Bound upload bytes, decoded image size, and model work before inference."""
from io import BytesIO
import hashlib
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError
from .config import Settings


def decode_upload(data: bytes, settings: Settings) -> tuple[Image.Image, dict]:
    if not data or len(data) > settings.max_upload_bytes:
        raise ValueError("Upload a PNG or JPEG smaller than 12 MB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as src:
                if src.format not in {"PNG", "JPEG"} or getattr(src, "is_animated", False):
                    raise ValueError("Only static PNG and JPEG images are supported.")
                if src.width * src.height > settings.max_pixels:
                    raise ValueError("Image exceeds the 12 megapixel limit.")
                rgba = ImageOps.exif_transpose(src).convert("RGBA")
                white = Image.new("RGBA", rgba.size, "white")
                image = Image.alpha_composite(white, rgba).convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as exc:
        raise ValueError("This image cannot be decoded safely. Choose a valid PNG or JPEG.") from exc
    original_size = image.size
    image.thumbnail((settings.model_max_side, settings.model_max_side), Image.Resampling.LANCZOS)
    return image, {"source_sha256": hashlib.sha256(data).hexdigest(),
                   "source_width": original_size[0], "source_height": original_size[1],
                   "resized": image.size != original_size}


def png_bytes(image: Image.Image) -> bytes:
    out = BytesIO()
    image.save(out, "PNG")
    return out.getvalue()
