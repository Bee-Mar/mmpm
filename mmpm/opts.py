#!/usr/bin/env python3
# pylint: disable=unused-argument
import argparse
import sys
from mmpm.consts import MMPM_WIKI_URL
import argcomplete

# subcommand names (these could go in consts.py, but for the sake of mnemonics for mmpm.py, they'll stay)
INSTALL = 'install'
SEARCH = 'search'
REMOVE = 'remove'
DATABASE = 'db'
LIST = 'list'
MM_CTL = 'mm-ctl'
OPEN = 'open'
ADD_EXT_MODULE = 'add-ext-module'
LOGS = 'logs'
UPDATE = 'update'
UPGRADE = 'upgrade'


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
        epilog=f'More details at {MMPM_WIKI_URL}',
        description='''
            The MagicMirror Package Manager is a CLI designed to simplify the
            installation, removal, and maintenance of MagicMirror modules.
            '''
    )

    subparsers = arg_parser.add_subparsers(
        title='MMPM subcommands',
        description='use `mmpm [name-of-sub-command] --help` to see more details',
        dest='subcommand'
    )

    # SEARCH PARSER
    search_parser = subparsers.add_parser(
        SEARCH,
        help='search for MagicMirror modules listed in the database'
    )

    search_parser.add_argument(
        '--table',
        action='store_true',
        help='display output in table format',
        dest='table_formatted'
    )

    search_parser.add_argument(
        '-c',
        '--case-sensitive',
        action='store_true',
        help='search for modules using a case-sensitive term',
        dest='search_case_sensitive'
    )

    # INSTALL PARSER
    install_parser = subparsers.add_parser(
        INSTALL,
        help='install MagicMirror modules found in the database'
    )

    # REMOVE PARSER
    install_parser = subparsers.add_parser(
        REMOVE,
        help='remove currently install modules'
    )

    # UPDATE PARSER
    update_parser = subparsers.add_parser(
        UPDATE,
        help='check for updates to installed modules or MMPM'
    )

    update_parser.add_argument(
        '--mmpm',
        action='store_true',
        help='check for updates to MMPM only'
    )

    update_parser.add_argument(
        '--magicmirror',
        action='store_true',
        help='check for updates to MagicMirror only'
    )

    update_parser.add_argument(
        '--full',
        action='store_true',
        help='check for updates to all installed modules, MMPM, and MagicMirror'
    )

    upgrade_parser = subparsers.add_parser(
        UPGRADE,
        help='upgrade modules and/or MMPM'
    )

    upgrade_parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        default=False,
        help='assume yes for user response and do not show prompt',
        dest='assume_yes'
    )

    upgrade_parser.add_argument(
        '--all',
        action='store_true',
        default=False,
        help='upgrade all modules, MMPM, and MagicMirror',
        dest='upgrade_all'
    )

    # DATABASE SUBCOMMANDS
    database_parser = subparsers.add_parser(
        DATABASE,
        help='subcommands to refresh or display basic details about the database'
    )

    database_parser.add_argument(
        '-r',
        '--refresh',
        action='store_true',
        help='forces a refresh of the modules database', dest='refresh'
    )

    database_parser.add_argument(
        '-d',
        '--details',
        action='store_true',
        help='display details about the most recent MagicMirror modules database',
        dest='details'
    )

    # LIST SUBCOMMANDS
    show_parser = subparsers.add_parser(
        LIST,
        help='subcommands to list items like installed modules, modules available, etc'
    )

    show_parser.add_argument(
        '-i',
        '--installed',
        action='store_true',
        help='show all currently installed modules', dest='installed'
    )

    show_parser.add_argument(
        '-c',
        '--categories',
        action='store_true',
        help='show all module categories',
        dest='categories'
    )

    show_parser.add_argument(
        '-a',
        '--all',
        action='store_true',
        help='show all modules available in the marketplace', dest='all'
    )

    show_parser.add_argument(
        '-g',
        '--gui-url',
        action='store_true',
        help='show the URL of the MMPM GUI',
        dest='gui_url'
    )

    show_parser.add_argument(
        '--table',
        action='store_true',
        help='display output in table format, where applicable',
        dest='table_formatted'
    )

    # OPEN SUBCOMMANDS
    open_parser = subparsers.add_parser(
        OPEN,
        help='subcommands to open MagicMirror config or MMPM GUI'
    )

    open_parser.add_argument(
        '-c',
        '--config',
        action='store_true',
        help='open MagicMirror config in your $EDITOR',
        dest='config'
    )

    open_parser.add_argument(
        '-g',
        '--gui',
        action='store_true',
        help='open the MMPM GUI in your browser',
        dest='gui'
    )

    # ADD EXTERNAL MODULE SUBCOMMANDS
    add_ext_module_parser = subparsers.add_parser(
        ADD_EXT_MODULE,
        help='manually add a module to the database not found in the 3rd Party Wiki'
    )

    add_ext_module_parser.add_argument(
        '-t',
        '--title',
        type=str,
        help='title of external module (will be prompted if not provided)',
        dest='title'
    )

    add_ext_module_parser.add_argument(
        '-a',
        '--author',
        type=str,
        help='author of external module (will be prompted if not provided)',
        dest='author'
    )

    add_ext_module_parser.add_argument(
        '-r',
        '--repo',
        type=str,
        help='repo URL of external module (will be prompted if not provided)',
        dest='repo'
    )

    add_ext_module_parser.add_argument(
        '-d',
        '--description',
        type=str,
        help='description external module (will be prompted if not provided)',
        dest='description'
    )

    add_ext_module_parser.add_argument(
        '--remove',
        type=str,
        help='remove external module (similar pattern of add-apt-repository --remove)',
        dest='remove'
    )

    # LOGS SUBCOMMANDS
    logs_parser = subparsers.add_parser(
        LOGS,
        help='display the MMPM and/or Gunicorn log files (displays all logs if no args are given)'
    )

    logs_parser.add_argument(
        '-m',
        '--mmpm',
        action='store_true',
        help='cat the MMPM log files',
        dest='mmpm_logs'
    )

    logs_parser.add_argument(
        '-g',
        '--gunicorn',
        action='store_true',
        help='cat the Gunicorn log files',
        dest='gunicorn_logs'
    )

    logs_parser.add_argument(
        '-t',
        '--tail',
        action='store_true',
        help='tail the log file(s) in real time (used in conjuction with -m and/or -g)', dest='tail'
    )

    # MM_CTL SUBCOMMANDS
    mm_ctl_parser = subparsers.add_parser(
        MM_CTL,
        help='subcommands to control MagicMirror'
    )

    mm_ctl_parser.add_argument(
        '--status',
        action='store_true',
        help='show the status of modules on your MagicMirror',
        dest='status'
    )

    mm_ctl_parser.add_argument(
        '--start',
        action='store_true',
        help='start the MagicMirror (works with pm2)',
        dest='start'
    )

    mm_ctl_parser.add_argument(
        '--stop',
        action='store_true',
        help='stop the MagicMirror (works with pm2)',
        dest='stop'
    )

    mm_ctl_parser.add_argument(
        '--restart',
        action='store_true',
        help='restart the MagicMirror (works with pm2)',
        dest='start'
    )

    # magicmirror_parser.add_argument(
    #        '--rotate',
    #        action='store_true',
    #        choices=['0', '90', '180', '270'],
    #        help='rotate MagicMirror screen',
    #        dest='rotate'
    # )

    mm_ctl_parser.add_argument(
        '-U',
        '--upgrade',
        action='store_true',
        help='upgrade MMPM, if available',
        dest='upgrade'
    )

    mm_ctl_parser.add_argument(
        '-u',
        '--update',
        action='store_true',
        help='Checks if upgrades are available for MMPM', dest='update'
    )

    mm_ctl_parser.add_argument(
        '-i',
        '--install',
        action='store_true',
        help='install the most recent version of MagicMirror',
        dest='install'
    )

    # MMPM AND GLOBAL OPTIONS
    arg_parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        help='display MMPM version number',
        dest='version'
    )

    # hidden argument used for the GUI interface
    arg_parser.add_argument(
        '--GUI',
        action='store_true',
        default=False,
        help=argparse.SUPPRESS,
        dest='GUI'
    )

    if len(sys.argv) < 2:
        arg_parser.print_help()
        sys.exit(0)

    return arg_parser.parse_known_args()
