#!/usr/bin/env python3
from mmpm.mmpm import MMPM

import sys


# for the setup.py console scripts
def main():
    try:
        app = MMPM()
        app.run()
    except KeyboardInterrupt:
        sys.exit(127)

if __name__ == "__main__":
    main()
