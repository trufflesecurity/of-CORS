import logging
import webbrowser
from typing import Any, Optional

from django.conf import settings
from django.core.management import BaseCommand
from django.urls import reverse

from web.models.auth import AuthTicket
from web.models.target import HostDomain

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Django management command for opening up the results page in an authenticated session."""

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        host_domain = HostDomain.objects.first()
        if host_domain is None:
            logger.fatal(
                "No host domain found! For this command to work you must first configure at "
                "least one host domain (see the configure_target Django management command)."
            )
            return None
        new_ticket = AuthTicket(used=False, used_at=None)
        new_ticket.save()
        url_path = reverse(
            viewname="consume_auth_ticket", kwargs={"ticket_guid": new_ticket.guid}
        )
        scheme = "http" if settings.DEBUG else "https"
        url = f"{scheme}://{host_domain.domain}{url_path}"
        logger.info(f"Ticket generated. Opening browser window to URL '{url}'...")
        webbrowser.open(url)
        return None
