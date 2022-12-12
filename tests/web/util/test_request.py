from unittest.mock import MagicMock

from faker import Faker

from web.util.request import get_redirect_target_from_request

f = Faker()


class TestGetRedirectTargetFromRequest:
    """Tests container for all tests related to the get_redirect_target_from_request function."""

    def _get_mock_request(self, url: str) -> MagicMock:
        to_return = MagicMock()
        to_return.build_absolute_uri.return_value = url
        return to_return

    def test_no_match(self) -> None:
        """Tests that get_redirect_target_from_request behaves as expected when there is no match on
        the from_domain in the request's URL.
        """
        from_domain = f.domain_name()
        to_domain = f.domain_name()
        url = "https://www.wootwoot.com/foo/bar/baz.php?hello=world"
        request = self._get_mock_request(url=url)
        result = get_redirect_target_from_request(
            request=request, from_domain=from_domain, to_domain=to_domain
        )
        assert result == url

    def test_match_in_netloc(self) -> None:
        """Tests that get_redirect_target_from_request behaves as expected when there is a single match in the
        netloc part of the request's URL.
        """
        from_domain = f.domain_name()
        to_domain = f.domain_name()
        url = f"https://{from_domain}/foo/bar/baz.php?hello=world"
        expected = f"https://{to_domain}/foo/bar/baz.php?hello=world"
        request = self._get_mock_request(url=url)
        result = get_redirect_target_from_request(
            request=request, from_domain=from_domain, to_domain=to_domain
        )
        assert result == expected

    def test_multiple_matches(self) -> None:
        """Tests that get_redirect_target_from_request behaves as expected when the from_domain appears in
        multiple places in the corresponding URL.
        """
        from_domain = f.domain_name()
        to_domain = f.domain_name()
        url = f"https://{from_domain}/foo/bar/{from_domain}.php?hello={from_domain}"
        expected = f"https://{to_domain}/foo/bar/{from_domain}.php?hello={from_domain}"
        request = self._get_mock_request(url=url)
        result = get_redirect_target_from_request(
            request=request, from_domain=from_domain, to_domain=to_domain
        )
        assert result == expected
