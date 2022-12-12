from web.util.domain import domain_to_all_subdomains


class TestDomainToAllSubdomains:
    """Container class for holding all tests related to the domain_to_all_subdomains function."""

    def test_empty_string(self) -> None:
        """Tests that domain_to_all_subdomains behaves as expected when given an empty string."""
        result = domain_to_all_subdomains(to_parse="")
        assert result == []

    def test_no_period(self) -> None:
        """Tests that domain_to_all_subdomains behaves as expected when given a string that
        does not contain a period.
        """
        result = domain_to_all_subdomains(to_parse="hello")
        assert result == ["hello"]

    def test_one_period(self) -> None:
        """Tests that domain_to_all_subdomains behaves as expected when given a string that
        contains a single period.
        """
        result = domain_to_all_subdomains(to_parse="hello.com")
        assert result == ["hello.com"]

    def test_two_periods(self) -> None:
        """Tests that domain_to_all_subdomains behaves as expected when given a string that
        contains two periods.
        """
        result = domain_to_all_subdomains(to_parse="world.hello.com")
        assert result == ["hello.com", "world.hello.com"]

    def test_many_periods(self) -> None:
        """Tests that domain_to_all_subdomains behaves as expected when given a string that
        contains many periods
        """
        result = domain_to_all_subdomains(
            to_parse="foo.bar.baz.bang.boom.bong.hello.com"
        )
        assert result == [
            "hello.com",
            "bong.hello.com",
            "boom.bong.hello.com",
            "bang.boom.bong.hello.com",
            "baz.bang.boom.bong.hello.com",
            "bar.baz.bang.boom.bong.hello.com",
            "foo.bar.baz.bang.boom.bong.hello.com",
        ]
