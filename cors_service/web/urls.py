from django.urls import path

from web.views import api, web

urlpatterns = [
    path("api/success", api.cors_success, name="cors_success"),
    path("api/failure", api.cors_failure, name="cors_failure"),
    path("web", web.index, name="web_index"),
    path("api", api.index, name="api_index"),
]
