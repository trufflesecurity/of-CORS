from base64 import b64encode

from django.test.client import Client
from django.urls import reverse
from faker import Faker

f = Faker()


def test_index(unauthed_client: Client) -> None:
    r = unauthed_client.get(reverse("api_index"))
    assert r.status_code == 200


class TestCORSSuccess:
    """Container class for all unit tests related to the cors_success endpoint."""

    def test_cors_success_no_url(self, unauthed_client: Client) -> None:
        """Tests that cors_success behaves as expected when it's missing the url POST argument."""
        r = unauthed_client.post(
            reverse("cors_success"),
            data={
                "content": b64encode("hello world".encode("utf-8")).decode("utf-8"),
                "duration": 0.8675309,
            },
        )
        assert r.status_code == 400

    def test_cors_success_no_content(self, unauthed_client: Client) -> None:
        """Tests that cors_success behaves as expected when it's missing the content POST argument."""
        r = unauthed_client.post(
            reverse("cors_success"), data={"url": f.url(), "duration": 0.8675309}
        )
        assert r.status_code == 400

    def test_cors_success_no_duration(self, unauthed_client: Client) -> None:
        """Tests that cors_success behaves as expected when it's missing the duration POST argument."""
        r = unauthed_client.post(
            reverse("cors_success"),
            data={
                "url": f.url(),
                "content": b64encode("hello world".encode("utf-8")).decode("utf-8"),
            },
        )
        assert r.status_code == 400

    def test_cors_success_content_not_b64(self, unauthed_client: Client) -> None:
        """Tests that cors_success behaves as expected when its content POST argument is not
        base64-encoded.
        """
        r = unauthed_client.post(
            reverse("cors_success"),
            data={"url": f.url(), "content": "ooooo", "duration": 0.8675309},
        )
        assert r.status_code == 400

    def test_cors_success_success(self, unauthed_client: Client) -> None:
        """Tests that cors_success behaves as expected when the POST request contains all the
        expected correct data.
        """
        r = unauthed_client.post(
            reverse("cors_success"),
            data={
                "url": f.url(),
                "content": b64encode("hello world".encode("utf-8")).decode("utf-8"),
                "duration": 0.8675309,
            },
            HTTP_HOST="best.host.ever",
        )
        assert r.status_code == 201


class TestCORSFailure:
    """Container class for all unit tests related to the cors_failure endpoint."""

    def test_cors_failure_no_url(self, unauthed_client: Client) -> None:
        """Tests that cors_failure behaves as expected when it's missing the url POST argument."""
        r = unauthed_client.post(
            reverse("cors_failure"),
            data={
                "err_msg": "whoopsie daisy",
                "duration": 0.8675309,
            },
        )
        assert r.status_code == 400

    def test_cors_failure_no_err_msg(self, unauthed_client: Client) -> None:
        """Tests that cors_failure behaves as expected when it's missing the err_msg POST argument."""
        r = unauthed_client.post(
            reverse("cors_failure"), data={"url": f.url(), "duration": 0.8675309}
        )
        assert r.status_code == 400

    def test_cors_failure_no_duration(self, unauthed_client: Client) -> None:
        """Tests that cors_failure behaves as expected when it's missing the duration POST argument."""
        r = unauthed_client.post(
            reverse("cors_failure"),
            data={
                "url": f.url(),
                "err_msg": "whoopsie daisy",
            },
        )
        assert r.status_code == 400

    def test_cors_failure_success(self, unauthed_client: Client) -> None:
        """Tests that cors_failure behaves as expected when the POST request contains all the
        expected correct data.
        """
        r = unauthed_client.post(
            reverse("cors_failure"),
            data={
                "url": f.url(),
                "err_msg": "whoopsie daisy",
                "duration": 0.8675309,
            },
            HTTP_HOST="best.host.ever",
        )
        assert r.status_code == 201
