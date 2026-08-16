"""Command line options for 'doctor' subcommand"""

import json
import sys

from mmpm.constants import color
from mmpm.doctor import FAIL, PASS, WARN
from mmpm.doctor import Doctor as MMPMDoctor
from mmpm.log.factory import MMPMLogFactory
from mmpm.subcommands.sub_cmd import SubCmd

logger = MMPMLogFactory.get_logger(__name__)


class Doctor(SubCmd):
    """
    The 'Doctor' subcommand runs read-only diagnostics on the MMPM installation:
    environment sanity, external dependencies, database health, installed package
    integrity, running services, and remote API availability.

    Custom Attributes:
        doctor (MMPMDoctor): The shared diagnostics runner (also used by the /api/doctor endpoint).
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.name = "doctor"
        self.help = f"Diagnose common problems with the {self.app_name}, MagicMirror, and package installations"
        self.usage = f"{self.app_name} {self.name} [--json]"
        self.doctor = MMPMDoctor(app_name)

    def register(self, subparser):
        self.parser = subparser.add_parser(self.name, usage=self.usage, help=self.help)

        self.parser.add_argument(
            "-j",
            "--json",
            action="store_true",
            help="output the diagnostic results as JSON",
            dest="as_json",
        )

    def display(self, result: dict) -> None:
        """
        Prints a single diagnostic result with a status symbol and remediation hint.

        Parameters:
            result (dict): a diagnostic result with status, check, and hint keys

        Returns:
            None
        """

        symbol = {PASS: color.n_green("✓"), WARN: color.n_yellow("⚠"), FAIL: color.n_red("✗")}[result["status"]]
        print(f" {symbol} {result['check']}")

        if result["hint"] and result["status"] != PASS:
            print(f"   → {result['hint']}")

    def exec(self, args, extra):
        if extra:
            logger.error(f"Extra arguments are not accepted. See '{self.app_name} {self.name} --help'")
            return

        results = self.doctor.run(on_check=None if args.as_json else self.display)

        failures = sum(result["status"] == FAIL for result in results)
        warnings = sum(result["status"] == WARN for result in results)

        if args.as_json:
            print(json.dumps({"results": results, "failures": failures, "warnings": warnings}, indent=2))
        else:
            summary = f"{len(results)} checks: {len(results) - failures - warnings} passed, {warnings} warning(s), {failures} failure(s)"
            print(f"\n{color.n_red(summary) if failures else color.n_yellow(summary) if warnings else color.n_green(summary)}")

        if failures:
            sys.exit(1)
