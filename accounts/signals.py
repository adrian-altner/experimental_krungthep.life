from __future__ import annotations

from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image, ImageOps
from wagtail.users.models import UserProfile


@receiver(post_save, sender=UserProfile)
def convert_avatar_to_webp(sender, instance: UserProfile, **kwargs):
    if getattr(instance, "_processing_avatar", False):
        return
    if not instance.avatar:
        return

    current_name = instance.avatar.name
    if current_name.lower().endswith(".webp"):
        return

    instance._processing_avatar = True
    storage = instance.avatar.storage
    old_name = current_name

    try:
        instance.avatar.open("rb")
        image = Image.open(instance.avatar)
        image = ImageOps.exif_transpose(image)
        if image.mode in ("RGBA", "LA"):
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")
        buffer = BytesIO()
        image.save(buffer, format="WEBP", quality=85, method=6)
        data = buffer.getvalue()
    finally:
        try:
            instance.avatar.close()
        except Exception:
            pass

    base = Path(old_name).stem
    folder = Path(old_name).parent
    new_name = str(folder / f"{base}.webp")

    instance.avatar.save(new_name, ContentFile(data), save=False)
    instance.save(update_fields=["avatar"])

    if storage.exists(old_name):
        storage.delete(old_name)
