"""Utility functions for the academics app."""

from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image


def generate_thumbnail(image_field, size=(150, 150)):
    """
    Generate a thumbnail from an ImageField.

    Args:
        image_field: Django ImageField instance
        size: Tuple of (width, height) for the thumbnail

    Returns:
        ContentFile containing the thumbnail image, or None if no image
    """
    if not image_field:
        return None

    try:
        # Open the image
        img = Image.open(image_field)

        # Convert RGBA to RGB if necessary (for PNG with transparency)
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background

        # Create thumbnail
        img.thumbnail(size, Image.Resampling.LANCZOS)

        # Save to BytesIO
        thumb_io = BytesIO()
        img.save(thumb_io, format="JPEG", quality=85)
        thumb_io.seek(0)

        # Generate filename
        original_name = Path(image_field.name).stem
        thumb_name = f"{original_name}_thumb.jpg"

        return ContentFile(thumb_io.read(), name=thumb_name)

    except Exception:
        # If thumbnail generation fails, return None
        return None


def get_thumbnail_url(student, default="/static/images/default-avatar.png"):
    """
    Get the thumbnail URL for a student's photo.

    Args:
        student: Student model instance
        default: Default image URL if no photo exists

    Returns:
        URL string for the thumbnail or default image
    """
    if student.photo:
        return student.photo.url
    return default
