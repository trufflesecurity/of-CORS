from unittest.mock import patch
from uuid import uuid4

import pytest
from faker import Faker

from tests.factories import (
    ScanDomainFactory,
    ScanSummaryFactory,
    TargetDomainFactory,
    TargetSubdomainFactory,
)
from web.logic.targets import TargetManager, TargetManagerException
from web.models.scan import ScanDomain, ScanSummary
from web.models.target import (
    HostDomain,
    HostToTargetMapping,
    TargetDomain,
    TargetSubdomain,
)

f = Faker()


def _get_full_target(subdomain_count: int = 10) -> TargetDomain:
    target = TargetDomainFactory()
    for _ in range(subdomain_count):
        TargetSubdomainFactory(target_domain=target)
    return target


class TestTargetManager:
    """Test cases for all functionality within TargetManager."""

    def test_get_all_internal_subdomains_for_parent_domain_parent_not_found(
        self,
    ) -> None:
        """Tests that get_all_internal_subdomains_for_parent_domain behaves as expected when no records are
        found matching the parent domain.
        """
        results = TargetManager.get_all_internal_subdomains_for_parent_domain(
            parent_domain=f.domain_name()
        )
        assert results == []

    def test_get_all_internal_subdomains_for_parent_domain_subdomains_not_found(
        self,
    ) -> None:
        """Tests that get_all_internal_subdomains_for_parent_domain behaves as expected when no subdomain
        records are found for the parent domain.
        """
        parent = ScanSummaryFactory()
        results = TargetManager.get_all_internal_subdomains_for_parent_domain(
            parent_domain=parent.parent_domain
        )
        assert results == []

    def test_get_all_internal_subdomains_for_parent_domain_duplicates(self) -> None:
        """Tests that get_all_internal_subdomains_for_parent_domain behaves as expected when there are multiple
        records for the same subdomain under the parent domain.
        """
        parent = ScanSummaryFactory()
        other_domain = f"{uuid4()}.{parent.parent_domain}"
        for i in range(5):
            ScanDomainFactory(summary=parent, domain=other_domain, has_https=False)
        results = TargetManager.get_all_internal_subdomains_for_parent_domain(
            parent_domain=parent.parent_domain
        )
        assert results == [other_domain]

    def test_get_all_internal_subdomains_for_parent_domain_multiple(self) -> None:
        """Tests that get_all_internal_subdomains_for_parent_domain behaves as expected when there are a
        multitude of records for the given parent domain.
        """
        parent = ScanSummaryFactory()
        subdomains = []
        for i in range(5):
            other_domain = f"{uuid4()}.{parent.parent_domain}"
            ScanDomainFactory(summary=parent, domain=other_domain, has_https=False)
            subdomains.append(other_domain)
        results = TargetManager.get_all_internal_subdomains_for_parent_domain(
            parent_domain=parent.parent_domain
        )
        assert results == subdomains

    def test_get_all_internal_subdomains_for_parent_domain_multiple_all_https(
        self,
    ) -> None:
        """Tests that get_all_internal_subdomains_for_parent_domain behaves as expected when there are a
        multitude of records for the given parent domain and they all have HTTPS enabled.
        """
        parent = ScanSummaryFactory()
        subdomains = []
        for i in range(5):
            other_domain = f"{uuid4()}.{parent.parent_domain}"
            ScanDomainFactory(summary=parent, domain=other_domain, has_https=True)
            subdomains.append(other_domain)
        results = TargetManager.get_all_internal_subdomains_for_parent_domain(
            parent_domain=parent.parent_domain
        )
        assert results == []

    def test_get_target_subdomains_for_parent_domains_no_records(self) -> None:
        """Tests that get_target_subdomains_for_parent_domains behaves as expected when no records matching any
        of the parent domains are found.
        """
        results = list(
            TargetManager.get_target_subdomains_for_parent_domains(
                parent_domains=[f.domain_name(), f.domain_name()]
            )
        )
        assert results == []

    def test_get_target_subdomains_for_parent_domains_records_exist_not_current(
        self,
    ) -> None:
        """Tests that get_target_subdomains_for_parent_domains behaves as expected when records are found matching
        a parent domain but they are from a past scan.
        """
        parent_domain = f.domain_name()
        target_domain = TargetDomainFactory(domain=parent_domain)
        wrong_scan_guid = uuid4()
        for i in range(10):
            TargetSubdomainFactory(
                target_domain=target_domain, scan_guid=wrong_scan_guid
            )
        results = list(
            TargetManager.get_target_subdomains_for_parent_domains(
                parent_domains=[parent_domain]
            )
        )
        assert results == []

    def test_get_target_subdomains_for_parent_domains_records_exist_current(
        self,
    ) -> None:
        """Tests that get_target_subdomains_for_parent_domains behaves as expected when records are found matching
        a parent domain and they are from a current scan.
        """
        parent_domain = f.domain_name()
        target_domain = TargetDomainFactory(domain=parent_domain)
        expected = []
        for i in range(10):
            subdomain = f"{uuid4()}.{parent_domain}"
            TargetSubdomainFactory(target_domain=target_domain, domain=subdomain)
            expected.append(subdomain)
        results = sorted(
            [
                x.domain
                for x in TargetManager.get_target_subdomains_for_parent_domains(
                    parent_domains=[parent_domain]
                )
            ]
        )
        assert results == sorted(expected)

    def test_get_target_subdomains_for_parent_domains_records_exist_multi_parent(
        self,
    ) -> None:
        """Tests that get_target_subdomains_for_parent_domains behaves as expected when records are found matching
        multiple parent domains and they are from a current scan.
        """
        parent_domain_1 = f.domain_name()
        target_domain_1 = TargetDomainFactory(domain=parent_domain_1)
        parent_domain_2 = f.domain_name()
        target_domain_2 = TargetDomainFactory(domain=parent_domain_2)
        expected = []
        for i in range(5):
            subdomain = f"{uuid4()}.{parent_domain_1}"
            TargetSubdomainFactory(target_domain=target_domain_1, domain=subdomain)
            expected.append(subdomain)
        for i in range(5):
            subdomain = f"{uuid4()}.{parent_domain_2}"
            TargetSubdomainFactory(target_domain=target_domain_2, domain=subdomain)
            expected.append(subdomain)
        results = sorted(
            [
                x.domain
                for x in TargetManager.get_target_subdomains_for_parent_domains(
                    parent_domains=[parent_domain_1, parent_domain_2]
                )
            ]
        )
        assert results == sorted(expected)

    def test_set_targets_for_domain_not_exist(self) -> None:
        """Tests that set_targets_for_domain behaves as expected when a target does not already exist
        for a given parent domain.
        """
        parent_domain = f.domain_name()
        subdomains = [f"{uuid4()}.{parent_domain}" for _ in range(10)]
        target_domain_count_1 = TargetDomain.objects.count()
        target_subdomain_count_1 = TargetSubdomain.objects.count()
        TargetManager.set_targets_for_domain(
            parent_domain=parent_domain, subdomains=subdomains
        )
        target_domain_count_2 = TargetDomain.objects.count()
        target_subdomain_count_2 = TargetSubdomain.objects.count()
        fetched_subdomains = sorted(
            [
                x.domain
                for x in TargetManager.get_target_subdomains_for_parent_domains(
                    parent_domains=[parent_domain]
                )
            ]
        )
        assert target_domain_count_2 == target_domain_count_1 + 1
        assert target_subdomain_count_2 == target_subdomain_count_1 + 10
        assert fetched_subdomains == sorted(subdomains)

    def test_set_targets_for_domain_already_exists(self) -> None:
        """Tests that set_targets_for_domain behaves as expected when a target already exists for a given
        parent domain.
        """
        parent_domain = f.domain_name()
        subdomains_1 = [f"{uuid4()}.{parent_domain}" for _ in range(10)]
        subdomains_2 = [f"{uuid4()}.{parent_domain}" for _ in range(10)]
        TargetManager.set_targets_for_domain(
            parent_domain=parent_domain, subdomains=subdomains_1
        )
        target_domain_count_1 = TargetDomain.objects.count()
        target_subdomain_count_1 = TargetSubdomain.objects.count()
        TargetManager.set_targets_for_domain(
            parent_domain=parent_domain, subdomains=subdomains_2
        )
        target_domain_count_2 = TargetDomain.objects.count()
        target_subdomain_count_2 = TargetSubdomain.objects.count()
        fetched_subdomains = sorted(
            [
                x.domain
                for x in TargetManager.get_target_subdomains_for_parent_domains(
                    parent_domains=[parent_domain]
                )
            ]
        )
        assert target_domain_count_2 == target_domain_count_1
        assert target_subdomain_count_2 == target_subdomain_count_1 + 10
        assert fetched_subdomains == sorted(subdomains_2)

    def test_set_host_to_target_mapping_targets_not_exist(self) -> None:
        """Tests set_host_to_target_mapping to ensure it behaves as expected when given target domains
        that we do not have record of.
        """
        with pytest.raises(TargetManagerException):
            TargetManager.set_host_to_target_mapping(
                host_domain=f.domain_name(),
                target_domains=[f.domain_name() for _ in range(3)],
                redirect_domain="www.redirect.com",
            )

    def test_set_host_to_target_mapping_host_not_exist(self) -> None:
        """Tests set_host_to_target_mapping to ensure it behaves as expected when given a host domain
        that we do not yet have a database record for.
        """
        host_domain = f.domain_name()
        targets = [_get_full_target(subdomain_count=10) for _ in range(3)]
        host_count_1 = HostDomain.objects.count()
        mapping_count_1 = HostToTargetMapping.objects.count()
        TargetManager.set_host_to_target_mapping(
            host_domain=host_domain,
            target_domains=[x.domain for x in targets],
            redirect_domain="www.redirect.com",
        )
        host_count_2 = HostDomain.objects.count()
        mapping_count_2 = HostToTargetMapping.objects.count()
        active_subdomains = TargetManager.get_active_target_subdomains_for_host_domain(
            host_domain=host_domain
        )
        assert host_count_1 == 0
        assert mapping_count_1 == 0
        assert host_count_2 == 1
        assert mapping_count_2 == 3
        assert active_subdomains.count() == 30

    def test_set_host_to_target_mapping_exists(self) -> None:
        """Tests that set_host_to_target_mapping behaves as expected when given a host mapping that
        already has active mappings.
        """
        host_domain = f.domain_name()
        targets_1 = [_get_full_target(subdomain_count=10) for _ in range(3)]
        targets_2 = [targets_1[2]]
        targets_2.extend([_get_full_target(subdomain_count=10) for _ in range(2)])
        TargetManager.set_host_to_target_mapping(
            host_domain=host_domain,
            target_domains=[x.domain for x in targets_1],
            redirect_domain="www.redirect.com",
        )
        host_count_1 = HostDomain.objects.count()
        mapping_count_1 = HostToTargetMapping.objects.count()
        TargetManager.set_host_to_target_mapping(
            host_domain=host_domain,
            target_domains=[x.domain for x in targets_2],
            redirect_domain="www.redirect.com",
        )
        host_count_2 = HostDomain.objects.count()
        mapping_count_2 = HostToTargetMapping.objects.count()
        active_subdomains = TargetManager.get_active_target_subdomains_for_host_domain(
            host_domain=host_domain
        )
        total_mapping_count = HostToTargetMapping.objects.filter(
            host_domain__domain=host_domain
        ).count()
        total_active_mapping_count = HostToTargetMapping.objects.filter(
            host_domain__domain=host_domain, active=True
        ).count()
        assert host_count_2 - host_count_1 == 0
        assert mapping_count_2 - mapping_count_1 == 2
        assert active_subdomains.count() == 30
        assert total_mapping_count == 5
        assert total_active_mapping_count == 3

    @patch("web.logic.amass.AmassManager.enumerate_subdomains_for_domain")
    @patch("web.logic.targets.TargetManager.test_domains_for_https")
    def test_scan_parent_domain_no_results(
        self, test_domains_for_https, enumerate_subdomains_for_domain
    ) -> None:
        """Tests scan_parent_domain to ensure that it creates all of the expected database records when
        no results are found from a subdomain scan.
        """
        enumerate_subdomains_for_domain.return_value = []
        test_domains_for_https.return_value = []
        domain = f.domain_name()
        summary_count_1 = ScanSummary.objects.count()
        domain_count_1 = ScanDomain.objects.count()
        result = TargetManager.scan_parent_domain(parent_domain=domain)
        summary_count_2 = ScanSummary.objects.count()
        domain_count_2 = ScanDomain.objects.count()
        assert summary_count_2 == summary_count_1 + 1
        assert domain_count_2 == domain_count_1
        assert result.subdomains_count == 0
        assert result.https_subdomains_count == 0

    @patch("web.logic.amass.AmassManager.enumerate_subdomains_for_domain")
    @patch("web.logic.targets.TargetManager.test_domains_for_https")
    def test_scan_parent_domain_one_result_no_https(
        self, test_domains_for_https, enumerate_subdomains_for_domain
    ) -> None:
        """Tests scan_parent_domain to ensure that it creates all of the expected database records when
        a single result is found from a subdomain scan that doesn't respond to HTTPS.
        """
        subdomain = f.domain_name()
        enumerate_subdomains_for_domain.return_value = [subdomain]
        test_domains_for_https.return_value = []
        domain = f.domain_name()
        summary_count_1 = ScanSummary.objects.count()
        domain_count_1 = ScanDomain.objects.count()
        result = TargetManager.scan_parent_domain(parent_domain=domain)
        summary_count_2 = ScanSummary.objects.count()
        domain_count_2 = ScanDomain.objects.count()
        payload_subdomains = (
            TargetManager.get_all_internal_subdomains_for_parent_domain(
                parent_domain=domain
            )
        )
        assert summary_count_2 == summary_count_1 + 1
        assert domain_count_2 == domain_count_1 + 1
        assert result.subdomains_count == 1
        assert result.https_subdomains_count == 0
        assert payload_subdomains == [subdomain]

    @patch("web.logic.amass.AmassManager.enumerate_subdomains_for_domain")
    @patch("web.logic.targets.TargetManager.test_domains_for_https")
    def test_scan_parent_domain_one_result_https(
        self, test_domains_for_https, enumerate_subdomains_for_domain
    ) -> None:
        """Tests scan_parent_domain to ensure that it creates all of the expected database records when
        a single result is found from a subdomain scan that does respond to HTTPS.
        """
        subdomain = f.domain_name()
        enumerate_subdomains_for_domain.return_value = [subdomain]
        test_domains_for_https.return_value = [(subdomain, 200)]
        domain = f.domain_name()
        summary_count_1 = ScanSummary.objects.count()
        domain_count_1 = ScanDomain.objects.count()
        result = TargetManager.scan_parent_domain(parent_domain=domain)
        summary_count_2 = ScanSummary.objects.count()
        domain_count_2 = ScanDomain.objects.count()
        payload_subdomains = (
            TargetManager.get_all_internal_subdomains_for_parent_domain(
                parent_domain=domain
            )
        )
        assert summary_count_2 == summary_count_1 + 1
        assert domain_count_2 == domain_count_1 + 1
        assert result.subdomains_count == 1
        assert result.https_subdomains_count == 1
        assert payload_subdomains == []

    @patch("web.logic.amass.AmassManager.enumerate_subdomains_for_domain")
    @patch("web.logic.targets.TargetManager.test_domains_for_https")
    def test_scan_parent_domain_many_results_no_https(
        self, test_domains_for_https, enumerate_subdomains_for_domain
    ) -> None:
        """Tests scan_parent_domain to ensure that it creates all of the expected database records when
        many results are found from a subdomain scan and none respond to HTTPS.
        """
        subdomains = [f.domain_name() for _ in range(10)]
        enumerate_subdomains_for_domain.return_value = subdomains
        test_domains_for_https.return_value = []
        domain = f.domain_name()
        summary_count_1 = ScanSummary.objects.count()
        domain_count_1 = ScanDomain.objects.count()
        result = TargetManager.scan_parent_domain(parent_domain=domain)
        summary_count_2 = ScanSummary.objects.count()
        domain_count_2 = ScanDomain.objects.count()
        payload_subdomains = (
            TargetManager.get_all_internal_subdomains_for_parent_domain(
                parent_domain=domain
            )
        )
        assert summary_count_2 == summary_count_1 + 1
        assert domain_count_2 == domain_count_1 + 10
        assert result.subdomains_count == 10
        assert result.https_subdomains_count == 0
        assert payload_subdomains == subdomains

    @patch("web.logic.amass.AmassManager.enumerate_subdomains_for_domain")
    @patch("web.logic.targets.TargetManager.test_domains_for_https")
    def test_scan_parent_domain_many_results_some_https(
        self, test_domains_for_https, enumerate_subdomains_for_domain
    ) -> None:
        """Tests scan_parent_domain to ensure that it creates all of the expected database records when
        many results are found from a subdomain scan and some respond to HTTPS.
        """
        subdomains = [f.domain_name() for _ in range(10)]
        https_subdomains = subdomains[:5]
        non_https_subdomains = subdomains[5:]
        enumerate_subdomains_for_domain.return_value = subdomains
        test_domains_for_https.return_value = [(x, 200) for x in https_subdomains]
        domain = f.domain_name()
        summary_count_1 = ScanSummary.objects.count()
        domain_count_1 = ScanDomain.objects.count()
        result = TargetManager.scan_parent_domain(parent_domain=domain)
        summary_count_2 = ScanSummary.objects.count()
        domain_count_2 = ScanDomain.objects.count()
        payload_subdomains = (
            TargetManager.get_all_internal_subdomains_for_parent_domain(
                parent_domain=domain
            )
        )
        assert summary_count_2 == summary_count_1 + 1
        assert domain_count_2 == domain_count_1 + 10
        assert result.subdomains_count == 10
        assert result.https_subdomains_count == 5
        assert payload_subdomains == non_https_subdomains

    @patch("web.logic.amass.AmassManager.enumerate_subdomains_for_domain")
    @patch("web.logic.targets.TargetManager.test_domains_for_https")
    def test_scan_parent_domain_many_results_all_https(
        self, test_domains_for_https, enumerate_subdomains_for_domain
    ) -> None:
        """Tests scan_parent_domain to ensure that it creates all of the expected database records when
        many results are found from a subdomain scan and all respond to HTTPS.
        """
        subdomains = [f.domain_name() for _ in range(10)]
        enumerate_subdomains_for_domain.return_value = subdomains
        test_domains_for_https.return_value = [(x, 200) for x in subdomains]
        domain = f.domain_name()
        summary_count_1 = ScanSummary.objects.count()
        domain_count_1 = ScanDomain.objects.count()
        result = TargetManager.scan_parent_domain(parent_domain=domain)
        summary_count_2 = ScanSummary.objects.count()
        domain_count_2 = ScanDomain.objects.count()
        payload_subdomains = (
            TargetManager.get_all_internal_subdomains_for_parent_domain(
                parent_domain=domain
            )
        )
        assert summary_count_2 == summary_count_1 + 1
        assert domain_count_2 == domain_count_1 + 10
        assert result.subdomains_count == 10
        assert result.https_subdomains_count == 10
        assert payload_subdomains == []

    @patch("web.logic.amass.AmassManager.enumerate_subdomains_for_domain")
    @patch("web.logic.targets.TargetManager.test_domains_for_https")
    def test_scan_parent_domain_many_results_all_https_mixed_codes(
            self, test_domains_for_https, enumerate_subdomains_for_domain
    ) -> None:
        """Tests scan_parent_domain to ensure that it creates all of the expected database records when
        many results are found from a subdomain scan, all respond to HTTPS, and some of those responses
        do not have 200 status codes.
        """
        subdomains_200 = [f.domain_name() for _ in range(5)]
        subdomains_400 = [f.domain_name() for _ in range(5)]
        enumerate_subdomains_for_domain.return_value = subdomains_200 + subdomains_400
        https_test = [(x, 200) for x in subdomains_200]
        https_test.extend([(x, 400) for x in subdomains_400])
        test_domains_for_https.return_value = https_test
        domain = f.domain_name()
        summary_count_1 = ScanSummary.objects.count()
        domain_count_1 = ScanDomain.objects.count()
        result = TargetManager.scan_parent_domain(parent_domain=domain)
        summary_count_2 = ScanSummary.objects.count()
        domain_count_2 = ScanDomain.objects.count()
        payload_subdomains = (
            TargetManager.get_all_internal_subdomains_for_parent_domain(
                parent_domain=domain
            )
        )
        assert summary_count_2 == summary_count_1 + 1
        assert domain_count_2 == domain_count_1 + 10
        assert result.subdomains_count == 10
        assert result.https_subdomains_count == 5
        assert sorted(payload_subdomains) == sorted(subdomains_400)
