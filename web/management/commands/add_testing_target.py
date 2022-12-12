import logging
from typing import Any, Optional
from uuid import uuid4

from django.core.management import (  # type: ignore[attr-defined]
    BaseCommand,
    CommandParser,
)
from django.utils import timezone

from web.logic.targets import TargetManager
from web.models.target import (
    HostDomain,
    HostToTargetMapping,
    TargetDomain,
    TargetSubdomain,
)

LOCAL_DOMAINS = [
    "127.0.0.1:8080",
]
REDIRECT_DOMAIN = "www.google.com"
CORS_PARENT_DOMAIN = "testing.corshunter.local"
CORS_TARGET_SUBDOMAINS = [
    "enable-cors.org",
    "www.google.com",
    "www.amazon.com",
    "www.reddit.com",
    "www.woot.com",
    "example.com",
]
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Django management command for populating the database with records that can be used in a local
    testing configuration.
    """

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-d",
            "--host-domains",
            metavar="<HOSTS>",
            type=str,
            help="A comma-separate list of host domains that will receive HTTP traffic.",
            required=False,
            default=",".join(LOCAL_DOMAINS),
        )

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        logger.info("Ensuring database has configuration for local testing...")
        try:
            target_domain = TargetDomain.objects.get(domain=CORS_PARENT_DOMAIN)
        except TargetDomain.DoesNotExist:
            target_domain = TargetDomain(
                domain=CORS_PARENT_DOMAIN,
                last_scan_guid=uuid4(),
                time_last_scan_set=timezone.now(),
            )
            target_domain.save()
        for subdomain in CORS_TARGET_SUBDOMAINS:
            TargetSubdomain.objects.update_or_create(
                target_domain=target_domain,
                domain=subdomain,
                scan_guid=target_domain.last_scan_guid,
            )
        host_domains = []
        local_domains = [x.strip() for x in options["host_domains"].split(",")]
        for domain in local_domains:
            try:
                host_domains.append(HostDomain.objects.get(domain=domain))
            except HostDomain.DoesNotExist:
                host_domain = HostDomain(
                    domain=domain,
                    redirect_domain=REDIRECT_DOMAIN,
                )
                host_domain.save()
                host_domains.append(host_domain)
        for host_domain in host_domains:
            try:
                mapping = HostToTargetMapping.objects.get(
                    host_domain=host_domain,
                    target_domain=target_domain,
                )
            except HostToTargetMapping.DoesNotExist:
                mapping = HostToTargetMapping(
                    host_domain=host_domain,
                    target_domain=target_domain,
                )
            mapping.active = True
            mapping.save()
        logger.info(
            "Records set up to reflect local testing setup. Ensuring mapping is correct..."
        )
        for domain in local_domains:
            results = list(
                TargetManager.get_active_target_subdomains_for_host_domain(
                    host_domain=domain
                )
            )
            if sorted([x.domain for x in results]) != sorted(CORS_TARGET_SUBDOMAINS):
                logger.fatal(f"Mapping was INVALID for domain '{domain}'. Exiting.")
                return None
            else:
                logger.info(f"Mapping is correct for domain '{domain}'.")
        target_desc = ", ".join([f"'{x}'" for x in local_domains])
        logger.info(
            f"Everything looks good! This instance is now configured to launch the CORS scanner "
            f"for requests to the domains {target_desc}. Happy hunting!"
        )
        return None
