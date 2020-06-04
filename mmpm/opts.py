#!/usr/bin/env python3
# pylint: disable=unused-argument
import sys
import argparse
import argcomplete
from mmpm.consts import MMPM_WIKI_URL

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
ENV = 'env'
SHOW = 'show'


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
        epilog=f'More details at {MMPM_WIKI_URL}',
        description='''
            The MagicMirror Package Manager is a CLI designed to simplify the
            installation, removal, and maintenance of MagicMirror modules.
            '''
    )

    subparsers = arg_parser.add_subparsers(
        title='MMPM subcommands',
        description='use `mmpm <subcommand> --help` to see more details',
        dest='subcommand'
    )

    # SEARCH PARSER
    search_parser = subparsers.add_parser(
        SEARCH,
        usage='\n  mmpm search <keyword> [--table] [--case-sensitive]',
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
        dest='case_sensitive'
    )

    # INSTALL PARSER
    install_parser = subparsers.add_parser(
        INSTALL,
        usage='\n  mmpm install <module> [--yes]',
        help='install MagicMirror modules found in the database'
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
        usage='\n  mmpm remove <module(s)> [--yes]',
        help='remove currently install modules'
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
    update_parser = subparsers.add_parser(
        UPDATE,
        usage='\n  mmpm update <module(s)>\n  mmpm update [--mmpm] [--magicmirror] [--full]',
        help='check for updates to installed modules or MMPM'
    )

    update_parser.add_argument(
        '--mmpm',
        action='store_true',
        help='only check for updates to MMPM',
        dest='mmpm'
    )

    update_parser.add_argument(
        '--magicmirror',
        action='store_true',
        help='only check for updates to MagicMirror',
        dest='magicmirror'
    )

    update_parser.add_argument(
        '--full',
        action='store_true',
        help='check for updates to all installed modules, MMPM, and MagicMirror',
        dest='full'
    )

    update_parser.add_argument(
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
        help='subcommands to refresh or display basic details about the database'
    )

    database_parser.add_argument(
        '-r',
        '--refresh',
        action='store_true',
        help='forces a refresh of the modules database',
        dest='refresh'
    )

    database_parser.add_argument(
        '-d',
        '--details',
        action='store_true',
        help='display details about the most recent MagicMirror modules database',
        dest='details'
    )

   # LIST SUBCOMMANDS
    list_parser = subparsers.add_parser(
        LIST,
        usage='\n  mmpm list [--installed] [--categories] [--all] [--gui-url] [--table]',
        help='subcommands to list items like installed modules, modules available, etc'
    )

    list_parser.add_argument(
        '-i',
        '--installed',
        action='store_true',
        help='list all currently installed modules',
        dest='installed'
    )

    list_parser.add_argument(
        '-c',
        '--categories',
        action='store_true',
        help='list all module categories',
        dest='categories'
    )

    list_parser.add_argument(
        '-a',
        '--all',
        action='store_true',
        help='list all modules available in the marketplace', dest='all'
    )

    list_parser.add_argument(
        '-g',
        '--gui-url',
        action='store_true',
        help='list the URL of the MMPM GUI',
        dest='gui_url'
    )

    list_parser.add_argument(
        '--table',
        action='store_true',
        help='display output in table format, where applicable',
        dest='table_formatted'
    )

    # OPEN SUBCOMMANDS
    open_parser = subparsers.add_parser(
        OPEN,
        usage='\n  mmpm open [--config] [--gui]',
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
        help='open the MMPM GUI in your default browser using xdg-open',
        dest='gui'
    )

    show_parser = subparsers.add_parser(
        SHOW,
        usage='\n  mmpm show <module(s)>',
        help='show details about one or more modules listed in the MagicMirror 3rd party database'
    )

    # ADD EXTERNAL MODULE SUBCOMMANDS
    add_ext_module_parser = subparsers.add_parser(
        ADD_EXT_MODULE,
        usage='\n  mmpm add-ext-module [--title=<title>] [--author=<author>] [--repo=<repo>] [--desc=<description>]\n  mmpm add-ext-module --remove <module>',
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
        '--desc',
        type=str,
        help='description of external module (will be prompted if not provided)',
        dest='desc'
    )

    add_ext_module_parser.add_argument(
        '--remove',
        nargs='+',
        help='remove external module (similar pattern of add-apt-repository --remove)',
        dest='remove'
    )

    add_ext_module_parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        default=False,
        help='assume yes for user response and do not show prompt',
        dest='assume_yes'
    )

    # LOGS SUBCOMMANDS
    logs_parser = subparsers.add_parser(
        LOGS,
        usage='\n  mmpm logs [--cli] [--web] [--tail]',
        help='display the MMPM and/or Gunicorn log files (displays all logs if no args are given)'
    )

    logs_parser.add_argument(
        '-c',
        '--cli',
        action='store_true',
        help='cat the MMPM CLI log files',
        dest='cli'
    )

    logs_parser.add_argument(
        '-g',
        '--gui',
        action='store_true',
        help='cat the MMPM GUI (Gunicorn) log files',
        dest='gui'
    )

    logs_parser.add_argument(
        '-t',
        '--tail',
        action='store_true',
        help='tail the log file(s) in real time (used in conjuction with -c and/or -g)',
        dest='tail'
    )

    # MM_CTL SUBCOMMANDS
    mm_ctl_parser = subparsers.add_parser(
        MM_CTL,
        usage='\n  mmpm mm-ctl [--status] [--restart] [--start] [--stop] [--update] [--upgrade] [--install]',
        help='subcommands to control MagicMirror'
    )

    mm_ctl_parser.add_argument(
        '--status',
        action='store_true',
        help='show the status of modules on your MagicMirror',
        dest='status'
    )

    mm_ctl_parser.add_argument(
        '--table',
        action='store_true',
        help='display output in table format, used with --status',
        dest='table_formatted'
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
        dest='restart'
    )

    # magicmirror_parser.add_argument(
    #        '--rotate',
    #        action='store_true',
    #        choices=['0', '90', '180', '270'],
    #        help='rotate MagicMirror screen',
    #        dest='rotate'
    # )

    # ENV SUBCOMMANDS
    env_parser = subparsers.add_parser(
        ENV,
        usage='\n  mmpm env',
        help='display the MMPM environment variables and their value(s)'
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

    argcomplete.autocomplete(arg_parser)

    if len(sys.argv) < 2:
        arg_parser.print_help()
        sys.exit(0)

    return arg_parser
