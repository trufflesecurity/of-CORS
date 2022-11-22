from django.http import HttpRequest, HttpResponse

from web.logic.targets import TargetManager


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello world")


def service_worker_payload(request: HttpRequest) -> HttpResponse:
    """Generate and serve the service worker payload for the subdomains mapped to the
    host present in the given HTTP request.
    """
    TargetManager.get_all_internal_subdomains_for_parent_domain(parent_domain="foo")
    return HttpResponse("Hello world")
