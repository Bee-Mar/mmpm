#!/usr/bin/env python3
import sys
from colorama import init
from mmpm.mmpm import main as _main_


def main(args=None):
    if args is None:
        args = sys.argv

    init()
    _main_(args)


if __name__ == "__main__":
    main()
