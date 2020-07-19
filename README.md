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
  <a href="https://pypi.org/project/mmpm/2.0/" target="_blank">
    <img src="https://img.shields.io/pypi/v/mmpm.svg" alt="PyPI version">
  </a>
  <!-- badges end -->

  <!-- The main Title -->
  <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=L2ML7F8DTMAT2&currency_code=USD&source=ur" target="_blank">
    <img src="assets/MagicMirrorPackageManager.png" alt="MagicMirror Package Manager">
  </a>
</p>

| Author          | Contact                           |
| --------------- | --------------------------------- |
| Brandon Marlowe | bpmarlowe-software@protonmail.com |

`MMPM`, the MagicMirror Package Manager is a command line and graphical interface designed to simplify the installation, removal, and maintenance of MagicMirror packages.

The MagicMirror Package Manager is featured as an alternative installation method on the [MagicMirror Documentation](https://docs.magicmirror.builders/getting-started/installation.html#alternative-installation-methods).

The supported features are comprised of the following categories:

- Search
- Installation
- Removal
- Updates/Upgrading
- Adding external module sources (think of it like PPAs for Ubuntu)
- Quick config editing access
- Self updating
- Installing MagicMirror
- Hiding/showing MagicMirror modules on the fly


## TLDR; What's the Installation/Removal Process?

See the [MMPM Installation](https://github.com/Bee-Mar/mmpm/wiki/MMPM-Installation) and [MMPM Removal](https://github.com/Bee-Mar/mmpm/wiki/MMPM-Removal) sections of the wiki for installation and removal instructions, respectively.

## Refer to the Wiki and Log Files First

If any issues arise, please consult the wiki first, which can be found [here](https://github.com/Bee-Mar/mmpm/wiki). Additionally, please examine the log files for `MMPM` located in `~/.config/mmpm/log/`, and post any relevant information when creating an issue.

## Potential Problems

This project is entirely dependent on the structure of the [MagicMirror 3rd Party Modules](https://github.com/MichMich/MagicMirror/wiki/3rd-Party-Modules) page. The HTML is parsed, and the appropriate text of each module is extracted. If for some reason any of the information is not displayed correctly, it is most likely due to someone changing the structure of the page. Ideally, in the future, a database will be constructed, and things will be handeled in a more formal, predictable way.
