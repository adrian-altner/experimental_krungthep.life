from __future__ import annotations

from io import BytesIO
from pathlib import Path
from uuid import uuid4

from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify
from PIL import Image, ImageOps
from wagtail.images.models import (
    AbstractImage,
    AbstractRendition,
    WagtailImageField,
)
from wagtail.models import Page


def image_upload_to(instance: "CustomImage", filename: str) -> str:
    base_name = slugify(Path(filename).stem) or "image"
    unique_suffix = uuid4().hex[:8]
    if instance.source_page_id:
        page_slug = slugify(instance.source_page.slug) or "page"
        folder = f"images/pages/{instance.source_page_id}-{page_slug}"
    else:
        folder = "images/unassigned"
    return f"{folder}/{base_name}-{unique_suffix}.webp"


def rendition_upload_to(instance: "CustomRendition", filename: str) -> str:
    base = Path(filename).stem
    ext = Path(filename).suffix or ".webp"
    unique_suffix = uuid4().hex[:8]
    safe_base = slugify(base) or "rendition"
    return f"images/cache/{safe_base}-{unique_suffix}{ext}"


class CustomImage(AbstractImage):
    file = WagtailImageField(
        upload_to=image_upload_to,
        width_field="width",
        height_field="height",
    )
    source_page = models.ForeignKey(
        Page,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    admin_form_fields = (
        "title",
        "file",
        "description",
        "collection",
        "tags",
        "focal_point_x",
        "focal_point_y",
        "focal_point_width",
        "focal_point_height",
        "source_page",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_file_name = self.file.name if self.file else None
        self._original_source_page_id = self.source_page_id

    def save(self, *args, **kwargs):
        file_name = self.file.name if self.file else None
        file_changed = file_name and file_name != self._original_file_name
        not_webp = file_name and not file_name.lower().endswith(".webp")
        source_page_changed = self.source_page_id != self._original_source_page_id
        missing_dimensions = self.width is None or self.height is None

        if self.file and (
            file_changed or not_webp or source_page_changed or missing_dimensions
        ):
            self._ensure_webp_and_location()

        super().save(*args, **kwargs)

        self._original_file_name = self.file.name if self.file else None
        self._original_source_page_id = self.source_page_id

    def _ensure_webp_and_location(self) -> None:
        old_name = self.file.name if self.file else None
        file_name = Path(self.file.name).name if self.file else "image"
        target_name = f"{slugify(Path(file_name).stem) or 'image'}.webp"

        if self.file.name.lower().endswith(".webp"):
            self.file.open("rb")
            data = self.file.read()
            self.file.seek(0)
            image = Image.open(self.file)
            image = ImageOps.exif_transpose(image)
            width, height = image.size
            self.file.close()
        else:
            self.file.open("rb")
            image = Image.open(self.file)
            image = ImageOps.exif_transpose(image)
            if image.mode in ("RGBA", "LA"):
                image = image.convert("RGBA")
            else:
                image = image.convert("RGB")
            width, height = image.size
            buffer = BytesIO()
            image.save(buffer, format="WEBP", quality=85, method=6)
            data = buffer.getvalue()
            self.file.close()

        self.file.save(target_name, ContentFile(data), save=False)
        self.width = width
        self.height = height
        self._set_image_file_metadata()

        if old_name and old_name != self.file.name:
            storage = self.file.storage
            if storage.exists(old_name):
                storage.delete(old_name)

    class Meta(AbstractImage.Meta):
        verbose_name = "image"
        verbose_name_plural = "images"


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage,
        on_delete=models.CASCADE,
        related_name="renditions",
    )

    def get_upload_to(self, filename):
        return rendition_upload_to(self, filename)

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
