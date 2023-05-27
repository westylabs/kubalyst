#!/usr/bin/env python3
import re
import sys
from pathlib import Path


PATH_RE = re.compile(r"\/Users?\/gregfee\/code\/colossus")


def fix_path(project_root: Path, filepath: Path) -> None:
    with open(filepath, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        lines[i] = PATH_RE.sub(str(project_root), line)

    with open(filepath, "w") as f:
        f.writelines(lines)


def main(args: list[str]) -> None:
    # __file__ is an absolute path to the current file on disk
    # so .parent.parent -> the root of the conduyt project.
    project_root = Path(__file__).parent.parent
    filenames = args[1:]
    cwd = Path.cwd()
    for filename in filenames:
        filepath = Path(filename)
        if not filepath.is_absolute():
            filepath = cwd / filepath
        fix_path(project_root, filepath)


if __name__ == "__main__":
    main(sys.argv)
