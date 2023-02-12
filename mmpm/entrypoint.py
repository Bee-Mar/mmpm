#!/usr/bin/env python3
from mmpm.mmpm import main

logger = MMPMLogger.get_logger(__name__)
logger.setLevel(MMPMEnv.mmpm_log_level.get())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info('User killed process with keyboard interrupt')
        sys.exit(127)
