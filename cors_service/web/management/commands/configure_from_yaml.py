import logging
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
            help="The local file path to the YAML file that contains the expected configuration for CORS hunter.",
            required=True,
        )

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        file_path = options["file"]
        logger.info(
            f"Configuring CORS Hunter based on contents of YAML file at '{file_path}'..."
        )
        YmlManager.configure_from_yml_file(path=file_path)
        return None
