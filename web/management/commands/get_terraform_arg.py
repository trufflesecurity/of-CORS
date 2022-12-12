from typing import Any, Optional

import yaml
from django.core.management import (  # type: ignore[attr-defined]
    BaseCommand,
    CommandParser,
)


class Command(BaseCommand):
    """Django management command for parsing out the contents of the configuration YAML file to
    command line arguments for Terraform invocation.
    """

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-f",
            "--file",
            metavar="<YAML_FILE>",
            type=str,
            help="The local file path to the YAML file that contains the expected configuration for CORS hunter.",
            required=True,
        )
        parser.add_argument(
            "-a",
            "--argument",
            metavar="<ARGUMENT>",
            type=str,
            help="The argument that should be parsed out from the YAML file.",
            choices=[
                "cloudflare_api_token",
                "heroku_app_name_var",
                "heroku_app_name",
                "host_domains",
            ],
            required=True,
        )

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        with open(options["file"], "r") as f:
            config = yaml.safe_load(f)
        if options["argument"] == "cloudflare_api_token":
            token = config["terraform"]["cloudflare_api_token"]
            self.stdout.write(f"cloudflare_api_token={token}", ending="")
        elif options["argument"] == "heroku_app_name_var":
            app_name = config["terraform"]["heroku_app_name"]
            self.stdout.write(f"heroku_app_name={app_name}", ending="")
        elif options["argument"] == "heroku_app_name":
            self.stdout.write(config["terraform"]["heroku_app_name"], ending="")
        elif options["argument"] == "host_domains":
            domains = []
            for _, v in config["hosts"].items():
                domains.append(v["host_domain"])
            domains = list(set(domains))
            domains_string = ",".join([f'"{x}"' for x in sorted(domains)])
            self.stdout.write(f"'host_domains=[{domains_string}]'", ending="")
        return None
