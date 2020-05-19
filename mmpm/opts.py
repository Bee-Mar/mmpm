#!/usr/bin/env python3
# pylint: disable=unused-argument
import argparse
import sys
from mmpm.consts import MMPM_WIKI_URL
import argcomplete

# subcommand names (these could go in consts.py, but for the sake of mnemonics for mmpm.py, they'll stay)
MODULE = 'module'
SNAPSHOT = 'snapshot'
SHOW = 'show'
MAGICMIRROR = 'magicmirror'
OPEN = 'open'
ADD_EXT_MODULE = 'add-ext-module'
LOGS = 'logs'


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

    subparsers = arg_parser.add_subparsers(title='MMPM subcommands', description='use `mmpm <sub-command> --help` to see more details', dest='subcommand')

    module_parser = subparsers.add_parser(MODULE, help='manage installation, removal, updating, and/or upgrading of MagicMirror modules')
    module_parser.add_argument('-i', '--install', nargs='+', help='install module(s) with given case-sensitive name(s) separated by spaces', dest='install')
    module_parser.add_argument('-r', '--remove', nargs='+', help='remove module(s) with given case-sensitive name(s) separated by spaces', dest='remove')
    module_parser.add_argument('-s', '--search', nargs=1, help='list all modules whose details match given search string', dest='search')
    module_parser.add_argument('-u', '--update', action='store_true', help='check for updates for each of the currently installed modules.', dest='update')
    module_parser.add_argument(
        '-U',
        '--upgrade',
        action='append',
        nargs='*',
        help='''
            Upgrade currently installed modules. If no module name is provided,
            all modules will be upgraded. To upgrade specific modules, supply
            one or more module name, space delimited.
            ''',
        dest='module_upgrade'
    )

    snapshot_parser = subparsers.add_parser(SNAPSHOT, help='subcommands to refresh snapshot or display basic details about snapshot')
    snapshot_parser.add_argument('-r', '--refresh', action='store_true', help='forces a refresh of the modules snapshot.', dest='refresh')
    snapshot_parser.add_argument('-d', '--details', action='store_true', help='display details about the most recent MagicMirror modules snapshot', dest='details')

    show_parser = subparsers.add_parser(SHOW, help='subcommands to show more details about modules and other MMPM utilities')
    show_parser.add_argument('-i', '--installed', action='store_true', help='show all currently installed modules', dest='installed')
    show_parser.add_argument('-c', '--categories', action='store_true', help='show all module categories', dest='categories')
    show_parser.add_argument('-a', '--all', action='store_true', help='show all modules available in the marketplace', dest='all')
    show_parser.add_argument('-g', '--gui-url', action='store_true', help='show the URL of the MMPM GUI', dest='gui_url')

    open_parser = subparsers.add_parser(OPEN, help='subcommands to open MagicMirror config or MMPM GUI')
    open_parser.add_argument('-c', '--config', action='store_true', help='open MagicMirror config in your $EDITOR', dest='config')
    open_parser.add_argument('-g', '--gui', action='store_true', help='open the MMPM GUI in your browser', dest='gui')

    add_ext_module_parser = subparsers.add_parser(
            ADD_EXT_MODULE,
            help='manually add a module to the database not found in the 3rd Party Wiki (can be extecuted without any arguments)'
    )
    add_ext_module_parser.add_argument('-t', '--title', type=str, help='title of external module', dest='title')
    add_ext_module_parser.add_argument('-a', '--author', type=str, help='author of external module', dest='author')
    add_ext_module_parser.add_argument('-r', '--repo', type=str, help='repo URL of external module', dest='repo')
    add_ext_module_parser.add_argument('-d', '--description', type=str, help='description external module', dest='description')
    add_ext_module_parser.add_argument('--remove', type=str, help='remove external module (similar pattern of add-apt-repository --remove)', dest='remove')

    open_parser = subparsers.add_parser(LOGS, help='display the MMPM and/or Gunicorn log files')
    open_parser.add_argument('-t', '--tail', action='store_true', help='tail the log file(s) in real time (used in conjuction with -m and/or -g)', dest='tail')
    open_parser.add_argument('-m', '--mmpm', action='store_true', help='cat the MMPM log files', dest='mmpm_logs')
    open_parser.add_argument('-g', '--gunicorn', action='store_true', help='cat the Gunicorn log files', dest='gunicorn_logs')

    magicmirror_parser = subparsers.add_parser(MAGICMIRROR, help='subcommands to control the MagicMirror')
    magicmirror_parser.add_argument('-i', '--install', action='store_true', help='install the most recent version of MagicMirror', dest='install')
    magicmirror_parser.add_argument('-u', '--update', action='store_true', help='Checks if upgrades are available for MMPM', dest='update')
    magicmirror_parser.add_argument('-U', '--upgrade', action='store_true', help='upgrade MMPM, if available', dest='upgrade')
    magicmirror_parser.add_argument('--status', action='store_true', help='show the status of modules on your MagicMirror', dest='status')
    magicmirror_parser.add_argument('--start', action='store_true', help='start the MagicMirror (works with pm2)', dest='start')
    magicmirror_parser.add_argument('--stop', action='store_true', help='stop the MagicMirror (works with pm2)', dest='stop')
    magicmirror_parser.add_argument('--restart', action='store_true', help='restart the MagicMirror (works with pm2)', dest='start')
    #magicmirror_parser.add_argument('--rotate', action='store_true', choices=['0', '90', '180', '270'], help='rotate MagicMirror screen', dest='rotate')

    arg_parser.add_argument('-u', '--update', action='store_true', help='Checks if upgrades are available for MMPM', dest='mmpm_update')
    arg_parser.add_argument('-U', '--upgrade', action='store_true', help='upgrade MMPM, if available', dest='mmpm_upgrade')
    arg_parser.add_argument( '-y', '--yes', action='store_true', default=False, help='Assume yes for anything interactive', dest='assume_yes')

    #hidden argument used for the GUI interface
    arg_parser.add_argument('--GUI', action='store_true', default=False, help=argparse.SUPPRESS, dest='GUI')
    arg_parser.add_argument('-v', '--version', action='store_true', help='display MMPM version number', dest='version')

    if len(sys.argv) < 2:
        arg_parser.print_help()
        sys.exit(0)

    argcomplete.autocomplete(arg_parser)
    return arg_parser.parse_args()
