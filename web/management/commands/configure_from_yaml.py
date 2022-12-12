import logging
from base64 import b64decode
from typing import Any, Optional

from django.core.management import (  # type: ignore[attr-defined]
    BaseCommand,
    CommandParser,
)

from web.logic.yml import YmlManager

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Django management command for configuring CORS hunter based on a YAML file."""

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-f",
            "--file",
            metavar="<YAML_FILE>",
            type=str,
            help="The local file path to the YAML file that contains the expected configuration "
            "for CORS hunter. Note that only this argument or --string should be provided "
            "(not both).",
            required=False,
        )
        parser.add_argument(
            "-s",
            "--string",
            metavar="<BASE64_ENCODED_YAML>",
            type=str,
            help="The contents of a YAML file base64 encoded. Note that only this argument or "
            "--file should be provided (not both).",
            required=False,
        )

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        if options["file"]:
            file_path = options["file"]
            logger.info(
                f"Configuring CORS Hunter based on contents of YAML file at '{file_path}'..."
            )
            YmlManager.configure_from_yml_file(path=file_path)
        elif options["string"]:
            logger.info(
                "Configuring CORS Hunter based on contents of base64-encoded YAML file..."
            )
            contents = b64decode(options["string"].encode("utf-8")).decode("utf-8")
            YmlManager.configure_from_yml_string(yml=contents)
        return None
