#!/usr/bin/env python3
"""Custom formatting pre-commit hook."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING

from add_trailing_comma._main import _fix_src  # type: ignore[import]
from black import format_str
from black.mode import Mode

if TYPE_CHECKING:
    from collections.abc import Sequence


def fix_file(file: str) -> bool:
    """Fix a single file and write the results if changed."""
    contents_text_orig = contents_text = Path(file).read_bytes().decode()

    # Remove trailing commas
    contents_text = format_str(contents_text, mode=Mode(magic_trailing_comma=False))

    # Add trailing commas
    contents_text = _fix_src(contents_text)

    # Format with black
    contents_text = format_str(contents_text, mode=Mode(magic_trailing_comma=True))

    if contents_text != contents_text_orig:
        Path(file).write_bytes(contents_text.encode())

    return contents_text != contents_text_orig


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

    ret = 0
    for filename in args.filenames:
        ret |= fix_file(filename)

    return ret


if __name__ == "__main__":
    """Run formatter."""
    raise SystemExit(main())
