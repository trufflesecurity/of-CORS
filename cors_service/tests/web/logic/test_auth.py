from datetime import timedelta
from uuid import uuid4

import freezegun
from django.utils import timezone

from tests.factories import AuthTicketFactory
from web.logic.auth import AuthManager


class TestAuthManager:
    """Container all for all tests related to AuthManager."""

    def test_use_auth_ticket_not_found(self) -> None:
        """Tests that use_auth_ticket behaves as expected when no ticket matching the GUID is found."""
        result = AuthManager.use_auth_ticket(guid=uuid4())
        assert result is False

    def test_use_auth_ticket_already_used(self) -> None:
        """Tests that use_auth_ticket behaves as expected when the ticket matching the GUID has already been
        used.
        """
        ticket = AuthTicketFactory(
            used=True,
            used_at=timezone.now(),
        )
        result = AuthManager.use_auth_ticket(guid=ticket.guid)
        assert result is False

    def test_use_auth_ticket_stale(self) -> None:
        """Tests that use_auth_ticket behaves as expected when the ticket matching the GUID has not been
        used but was created too long ago.
        """
        ticket = AuthTicketFactory(
            used=False,
            used_at=None,
        )
        validity_window = 500
        with freezegun.freeze_time(
            timezone.now() + timedelta(seconds=2 * validity_window)
        ):
            result = AuthManager.use_auth_ticket(
                guid=ticket.guid, validity_window_s=validity_window
            )
        assert result is False

    def test_use_auth_ticket_success(self) -> None:
        """Tests that use_auth_ticket behaves as expected when a ticket that has not been used yet is found
        matching the GUID."""
        ticket = AuthTicketFactory(
            used=False,
            used_at=None,
        )
        result_1 = AuthManager.use_auth_ticket(guid=ticket.guid)
        assert result_1 is True
        result_2 = AuthManager.use_auth_ticket(guid=ticket.guid)
        assert result_2 is False
