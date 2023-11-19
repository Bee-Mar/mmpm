#!/usr/bin/env python3
from importlib import import_module
from pkgutil import iter_modules
from typing import Dict, List

import mmpm.subcommands


class Loader:
    """Handles dynamically loading all subcommands in the subcommands module"""

    def __init__(self, app_name: str = ""):
        self.subcommands: Dict[str, object] = self.__load__(app_name)

    def __load__(self, app_name: str) -> Dict[str, object]:
        subcommands: Dict[str, object] = {}
        snake_to_pascal = lambda name : name.replace("_", " ").title().replace(" ", "")

        for module in iter_modules(mmpm.subcommands.__path__):
            if module.name.startswith("_sub_cmd"):
                class_name = snake_to_pascal(module.name.replace("_sub_cmd", ""))

                try:
                    imported_module = import_module(f"mmpm.subcommands.{module.name}")
                    subcommand = getattr(imported_module, class_name)
                    instance = subcommand(app_name)

                    has_basic_attrs = hasattr(instance, "register") and hasattr(instance, "exec") and hasattr(instance, "name")

                    assert has_basic_attrs, f"{class_name} must inherit and implement all SubCmd attributes"
                    subcommands[instance.name] = instance

                except (AttributeError, AssertionError, Exception) as error:
                    print(f"Failed to load subcommand module: {error}")

        return subcommands


