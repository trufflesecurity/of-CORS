import logging
from typing import Any, Optional

from django.core.management import BaseCommand, CommandParser

from web.logic.targets import TargetManager

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Django management command for adding a new domain as a target for CORS Hunter payloads."""

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "domain",
            metavar="<DOMAIN>",
            type=str,
            help="The domain to add as a target.",
        )

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        TargetManager.add_targets_for_parent_domain(parent_domain=options["domain"])
        # logger.info(
        #     f"Adding domain '{target_domain}' as a target to CORS Hunter configuration..."
        # )
        # logger.info("First we need to identify subdomains for this domain...")
        # subdomains = DomainManager.enumerate_subdomains(parent_domain=target_domain)
        # logger.info(f"A total of {len(subdomains)} subdomains were found under the domain '{target_domain}'.")
        # logger.info("Now let's see which of these domains is potentially an 'internal' subdomain...")
