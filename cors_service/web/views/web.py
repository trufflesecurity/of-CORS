from typing import Any, Optional

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from web.logic.targets import TargetManager
from web.models.target import HostDomain
from web.util.request import get_redirect_target_from_request, get_request_host


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello world")


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
    redirect_ms: int = settings.JS_REDIRECT_MS,
    include_payload_targets: bool = False,
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
        template_name="web/landing.html",
        context={},
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


def service_worker_payload(request: HttpRequest) -> HttpResponse:
    """Generate and serve the service worker payload for the subdomains mapped to the
    host present in the given HTTP request.
    """
    TargetManager.get_all_internal_subdomains_for_parent_domain(parent_domain="foo")
    return HttpResponse("Hello world")
