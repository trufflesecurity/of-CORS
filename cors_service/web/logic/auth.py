from datetime import timedelta
from uuid import UUID

from django.conf import settings
from django.utils import timezone

from web.models.auth import AuthTicket


class AuthManager:
    """Manager class for containing all functionality related to authN and authZ."""

    @staticmethod
    def use_auth_ticket(
        guid: UUID, validity_window_s: int = settings.AUTH_TICKET_VALID_WINDOW_S
    ) -> bool:
        """Attempt to consume the auth ticket corresponding to the given UUID. Returns a boolean indicating
        whether the ticket was successfully consumed. Authentication _should only ever happen_ upon
        successful consumption.
        """
        return (
            AuthTicket.objects.filter(
                guid=guid,
                used=False,
                time_created__gte=timezone.now() - timedelta(seconds=validity_window_s),
            ).update(used=True, used_at=timezone.now())
            == 1
        )
