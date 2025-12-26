from typing import cast

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.text import slugify
from wagtail import blocks
from wagtail.fields import StreamField


class CustomUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        username = username or email
        return cast(UserManager, super())._create_user(  # type: ignore[attr-defined]
            username,
            email,
            password,
            **extra_fields,
        )

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Minimal custom user model.
    Extend later with additional fields if needed.
    """
    email = models.EmailField("email address", unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    author_slug = models.SlugField(max_length=160, unique=True, blank=True, null=True)
    bio = StreamField(
        [
            ("paragraph", blocks.RichTextBlock()),
        ],
        blank=True,
        use_json_field=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        if not self.author_slug:
            base = slugify(self.get_full_name()) or slugify(self.username or "") or "user"
            slug = base
            suffix = 2
            while User.objects.filter(author_slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{suffix}"
                suffix += 1
            self.author_slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        full_name = self.get_full_name()
        return full_name or self.email
