#!/usr/bin/env python3
# pylint: disable=unused-argument
import sys
from argparse import ArgumentParser
from importlib import import_module
from pkgutil import iter_modules

import argcomplete
import mmpm.subcommands
from mmpm.constants import urls
from mmpm.subcommands.loader import Loader


def setup() -> ArgumentParser:
    '''
    Initializes all subcommand and their options.

    Parameters:
        None

    Returns:
        ArgumentParser
    '''

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
    print(loader.subcommands)

    sys.exit(0)

    # dynamically load all the submodules prefixed with "_sub_cmd"
    for module in iter_modules(mmpm.subcommands.__path__):
        if module.name.startswith("_sub_cmd"):
            try:
                import_module(f"mmpm.subcommands.{module.name}").setup(subparser)
            except Exception as error:
                print(f"Failed to load subcommand module: {error}")

    argcomplete.autocomplete(parser) # register autocompletion for the subcommands

    return parser
