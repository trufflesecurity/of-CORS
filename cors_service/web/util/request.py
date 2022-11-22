from typing import Any, Optional

from rest_framework.request import Request


def get_client_ip(request: Request) -> Optional[str]:
    """Get the client IP address from the given request, parsing various HTTP request headers to
    determine the IP if traffic is being routed through a standards-adherent proxy.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_request_host(request: Request) -> str:
    """Get the contents of the HTTP Host header in the request."""
    return request.META["HTTP_HOST"]


def get_request_metadata(request: Request) -> dict[str, Any]:
    """Review the content of the given rest framework request and return a dictionary of metadata
    about the request.
    """
    return {
        "ip": get_client_ip(request=request),
        "user_agent": request.META.get("HTTP_USER_AGENT"),
    }
