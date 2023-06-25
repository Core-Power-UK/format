#!/usr/bin/env python3
"""Custom formatting pre-commit hook."""
import argparse
from pathlib import Path

from add_trailing_comma._main import _fix_src
from black import format_str
from black.mode import Mode


def fix_file(file):
    """Fix a single file and write the results if changed."""
    contents_text_orig = contents_text = Path(file).read_bytes().decode()

    # Remove trailing commas
    contents_text = format_str(contents_text, mode=Mode(magic_trailing_comma=False))

    # Add trailing commas
    contents_text = _fix_src(contents_text, (3, 6))

    # Format with black
    contents_text = format_str(contents_text, mode=Mode(magic_trailing_comma=True))

    if contents_text != contents_text_orig:
        Path(file).write_bytes(contents_text.encode())


def format_files(args):
    """Format specified files."""
    if len(args.filenames) == 0:
        print("Please pass files to be formatted")

        return 1

    for file in args.filenames:
        if not Path(file).is_file():
            print(f"'{file}' - is not a file")

            return 1

    for filename in args.filenames:
        fix_file(filename)

    return 0


def main(argv=None):
    """Run Formatter."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(argv)

    return format_files(args)


if __name__ == "__main__":
    """Run formatter."""
    raise SystemExit(main())
