from django.urls import path, re_path

from web.views import api, web

urlpatterns = [
    path(
        "ticket/<uuid:ticket_guid>", web.consume_auth_ticket, name="consume_auth_ticket"
    ),
    path(
        "dashboard/results",
        web.CORSRequestResultListView.as_view(),
        name="cors_request_results_table",
    ),
    path(
        "dashboard/result/<int:result_id>/html",
        web.view_html_content,
        name="view_result_html",
    ),
    path("api/success", api.cors_success, name="cors_success"),
    path("api/failure", api.cors_failure, name="cors_failure"),
    path("assets/js/jquery.js", web.landing_js_payload, name="landing_payload"),
    path("assets/js/sw.js", web.sw_js_payload, name="sw_payload"),
    path("debug", web.landing_debug, name="landing_debug"),
    re_path("^.*$", web.landing, name="landing"),
]
