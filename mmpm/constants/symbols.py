#!/usr/bin/env python3
from os import getenv
from mmpm import color
__UNICODE_SUPPORT__ = getenv("LANG", "").endswith("UTF-8")

GREEN_CHECK_MARK: str = color.N_GREEN + ('\u2713' if __UNICODE_SUPPORT__ else "+") + color.RESET
YELLOW_X: str = color.N_YELLOW + ('\u2718' if __UNICODE_SUPPORT__ else "x") + color.RESET
RED_X: str = color.N_RED + '\u2718' + color.RESET
GREEN_DASHES: str = color.N_GREEN + '----' + color.RESET

