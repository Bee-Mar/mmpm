#!/usr/bin/env python3
import sys
from os import chdir, getenv, system
from pathlib import Path
from shutil import copytree, which


def build_ui():
    print(f"  - Running custom build hook in {Path(__file__)}")

    # if the DEVBOX_PROJECT_ROOT exists, it'll be returned as a string, make sure it's a Path object
    root = Path(getenv("DEVBOX_PROJECT_ROOT", Path.cwd()))

    Path(root / "mmpm" / "ui").mkdir(exist_ok=True, parents=True)
    chdir(root / "ui")

    if not which("bun") and not which("npm"):
        print("ERROR: both `npm` and `bun` are not installed. Cannot continue")
        sys.exit(1)

    node = which("bun") or "npm"

    system(f"{node} install --legacy-peer-deps")
    system("./node_modules/@angular/cli/bin/ng.js build --configuration production --output-hashing none --base-href /")

    chdir(root)

    copytree(root / "ui" / "build" / "browser", root / "mmpm" / "ui", dirs_exist_ok=True)


if __name__ == "__main__":
    build_ui()
