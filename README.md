# MMPM - The MagicMirror Package Manager                                                                                                                                                                             

| Author          | Contact                           |
| --------------- | --------------------------------- |
| Brandon Marlowe | bpmarlowe-software@protonmail.com |

The MagicMirror Package Manager (`mmpm`) is a command line interface designed to simplify the installation, removal, and maintenance of MagicMirror modules.

Consider this project to be in an Alpha state, as you most likely will discover some bugs I was unable to find. Additionally, the features are rather basic at the moment, with an eye on stability, followed by feature expansion. Again, do not consider this to be feature complete, but rather a step in right direction.

Currently, the supported features consist of five main categories:

    1) Search
    2) Installation
    3) Removal
    4) Checking for updates
    5) Upgrading packages that have updates available

## Prior State of Affairs

Prior to this project, the installation process of MagicMirror modules was rather tedious. First, you needed to navigate to the [MagicMirror 3rd Party Modules](https://github.com/MichMich/MagicMirror/wiki/3rd-Party-Modules) page, scroll through a large list of modules available. Then, once you found the modules you wanted to install, you needed to clone each of the repos manually,
then handle the updates all your own.

## Future State of Affairs

Ideally, this project will become the official package manager of [Magic Mirror](https://github.com/MichMich/MagicMirror) (lofty, I know). However, I believe once you begin using this, you will find it's simplicity and convenience very inviting. Additionally, once this project is considered stable, I would like to make this available on PyPi, so the executable can be pip-installable.

## Potential Problems

As it stands, this project is entirely dependent on the structure of the [MagicMirror 3rd Party Modules](https://github.com/MichMich/MagicMirror/wiki/3rd-Party-Modules) page. The HTML is parsed, and the appropriate text of each module is extracted. If for some reason any of the information is not displayed correctly, it is most likely due to someone changing the structure of the page. Ideally, a database will be constructed, and things will be handeled in a more formal, predictable way in the future. So, think of this currently as a shim, just to get the project going.

## Installation of MMPM

The only system requirements are `python3` and the `pip3` package manager. If you are unsure as to whether or not you have `pip3` installed, open a terminal, and execute `which pip3`. If the program exists within your `$PATH`, then the previous command will display something like `/usr/bin/pip3`. If nothing is printed, then you probably do not have it installed, and you can install it with `sudo apt install python3-pip`. To install `python3`, simply run `sudo apt install python3`, but it is most likely already installed.

Next, clone this repository anywhere you like, and execute `make install` from a terminal. The required Python3 packages will be installed, and the command line program will be placed in `/usr/local/bin`. Moving the executable to `/usr/local/bin` requires `sudo` permission, so depending on your system configuration you may or may not be prompted for the root password. From here, you'll be able to execute any of the below `mmpm` commands.

```sh
# check for python3 installation
$ which python3

# check for the installation of pip3
$ which pip3

# execute inside the mmpm cloned repository
$ make install

```
Full Installation:
```sh
$ git clone https://github.com/Bee-Mar/mmpm.git && cd mmpm && make install
```

Obviously, MagicMirror is required as well. If you do not have it installed, head over to [Magic Mirror](https://github.com/MichMich/MagicMirror)'s home page for instructions. I intend to add an option to install MagicMirror from `mmpm` in the future.

After executing `make install` within the cloned repository, you may remove the folder for `mmpm`.

## `magic_mirror_modules_snapshot.json`

This JSON file will be placed in your home folder as a hidden file. `mmpm` takes snapshots of the [MagicMirror 3rd Party Modules](https://github.com/MichMich/MagicMirror/wiki/3rd-Party-Modules) every six hours, unless you force a refresh manually. This is done to quicken the response time when searching for packages.

However, this is not a process that runs in the background. If a command is issued, and the snapshot is more than six hours old, a new one is taken. Conceivably, you could issue a search or installation command, wait two weeks until the next one, and the same snapshot would exist on your hard drive until another search or install command is issued.

## Uninstall MMPM

If you decide to remove `mmpm`, you can execute `make uninstall` from within the cloned repository. This will remove the executable, and the `magic_mirror_modules_snapshot.json` from your home directory. However, the Python3 packages that were installed will still remain on your system.

```sh
# execute inside the mmpm cloned repository
$ make uninstall
```

# Overview of Commands

## `-h` or `--help`

This command line option simply displays the help message.

```sh
$ mmpm -h

# LONG FORM

$ mmpm --help
```

## `-u` or `--update`

This command line option takes no additional arguments. The master branches of all currently installed modules are queried to determine if any new commits have been made, and returns a message indicating which modules have available updates.

Example usage:

```sh

$ mmpm -u

# LONG FORM

$ mmpm --update
```

## `-U` or `--upgrade`

This command line option may take one or more additional arguments. If no arguments are provided, **all** modules that have available updates will be upgraded. You may however upgrade specific modules by supplying the name of those modules as additional argument(s).

Example usage:
```sh                                                                                                                                                                                                                
# upgrade every single currently installed module
$ mmpm -U

# upgrade specific modules
$ mmpm -U MMM-Simple-Swiper MMM-pages

# LONG FORM
$ mmpm --upgrade
$ mmpm --upgrade MMM-Simple-Swiper MMM-pages
```

## `-a` or `--all`

This command line option takes no arguments, and displays the category, title, repository link, author, and description of each module currently available. For any field that does not have valid information, a string of `N/A` is displayed.

Example usage:

```sh
# to view every single module available

$ mmpm -a

# or

$ mmpm --all
```

Example output:

```sh
...

Category: Entertainment / Misc
Title: MMM-Scrobbler
Repository: https://github.com/PtrBld/MMM-Scrobbler
Author: PtrBld
Description: Display the current playing song from Spotify, ITunes and Co.


Category: Entertainment / Misc
Title: MMM-Snow
Repository: https://github.com/MichMich/MMM-Snow
Author: MichMich
Description: More realistic snow plugin to improve your winter experience

...
```

## `-f` or `--force-refresh`

This comamnd line option takes no arguments, and retrieves a new snapshot of the [MagicMirror 3rd Party Modules](https://github.com/MichMich/MagicMirror/wiki/3rd-Party-Modules). Once the new snapshot is retrieved, the function associated with displaying the snapshot details is called, and the timestamp and module count is displayed to the user.

```sh
$ mmpm -f

Most recent snapshot of MagicMirror Modules taken @ 2019-05-19 13:03:53.
The next snapshot will be taken on or after 2019-05-19 19:03:53.

Module Categories: 10
Modules Available: 509

To forcibly refresh the snapshot, run 'mmpm -f' or 'mmpm --force-refresh'

# LONG FORM
$ mmpm --force-refresh
# … same output as previous
```

## `-c` or `--categories`

This command line option takes no arguments, and lists all category names found on [MagicMirror 3rd Party Modules](https://github.com/MichMich/MagicMirror/wiki/3rd-Party-Modules).

```sh
$ mmpm -c

MagicMirror Module Categories

1) Development / Core MagicMirror
2) Finance
3) News / Religion / Information
4) Transport / Travel
5) Voice Control
6) Weather
7) Sports
8) Utility / IOT / 3rd Party / Integration
9) Entertainment / Misc
10) Health

# LONG FORM
$ mmpm --categories
# … same output as previous

```

## `-s` or `--search`

This command line option requires at least one argument. Without reading this section, the search functionality may seem slightly initially. However, the actions are intentional.

When a query is entered, first, an attempt to match the query to a category name is made. The search in this instance is case-sensitive. If no category name matches the query **exactly**, the search becomes non-case-sensitive, and attempts to match text within the *title*, *author*, or *description* are made. If any one of those fields contains matching text, that module is returned a search result. For any search query that contains more than one word, surround the text in quotation marks. This was done intentionally to prevent bombarding the user with large numbers of search results when possible.

When searching for a category name that is lengthy, it is best to list the categories using `mmpm -c` first, then copy and paste the **exact** category name into terminal. See the examples below:

Example usage:

```sh
# this search will return all modules within the "Finance" category
$ mmpm -s Finance

# however, this search will return only modules that contain the term "finance" within the title, author, or description
# which may return far fewer results than anticipated
$ mmpm -s finance

# when searching for modules within a category with a lengthy category name
$ mmpm -s "Utility / IOT / 3rd Party / Integration"

# searching for modules that contain the term "facial recognition"
$ mmpm -s "facial recognition"

# this will return the same results as the previous example
$ mmpm --search "FACIAL RECOGNITION"
```


## `-d` or `--snapshot-details`

This command line option takes no arguments, and displays the details of the most recent MagicMirror 3rd Party Modules snapshot. The snapshot may be forcibly refreshed by executing `mmpm -f` or `mmpm --force-refresh`.

```sh
$ mmpm -d

Most recent snapshot of MagicMirror Modules taken @ 2019-05-19 12:53:51.
The next snapshot will be taken on or after 2019-05-19 18:53:51.

Module Categories: 10
Modules Available: 509

To forcibly refresh the snapshot, run 'mmpm -f' or 'mmpm --force-refresh'

# LONG FORM
$ mmpm --snapshot-details
# … same output as previous
```

## `-i` or `--install`

This command line option requires at least one argument. The spelling of the modules is case-sensitive, and each of the module names must be separated by at least one space. If any module name(s) contain a space, surround the name of the module in quotation marks.

install

```sh
# install a single package
$ mmpm -i MMM-Facial-Recognition

# or install multiple packages at once
$ mmpm -i MMM-Simple-Swiper MMM-pages MMM-soccer

# LONG FORMS
$ mmpm --install MMM-Facial-Recognition
$ mmpm --install MMM-Simple-Swiper MMM-pages MMM-soccer
```

Following the installation, there may be additional manual steps required. For example, resolving package version conflicts, running make within the module directory, etc. In the future, I plan on doing my best to automate the entire process, but again, baby steps.

## `-r` or `--remove`

This command line option requires at least one argument, but may take more than one. The directories associated with the specified modules are removed from the `~/MagicMirror/modules` directory.

```sh
# remove one module at a time
$ mmpm -r MMM-soccer

The following modules were successfully deleted:
MMM-soccer

# or remove multiple modules at once
$ mmpm -r MMM-pages MMM-Simple-Swiper MMM-Facial-Recognition

The following modules were successfully deleted:
MMM-pages MMM-Simple-Swiper MMM-Facial-Recognition

# LONG FORMS
$ mmpm -r MMM-soccer
$ mmpm --remove MMM-pages MMM-Simple-Swiper MMM-Facial-Recognition

```

## `-L` or `--list-installed`

This command line option takes no arguments, and lists all the modules you currently have installed within the `~/MagicMirror/modules` directory.

```sh
$ mmpm -L

Module(s) Installed:

MMM-pages
MMM-Simple-Swiper
MMM-soccer
MMM-Facial-Recognition

# LONG FORM

$ mmpm --list-installed
``` 

