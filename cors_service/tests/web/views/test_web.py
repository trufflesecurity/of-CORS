from uuid import uuid4

from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
from faker import Faker

from tests.factories import (
    AuthTicketFactory,
    HostDomainFactory,
    get_populated_host_domain,
)

f = Faker()


class TestLanding:
    """Container class for all tests for the landing HTTP request handler."""

    def test_no_match_found(self, unauthed_client: Client) -> None:
        """Tests that landing behaves as expected when no host domain is found to match the
        requested host.
        """
        r = unauthed_client.get(reverse("landing"), HTTP_HOST=f.domain_name())
        assert r.status_code == 404

    def test_match_but_no_subdomains(self, unauthed_client: Client) -> None:
        """Tests that landing behaves as expected when a host domain match is found but no internal
        subdomains are configured for the match.
        """
        host_domain = HostDomainFactory()
        r = unauthed_client.get(reverse("landing"), HTTP_HOST=host_domain.domain)
        assert r.status_code == 404

    def test_exact_match_success(self, unauthed_client: Client) -> None:
        """Tests that landing behaves as expected when a host domain match is found for the exact requested
        host AND internal subdomains are configured for the match.
        """
        host_domain = get_populated_host_domain()
        r = unauthed_client.get(reverse("landing"), HTTP_HOST=host_domain.domain)
        assert r.status_code == 200

    def test_parent_domain_match_success(self, unauthed_client: Client) -> None:
        """Tests that landing behaves as expected when a host domain match is found for a parent domain
        of the requested host AND internal subdomains are configured for the match.
        """
        host_domain = get_populated_host_domain()
        r = unauthed_client.get(
            reverse("landing"), HTTP_HOST=f"foo.bar.baz.{host_domain.domain}"
        )
        assert r.status_code == 200


class TestLandingDebug:
    """Container class for all tests for the landing_debug handler."""

    def test_no_match_found(self, unauthed_client: Client) -> None:
        """Tests that landing_debug behaves as expected when no host domain is found to match the
        requested host.
        """
        r = unauthed_client.get(reverse("landing_debug"), HTTP_HOST=f.domain_name())
        assert r.status_code == 404

    def test_match_but_no_subdomains(self, unauthed_client: Client) -> None:
        """Tests that landing_debug behaves as expected when a host domain match is found but no internal
        subdomains are configured for the match.
        """
        host_domain = HostDomainFactory()
        r = unauthed_client.get(reverse("landing_debug"), HTTP_HOST=host_domain.domain)
        assert r.status_code == 404

    def test_exact_match_success(self, unauthed_client: Client) -> None:
        """Tests that landing_debug behaves as expected when a host domain match is found for the exact requested
        host AND internal subdomains are configured for the match.
        """
        host_domain = get_populated_host_domain()
        r = unauthed_client.get(reverse("landing_debug"), HTTP_HOST=host_domain.domain)
        assert r.status_code == 200

    def test_parent_domain_match_success(self, unauthed_client: Client) -> None:
        """Tests that landing_debug behaves as expected when a host domain match is found for a parent domain
        of the requested host AND internal subdomains are configured for the match.
        """
        host_domain = get_populated_host_domain()
        r = unauthed_client.get(
            reverse("landing_debug"), HTTP_HOST=f"foo.bar.baz.{host_domain.domain}"
        )
        assert r.status_code == 200


class TestLandingJsPayload:
    """Container class for all tests for the landing_js_payload handler."""

    def test_no_match_found(self, unauthed_client: Client) -> None:
        """Tests that landing_js_payload behaves as expected when no host domain is found to match the
        requested host.
        """
        r = unauthed_client.get(reverse("landing_payload"), HTTP_HOST=f.domain_name())
        assert r.status_code == 404

    def test_match_but_no_subdomains(self, unauthed_client: Client) -> None:
        """Tests that landing_js_payload behaves as expected when a host domain match is found but no internal
        subdomains are configured for the match.
        """
        host_domain = HostDomainFactory()
        r = unauthed_client.get(
            reverse("landing_payload"), HTTP_HOST=host_domain.domain
        )
        assert r.status_code == 404

    def test_exact_match_success(self, unauthed_client: Client) -> None:
        """Tests that landing_js_payload behaves as expected when a host domain match is found for the exact requested
        host AND internal subdomains are configured for the match.
        """
        host_domain = get_populated_host_domain()
        r = unauthed_client.get(
            reverse("landing_payload"), HTTP_HOST=host_domain.domain
        )
        assert r.status_code == 200

    def test_parent_domain_match_success(self, unauthed_client: Client) -> None:
        """Tests that landing_js_payload behaves as expected when a host domain match is found for a parent domain
        of the requested host AND internal subdomains are configured for the match.
        """
        host_domain = get_populated_host_domain()
        r = unauthed_client.get(
            reverse("landing_payload"), HTTP_HOST=f"foo.bar.baz.{host_domain.domain}"
        )
        assert r.status_code == 200


class TestSwJsPayload:
    """Container class for all tests for the sw_js_payload handler."""

    def test_no_match_found(self, unauthed_client: Client) -> None:
        """Tests that sw_js_payload behaves as expected when no host domain is found to match the
        requested host.
        """
        r = unauthed_client.get(reverse("sw_payload"), HTTP_HOST=f.domain_name())
        assert r.status_code == 404

    def test_match_but_no_subdomains(self, unauthed_client: Client) -> None:
        """Tests that sw_js_payload behaves as expected when a host domain match is found but no internal
        subdomains are configured for the match.
        """
        host_domain = HostDomainFactory()
        r = unauthed_client.get(reverse("sw_payload"), HTTP_HOST=host_domain.domain)
        assert r.status_code == 404

    def test_exact_match_success(self, unauthed_client: Client) -> None:
        """Tests that sw_js_payload behaves as expected when a host domain match is found for the exact requested
        host AND internal subdomains are configured for the match.
        """
        host_domain = get_populated_host_domain()
        r = unauthed_client.get(reverse("sw_payload"), HTTP_HOST=host_domain.domain)
        assert r.status_code == 200

    def test_parent_domain_match_success(self, unauthed_client: Client) -> None:
        """Tests that sw_js_payload behaves as expected when a host domain match is found for a parent domain
        of the requested host AND internal subdomains are configured for the match.
        """
        host_domain = get_populated_host_domain()
        r = unauthed_client.get(
            reverse("sw_payload"), HTTP_HOST=f"foo.bar.baz.{host_domain.domain}"
        )
        assert r.status_code == 200


class TestConsumeAuthTicket:
    """Container class for all tests for the consume_auth_ticket handler."""

    def test_ticket_not_found(self, unauthed_client: Client) -> None:
        """Tests that consume_auth_ticket behaves as expected when the referenced GUID does not map to
        a ticket.
        """
        r = unauthed_client.get(
            reverse(viewname="consume_auth_ticket", kwargs={"ticket_guid": uuid4()})
        )
        assert r.status_code == 400

    def test_ticket_not_valid(self, unauthed_client: Client) -> None:
        """Tests that consume_auth_ticket behaves as expected when the ticket mapped to the given GUID
        is no longer valid.
        """
        ticket = AuthTicketFactory(used=True, used_at=timezone.now())
        r = unauthed_client.get(
            reverse(viewname="consume_auth_ticket", kwargs={"ticket_guid": ticket.guid})
        )
        assert r.status_code == 400

    def test_success(self, unauthed_client: Client) -> None:
        """Tests that consume_auth_ticket behaves as expected when the ticket mapped is still valid."""
        ticket = AuthTicketFactory(used=False, used_at=None)
        r = unauthed_client.get(
            reverse(viewname="consume_auth_ticket", kwargs={"ticket_guid": ticket.guid})
        )
        assert r.status_code == 302
