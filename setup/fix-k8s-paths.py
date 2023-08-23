#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path


def fix_file(filepath: Path, project_root: Path, repo_name: str) -> None:
    with open(filepath, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        lines[i] = lines[i].replace("@PROJECT_ROOT@", str(project_root)).replace("@REPO_NAME@", repo_name)

    with open(filepath, "w") as f:
        f.writelines(lines)


def main(args: list[str]) -> None:
    # __file__ is an absolute path to the current file on disk
    # so .parent.parent -> the root of the conduyt project.
    project_root = Path(__file__).parent.parent
    repo_name = os.environ.get("USER")
    filenames = args[1:]
    cwd = Path.cwd()
    for filename in filenames:
        filepath = Path(filename)
        if not filepath.is_absolute():
            filepath = cwd / filepath
        fix_file(filepath, project_root, repo_name)


if __name__ == "__main__":
    main(sys.argv)
