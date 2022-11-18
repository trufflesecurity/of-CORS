from django.urls import path

from web.views import api, web

urlpatterns = [
    path("web", web.index, name="web_index"),
    path("api", api.index, name="api_index"),
]
