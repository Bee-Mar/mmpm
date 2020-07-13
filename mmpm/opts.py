#!/usr/bin/env python3
# pylint: disable=unused-argument
import sys
import argparse
import argcomplete
import mmpm.consts
from typing import List

# subcommand names. These could go in mmpm.consts.py, but for the sake of mnemonics
# for mmpm.py, they'll stay (ie, opts.INSTALL, opts.LIST, etc)
INSTALL: str = 'install'
SEARCH: str = 'search'
REMOVE: str = 'remove'
DATABASE: str = 'db'
LIST: str = 'list'
MM_CTL: str = 'mm-ctl'
OPEN: str = 'open'
ADD_EXT_PKG: str = 'add-ext-pkg'
LOG: str = 'log'
UPDATE: str = 'update'
UPGRADE: str = 'upgrade'
ENV: str = 'env'
SHOW: str = 'show'

SINGLE_OPTION_ARGS: List[str] = [INSTALL, DATABASE, LIST, OPEN]


def get_user_args() -> object:
    '''
    Wrapper method around ArgumentParser.parse_args()

    Parameters:
        None

    Returns:
        ArgumentParser objects
    '''

    arg_parser = argparse.ArgumentParser(
        prog='mmpm',
        usage='mmpm <subcommand> [option(s)]',
        epilog=f'Visit {mmpm.consts.MMPM_WIKI_URL} for more details',
        description='''
            The MagicMirror Package Manager CLI simplifies the
            installation, removal, and general maintenance of MagicMirror packages
            '''
    )

    subparsers = arg_parser.add_subparsers(
        title='MMPM subcommands',
        description='use `mmpm <subcommand> --help` to see more details',
        dest='subcmd',
    )

    # SEARCH PARSER
    search_parser = subparsers.add_parser(
        SEARCH,
        usage='\n  mmpm search <query> [--case-sensitive] [--exclude-local]',
        help='search for MagicMirror packages'
    )

    search_parser.add_argument(
        '-t',
        '--title-only',
        action='store_true',
        help='only show the title of the packages matching the search results',
        dest='title_only'
    )

    search_parser.add_argument(
        '-c',
        '--case-sensitive',
        action='store_true',
        help='search for packages using a case-sensitive query',
        dest='case_sensitive'
    )

    search_parser.add_argument(
        '-e',
        '--exclude-local',
        action='store_true',
        help='exclude locally installed packages from search results',
        dest='exclude_local'
    )

    # INSTALL PARSER
    install_parser = subparsers.add_parser(
        INSTALL,
        usage='\n  mmpm install <package(s)> [--yes]\n  mmpm install [--magicmirror] [--autocomplete]',
        help='install MagicMirror packages'
    )

    install_parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        default=False,
        help='assume yes for user response and do not show prompt',
        dest='assume_yes'
    )

    install_parser.add_argument(
        '--magicmirror',
        action='store_true',
        default=False,
        help='install MagicMirror, if not already installed',
        dest='magicmirror'
    )

    install_parser.add_argument(
        '--autocomplete',
        action='store_true',
        help='install autocompletion for the MMPM CLI',
        dest='autocomplete'
    )

    # REMOVE PARSER
    remove_parser = subparsers.add_parser(
        REMOVE,
        usage='\n  mmpm remove <package(s)> [--yes]',
        help='remove locally installed packages'
    )

    remove_parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        default=False,
        help='assume yes for user response and do not show prompt',
        dest='assume_yes'
    )

    # UPDATE PARSER
    subparsers.add_parser(
        UPDATE,
        usage='\n  mmpm update',
        help='check for updates for installed packages, MMPM, and MagicMirror'
    )

    # UPGRADE SUBCOMMANDS
    upgrade_parser = subparsers.add_parser(
        UPGRADE,
        usage='\n  mmpm upgrade [--yes]\n  mmpm upgrade <package(s)> <application(s)> [--yes]',
        help='upgrade packages, MMPM, and/or MagicMirror, if available'
    )

    upgrade_parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        default=False,
        help='assume yes for user response and do not show prompt',
        dest='assume_yes'
    )

    # DATABASE SUBCOMMANDS
    database_parser = subparsers.add_parser(
        DATABASE,
        usage='\n  mmpm db [--refresh] [--details]',
        help='refresh or display basic details about the database'
    )

    database_parser.add_argument(
        '-r',
        '--refresh',
        action='store_true',
        help='forces a refresh of the packages database',
        dest='refresh'
    )

    database_parser.add_argument(
        '-d',
        '--details',
        action='store_true',
        help='display details about the most recent MagicMirror packages database',
        dest='details'
    )

    database_parser.add_argument(
        '--dump',
        action='store_true',
        help='dump the database JSON contents to stdout',
        dest='dump'
    )

   # LIST SUBCOMMANDS
    list_parser = subparsers.add_parser(
        LIST,
        usage='\n  mmpm list [--all] [--exclude-local] [--categories] [--gui-url]',
        help='list items such as installed packages, packages available, available upgrades, etc'
    )

    list_parser.add_argument(
        '-a',
        '--all',
        action='store_true',
        help='list all available packages in the marketplace',
        dest='all'
    )

    list_parser.add_argument(
        '-e',
        '--exclude-local',
        action='store_true',
        help='list all available packages in the marketplace, excluding locally installed packages',
        dest='exclude_local'
    )

    list_parser.add_argument(
        '-i',
        '--installed',
        action='store_true',
        help='list all locally installed packages',
        dest='installed'
    )

    list_parser.add_argument(
        '-c',
        '--categories',
        action='store_true',
        help='list all available package categories',
        dest='categories'
    )

    list_parser.add_argument(
        '-t',
        '--title-only',
        action='store_true',
        help='display title only of packages (used with -c, -a, -e, or -i)',
        dest='title_only'
    )

    list_parser.add_argument(
        '-g',
        '--gui-url',
        action='store_true',
        help='list the URL of the MMPM GUI',
        dest='gui_url'
    )

    list_parser.add_argument(
        '--upgradeable',
        action='store_true',
        help='list packages that have available upgrades',
        dest='upgradeable'
    )

    # OPEN SUBCOMMANDS
    open_parser = subparsers.add_parser(
        OPEN,
        usage='\n  mmpm open [--config] [--css] [--gui] [--mm-wiki] [--mmpm-wiki]',
        help='open MagicMirror config.js, custom.css, the MMPM wiki, the MagicMirror wiki, or MagicMirror itself'
    )

    open_parser.add_argument(
        '--config',
        action='store_true',
        help='open MagicMirror config/config.js file in your $EDITOR',
        dest='config'
    )

    open_parser.add_argument(
        '--css',
        action='store_true',
        help='open MagicMirror custom/custom.css file (if it exists) in your $EDITOR',
        dest='custom_css'
    )

    open_parser.add_argument(
        '--gui',
        action='store_true',
        help='open the MMPM GUI in your default browser',
        dest='gui'
    )

    open_parser.add_argument(
        '--magicmirror',
        action='store_true',
        help='open MagicMirror in your default browser (uses the MMPM_MAGICMIRROR_URI address)',
        dest='magicmirror'
    )

    open_parser.add_argument(
        '--mm-wiki',
        action='store_true',
        help='open the MagicMirror GitHub wiki in your default browser',
        dest='mm_wiki'
    )

    open_parser.add_argument(
        '--mmpm-wiki',
        action='store_true',
        help='open the MMPM GitHub wiki in your default browser',
        dest='mmpm_wiki'
    )

    # show_parser
    show_parser = subparsers.add_parser(
        SHOW,
        usage='\n  mmpm show <package(s)> [--verbose]',
        help='show details about one or more packages listed in the MagicMirror 3rd party database'
    )

    show_parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='display extra detail for each package from the GitHub/GitLab/Bitbucket API',
        dest='verbose'
    )

    # ADD EXTERNAL PACKAGE SUBCOMMANDS
    add_ext_package_parser = subparsers.add_parser(
        ADD_EXT_PKG,
        usage='\n  mmpm add-ext-package [--title=<title>] [--author=<author>] [--repo=<repo>] [--desc=<description>]\n  mmpm add-ext-package --remove <package> [--yes]',
        help='manually add MagicMirror packages to your local database'
    )

    add_ext_package_parser.add_argument(
        '-t',
        '--title',
        type=str,
        help='title of external package (will be prompted if not provided)',
        dest='title'
    )

    add_ext_package_parser.add_argument(
        '-a',
        '--author',
        type=str,
        help='author of external package (will be prompted if not provided)',
        dest='author'
    )

    add_ext_package_parser.add_argument(
        '-r',
        '--repo',
        type=str,
        help='repo URL of external package (will be prompted if not provided)',
        dest='repo'
    )

    add_ext_package_parser.add_argument(
        '-d',
        '--desc',
        type=str,
        help='description of external package (will be prompted if not provided)',
        dest='desc'
    )

    add_ext_package_parser.add_argument(
        '--remove',
        nargs='+',
        help='remove external package (similar to `add-apt-repository` --remove)',
        dest='remove'
    )

    add_ext_package_parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        default=False,
        help='assume yes for user response and do not show prompt (used with --remove)',
        dest='assume_yes'
    )

    # LOGS SUBCOMMANDS
    log_parser = subparsers.add_parser(
        LOG,
        usage='\n  mmpm log [--cli] [--web] [--tail]',
        help='display or tail MMPM log files'
    )

    log_parser.add_argument(
        '-c',
        '--cli',
        action='store_true',
        help='cat the MMPM CLI log files',
        dest='cli'
    )

    log_parser.add_argument(
        '-g',
        '--gui',
        action='store_true',
        help='cat the MMPM GUI (Gunicorn) log files',
        dest='gui'
    )

    log_parser.add_argument(
        '-t',
        '--tail',
        action='store_true',
        help='tail the log file(s) in real time',
        dest='tail'
    )

    # MM_CTL SUBCOMMANDS
    mm_ctl_parser = subparsers.add_parser(
        MM_CTL,
        usage='\n  mmpm mm-ctl [--status] [--restart] [--start] [--stop]\n  mmpm mm-ctl [--rotate] {0, 90, 180, 270}',
        help='commands to control the MagicMirror'
    )

    mm_ctl_parser.add_argument(
        '--status',
        action='store_true',
        help='show the hidden/visible status of modules on your MagicMirror',
        dest='status'
    )

    mm_ctl_parser.add_argument(
        '--hide',
        nargs='+',
        help='hide modules on your MagicMirror',
        dest='hide'
    )

    mm_ctl_parser.add_argument(
        '--show',
        nargs='+',
        help='show modules on your MagicMirror',
        dest='show'
    )

    mm_ctl_parser.add_argument(
        '--start',
        action='store_true',
        help='start MagicMirror; works with pm2 and docker-compose',
        dest='start'
    )

    mm_ctl_parser.add_argument(
        '--stop',
        action='store_true',
        help='stop MagicMirror; works with pm2 and docker-compose',
        dest='stop'
    )

    mm_ctl_parser.add_argument(
        '--restart',
        action='store_true',
        help='restart MagicMirror; works with pm2 and docker-compose',
        dest='restart'
    )

    mm_ctl_parser.add_argument(
        '--rotate',
        choices=[0, 90, 180, 270],
        type=int,
        help='rotate MagicMirror screen to 0, 90, 180, or 270 degrees',
        dest='rotate'
    )

    # ENV SUBCOMMANDS
    env_parser = subparsers.add_parser(
        ENV,
        usage='\n  mmpm env',
        help='display the MMPM environment variables and their value(s)'
    )

    env_parser.add_argument(
        '-d',
        '--describe',
        action='store_true',
        help='display description for each environment variable',
        dest='describe'
    )

    # MMPM AND GLOBAL OPTIONS
    arg_parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        help='display MMPM version number',
        dest='version'
    )

    # adding this as an option in case the user doesn't install via 'make'
    arg_parser.add_argument(
        '--migrate',
        action='store_true',
        help='migrate legacy file names and database keys. Only required once if prior version of MMPM is < 1.25',
        dest='migrate'
    )

    # hidden argument used for the GUI interface
    arg_parser.add_argument(
        '--GUI',
        action='store_true',
        default=False,
        help=argparse.SUPPRESS,
        dest='GUI'
    )

    argcomplete.autocomplete(arg_parser)

    if len(sys.argv) < 2:
        arg_parser.print_help()
        sys.exit(0)

    return arg_parser
