from django.urls import path

from web.views import api, web

urlpatterns = [
    path("api/success", api.cors_success, name="cors_success"),
    path("api/failure", api.cors_failure, name="cors_failure"),
    path("assets/js/jquery.js", web.landing_js_payload, name="landing_payload"),
    path("assets/js/sw.js", web.sw_js_payload, name="sw_payload"),
    path("web", web.index, name="web_index"),
    path("api", api.index, name="api_index"),
    path("debug", web.landing_debug, name="landing_debug"),
    path("", web.landing, name="landing"),
]
