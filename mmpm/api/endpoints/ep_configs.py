from pathlib import Path
from shutil import copyfile
from typing import Dict

from flask import Blueprint, Response, request, send_file

from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.constants import paths
from mmpm.env import MMPMEnv
from mmpm.log.factory import MMPMLogFactory
from mmpm.magicmirror.magicmirror import MagicMirrorConfigs

logger = MMPMLogFactory.get_logger(__name__)


class Configs(Endpoint):
    """
    A Flask endpoint class for handling operations related to the MagicMirror configuration files,
    including retrieving and updating various configuration files.
    """

    def __init__(self):
        self.name = "configs"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")
        self.handler = None
        self.env = MMPMEnv()
        self.mm_files = MagicMirrorConfigs()
        self.files: Dict[str, Path] = {
            "mmpm-env.json": paths.MMPM_ENV_FILE,
            "config.js": self.mm_files.config_js,
            "custom.css": self.mm_files.custom_css,
            "config.js.sample": self.mm_files.config_js_sample,
        }

        @self.blueprint.route("/retrieve/<filename>", methods=[http.GET])
        def retrieve_mmpm_env_json(filename: str) -> Response:
            """
            A Flask route method for retrieving a specified configuration file.

            Parameters:
                filename (str): The name of the file to retrieve.

            Returns:
                Response: A Flask Response object containing the requested file or an error message.
            """
            if filename not in self.files:
                return self.failure(f"File '{filename}' is not recognized. Only {list(self.files.keys())} are valid.")

            file = self.files.get(filename)

            if filename == self.mm_files.config_js.name and (not file.exists() or not bool(file.stat().st_size)):
                if self.mm_files.config_js_sample.exists():
                    copyfile(self.mm_files.config_js_sample, file)
                    logger.debug("The config.js hasn't been initialized yet, but found the sample file. Copying config.js.sample to config.js")

            if not file.exists():
                logger.debug(f"File '{file}' does not exist, creating empty file")
                file.parent.mkdir(parents=True, exist_ok=True)
                file.touch(mode=0o664, exist_ok=True)

            logger.debug(f"Sending back {file}")

            return send_file(self.files.get(filename), filename, as_attachment=True)

        @self.blueprint.route("/update/<filename>", methods=[http.POST])
        def update_mmpm_env_json(filename: str) -> Response:
            """
            A Flask route method for updating the contents of a specified configuration file.

            Parameters:
                filename (str): The name of the file to update.

            Returns:
                Response: A Flask Response object indicating the success or failure of the update operation.
            """

            if filename not in self.files:
                return self.failure(f"File '{filename}' is not recognized. Only {list(self.files.keys())} are valid.")

            file = self.files.get(filename)
            logger.debug(f"Editing {file} with provided contents")

            contents = request.get_json().get("contents")

            try:
                with open(file, mode="w", encoding="utf-8") as file_to_edit:
                    file_to_edit.write(contents)
            except Exception as error:
                logger.error(error)
                self.failure(False)

            return self.success(True)
