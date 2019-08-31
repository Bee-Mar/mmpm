#!/usr/bin/env python3
import sys
from mmpm import mmpm

def main(args=None):
    if args is None:
        args = sys.argv

    mmpm.main(args)


if __name__ == "__main__":
    main()
