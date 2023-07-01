#!/usr/bin/env python3
import sys
from mmpm.mmpm import MMPM

# for the setup.py console scripts
def main():
    try:
        app = MMPM()
        app.run()
    except KeyboardInterrupt:
        sys.exit(127)

if __name__ == "__main__":
    main()
