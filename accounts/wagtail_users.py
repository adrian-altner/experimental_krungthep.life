from wagtail.users.apps import WagtailUsersAppConfig


class CustomWagtailUsersAppConfig(WagtailUsersAppConfig):
    user_viewset = "accounts.wagtail_viewsets.CustomUserViewSet"
