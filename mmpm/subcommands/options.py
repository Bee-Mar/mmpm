#!/usr/bin/env python3
# pylint: disable=unused-argument
import sys
import argparse
import argcomplete
import mmpm.consts
from typing import List, Tuple
from mmpm.subcommands import (
    _search,
    _install,
    _remove,
    _update,
    _db,
    _upgrade,
    _list,
    _open,
    _show,
    _add_ext_pkg,
    _log,
    _mm_ctl,
    _env,
    _version,
    _completion,
    _guided_setup,
)

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
            installation, removal, and general maintenance of MagicMirror packages
            '''
    )

    subparser = parser.add_subparsers(
        title='MMPM subcommands',
        description='use `mmpm <subcommand> --help` to see more details',
        dest='subcmd',
    )

    # setup of all the subcommands and their options
    _install.setup(subparser)
    _search.setup(subparser)
    _remove.setup(subparser)
    _update.setup(subparser)
    _upgrade.setup(subparser)
    _db.setup(subparser)
    _list.setup(subparser)
    _open.setup(subparser)
    _show.setup(subparser)
    _add_ext_pkg.setup(subparser)
    _log.setup(subparser)
    _mm_ctl.setup(subparser)
    _env.setup(subparser)
    _version.setup(subparser)
    _completion.setup(subparser)
    _guided_setup.setup(subparser)

    argcomplete.autocomplete(parser) # register autocompletion for the subcommands

    return parser
