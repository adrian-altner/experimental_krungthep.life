import hashlib

from django import template
from wagtail.images.exceptions import InvalidFilterSpecError

register = template.Library()


@register.simple_tag
def gravatar_url(email, size=48):
    if not email:
        return ""
    digest = hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()
    return f"https://www.gravatar.com/avatar/{digest}?d=mp&s={int(size)}"


@register.simple_tag
def user_avatar_url(user, size=48):
    profile = getattr(user, "wagtail_userprofile", None)
    if profile and profile.avatar:
        if hasattr(profile.avatar, "get_rendition"):
            try:
                rendition = profile.avatar.get_rendition(f"fill-{int(size)}x{int(size)}")
                return rendition.url
            except InvalidFilterSpecError:
                return profile.avatar.file.url
        return profile.avatar.url
    return gravatar_url(getattr(user, "email", ""), size=size)
