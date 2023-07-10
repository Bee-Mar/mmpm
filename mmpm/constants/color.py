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

__reset = lambda text: str(text + RESET)
n_green = lambda text: N_GREEN + __reset(text)
n_cyan = lambda text: N_CYAN + __reset(text)
n_red = lambda text: N_RED + __reset(text)
n_magenta = lambda text: N_MAGENTA + __reset(text)
n_yellow = lambda text: N_YELLOW + __reset(text)

b_green = lambda text: B_GREEN + __reset(text)
b_cyan = lambda text: B_CYAN + __reset(text)
b_red = lambda text: B_RED + __reset(text)
b_magenta = lambda text: B_MAGENTA + __reset(text)
b_yellow = lambda text: B_YELLOW + __reset(text)
