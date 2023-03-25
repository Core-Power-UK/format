#!/usr/bin/env python3
"""Custom formatting pre-commit hook."""
import argparse
from pathlib import Path

from add_trailing_comma._main import _fix_src
from black import WriteBack
from black.mode import Mode
from black.report import Report


def fix_file(file, args):
    """Updated version of add_trailing_comma function to remove logging."""
    contents_text_orig = contents_text = file.read_bytes().decode()
    contents_text = _fix_src(contents_text, args.min_version)
    if contents_text != contents_text_orig:
        file.write_bytes(contents_text.encode())


class BlackFormatter:
    """Configuration to run black."""

    report = Report(check=False, diff=False, quiet=True, verbose=False)
    write_back = WriteBack.from_configuration(check=False, diff=False, color=True)

    def run(self, filenames, skip_magic_trailing_comma):
        """Run trimmed down version of black formatting."""
        mode = Mode(magic_trailing_comma=not skip_magic_trailing_comma)
        if len(filenames) == 1:
            from black import reformat_one

            reformat_one(
                src=Path(filenames[0]),
                fast=False,
                write_back=self.write_back,
                mode=mode,
                report=self.report,
            )
        else:
            from black.concurrency import reformat_many

            reformat_many(
                sources=[Path(file) for file in filenames],
                fast=False,
                write_back=self.write_back,
                mode=mode,
                report=self.report,
                workers=None,
            )


class TrailingCommaArgs:
    """Trailing commas arguments class."""

    min_version = (3, 6)


def run_formatting(args):
    """Run formatting for specified files."""
    trailing_comma_cargs = TrailingCommaArgs()
    black = BlackFormatter()
    black.run(args.filenames, skip_magic_trailing_comma=True)
    for filename in args.filenames:
        fix_file(Path(filename), trailing_comma_cargs)

    black.run(args.filenames, skip_magic_trailing_comma=False)


def format_files(args):
    """Format specified files."""
    if len(args.filenames) == 0:
        print("Please pass files to be formatted")

        return 1

    for file in args.filenames:
        if not Path(file).is_file():
            print(f"'{file}' - is not a file")

            return 1

    run_formatting(args)

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
