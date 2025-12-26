from wagtail import hooks

from public_transport import snippets  # noqa: F401


@hooks.register("insert_editor_js")
def station_title_sync_js():
    return '<script src="/static/public_transport/js/station_title_sync.js"></script>'
