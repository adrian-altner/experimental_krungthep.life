from __future__ import annotations

from typing import Any

from django.db import models
from wagtail.fields import StreamField
from wagtail.images import get_image_model


def _collect_image_ids(value: Any, image_ids: set[int]) -> None:
    if isinstance(value, dict):
        block_type = value.get("type")
        if block_type == "image":
            image_id = value.get("value")
            if isinstance(image_id, int):
                image_ids.add(image_id)
        elif block_type is not None:
            nested_value = value.get("value")
            _collect_image_ids(nested_value, image_ids)
        else:
            for item in value.values():
                _collect_image_ids(item, image_ids)
        return

    if isinstance(value, list):
        for item in value:
            _collect_image_ids(item, image_ids)


def assign_page_images(page: models.Model) -> None:
    ImageModel = get_image_model()
    if not hasattr(ImageModel, "source_page"):
        return

    image_ids: set[int] = set()

    for field in page._meta.fields:
        if isinstance(field, models.ForeignKey) and field.related_model == ImageModel:
            image_id = getattr(page, f"{field.name}_id", None)
            if image_id:
                image_ids.add(image_id)
        elif isinstance(field, StreamField):
            stream_value = getattr(page, field.name)
            raw_data = getattr(stream_value, "raw_data", None)
            if raw_data:
                _collect_image_ids(raw_data, image_ids)

    if not image_ids:
        return

    images = ImageModel.objects.filter(id__in=image_ids, source_page__isnull=True)
    for image in images:
        image.source_page = page
        image.save()
