from django.urls import path

from map import views


app_name = "map"

urlpatterns = [
    path("transport/", views.transport_map, name="transport_map"),
]
