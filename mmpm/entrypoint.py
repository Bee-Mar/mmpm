#!/usr/bin/env python3
import sys
from argparse import ArgumentParser

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

    parser = ArgumentParser(
            prog='mmpm',
            usage='mmpm <subcommand> [option(s)]',
            epilog=f'Visit {urls.MMPM_WIKI_URL} for more details',
            description='''
            The MagicMirror Package Manager CLI simplifies the
            installation, removal, and general maintenance of MagicMirror packages.
            '''
            )

    subparser = parser.add_subparsers(
            title='MMPM subcommands',
            description='use `mmpm <subcommand> --help` to see more details',
            dest='subcmd',
            )

    loader = Loader("mmpm")

    for subcommand in loader.subcommands.values():
        subcommand.register(subparser)

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(127)

    args, extra = parser.parse_known_args()
    subcommand = loader.subcommands.get(args.subcmd)

    MagicMirrorDatabase().load()

    subcommand.exec(args, extra)


if __name__ == "__main__":
    main()
