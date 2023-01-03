from typing import Optional

import pytest
from django.test.client import Client


def create_default_client(auth_token: Optional[str] = None) -> Client:
    """Create and return an HTTP-esque client for use in testing live HTTP endpoints in
    unit tests.
    """
    kwargs = {
        "HTTP_CONTENT_TYPE": "application/json",
        "HTTP_USER_AGENT": "hello user agent",
    }
    if auth_token:
        kwargs["HTTP_AUTHORIZATION"] = f"Token {auth_token}"
    return Client(**kwargs)  # type: ignore[arg-type]


@pytest.fixture
def unauthed_client() -> Client:
    """Test fixture for providing an HTTP client that is not authenticated."""
    return create_default_client()
