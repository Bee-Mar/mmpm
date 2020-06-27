#!/usr/bin/env python3
# pylint: disable=unused-argument
import sys
import argparse
import argcomplete
import mmpm.consts

# subcommand names (these could go in consts.py, but for the sake of mnemonics for mmpm.py, they'll stay)
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
        dest='subcommand',
    )

    # SEARCH PARSER
    search_parser = subparsers.add_parser(
        SEARCH,
        usage='\n  mmpm search <query> [--table] [--case-sensitive]',
        help='search for MagicMirror packages'
    )

    search_parser.add_argument(
        '-c',
        '--case-sensitive',
        action='store_true',
        help='search for packages using a case-sensitive term',
        dest='case_sensitive'
    )

    search_parser.add_argument(
        '--table',
        action='store_true',
        help='display output in table format',
        dest='table_formatted'
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
    update_parser = subparsers.add_parser(
        UPDATE,
        usage='\n  mmpm update [--mmpm] [--magicmirror] [--full] [--yes]',
        help='check for updates to installed packages, MMPM, and/or MagicMirror'
    )

    update_parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        default=False,
        help='assume yes for user response and do not show prompt',
        dest='assume_yes'
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
        help='check for updates to all installed packages, MMPM, and MagicMirror',
        dest='full'
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

   # LIST SUBCOMMANDS
    list_parser = subparsers.add_parser(
        LIST,
        usage='\n  mmpm list [--installed] [--categories] [--all] [--gui-url] [--table]',
        help='list items like installed packages, packages available, etc'
    )

    list_parser.add_argument(
        '-i',
        '--installed',
        action='store_true',
        help='list all currently installed packages',
        dest='installed'
    )

    list_parser.add_argument(
        '-c',
        '--categories',
        action='store_true',
        help='list all package categories',
        dest='categories'
    )

    list_parser.add_argument(
        '-a',
        '--all',
        action='store_true',
        help='list all packages available in the marketplace', dest='all'
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
        help='open MagicMirror config or MMPM GUI'
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

    #show_parser
    subparsers.add_parser(
        SHOW,
        usage='\n  mmpm show <package(s)>',
        help='show details about one or more packages listed in the MagicMirror 3rd party database'
    )

    # ADD EXTERNAL PACKAGE SUBCOMMANDS
    add_ext_package_parser = subparsers.add_parser(
        ADD_EXT_PKG,
        usage='\n  mmpm add-ext-package [--title=<title>] [--author=<author>] [--repo=<repo>] [--desc=<description>]\n  mmpm add-ext-package --remove <package> [--yes]',
        help='manually add packages to the database not found in the MagicMirror 3rd party database'
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
        help='display MMPM and/or Gunicorn log files'
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
        usage='\n  mmpm mm-ctl [--status] [--restart] [--start] [--stop]\n  mmpm mm-ctl [--status] [--table]',
        help='commands to control the MagicMirror'
    )

    mm_ctl_parser.add_argument(
        '--status',
        action='store_true',
        help='show the status of packages on your MagicMirror',
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
    subparsers.add_parser(
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
