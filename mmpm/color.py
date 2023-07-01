#!/usr/bin/env python3
from colorama import Fore, Style

RESET = Style.RESET_ALL  # resets back to the original color of the terminal text

N_RED = Style.NORMAL + Fore.RED  # normal red
B_RED = Style.BRIGHT + Fore.RED  # bright red

N_MAGENTA = Style.NORMAL + Fore.MAGENTA  # normal magenta
B_MAGENTA = Style.BRIGHT + Fore.MAGENTA  # bright magenta

N_CYAN = Style.NORMAL + Fore.CYAN  # normal cyan
B_CYAN = Style.BRIGHT + Fore.CYAN  # bright cyan

N_YELLOW = Style.NORMAL + Fore.YELLOW  # normal yellow
B_YELLOW = Style.BRIGHT + Fore.YELLOW  # bright yellow

N_WHITE = Style.NORMAL + Fore.WHITE  # normal white
B_WHITE = Style.BRIGHT + Fore.WHITE  # bright white

N_GREEN = Style.NORMAL + Fore.GREEN  # normal green
B_GREEN = Style.BRIGHT + Fore.GREEN  # bright green

n_green = lambda text: str(N_GREEN + text + RESET)
n_cyan = lambda text: str(N_CYAN + text + RESET)
n_red = lambda text: str(N_RED + text + RESET)
n_magenta = lambda text: str(N_MAGENTA + text + RESET)
n_yellow = lambda text: str(N_YELLOW + text + RESET)

b_green = lambda text: str(B_GREEN + text + RESET)
b_cyan = lambda text: str(B_CYAN + text + RESET)
b_red = lambda text: str(B_RED + text + RESET)
b_magenta = lambda text: str(B_MAGENTA + text + RESET)
b_yellow = lambda text: str(B_YELLOW + text + RESET)
