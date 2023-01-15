`MMPM`, the MagicMirror Package Manager is a self updating command line and graphical interface designed to simplify the installation, removal, and maintenance of MagicMirror packages.

The MagicMirror Package Manager is featured as an alternative installation method on the [MagicMirror Documentation](https://docs.magicmirror.builders/getting-started/installation.html#alternative-installation-methods).

## Features

- Installation, removal, updating, and upgrading of packages
- Search for and show package details
- Adding external packages (think of it like PPAs for Ubuntu)
- Tab-Autocompletion for the CLI
- Quick MagicMirror config editing access
- Installing MagicMirror
- [Hide/Show MagicMirror modules](https://github.com/Bee-Mar/mmpm/wiki/Status,-Hide,-Show-MagicMirror-Modules)
- Start/Stop/Restart MagicMirror (works with `npm`, `pm2`, and `docker-compose`)
- RaspberryPi 3 screen rotation

## Quick Installation Guide

```sh
sudo apt install libffi-dev nginx-full -y
python3 -m pip install --upgrade --no-cache-dir mmpm
mmpm --guided-setup
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
```

## Look to the [Wiki](https://github.com/Bee-Mar/mmpm/wiki)

Make sure you've followed all the instructions for [installation](https://github.com/Bee-Mar/mmpm/wiki/MMPM-Installation), configuring [environment variables](https://github.com/Bee-Mar/mmpm/wiki/MMPM-Environment-Variables), and the [hide/show modules feature](https://github.com/Bee-Mar/mmpm/wiki/Status,-Hide,-Show-MagicMirror-Modules) setup.

Note: the Environment Variables setup is **extremely** important.

## Creating Issues

Consult the Wiki before posting any issues, and use one of the provided templates (if possible) when filing an issue.

For any bugs encountered, examine the log files by running `mmpm log`. If creating a GitHub issue is
needed, use one of the issue templates, and please attach the log files, your `config.js`, and
provide what steps can be take to reproduce the bug. You can create a ZIP archive of the MMPM log
files files through the Control Center of the GUI, or by running `mmpm log --zip` through the CLI. If for some reason you cannot access `mmpm log --zip`, you can find the files in `~/.config/mmpm/log` and `/var/log/nginx`. All log files for MMPM in `/var/log/nginx` will be prefixed with either `mmpm-access` or `mmpm-error`.
