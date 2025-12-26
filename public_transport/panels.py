from django.apps import apps
from wagtail.admin.panels import Panel
from wagtail.models import Page


class ParentLinePanel(Panel):
    class BoundPanel(Panel.BoundPanel):
        template_name = "public_transport/admin/parent_line_panel.html"

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context=parent_context)
            parent_line = None
            parent_system = None
            PublicTransportLinePage = apps.get_model(
                "public_transport", "PublicTransportLinePage"
            )
            PublicTransportSystemPage = apps.get_model(
                "public_transport", "PublicTransportSystemPage"
            )
            if self.instance and self.instance.get_parent():
                parent = self.instance.get_parent().specific
                if isinstance(parent, PublicTransportLinePage):
                    parent_line = parent
                if isinstance(parent, PublicTransportSystemPage):
                    parent_system = parent

            if not parent_line and self.request and self.request.resolver_match:
                parent_id = self.request.resolver_match.kwargs.get("parent_page_id")
                if parent_id:
                    page = Page.objects.filter(id=parent_id).first()
                    if page and isinstance(page.specific, PublicTransportLinePage):
                        parent_line = page.specific
                    if page and isinstance(page.specific, PublicTransportSystemPage):
                        parent_system = page.specific

            context["parent_line"] = parent_line
            context["parent_system"] = parent_system
            return context
