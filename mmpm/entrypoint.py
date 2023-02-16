#!/usr/bin/env python3
from mmpm.mmpm import MMPM

def main():
    MMPM.run() # for the setup.py entry_points

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info('User killed process with keyboard interrupt')
        sys.exit(127)
