#!/usr/bin/env python3
import sys
from mmpm.mmpm import MMPM

def main(): # for the setup.py console scripts
    try:
        app = MMPM()
        app.run()
    except KeyboardInterrupt:
        sys.exit(127)

if __name__ == "__main__":
    main()
