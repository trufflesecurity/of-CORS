import logging
from multiprocessing import Pool

import requests
import sublist3r
from django.conf import settings

logger = logging.getLogger(__name__)


def _test_https_domain(domain: str, timeout_s: int = settings.HTTPS_TESTING_TIMEOUT) -> tuple[str, bool]:
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
    def test_domains_for_https(
            domains: list[str],
            pool_size: int = settings.HTTPS_TESTING_POOL_SIZE,
    ) -> list[str]:
        """Test the given list of domains for whether an HTTPS service is listening on it. Return the
        list of domains that responded to HTTPS requests.
        """

        with Pool(processes=pool_size) as pool:
            logger.debug(f"Enqueueing a total of {len(domains)} tasks to test domains for HTTPS (pool size {pool_size}).")
            results: list[tuple[str, bool]] = pool.map(func=_test_https_domain, iterable=domains)
            logger.debug("Tasks enqueued. Waiting for results...")

        return [x for x, y in results if y]

    @staticmethod
    def add_targets_for_parent_domain(parent_domain: str) -> None:
        """Perform all of the necessary intelligence gathering and book-keeping to add the given parent
        domain as a target for CORS Hunter.
        """
        logger.debug(f"Adding domain '{parent_domain}' as a target to CORS Hunter...")
        logger.debug(f"First finding all the subdomains that we can for parent domain '{parent_domain}'...")
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
            return
        logger.debug(
            f"A total of {len(internal_domains)} domains appear to be potential internal domains. "
            f"Adding them as targets..."
        )
        return None
