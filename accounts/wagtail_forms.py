from django import forms
from wagtail.users.forms import UserCreationForm, UserEditForm
from wagtail.users.models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    avatar = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields | {"author_slug", "bio"}

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

    def save(self, commit=True):
        user = super().save(commit=commit)
        avatar = self.cleaned_data.get("avatar")
        if avatar is not None:
            profile = UserProfile.get_for_user(user)
            profile.avatar = avatar
            profile.save(update_fields=["avatar"])
        return user
