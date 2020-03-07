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
          'setuptools >= 45.0.0',
          'wheel >= 0.33.6',
          'tabulate >= 0.8.6',
          'argparse >= 1.1',
          'bs4 >= 0.0.1',
          'beautifulsoup4 >= 4.6.0',
          'colorama >= 0.4.3',
          'flask >= 1.1.1',
          'Flask-Cors >= 3.0.8',
          'gunicorn >= 20.0.4',
          'webssh >= 1.5.1',
          'flask-socketio >= 4.2.1',
          'shelljob >= 0.5.6',
          'greenlet >= 0.4.15',
      ])
