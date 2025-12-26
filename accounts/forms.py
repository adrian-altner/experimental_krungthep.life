from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "author_slug",
            "bio",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )
