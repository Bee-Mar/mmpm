#!/usr/bin/env python3
import sys
from argparse import ArgumentParser

import mmpm.subcommands
from mmpm.constants import urls
from mmpm.magicmirror.database import MagicMirrorDatabase
from mmpm.subcommands.loader import Loader


# for the console script
def main():
    """
    Initializes all subcommand and their options.

    Parameters:
        None

    Returns:
        None
    """

    app_name = "mmpm"

    parser = ArgumentParser(
        prog=app_name,
        usage=f"{app_name} <subcommand> [option(s)]",
        epilog=f"Visit {urls.MMPM_WIKI_URL} for more details",
        description="""
            The MagicMirror Package Manager CLI simplifies the
            installation, removal, and general maintenance of MagicMirror packages.
            """,
    )

    subparser = parser.add_subparsers(
        title="MMPM subcommands",
        description=f"use `{app_name} <subcommand> --help` to see more details",
        dest="subcmd",
        metavar="",
    )

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(127)

    path = mmpm.subcommands.__path__

    loader = Loader(
        module_path=path,
        module_name="mmpm.subcommands",
        app_name=app_name,
        prefix="_sub_cmd",
    )

    for subcommand in loader.objects.values():
        subcommand.register(subparser)

    args, extra = parser.parse_known_args()
    subcommand = loader.objects.get(args.subcmd)

    subcommand.exec(args, extra)


if __name__ == "__main__":
    main()
