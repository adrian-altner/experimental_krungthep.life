from wagtail import hooks


@hooks.register("insert_global_admin_css")
def blog_admin_css():
    return '<link rel="stylesheet" href="/static/css/blog-admin.css">'
