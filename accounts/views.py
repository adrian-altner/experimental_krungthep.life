from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from wagtail.users.models import UserProfile

@login_required
@require_POST
def avatar_upload(request, user_id):
    User = get_user_model()
    user = User.objects.filter(pk=user_id).first()
    if not user:
        return HttpResponseForbidden("User not found.")

    can_edit = request.user == user or request.user.is_superuser
    if not can_edit:
        can_edit = request.user.has_perm("wagtailusers.change_user")
    if not can_edit:
        return HttpResponseForbidden("Not allowed.")

    if request.POST.get("avatar-avatar-clear"):
        profile = UserProfile.get_for_user(user)
        profile.avatar.delete(save=False)
        profile.avatar = None
        profile.save(update_fields=["avatar"])
        return _avatar_response(request, user, "Avatar reset.")

    avatar = request.FILES.get("avatar") or request.FILES.get("avatar-avatar")
    if not avatar:
        return _avatar_response(request, user, "No file selected.")

    profile = UserProfile.get_for_user(user)
    profile.avatar = avatar
    profile.save(update_fields=["avatar"])
    profile.refresh_from_db()

    return _avatar_response(request, user, "Avatar updated.")


def _avatar_response(request, user, message):
    if request.headers.get("HX-Request") == "true":
        template = (
            "accounts/_account_avatar_status.html"
            if request.GET.get("context") == "account"
            else "accounts/_avatar_status.html"
        )
        return render(
            request,
            template,
            {
                "avatar_user": user,
                "status_message": message,
            },
        )
    return redirect(request.META.get("HTTP_REFERER", "/"))
