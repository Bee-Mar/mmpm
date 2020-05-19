#!/usr/bin/env python3
# pylint: disable=unused-argument
import argparse
import sys
from mmpm.utils import MMPM_WIKI_URL


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

    subparsers = arg_parser.add_subparsers(title='MMPM subcommands', description='use `mmpm <sub-command> --help` to see more details')

    module_parser = subparsers.add_parser('module', help='subcommands to handle installation, removal, updating, and/or upgrading of MagicMirror modules')
    module_parser.add_argument('-i', '--install', nargs='+', help='install module(s) with given case-sensitive name(s) separated by spaces', dest='module_install')
    module_parser.add_argument('-r', '--remove', nargs='+', help='remove module(s) with given case-sensitive name(s) separated by spaces', dest='module_remove')
    module_parser.add_argument('-s', '--search', nargs=1, help='list all modules whose details match given search string', dest='module_search')
    module_parser.add_argument('-u', '--update', action='store_true', help='check for updates for each of the currently installed modules.', dest='module_update')
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

    snapshot_parser = subparsers.add_parser('snapshot', help='subcommands to refresh snapshot or display basic details about snapshot')
    snapshot_parser.add_argument('-r', '--refresh', action='store_true', help='forces a refresh of the modules snapshot.', dest='snapshot_refresh')
    snapshot_parser.add_argument('-d', '--details', action='store_true', help='display details about the most recent MagicMirror modules snapshot', dest='snapshot_details')

    show_parser = subparsers.add_parser('show')
    show_parser.add_argument('-i', '--installed', action='store_true', help='show all currently installed modules', dest='show_installed')
    show_parser.add_argument('-c', '--categories', action='store_true', help='show all module categories', dest='show_categories')
    show_parser.add_argument('-a', '--all', action='store_true', help='show all modules available in the marketplace', dest='show_all')
    show_parser.add_argument('-g', '--gui-url', action='store_true', help='show the URL of the MMPM GUI', dest='show_gui_url')
    show_parser.add_argument('-v', '--version', action='store_true', help='display MMPM version number', dest='show_version')

    open_parser = subparsers.add_parser('open', help='subcommand to open MagicMirror config or MMPM GUI')
    open_parser.add_argument('-c', '--config', action='store_true', help='open MagicMirror config in your $EDITOR', dest='open_config')
    open_parser.add_argument('-g', '--gui', type=list, help='open the MMPM GUI in your browser', dest='open_gui')

    add_ext_module_parser = subparsers.add_parser('add-ext-module', help='manually add a module to the database not found in the 3rd Party Wiki')
    add_ext_module_parser.add_argument('-t', '--title', type=str, help='title of external module', dest='ext_module_title')
    add_ext_module_parser.add_argument('-a', '--author', type=str, help='author of external module', dest='ext_module_author')
    add_ext_module_parser.add_argument('-r', '--repo', type=str, help='repo URL of external module', dest='ext_module_repo')
    add_ext_module_parser.add_argument('-d', '--description', type=str, help='description external module', dest='ext_module_description')
    add_ext_module_parser.add_argument('--remove', type=str, help='remove external module (similar pattern of add-apt-repository --remove)', dest='ext_module_remove')

    open_parser = subparsers.add_parser('tail', help='tail the MMPM and/or Gunicorn log files')
    open_parser.add_argument('-m', '--mmpm', action='store_true', help='tail the MMPM log files', dest='tail_mmpm')
    open_parser.add_argument('-g', '--gunicorn', type=list, help='tail the Gunicorn log files', dest='tail_gunicorn')

    magicmirror_parser = subparsers.add_parser('magicmirror', help='subcommands to control the MagicMirror')
    magicmirror_parser.add_argument('-i', '--install', action='store_true', help='install the most recent version of MagicMirror', dest='magicmirror_install')
    magicmirror_parser.add_argument('-u', '--update', action='store_true', help='Checks if upgrades are available for MMPM', dest='magicmirror_update')
    magicmirror_parser.add_argument('-U', '--upgrade', action='store_true', help='upgrade MMPM, if available', dest='magicmirror_upgrade')
    magicmirror_parser.add_argument('--status', action='store_true', help='show the status of modules on your MagicMirror', dest='magicmirror_status')
    magicmirror_parser.add_argument('--start', action='store_true', help='start the MagicMirror (works with pm2)', dest='magicmirror_start')
    magicmirror_parser.add_argument('--stop', action='store_true', help='stop the MagicMirror (works with pm2)', dest='magicmirror_stop')
    magicmirror_parser.add_argument('--restart', action='store_true', help='restart the MagicMirror (works with pm2)', dest='magicmirror_restart')

    arg_parser.add_argument('-u', '--update', action='store_true', help='Checks if upgrades are available for MMPM', dest='mmpm_update')
    arg_parser.add_argument('-U', '--upgrade', action='store_true', help='upgrade MMPM, if available', dest='mmpm_upgrade')
    arg_parser.add_argument( '-y', '--yes', action='store_true', default=False, help='Assume yes for anything interactive', dest='assume_yes')

    #hidden argument used for the GUI interface
    arg_parser.add_argument('--GUI', action='store_true', default=False, help=argparse.SUPPRESS, dest='GUI')

    if len(sys.argv) < 2:
        arg_parser.print_help()
        sys.exit(0)

    print(arg_parser.parse_args())

    return arg_parser.parse_args()
