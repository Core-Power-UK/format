#!/usr/bin/env python3
"""Custom formatting pre-commit hook."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


def cmd_output(*cmd: str) -> None:
    """Run a command on the command line ."""
    process = subprocess.Popen(
        cmd,  # noqa: S603
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    assert process.stdout is not None
    for line in iter(process.stdout.readline, ""):
        print(line.strip())


def fix_files(files: Sequence[str]) -> bool:
    """Run ruff on files."""
    print("Removing trailing commas")
    cmd_output(
        "ruff",
        "format",
        *files,
        "--config",
        "format.skip-magic-trailing-comma = true",
    )
    print("\n")

    print("Adding trailing commas")
    cmd_output("ruff", "check", *files, "--fix", "--select=COM812")
    print("\n")

    print("Running Formatter")
    cmd_output("ruff", "format", *files)

    return False


def main(argv: Sequence[str] | None = None) -> int:
    """Run Formatter."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(argv)

    if len(args.filenames) == 0:
        print("Please pass files to be formatted")

        return 1

    for file in args.filenames:
        if not Path(file).is_file():
            print(f"'{file}' - is not a file")

            return 1

    return fix_files(args.filenames)


if __name__ == "__main__":
    """Run formatter."""
    raise SystemExit(main())
