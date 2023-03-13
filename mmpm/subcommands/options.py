#!/usr/bin/env python3
# pylint: disable=unused-argument
import sys
import argparse
import argcomplete
import mmpm.consts
import mmpm.subcommands
from typing import List
from pkgutil import iter_modules
from importlib import import_module

# subcommand names. These could go in mmpm.consts.py, but for the sake of mnemonics
# for mmpm.py, they'll stay (ie, opts.INSTALL, opts.LIST, etc)
INSTALL: str = 'install'
SEARCH: str = 'search'
REMOVE: str = 'remove'
DB: str = 'db'
LIST: str = 'list'
MM_CTL: str = 'mm-ctl'
OPEN: str = 'open'
ADD_EXT_PKG: str = 'add-ext-pkg'
LOG: str = 'log'
UPDATE: str = 'update'
UPGRADE: str = 'upgrade'
ENV: str = 'env'
SHOW: str = 'show'
VERSION: str = "version"

SINGLE_OPTION_ARGS: List[str] = [INSTALL, DB, LIST, OPEN]


def setup() -> argparse.ArgumentParser:
    '''
    Initializes all subcommand and their options.

    Parameters:
        None

    Returns:
        ArgumentParser
    '''

    parser = argparse.ArgumentParser(
        prog='mmpm',
        usage='mmpm <subcommand> [option(s)]',
        epilog=f'Visit {mmpm.consts.MMPM_WIKI_URL} for more details',
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

    # dynamically load all the submodules prefixed with "_sub_cmd"
    for module in iter_modules(mmpm.subcommands.__path__):
        if module.name.startswith("_sub_cmd"):
            try:
                import_module(f"mmpm.subcommands.{module.name}").setup(subparser)
            except Exception as error:
                print(f"Failed to load subcommand module: {error}")

    argcomplete.autocomplete(parser) # register autocompletion for the subcommands

    return parser
