import subprocess

import validators  # type: ignore[import]
from django.conf import settings


class AmassException(Exception):
    """Generic exception to use for all errors that occur within AmassManager."""


class AmassManager:
    """Manager class for containing all functions related to Amass."""

    @staticmethod
    def _assert_valid_domain(domain: str) -> None:
        """Analyze the given domain to determine whether it's a valid format. Throw an exception if the
        domain is not valid.
        """
        if validators.domain(domain) is not True:
            raise AmassException(f"'{domain}' is not a valid domain")

    @staticmethod
    def _invoke_amass_binary(
        args: list[str], bin_path: str = settings.AMASS_BIN_PATH
    ) -> tuple[str, str, int]:
        """Invoke the Amass binary with the given flags and get the string contents of stdout from that
        invocation. Returns a tuple of (1) STDERR, (2) STDOUT, and (3) the exit code.
        """
        command = [bin_path]
        command.extend(args)
        result = subprocess.run(command, shell=False, capture_output=True)
        return (
            result.stdout.decode("utf-8"),
            result.stderr.decode("utf-8"),
            result.returncode,
        )

    @staticmethod
    def query_amass_for_domain(domain: str) -> list[str]:
        """Query the Amass database to get all of the subdomains that have been found for the given
        parent domain.
        """
        AmassManager._assert_valid_domain(domain=domain)
        stdout, stderr, status_code = AmassManager._invoke_amass_binary(
            args=["db", "-d", domain, "-names"]
        )
        if status_code != 0:
            raise AmassException(
                f"bad status code from db invocation ({status_code}). STDERR was '{stderr}'."
            )
        return [x.strip() for x in stdout.strip().split("\n")]

    @staticmethod
    def enumerate_subdomains_for_domain(domain: str) -> list[str]:
        """Use Amass to enumerate as many subdomains as possible for the given domain. Return a list of all the
        subdomains that are discovered.
        """
        AmassManager._assert_valid_domain(domain=domain)
        _, stderr, status_code = AmassManager._invoke_amass_binary(
            args=["enum", "-d", domain]
        )
        if status_code != 0:
            raise AmassException(
                f"bad status code from enum invocation ({status_code}). STDERR was '{stderr}'."
            )
        return AmassManager.query_amass_for_domain(domain=domain)
