#!/usr/bin/env python3
from mmpm.mmpm import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info('User killed process with keyboard interrupt')
        sys.exit(127)
