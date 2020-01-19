# MMPM - The MagicMirror Package Manager

| Author          | Contact                           |
| --------------- | --------------------------------- |
| Brandon Marlowe | bpmarlowe-software@protonmail.com |

The MagicMirror Package Manager (`mmpm`) is a command line interface designed to simplify the installation, removal, and maintenance of MagicMirror modules.

(See `CHANGELOG.md` for details of updates)

Consider this project to be in an Alpha state, as you most likely will discover some bugs I was unable to find. Additionally, the features are rather basic at the moment, with an eye on stability, followed by feature expansion. Again, do not consider this to be feature complete, but rather a step in right direction.

Currently, the supported features consist of five main categories:

    1) Search
    2) Installation
    3) Removal
    4) Checking for updates
    5) Upgrading packages that have updates available

## Prior State of Affairs

Prior to this project, the installation process of MagicMirror modules was rather tedious. First, you needed to navigate to the [MagicMirror 3rd Party Modules](https://github.com/MichMich/MagicMirror/wiki/3rd-Party-Modules) page and scroll through a large list of available modules. Once you found the module(s) you wanted to install, you needed to clone each of the repos manually,
then handle the updates all your own.

## Future State of Affairs

Ideally, this project will become the official package manager of [Magic Mirror](https://github.com/MichMich/MagicMirror) (lofty, I know). However, I believe once you begin using this, you will find it's simplicity and convenience very inviting. Additionally, once this project is considered stable, I would like to make this available on PyPi, so the executable can be pip-installable.

## Potential Problems

As it stands, this project is entirely dependent on the structure of the [MagicMirror 3rd Party Modules](https://github.com/MichMich/MagicMirror/wiki/3rd-Party-Modules) page. The HTML is parsed, and the appropriate text of each module is extracted. If for some reason any of the information is not displayed correctly, it is most likely due to someone changing the structure of the page. Ideally, in the future, a database will be constructed, and things will be handeled in a more formal, predictable way. So, think of this currently as a shim, just to get the project going.

## Installation
Please see the [MMPM Installation](https://github.com/Bee-Mar/mmpm/wiki/Installation) of the wiki.

## Font Size

The `tabulate` package is used to format output, and it is expected the user will be ssh'ing into
their Pi. However, if viewing on the your Pi, reduce your font-size to **at most** 7 so the output is
displayed more properly. This is not intended to be the long-term solution.

## `magic_mirror_modules_snapshot.json`

This JSON file will be placed in your home folder as a hidden file. `mmpm` takes snapshots of the [MagicMirror 3rd Party Modules](https://github.com/MichMich/MagicMirror/wiki/3rd-Party-Modules) every six hours, unless you force a refresh manually. This is done to quicken the response time when searching for packages.

However, this is not a process that runs in the background. If a command is issued, and the snapshot is more than six hours old, a new one is taken. Conceivably, you could issue a search or installation command, wait two weeks until the next one, and the same snapshot would exist on your hard drive until another search or install command is issued.

## Uninstall MMPM

If you decide to remove `mmpm`, you can execute `make uninstall` from within the cloned repository. This will remove the executable, and the `magic_mirror_modules_snapshot.json` from your home directory. However, the Python3 packages that were installed will still remain on your system.

```sh
# execute inside the mmpm cloned repository
$ make uninstall
```

Or, you can manually remove the executable, along with the `magic_mirror_modules_snapshot.json` file by executing the following:

```sh
$ sudo rm /usr/local/bin/mmpm
$ rm ~/.magic_mirror_modules_snapshot.json
```

# MagicMirror Root Directory

If you choose to install MagicMirror in a location other than ~/MagicMirror, you should set an
environment variable named `MMPM_MAGICMIRROR_ROOT` to the location of your MagicMirror installation.
This environment variable must be an absolute path.

```sh
# within your bashrc
export MMPM_MAGICMIRROR_ROOT='/home/pi/some_directory/MagicMirror'

```

# Overview of Commands

Please see the [MMPM Command Line Options](https://github.com/Bee-Mar/mmpm/wiki/MMPM-Command-Line-Options) portion of the wiki.
