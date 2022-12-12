from typing import Any, Optional, Union
from urllib.parse import urlparse, urlunparse

from django.http import HttpRequest
from rest_framework.request import Request

DjangoRequest = Union[Request, HttpRequest]


def get_client_ip(request: DjangoRequest) -> Optional[str]:
    """Get the client IP address from the given request, parsing various HTTP request headers to
    determine the IP if traffic is being routed through a standards-adherent proxy.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_client_user_agent(request: DjangoRequest) -> Optional[str]:
    """Get the contents of the User-Agent header in the request if such a header exists."""
    return request.META.get("HTTP_USER_AGENT")


def get_request_host(request: DjangoRequest) -> str:
    """Get the contents of the HTTP Host header in the request."""
    return request.META["HTTP_HOST"]


def get_request_metadata(request: DjangoRequest) -> dict[str, Any]:
    """Review the content of the given rest framework request and return a dictionary of metadata
    about the request.
    """
    return {
        "ip": get_client_ip(request=request),
        "user_agent": get_client_user_agent(request=request),
    }


def get_redirect_target_from_request(
    request: DjangoRequest, from_domain: str, to_domain: str
) -> str:
    """Process the given request and produce a URL that our landing page should redirect to."""
    absolute_uri = request.build_absolute_uri()
    parsed = urlparse(absolute_uri)
    return urlunparse(
        parsed._replace(netloc=parsed.netloc.replace(from_domain, to_domain))
    )
