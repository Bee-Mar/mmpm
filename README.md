<p align="center">
  <!-- badges start -->
  <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=L2ML7F8DTMAT2&currency_code=USD&source=ur" target="_blank">
    <img src="https://img.shields.io/badge/Donate-PayPal-green.svg" alt="PayPal">
  </a>
  <a href="http://choosealicense.com/licenses/mit" target="_blank">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  </a>
  <a href="https://travis-ci.org/github/Bee-Mar/mmpm" target="_blank">
    <img src="https://travis-ci.org/Bee-Mar/mmpm.svg?branch=master" alt="Travis CI">
  </a>
  <a href="https://hub.docker.com/r/karsten13/mmpm" target="_blank">
    <img src="https://img.shields.io/docker/pulls/karsten13/mmpm.svg" alt="Docker Pulls">
  </a>
  <a href="https://pypi.org/project/mmpm" target="_blank">
    <img src="https://img.shields.io/pypi/v/mmpm.svg" alt="PyPI version">
  </a>
  <!-- badges end -->

  <!-- main title/logo -->
  <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=L2ML7F8DTMAT2&currency_code=USD&source=ur" target="_blank">
    <img src="assets/MagicMirrorPackageManager.png" alt="MagicMirror Package Manager">
  </a>
</p>

| Author          | Contact                           |
| --------------- | --------------------------------- |
| Brandon Marlowe | bpmarlowe-software@protonmail.com |

`MMPM`, the MagicMirror Package Manager is a self updating command line and graphical interface designed to simplify the installation, removal, and maintenance of MagicMirror packages.

The MagicMirror Package Manager is featured as an alternative installation method on the [MagicMirror Documentation](https://docs.magicmirror.builders/getting-started/installation.html#alternative-installation-methods).

Features of MMPM include the following:

- Installation, removal, updating, and upgrading of packages
- Search, and show package details
- Adding external package sources (think of it like PPAs for Ubuntu)
- Tab-Autocompletion
- Quick config editing access
- Installing MagicMirror
- Hide/Show MagicMirror modules
- Start/Stop/Restart MagicMirror (works with `npm`, `pm2`, and `docker-compose`)
- RaspberryPi 3 screen rotation

## TLDR; What's the Installation/Removal Process?

MMPM is available on [PyPI](https://pypi.org/project/mmpm), and can be installed through `pip`. See below for details before installing.

Requirements:
- Python3.7 or greater. Installation will fail if you do not meet this requirement
- Python3 Virtual Environment (`pip3 install virtualenv --user`)

Optional Requirements:
- NGINX (`nginx-full` for Debian/Ubuntu, `nginx-mainline` for Arch), only if wanting to install the GUI

Using a virtualenv is the recommended way of installing MMPM. The version numbers of dependencies used by
MMPM are strict because bugs have been found within both newer and older versions of those packages
that cause undefined behavior.

The quickstart guide:

``` sh
python3 -m venv ~/.venv;
echo PATH=$PATH:~/.venv/bin >> ~/.bashrc # assuming you're using bash
source .bashrc .venv/bin/activate

pip install mmpm

mmpm install --gui # if you would like to install the GUI
mmpm install --as-module # reuired if you would like the ability to hide/show MagicMirror modules
mmpm install --autocomplete # if you would like to install the CLI auto-completion feature
```

See the [MMPM Installation](https://github.com/Bee-Mar/mmpm/wiki/MMPM-Installation) and [MMPM Removal](https://github.com/Bee-Mar/mmpm/wiki/MMPM-Removal) sections of the wiki for more detailed installation and removal instructions, respectively.



## Refer to the Wiki and Log Files First

If any issues arise, please consult the wiki first, which can be found [here](https://github.com/Bee-Mar/mmpm/wiki). Additionally, please examine the log files for `MMPM` located in `~/.config/mmpm/log/`, and post any relevant information when creating an issue.

## Potential Problems

This project is entirely dependent on the structure of the [MagicMirror 3rd Party Modules](https://github.com/MichMich/MagicMirror/wiki/3rd-Party-Modules) page. The HTML is parsed, and the appropriate text of each module is extracted. If for some reason any of the information is not displayed correctly, it is most likely due to someone changing the structure of the page. Ideally, in the future, a database will be constructed, and things will be handeled in a more formal, predictable way.
