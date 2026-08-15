"""Command line options for the deprecated 'install' subcommand (alias of 'add')"""

from mmpm.log.factory import MMPMLogFactory
from mmpm.subcommands._sub_cmd_add import Add

logger = MMPMLogFactory.get_logger(__name__)


class Install(Add):
    """
    Deprecated alias of the 'Add' subcommand, kept for backwards compatibility.
    """

    def __init__(self, app_name):
        super().__init__(app_name)
        self.name = "install"
        self.help = "[deprecated] Use 'add' instead"
        self.usage = f"{self.app_name} {self.name} <package(s)> [--yes]"

    def exec(self, args, extra):
        logger.warning(f"'{self.app_name} install' is deprecated and will be removed in a future release; use '{self.app_name} add' instead")
        super().exec(args, extra)
