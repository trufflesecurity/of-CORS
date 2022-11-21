import logging
from uuid import uuid4

import requests
import sublist3r
from django.conf import settings
from django.db.models import F, QuerySet
from django.utils import timezone

from web.models.scan import ScanDomain, ScanSummary
from web.models.target import (
    HostDomain,
    HostToTargetMapping,
    TargetDomain,
    TargetSubdomain,
)

logger = logging.getLogger(__name__)


def _test_https_domain(
    domain: str, timeout_s: int = settings.HTTPS_TESTING_TIMEOUT
) -> tuple[str, bool]:
    logger.debug(f"Attempting to request HTTPS site for domain '{domain}'...")
    try:
        requests.head(
            url=f"https://{domain}/",
            timeout=timeout_s,
        )
    except requests.exceptions.ConnectionError:
        logger.debug(f"Failed to open an HTTPS connection to domain '{domain}'.")
        return domain, False
    logger.debug(f"Successfully opened an HTTPS connection to domain '{domain}'.")
    return domain, True


class TargetManagerException(Exception):
    """Base exception for denoting exceptions that are thrown within TargetManager."""


class TargetManager:
    """Manager class for containing all methods that relate to updating our internal database records
    to reflect the subdomains that should be targeted as a result of a request to a parent domain.
    """

    @staticmethod
    def enumerate_subdomains(parent_domain: str) -> list[str]:
        """Find as many subdomains for the given parent domain as possible."""
        results = sublist3r.main(
            domain=parent_domain,
            threads=40,
            savefile=None,
            ports=None,
            silent=True,
            verbose=False,
            enable_bruteforce=False,
            engines=None,
        )
        return list(set(results))

    @staticmethod
    def get_all_internal_subdomains_for_parent_domain(parent_domain: str) -> list[str]:
        """Query the database to find all subdomains that have ever presented as potentially being
        an internal domain for the given parent domain.
        """
        return list(
            ScanDomain.objects.filter(
                summary__parent_domain=parent_domain,
                has_https=False,
            )
            .values_list("domain", flat=True)
            .distinct()
        )

    @staticmethod
    def get_target_subdomains_for_parent_domains(
        parent_domains: list[str],
    ) -> QuerySet[TargetSubdomain]:
        """Get a list of all the current target subdomains for the given list of parent domains."""
        return TargetSubdomain.objects.filter(
            target_domain__domain__in=parent_domains,
            scan_guid=F("target_domain__last_scan_guid"),
        )

    @staticmethod
    def set_targets_for_domain(
        parent_domain: str, subdomains: list[str]
    ) -> TargetDomain:
        """Update the database to reflect that the payload for the given parent domain should contain
        only the given list of subdomains.
        """
        scan_guid = uuid4()
        target_domain, _ = TargetDomain.objects.update_or_create(
            domain=parent_domain,
            defaults={
                "last_scan_guid": scan_guid,
                "time_last_scan_set": timezone.now(),
            },
        )
        for subdomain in subdomains:
            target_subdomain = TargetSubdomain(
                target_domain=target_domain,
                domain=subdomain,
                scan_guid=scan_guid,
            )
            target_subdomain.save()
        return target_domain

    @staticmethod
    def get_active_target_domains_for_host_domain(
        host_domain: str,
    ) -> list[TargetDomain]:
        """Query the database to find all of the TargetDomain objects that are currently set as an
        active mapping to the given host domain.
        """
        return [
            x.target_domain
            for x in HostToTargetMapping.objects.filter(
                host_domain__domain=host_domain, active=True
            )
        ]

    @staticmethod
    def get_active_target_subdomains_for_host_domain(
        host_domain: str,
    ) -> QuerySet[TargetSubdomain]:
        """Query the database to find all of the subdomains that should be used in a payload when the
        given host domain is requested against the Django server.
        """
        active_target_domains = TargetManager.get_active_target_domains_for_host_domain(
            host_domain=host_domain
        )
        return TargetManager.get_target_subdomains_for_parent_domains(
            parent_domains=[x.domain for x in active_target_domains]
        )

    @staticmethod
    def set_host_to_target_mapping(
        host_domain: str, target_domains: list[str]
    ) -> HostDomain:
        """Configure things so that when the give host domain is requested, a payload is served up targeting
        all of the subdomains underneath the list of target_domains.
        """
        targets = []
        for cur_domain in target_domains:
            try:
                targets.append(TargetDomain.objects.get(domain=cur_domain))
            except TargetDomain.DoesNotExist:
                raise TargetManagerException(
                    f"No TargetDomain record found for domain '{cur_domain}'."
                )
        HostToTargetMapping.objects.filter(host_domain__domain=host_domain).update(
            active=False
        )
        host, _ = HostDomain.objects.update_or_create(domain=host_domain)
        for cur_target in targets:
            HostToTargetMapping.objects.update_or_create(
                host_domain=host,
                target_domain=cur_target,
                defaults={
                    "active": True,
                },
            )
        return host

    @staticmethod
    def test_domains_for_https(
        domains: list[str],
        pool_size: int = settings.HTTPS_TESTING_POOL_SIZE,
        timeout_s: int = settings.HTTPS_TESTING_TIMEOUT,
    ) -> list[str]:
        """Test the given list of domains for whether an HTTPS service is listening on it. Return the
        list of domains that responded to HTTPS requests.
        """
        if len(domains) == 0:
            return []
        results = []
        for domain in domains:
            results.append(_test_https_domain(domain=domain, timeout_s=timeout_s))

        # TODO convert back to multiprocessing, but Django throws a fit with this configuration
        # with multiprocessing.Pool(processes=pool_size) as pool:
        #     logger.debug(
        #         f"Enqueueing a total of {len(domains)} tasks to test domains for HTTPS (pool size {pool_size})."
        #     )
        #     results: list[tuple[str, bool]] = pool.map(
        #         func=_test_https_domain, iterable=domains
        #     )
        #     logger.debug("Tasks enqueued. Waiting for results...")

        return [x for x, y in results if y]

    @staticmethod
    def scan_parent_domain(parent_domain: str) -> ScanSummary:
        """Attempt to find as many 'internal' subdomains as possible for the given parent domain."""
        time_started = timezone.now()
        logger.debug(f"Starting scan for parent domain of '{parent_domain}'.")
        logger.debug(
            f"First finding all the subdomains that we can for parent domain '{parent_domain}'..."
        )
        subdomains = TargetManager.enumerate_subdomains(parent_domain=parent_domain)
        logger.debug(
            f"A total of {len(subdomains)} subdomains were found for parent domain '{parent_domain}'. "
            f"Now testing to see which of those domains may be an internal-facing domain..."
        )
        live_subdomains = TargetManager.test_domains_for_https(domains=subdomains)
        internal_domains = set(subdomains) - set(live_subdomains)
        if len(internal_domains) == 0:
            logger.warning(
                f"None of the {len(subdomains)} subdomains appear to be internal only domains :( "
                f"Nothing to add to our targets list for parent domain of '{parent_domain}'."
            )
        else:
            logger.debug(
                f"A total of {len(internal_domains)} domains appear to be potential internal domains."
            )
        logger.debug("Saving scan results...")
        summary = ScanSummary(
            parent_domain=parent_domain,
            subdomains_count=len(subdomains),
            https_subdomains_count=len(live_subdomains),
            time_started=time_started,
            time_completed=timezone.now(),
        )
        summary.save()
        for subdomain in subdomains:
            scan_domain = ScanDomain(
                summary=summary,
                domain=subdomain,
                has_https=subdomain in live_subdomains,
            )
            scan_domain.save()
        logger.debug(f"Results for scan saved under ScanSummary with ID {summary.id}.")
        return summary

    @staticmethod
    def add_target_for_parent_domain(parent_domain: str) -> None:
        """Perform all of the necessary intelligence gathering and book-keeping to add the given parent
        domain as a target for CORS Hunter.
        """
        logger.debug(f"Adding domain '{parent_domain}' as a target to CORS Hunter...")
        TargetManager.scan_parent_domain(parent_domain=parent_domain)
        logger.debug(
            f"Subdomain scanning for parent domain '{parent_domain}' completed. Adding results as target..."
        )
        subdomains = TargetManager.get_all_internal_subdomains_for_parent_domain(
            parent_domain=parent_domain
        )
        logger.debug(
            f"A total of {len(subdomains)} subdomains were found under parent domain '{parent_domain}'."
        )
        TargetManager.set_targets_for_domain(
            parent_domain=parent_domain, subdomains=subdomains
        )
        logger.debug(
            f"All {len(subdomains)} have been set as payload candidates for parent domain '{parent_domain}'."
        )
