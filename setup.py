#!/usr/bin/env python3

from setuptools import setup, find_packages
from mmpm.mmpm import __version__

VERSION = __version__

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
      install_requires=[
          "setuptools",
          "wheel",
          "argparse",
          "tabulate",
          "bs4",
          "colorama",
      ])
