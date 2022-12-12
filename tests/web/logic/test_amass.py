import pytest

from web.logic.amass import AmassException, AmassManager


class TestAmassManager:
    """Container class for all test cases related to AmassManager."""

    def test_invoke_works(self) -> None:
        """Tests that the Amass binary van be invoked without issue."""
        _, _, return_code = AmassManager._invoke_amass_binary(args=["-version"])
        assert return_code == 0

    def test_assert_valid_domain_fails(self) -> None:
        """Tests that _assert_valid_domain behaves as expected when given a bad domain."""
        with pytest.raises(AmassException):
            AmassManager._assert_valid_domain("hello woopdy _+~!@#doo")

    def test_assert_valid_domain_success(self) -> None:
        """Tests that _assert_valid_domain behaves as expected when given a good domain."""
        AmassManager._assert_valid_domain("www.google.com")
