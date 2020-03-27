<p align="center">
  <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=L2ML7F8DTMAT2&currency_code=USD&source=ur">
    <img src="https://img.shields.io/badge/Donate-PayPal-green.svg">
  </a>
  <a href="http://choosealicense.com/licenses/mit">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  </a>
  <a href="https://travis-ci.org/github/Bee-Mar/mmpm">
    <img src="https://travis-ci.org/Bee-Mar/mmpm.svg?branch=master">
  </a>
</p>

# MMPM - The MagicMirror Package Manager

| Author          | Contact                           |
| --------------- | --------------------------------- |
| Brandon Marlowe | bpmarlowe-software@protonmail.com |

The MagicMirror Package Manager (`mmpm`) is both a command line and web interface designed to simplify the installation, removal, and maintenance of MagicMirror modules.

<i>Consider this project to be in an Alpha state, so don't get too picky just yet, as you most likely will discover some bugs I was unable to find.</i>

The supported features are comprised of the following categories:

    1) Search
    2) Installation
    3) Removal
    4) Checking for updates
    5) Upgrading packages that have updates available
    6) Adding external module sources
    7) Accessing MagicMirror config file
    8) Self updating
    9) Installing MagicMirror

## TLDR; What's the Installation/Removal Process?

See the [MMPM Installation](https://github.com/Bee-Mar/mmpm/wiki/MMPM-Installation) and [MMPM Removal](https://github.com/Bee-Mar/mmpm/wiki/MMPM-Removal) sections of the wiki for installation and removal instructions, respectively.

## Refer to the Wiki First

If any issues arise, please consult the wiki first, which can be found [here](https://github.com/Bee-Mar/mmpm/wiki).

## GUI Demo

- Managing Packages with Live Terminal Feed and Responsive Search

![Managing Packages](https://media.giphy.com/media/MEuuL0fOIzcejxWATL/giphy.gif)

- Editing MagicMirror Config

![Editing MagicMirror Config](https://media.giphy.com/media/XDdeJQpzZRRwrylBVg/giphy.gif)

- Using [WebSSH](https://github.com/huashengdun/webssh) within GUI

![Using WebSSH](https://media.giphy.com/media/gkLZiyqWfDqcH0tHE0/giphy.gif)

- Adding External Sources

![Adding External Sources](https://media.giphy.com/media/loAdplweaF3BpyGS1M/giphy.gif)

## Future State of Affairs

In the not-to-distant future, `.deb` releases of this package will be available for download, simplifying the installation.

## Potential Problems

This project is entirely dependent on the structure of the [MagicMirror 3rd Party Modules](https://github.com/MichMich/MagicMirror/wiki/3rd-Party-Modules) page. The HTML is parsed, and the appropriate text of each module is extracted. If for some reason any of the information is not displayed correctly, it is most likely due to someone changing the structure of the page. Ideally, in the future, a database will be constructed, and things will be handeled in a more formal, predictable way.
