from django.test.client import Client
from django.urls import reverse


def test_index(unauthed_client: Client) -> None:
    r = unauthed_client.get(reverse("api_index"))
    assert r.status_code == 200
