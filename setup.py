#!/usr/bin/env python3

from setuptools import setup, find_packages

DEPENDENCIES = [
    "argparse == 1.1",
    "beautifulsoup4 == 4.7.1",
    "colorama == 0.4.1",
    "tabulate == 0.8.3",
]

VERSION = "0.33"

setup(name="mmpm",
      version=VERSION,
      description="The MagicMirror Package Manager (mmpm)",
      url="https://github.com/Bee-Mar/mmpm",
      author="Brandon Marlowe",
      author_email="bpmarlowe-software@protonmail.com",
      license="MIT",
      include_package_data=True,
      keywords="MagicMirror magicmirror",
      packages=find_packages(),
      entry_points={"console_scripts": ["mmpm=mmpm.__main__:main"]},
      install_requires=DEPENDENCIES)
