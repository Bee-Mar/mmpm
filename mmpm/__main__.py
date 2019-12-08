#!/usr/bin/env python3
import sys
from colorama import init
import mmpm


def main(args=None):
    if args is None:
        args = sys.argv

    init()
    mmpm.main(args)


if __name__ == "__main__":
    main()
