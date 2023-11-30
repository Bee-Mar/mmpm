#!/usr/bin/env python3
from importlib import import_module
from pkgutil import iter_modules
from typing import Dict, List

from mmpm.logger import MMPMLogger

logger = MMPMLogger.get_logger(__name__)


class Loader:
    """Handles dynamically loading all subcommands/endpoints in the subcommands and endpoints module"""

    def __init__(self, module_path, module_name: str, app_name: str = "", prefix: str = ""):
        self.objects: Dict[str, object] = self.__load__(module_path, module_name, app_name, prefix)

    def __load__(self, module_path, module_name: str, app_name: str = "", prefix: str = "") -> Dict[str, object]:
        objects: Dict[str, object] = {}
        snake_to_pascal = lambda name: name.replace("_", " ").title().replace(" ", "")

        for module in iter_modules(module_path):
            if module.name.startswith(prefix):
                class_name = snake_to_pascal(module.name.replace(prefix, ""))

                try:
                    imported_module = import_module(f"{module_name}.{module.name}")
                    objekt = getattr(imported_module, class_name)
                    instance = objekt(app_name) if app_name else objekt()
                    objects[instance.name] = instance
                    logger.debug(f"Loaded subcommand instance of '{class_name}' {instance}")

                except (AttributeError, AssertionError, Exception) as error:
                    logger.error(f"Failed to load subcommand module: {error}")

        return objects
