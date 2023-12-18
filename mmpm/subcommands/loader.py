#!/usr/bin/env python3
from importlib import import_module
from pkgutil import iter_modules
from typing import Dict

from mmpm.log.factory import MMPMLogFactory

logger = MMPMLogFactory.get_logger(__name__)


class Loader:
    """
    This class handles dynamically loading all subcommands/endpoints from given modules.

    Attributes:
        objects (Dict[str, object]): A dictionary holding the loaded objects with their names as keys.

    Args:
        module_path (str): The file system path to the module to load objects from.
        module_name (str): The name of the module from which objects are to be loaded.
        app_name (str, optional): The name of the app, if applicable. Defaults to an empty string.
        prefix (str, optional): A prefix to filter which submodules to load. Defaults to an empty string.
    """

    def __init__(self, module_path, module_name: str, app_name: str = "", prefix: str = ""):
        """
        Initializes the Loader instance and loads objects from the specified module.

        Args:
            module_path (str): The file system path to the module to load objects from.
            module_name (str): The name of the module from which objects are to be loaded.
            app_name (str, optional): The name of the app, if applicable. Defaults to an empty string.
            prefix (str, optional): A prefix to filter which submodules to load. Defaults to an empty string.
        """

        self.objects: Dict[str, object] = self.__load__(module_path, module_name, app_name, prefix)

    def __load__(self, module_path, module_name: str, app_name: str = "", prefix: str = "") -> Dict[str, object]:
        """
        Loads objects dynamically from the specified module.

        This method scans the given module path for submodules that start with the specified prefix,
        imports them, and creates instances of the classes found within those modules.

        Args:
            module_path (str): The file system path to the module to load objects from.
            module_name (str): The name of the module from which objects are to be loaded.
            app_name (str, optional): The name of the app, if applicable. Used to instantiate the objects if required.
            prefix (str, optional): A prefix to filter which submodules to load. Defaults to an empty string.

        Returns:
            Dict[str, object]: A dictionary of the loaded objects, with object names as keys.

        Raises:
            AttributeError: If a required attribute is missing in the loaded module.
            AssertionError: If an assertion fails in the process of loading.
            Exception: For any other exceptions encountered during loading.
        """

        objects: Dict[str, object] = {}
        snake_to_pascal = lambda name: name.replace("_", " ").title().replace(" ", "")

        for submodule in iter_modules(module_path):
            if submodule.name.startswith(prefix):
                class_name = snake_to_pascal(submodule.name.replace(prefix, ""))

                try:
                    imported_module = import_module(f"{module_name}.{submodule.name}")
                    objekt = getattr(imported_module, class_name)
                    instance = objekt(app_name) if app_name else objekt()
                    objects[instance.name] = instance
                except (AttributeError, AssertionError, Exception) as error:
                    logger.error(f"Failed to load subcommand module: {error}")

        return objects
