#!/usr/bin/env python3
from mmpm.mmpm import MMPM

def main(): # for the setup.py console scripts
    try:
        MMPM().run()
    except KeyboardInterrupt:
        sys.exit(127)

if __name__ == "__main__":
    main()
