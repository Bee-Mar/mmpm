<p align="center">
  <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=L2ML7F8DTMAT2&currency_code=USD&source=ur">
    <img src="https://img.shields.io/badge/Donate-PayPal-green.svg">
  </a>
  <a href="http://choosealicense.com/licenses/mit">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  </a>
</p>

# MMPM - The MagicMirror Package Manager

| Author          | Contact                           |
| --------------- | --------------------------------- |
| Brandon Marlowe | bpmarlowe-software@protonmail.com |

The MagicMirror Package Manager (`mmpm`) is both a command line and web interface designed to simplify the installation, removal, and maintenance of MagicMirror modules.

<i>Consider this project to be in an Alpha state, so don't get too picky just yet, as you most likely will discover some bugs I was unable to find.</i>

The supported features consist of following categories:

    1) Search
    2) Installation
    3) Removal
    4) Checking for updates
    5) Upgrading packages that have updates available
    6) Adding external module sources
    7) Accessing MagicMirror config file
    8) Self updating
    9) Installing MagicMirror

## TLDR; What's the Installation Process?

Please see the [MMPM Installation](https://github.com/Bee-Mar/mmpm/wiki/Installation) for installation instructions, and [MMPM Removal](https://github.com/Bee-Mar/mmpm/wiki/Removal) for
removal instructions.

## Future State of Affairs

In the not-to-distant future, `.deb` releases of this package will be available for download, simplifying installation.

## Potential Problems

This project is entirely dependent on the structure of the [MagicMirror 3rd Party Modules](https://github.com/MichMich/MagicMirror/wiki/3rd-Party-Modules) page. The HTML is parsed, and the appropriate text of each module is extracted. If for some reason any of the information is not displayed correctly, it is most likely due to someone changing the structure of the page. Ideally, in the future, a database will be constructed, and things will be handeled in a more formal, predictable way.

## CLI Font Size and Table Formatting

The `tabulate` package is used to format output, and it is expected the user will be ssh'ing into
their Pi, using a laptop, or desktop monitor. If using a small monitor, or the RaspberryPi touch
screen, experiment with reducing your font-size until the ouput is displayed properly.

## `~/.config/mmpm/MagicMirror-modules-snapshot.json`

This JSON file contains all the retrieved MagicMirror module data. `mmpm` takes snapshots of the [MagicMirror 3rd Party Modules](https://github.com/MichMich/MagicMirror/wiki/3rd-Party-Modules) every six hours, unless you force a refresh manually. This is done to quicken the response time when searching for packages.

However, this is not a process that runs in the background. If a command utilizing the snapshot data is issued, and the snapshot is more than six hours old, a new one is taken.

# MagicMirror Root Directory

If you choose to install MagicMirror in a location other than ~/MagicMirror, you should set an
environment variable named `MMPM_MAGICMIRROR_ROOT` to the location of your MagicMirror installation.
This environment variable must be an absolute path.

```sh
# within your bashrc
export MMPM_MAGICMIRROR_ROOT='/home/$USER/some_directory/MagicMirror'
```

# Overview of Commands

Please see the [MMPM Command Line Options](https://github.com/Bee-Mar/mmpm/wiki/MMPM-Command-Line-Options) portion of the wiki for details.
