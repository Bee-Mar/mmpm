#!/usr/bin/env python3

#!/usr/bin/env python3
import json
from pathlib import PosixPath
from shutil import copyfile
from typing import Dict

from flask import Blueprint, Response, request, send_file
from mmpm.api.constants import http
from mmpm.api.endpoints.endpoint import Endpoint
from mmpm.constants import paths
from mmpm.env import MMPMEnv
from mmpm.logger import MMPMLogger

logger = MMPMLogger.get_logger(__name__)


class Configs(Endpoint):
    def __init__(self):
        self.name = "configs"
        self.blueprint = Blueprint(self.name, __name__, url_prefix=f"/api/{self.name}")
        self.handler = None
        self.env = MMPMEnv()
        self.files: Dict[str, PosixPath] = {
            "mmpm-env.json": paths.MMPM_ENV_FILE,
            "config.js": self.env.MMPM_MAGICMIRROR_ROOT.get() / "config" / "config.js",
            "custom.css": self.env.MMPM_MAGICMIRROR_ROOT.get() / "css" / "custom.css",
            "config.js.sample": self.env.MMPM_MAGICMIRROR_ROOT.get() / "config" / "config.js",
        }

        @self.blueprint.route("/retrieve/<filename>", methods=[http.GET])
        def retrieve_mmpm_env_json(filename: str) -> Response:
            if filename not in self.files:
                return self.failure(f"File '{filename}' is not recognized. Only {list(self.files.keys())} are valid.")

            file = self.files.get(filename)

            if filename == "config.js" and (not file.exists() or not bool(file.stat().st_size)):
                sample = self.files.get("config.js.sample")

                if sample.exists():
                    copyfile(config_js_sample, config_js)
                    logger.debug("The config.js hasn't been initialized yet, but found the sample file. Copying config.js.sample to config.js")

            if not file.exists():
                logger.debug(f"File '{file}' does not exist, creating empty file")
                file.parent.mkdir(parents=True, exist_ok=True)
                file.touch(mode=0o664, exist_ok=True)

            logger.debug(f"Sending back {file}")

            return send_file(self.files.get(filename), filename, as_attachment=True)

        @self.blueprint.route("/update/<filename>", methods=[http.POST])
        def update_mmpm_env_json(filename: str) -> Response:
            if filename not in self.files:
                return self.failure(f"File '{filename}' is not recognized. Only {list(self.files.keys())} are valid.")

            file = self.files.get(filename)
            logger.debug(f"Editing {file} with provided contents")

            with open(file, mode="w", encoding="utf-8") as file_to_edit:
                file_to_edit.write(data.get("contents"))

            return send_file(self.files.get(filename), filename, as_attachment=True)