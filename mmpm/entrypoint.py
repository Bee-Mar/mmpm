#!/usr/bin/env python3
import sys
from argparse import ArgumentParser

import argcomplete

import mmpm.subcommands
from mmpm.constants import urls
from mmpm.log.factory import MMPMLogFactory
from mmpm.subcommands.loader import Loader

logger = MMPMLogFactory.get_logger(__name__)


# for the console script
def main():
    """
    Initializes all subcommand and their options.

    Parameters:
        None

    Returns:
        None
    """

    if "--help" in sys.argv or "-h" in sys.argv:
        # close up any SocketIO connection in the logger that could linger before it becomes a problem
        MMPMLogFactory.shutdown()

    app_name = "mmpm"

    parser = ArgumentParser(
        prog=app_name,
        usage=f"{app_name} <subcommand> [option(s)]",
        epilog=f"Visit {urls.MMPM_WIKI_URL} for more details",
        description="""
            The MagicMirror Package Manager (MMPM) CLI simplifies the
            installation, removal, and general maintenance of MagicMirror packages.
            """,
    )

    subparser = parser.add_subparsers(
        title=f"{app_name} subcommands",
        description=f"use `{app_name} <subcommand> --help` to see more details",
        dest="subcmd",
        metavar="",
    )

    loader = Loader(
        module_path=mmpm.subcommands.__path__,
        module_name="mmpm.subcommands",
        app_name=app_name,
        prefix="_sub_cmd",
    )

    for subcommand in loader.objects.values():
        subcommand.register(subparser)

    argcomplete.autocomplete(parser)

    args, extra = parser.parse_known_args()
    subcommand = loader.objects.get(args.subcmd)

    if not subcommand:
        logger.debug(f"Unable to match '{args.subcmd}' to a valid subcommand")
        parser.print_help()
    else:
        subcommand.exec(args, extra)

    MMPMLogFactory.shutdown()


if __name__ == "__main__":
    main()
