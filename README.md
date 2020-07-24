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

## Features:

- Installation, removal, updating, and upgrading of packages
- Search for and show package details
- Adding external package sources (think of it like PPAs for Ubuntu)
- Tab-Autocompletion for the CLI
- Quick MagicMirror config editing access
- Installing MagicMirror
- Hide/Show MagicMirror modules
- Start/Stop/Restart MagicMirror (works with `npm`, `pm2`, and `docker-compose`)
- RaspberryPi 3 screen rotation

## TLDR; What's the Installation/Removal Process?

MMPM is available on [PyPI](https://pypi.org/project/mmpm), and can be installed through `pip`. See below for details before installing.

**NOTE**: Using a virtualenv is STRONGLY recommended. Some of the dependency versions used by MMPM
are strict. Bugs have been found within other versions that cause undefined behavior, and break
parts of MMPM.

**MMPM Environment Variables**: Please read the [MMPM Environment
Variables](https://github.com/Bee-Mar/mmpm/wiki/MMPM-Environment-Variables) section. Not setting
these properly will cause MMPM to not function as expected.

Requirements:

- `python >= 3.7`. Installation will fail if your version of Python is not >= 3.7
- NGINX (`nginx-full` for Debian/Ubuntu, `nginx-mainline` for Arch), only if wanting to install the GUI

The quickstart guide using a virtualenv:

``` sh
$ pip3 install --user virtualenv
$ python3 -m venv ~/.venv

# OPTION 1: you can add the venv to your PATH
$ echo "export PATH=$PATH:~/.venv/bin" >> ~/.bashrc

# OPTION 2: create an alias, but DO NOT
$ echo "alias mmpm=~/.venv/bin/mmpm" >> ~/.bashrc

$ source ~/.bashrc ~/.venv/bin/activate

$ pip3 install mmpm
$ mmpm install --gui # to install the GUI (needs sudo permissions)
$ mmpm install --autocomplete # to install the CLI auto-completion feature
$ mmpm install --as-module  # required to hide/show MagicMirror modules
```


The quickstart guide _without_ a virtualenv:

``` sh
$ pip3 install --user --no-cache-dir mmpm
$ mmpm install --gui # to install the GUI (needs sudo permissions)
$ mmpm install --autocomplete # to install the CLI auto-completion feature
$ mmpm install --as-module  # required to hide/show MagicMirror modules
```


See the [MMPM Installation](https://github.com/Bee-Mar/mmpm/wiki/MMPM-Installation) and [MMPM Removal](https://github.com/Bee-Mar/mmpm/wiki/MMPM-Removal) sections of the wiki for more detailed installation and removal instructions, respectively.

## Refer to the [Wiki](https://github.com/Bee-Mar/mmpm/wiki) and Log Files First

For any bugs encountered, please examine the log files by running `mmpm log`. If creating a GitHub issue
is needed, please attach the log files. You can create a ZIP archive of files through the Control
Center of the GUI, or by running `mmpm log --zip` through the CLI.

## Potential Problems

This project is entirely dependent on the structure of the [MagicMirror 3rd Party
Modules](https://github.com/MichMich/MagicMirror/wiki/3rd-Party-Modules) page. The HTML is parsed,
and the appropriate text of each module is extracted. If for some reason any of the information is
not displayed correctly, it is most likely due to someone changing the structure of the page.
Ideally, in the future, a database will be constructed, and things will be handeled in a more
formal, predictable way.
