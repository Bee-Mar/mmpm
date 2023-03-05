#!/usr/bin/env python3
from mmpm.mmpm import MMPM

def main():
    try:
        MMPM.run()
    except KeyboardInterrupt:
        logger.info('User killed process with keyboard interrupt')
        sys.exit(127)

if __name__ == "__main__":
    main()
