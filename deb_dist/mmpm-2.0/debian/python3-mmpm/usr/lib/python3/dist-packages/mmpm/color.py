#!/usr/bin/env python3
from colorama import Fore, Style

RESET: str = Style.RESET_ALL  # resets back to the original color of the terminal text

N: str = Style.NORMAL  # normal
B: str = Style.BRIGHT  # bright

N_RED: str = N + Fore.RED  # normal red
B_RED: str = B + Fore.RED  # bright red

N_MAGENTA: str = N + Fore.MAGENTA  # normal magenta
B_MAGENTA: str = B + Fore.MAGENTA  # bright magenta

N_CYAN: str = N + Fore.CYAN  # normal cyan
B_CYAN: str = B + Fore.CYAN  # bright cyan

N_YELLOW: str = N + Fore.YELLOW  # normal yellow
B_YELLOW: str = B + Fore.YELLOW  # bright yellow

N_WHITE: str = N + Fore.WHITE  # normal white
B_WHITE: str = B + Fore.WHITE  # bright white

N_GREEN: str = N + Fore.GREEN  # normal green
B_GREEN: str = B + Fore.GREEN  # bright green

normal_green = lambda text: str(N_GREEN + text + RESET)
normal_cyan = lambda text: str(N_CYAN + text + RESET)
normal_red = lambda text: str(N_RED + text + RESET)
normal_magenta = lambda text: str(N_MAGENTA + text + RESET)
normal_yellow = lambda text: str(N_YELLOW + text + RESET)

bright_green = lambda text: str(B_GREEN + text + RESET)
bright_cyan = lambda text: str(B_CYAN + text + RESET)
bright_red = lambda text: str(B_RED + text + RESET)
bright_magenta = lambda text: str(B_MAGENTA + text + RESET)
bright_yellow = lambda text: str(B_YELLOW + text + RESET)
