import os
from io import StringIO
from typing import Any, Final

import pytest
from django.core.management import call_command

from web.util.fs import get_temp_file_path

SAMPLE_CONFIG_FILE: Final[
    str
] = """
terraform:
  # You must change this to a unique string that is a valid Heroku app name
  heroku_app_name: best-of-cors
  # Fill this out with your Cloudflare API token
  cloudflare_api_token: this-is-my-api-token

hosts:
  testing:
    host_domain: 127.0.0.1:8080
    redirect_domain: google.com
    targets:
      - enable-cors.org
      - example.com
  testing_1:
    host_domain: 127.0.0.2:8080
    redirect_domain: google.com
    targets:
      - enable-cors.org
      - example.com
""".strip()


@pytest.fixture
def temp_config_file() -> str:
    path = get_temp_file_path()
    with open(path, "w+") as f:
        f.write(SAMPLE_CONFIG_FILE)
    yield path
    os.remove(path)


class TestCommand:
    """Test case for all the tests related to the get_terraform_arg Django management command."""

    def _call_command(self, *args: Any, **kwargs: Any) -> str:
        """Wrapper for invoking a command and returning the STDOUT value.

        https://adamj.eu/tech/2020/09/07/how-to-unit-test-a-django-management-command/
        """
        out = StringIO()
        call_command(
            "get_terraform_arg", *args, stdout=out, stderr=StringIO(), **kwargs
        )
        return out.getvalue()

    def test_cloudflare_api_token(self, temp_config_file) -> None:
        """Tests that get_terraform_arg behaves as expected when asked to retrieve the Cloudflare API
        token arg."""
        result = self._call_command(
            "-f", temp_config_file, "-a", "cloudflare_api_token"
        )
        assert result == "cloudflare_api_token=this-is-my-api-token"

    def test_heroku_app_name_var(self, temp_config_file) -> None:
        """Tests that get_terraform_arg behaves as expected when asked to retrieve the Heroku app name variable
        arg."""
        result = self._call_command("-f", temp_config_file, "-a", "heroku_app_name_var")
        assert result == "heroku_app_name=best-of-cors"

    def test_heroku_app_name(self, temp_config_file) -> None:
        """Tests that get_terraform_arg behaves as expected when asked to retrieve the Heroku app name arg."""
        result = self._call_command("-f", temp_config_file, "-a", "heroku_app_name")
        assert result == "best-of-cors"

    def test_host_domains(self, temp_config_file) -> None:
        """Tests that get_terraform_arg behaves as expected when asked to retrieve the host domains variable arg."""
        result = self._call_command("-f", temp_config_file, "-a", "host_domains")
        assert result == '\'host_domains=["127.0.0.1:8080","127.0.0.2:8080"]\''
