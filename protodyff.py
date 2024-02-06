
import google.protobuf.text_format as text_format
from google.protobuf.json_format import MessageToDict, ParseError
import json
import difflib
from deepdiff import DeepDiff
from typing import Callable
from argparse import ArgumentParser, Namespace
from colorama import Fore
import sys


def parse_file(file, old=False):
    if old:
        import proto5.thruster5 as proto5
        with open(file, 'r') as f:
            return text_format.Parse(f.read(), proto5.ThrusterParameters())

    import proto6.thruster6 as proto6
    with open(file, 'r') as f:
        return text_format.Parse(f.read(), proto6.ThrusterParameters())


RED: Callable[[str], str] = lambda text: f"\u001b[31m{text}\033\u001b[0m"
GREEN: Callable[[str], str] = lambda text: f"\u001b[32m{text}\033\u001b[0m"


def get_edits_string(old: str, new: str, short: bool = False) -> str:
    result = ""
    if short:
        add = 0
        remove = 0
        lines = difflib.unified_diff(old.splitlines(
            keepends=True), new.splitlines())
        for line in lines:
            line = line.rstrip()
            if line.startswith("+"):
                add += 1
            elif line.startswith("-"):
                remove += 1
            elif line.startswith("?"):
                continue

        return Fore.GREEN + f"Added {add}" + "      " + Fore.RED + f"Removed {remove}"

    lines = difflib.unified_diff(old.splitlines(
        keepends=True), new.splitlines(keepends=True))

    for line in lines:
        line = line.rstrip()
        if line.startswith("+"):
            result += GREEN(line) + "\n"
        elif line.startswith("-"):
            result += RED(line) + "\n"
        elif line.startswith("?"):
            continue

    return result


if __name__ == "__main__":
    try:
        parser = ArgumentParser(
            description=f"A tool to find differences in brunvoll protobuf files")

        # Example usage
        parser.add_argument("file1")
        parser.add_argument("file2")

        parser.add_argument(
            "-v5", "--version5", help="Selects the protobuf 5 version", action="store_true")
        parser.add_argument(
            "-s", "--short", help=f"displays a short format with adds and removes ex: {Fore.GREEN + f'Added: 3' + '      ' + Fore.RED + f'Removed: 4'}", action="store_true")
        args: Namespace = parser.parse_args()

        parsed1 = MessageToDict(parse_file(
            str(args.file1), True if args.version5 else False))

        parsed2 = MessageToDict(parse_file(
            str(args.file2), True if args.version5 else False))

        print(
            get_edits_string(
                json.dumps(parsed1, indent=4, sort_keys=True),
                json.dumps(parsed2, indent=4, sort_keys=True),
                True if args.short else False
            )
        )
    except:
        parser.print_help()
        sys.exit(0)
