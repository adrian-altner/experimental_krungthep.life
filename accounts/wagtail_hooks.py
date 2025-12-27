from django import forms
from django.contrib.auth import get_user_model
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from wagtail import hooks
from wagtail.admin.views.account import BaseSettingsPanel, profile_tab


class BioForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["author_slug", "bio"]


class BioSettingsPanel(BaseSettingsPanel):
    name = "bio"
    title = _("Bio")
    order = 150
    tab = profile_tab
    form_class = BioForm


@hooks.register("register_account_settings_panel")
def register_bio_panel(request, user, profile):
    return BioSettingsPanel(request, user, profile)


@hooks.register("insert_global_admin_css")
def add_user_admin_css():
    return '<link rel="stylesheet" href="/static/accounts/css/admin.css">'


@hooks.register("insert_global_admin_js")
def add_admin_htmx():
    return format_html(
        '<script type="module" src="{}"></script>',
        static("vite/app.js"),
    )
