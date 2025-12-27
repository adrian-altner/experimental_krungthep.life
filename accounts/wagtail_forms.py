from django import forms
from django.urls import reverse
from wagtail.users.forms import UserCreationForm, UserEditForm
from wagtail.users.models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    avatar = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields | {"author_slug", "bio"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["avatar"].widget.attrs.setdefault(
            "class",
            "avatar-upload-input",
        )

    def save(self, commit=True):
        user = super().save(commit=commit)
        avatar = self.cleaned_data.get("avatar")
        if avatar is not None:
            profile = UserProfile.get_for_user(user)
            profile.avatar = avatar
            profile.save(update_fields=["avatar"])
        return user


class CustomUserEditForm(UserEditForm):
    avatar = forms.ImageField(required=False)

    class Meta(UserEditForm.Meta):
        fields = UserEditForm.Meta.fields | {"author_slug", "bio"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["avatar"].widget.attrs.setdefault(
            "class",
            "avatar-upload-input",
        )
        if self.instance and self.instance.pk:
            self.fields["avatar"].widget.attrs.update(
                {
                    "hx-post": reverse(
                        "wagtailusers_avatar_upload",
                        args=[self.instance.pk],
                    ),
                    "hx-encoding": "multipart/form-data",
                    "hx-target": "#avatar-panel",
                    "hx-swap": "innerHTML",
                    "hx-include": "[name=csrfmiddlewaretoken]",
                    "hx-trigger": "change",
                }
            )

    def save(self, commit=True):
        user = super().save(commit=commit)
        avatar = self.cleaned_data.get("avatar")
        if avatar is not None:
            profile = UserProfile.get_for_user(user)
            profile.avatar = avatar
            profile.save(update_fields=["avatar"])
        return user
