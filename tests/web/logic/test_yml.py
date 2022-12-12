from typing import Final
from unittest.mock import patch

from web.logic.targets import TargetManager
from web.logic.yml import YmlManager
from web.models.target import HostDomain, TargetDomain, TargetSubdomain

YML_PAYLOAD_1: Final[
    str
] = """
hosts:
  testing:
    host_domain: 127.0.0.1:8080
    redirect_domain: google.com
    targets:
      - foo.com
      - bar.com
      - baz.com
  other_guy:
    host_domain: 127.0.0.1:8081
    redirect_domain: woot.com
    targets:
      - bar.com
      - baz.com
      - boop.com
""".strip()

YML_PAYLOAD_2: Final[
    str
] = """
hosts:
  testing:
    host_domain: 127.0.0.1:8080
    redirect_domain: google.com
    targets:
      - lol1.com
      - lol2.com
  hoopjoop:
    host_domain: 127.0.0.1:8082
    redirect_domain: loller.com
    targets:
      - hello.com
""".strip()


class TestYmlManager:
    """Test case for all functionality contained within YmlManager."""

    @patch("web.logic.amass.AmassManager.enumerate_subdomains_for_domain")
    @patch("web.logic.targets.TargetManager.test_domains_for_https")
    def test_configure_from_yml_string(
        self, test_domains_for_https, enumerate_subdomains_for_domain
    ) -> None:
        """Tests that configure_from_yml_string behaves as expected on the first run as well as
        subsequent runs.
        """
        result_domains = [
            "cool_domain_1.com",
            "cool_domain_2.com",
            "cool_domain_3.com",
        ]
        test_domains_for_https.return_value = []
        enumerate_subdomains_for_domain.return_value = result_domains
        host_domain_count_1 = HostDomain.objects.count()
        target_domain_count_1 = TargetDomain.objects.count()
        target_subdomain_count_1 = TargetSubdomain.objects.count()
        assert host_domain_count_1 == 0
        assert target_domain_count_1 == 0
        assert target_subdomain_count_1 == 0
        YmlManager.configure_from_yml_string(yml=YML_PAYLOAD_1)
        host_domain_count_2 = HostDomain.objects.count()
        target_domain_count_2 = TargetDomain.objects.count()
        target_subdomain_count_2 = TargetSubdomain.objects.count()
        assert host_domain_count_2 == 2
        assert target_domain_count_2 == 4
        assert target_subdomain_count_2 == 12
        host_domain_payload_entries_1 = (
            TargetManager.get_active_target_subdomains_for_host_domain(
                host_domain="127.0.0.1:8080"
            )
        )
        host_domain_payload_entries_2 = (
            TargetManager.get_active_target_subdomains_for_host_domain(
                host_domain="127.0.0.1:8081"
            )
        )
        assert len(host_domain_payload_entries_1) == 9
        assert len(host_domain_payload_entries_2) == 9
        YmlManager.configure_from_yml_string(yml=YML_PAYLOAD_2)
        host_domain_count_3 = HostDomain.objects.count()
        target_domain_count_3 = TargetDomain.objects.count()
        target_subdomain_count_3 = TargetSubdomain.objects.count()
        assert host_domain_count_3 == 3
        assert target_domain_count_3 == 7
        assert target_subdomain_count_3 == 21
        host_domain_payload_entries_3 = (
            TargetManager.get_active_target_subdomains_for_host_domain(
                host_domain="127.0.0.1:8080"
            )
        )
        host_domain_payload_entries_4 = (
            TargetManager.get_active_target_subdomains_for_host_domain(
                host_domain="127.0.0.1:8081"
            )
        )
        host_domain_payload_entries_5 = (
            TargetManager.get_active_target_subdomains_for_host_domain(
                host_domain="127.0.0.1:8082"
            )
        )
        assert len(host_domain_payload_entries_3) == 6
        assert len(host_domain_payload_entries_4) == 0
        assert len(host_domain_payload_entries_5) == 3
