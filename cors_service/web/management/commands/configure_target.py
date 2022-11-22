import logging
from typing import Any, Optional

from django.core.management import (  # type: ignore[attr-defined]
    BaseCommand,
    CommandParser,
)

from web.logic.targets import TargetManager

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Django management command for adding a new domain mapping as a target for CORS Hunter payloads."""

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-d",
            "--host_domain",
            metavar="<HOST>",
            type=str,
            help="The domain you will receive requests at.",
            required=True,
        )
        parser.add_argument(
            "-t",
            "--targets",
            metavar="<TARGETS>",
            type=str,
            help="A comma-separated list of parent domains that should be considered as "
            "targets when a request is received to the host domain.",
            required=True,
        )

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        host_domain = options["host_domain"]
        targets = [x.strip() for x in options["targets"].split(",")]
        logger.info(
            f"Now adding the host domain of '{host_domain}' to CORS Hunter configuration."
        )
        logger.info(
            f"First we will need to enumerate subdomains for the {len(targets)} targets you supplied..."
        )
        for cur_target in targets:
            TargetManager.add_target_for_parent_domain(parent_domain=cur_target)
        logger.info(
            f"Subdomains have successfully been enumerated for the {len(targets)} targets. "
            f"Now setting up the mapping from '{host_domain}' to the {len(targets)} targets..."
        )
        TargetManager.set_host_to_target_mapping(
            host_domain=host_domain, target_domains=targets
        )
        payload_subdomains = TargetManager.get_active_target_subdomains_for_host_domain(
            host_domain=host_domain
        )
        logger.info(
            f"Configuration complete! When a request is received for the domain '{host_domain}' "
            f"we will serve a payload that checks for CORS misconfigurations on {len(payload_subdomains)} "
            f"related domains (listed below)."
        )
        for subdomain in payload_subdomains:
            logger.info(f"-- {subdomain.domain}")
        return None
