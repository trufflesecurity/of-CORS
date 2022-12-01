import logging

import yaml

from web.logic.targets import TargetManager
from web.models.target import HostToTargetMapping, TargetDomain

logger = logging.getLogger(__name__)


class YmlManager:
    """Manager class for containing all code relating to the processing of YML files for use
    by CORS Hunter.
    """

    @staticmethod
    def configure_from_yml_string(yml: str) -> None:
        """Configure the backing database to reflect the contents of the YML string content passed
        to the function.
        """
        parsed = yaml.safe_load(yml)
        hosts = parsed.get("hosts", {})
        all_targets = []
        for k, v in hosts.items():
            all_targets.extend(v.get("targets", []))
            host_domain = v.get("host_domain")
            redirect_domain = v.get("redirect_domain")
            targets = v.get("targets", [])
            logger.info(
                f"Host domain of '{host_domain}' will redirect to '{redirect_domain}' "
                f"and launch a payload for the following domains:"
            )
            for target in targets:
                logger.info(f"-- {target}")
        all_targets = list(set(all_targets))
        for cur_target in all_targets:
            logger.info(f"Checking if we have target data for '{cur_target}' first...")
            try:
                TargetDomain.objects.get(domain=cur_target)
                logger.info(
                    f"Target domain for '{cur_target}' found! No need to enumerate again."
                )
            except TargetDomain.DoesNotExist:
                logger.info(
                    f"Target domain for '{cur_target}' not found. Enumerating now."
                )
                TargetManager.add_target_for_parent_domain(parent_domain=cur_target)
        logger.info(
            "All target domains populated successfully! Now setting up host to target mappings..."
        )
        HostToTargetMapping.objects.update(active=False)
        for k, v in hosts.items():
            host_domain = v["host_domain"]
            TargetManager.set_host_to_target_mapping(
                host_domain=host_domain,
                redirect_domain=v["redirect_domain"],
                target_domains=v["targets"],
            )
            logger.info(f"Host '{host_domain}' configured.")

    @staticmethod
    def configure_from_yml_file(path: str) -> None:
        """Configure the backing database to reflect the contents of the YML configuration file
        at the given path.
        """
        with open(path, "r") as f:
            return YmlManager.configure_from_yml_string(yml=f.read())
