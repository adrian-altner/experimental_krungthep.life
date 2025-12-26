from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import (
    BooleanColumn,
    BulkActionsCheckboxColumn,
    Column,
    DateColumn,
)
from wagtail.admin.utils import get_user_display_name
from wagtail.users.views.users import IndexView, UserColumn, UserViewSet

from .wagtail_forms import CustomUserCreationForm, CustomUserEditForm


class CustomUserIndexView(IndexView):
    @cached_property
    def columns(self):
        _UserColumn = self._get_title_column_class(UserColumn)
        name_sort = "name" if self.model_fields.issuperset({"first_name", "last_name"}) else None
        email_sort = "email" if "email" in self.model_fields else None
        return [
            BulkActionsCheckboxColumn("bulk_actions", obj_type="user"),
            _UserColumn(
                "name",
                accessor=lambda u: get_user_display_name(u),
                label=_("Name"),
                sort_key=name_sort,
                get_url=self.get_edit_url,
                classname="name",
            ),
            Column(
                "email",
                accessor="email",
                label=_("Email"),
                sort_key=email_sort,
                classname="email",
                width="25%",
            ),
            Column(
                "is_superuser",
                accessor=lambda u: _("Admin") if u.is_superuser else None,
                label=_("Access level"),
                sort_key="is_superuser",
                classname="level",
                width="10%",
            ),
            BooleanColumn(
                "is_active",
                label=_("Active"),
                sort_key="is_active" if "is_active" in self.model_fields else None,
                classname="status",
                width="10%",
            ),
            DateColumn(
                "last_login",
                label=_("Last login"),
                sort_key="last_login",
                classname="last-login",
                width="15%",
            ),
        ]


class CustomUserViewSet(UserViewSet):
    index_view_class = CustomUserIndexView

    def get_form_class(self, for_update=False):
        if for_update:
            return CustomUserEditForm
        return CustomUserCreationForm
