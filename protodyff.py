
import json, difflib, sys, re
import google.protobuf.text_format as text_format
from google.protobuf.json_format import MessageToDict, ParseError
from deepdiff import DeepDiff
from typing import Callable
from argparse import ArgumentParser, Namespace
from colorama import Fore


RED: Callable[[str], str] = lambda text: f"\u001b[31m{text}\033\u001b[0m"
GREEN: Callable[[str], str] = lambda text: f"\u001b[32m{text}\033\u001b[0m"

def parse_file(file, version):
    if not version:
        print(Fore.RED + "Error:", end=" ")
        print("No version specified\n", Fore.WHITE)
        parser.print_help()
        sys.exit(0)

    if version == 1.5:
        try:
            import proto5.thruster5 as proto5
            with open(file, 'r') as f:
                return text_format.Parse(f.read(), proto5.ThrusterParameters())
        except Exception:
            print(f"File {RED(file)} is invalid", file=sys.stderr)
            sys.exit(0)

    elif version == 1.6:
        try:
            import proto6.thruster6 as proto6
            with open(file, 'r') as f:
                return text_format.Parse(f.read(), proto6.ThrusterParameters())
        except Exception:
            print(f"File {RED(file)} is invalid", file=sys.stderr)
            sys.exit(0)

    #Gives an error invalid if the version is not in this
    print(Fore.RED + "+"*15+"\nInvalid version\n"+"+"*15, Fore.WHITE)
    sys.exit(0)


def output_format(string, version):
    print
    if args.version == 1.5:
        #Regex to make everything CamelCase
        return ''.join(x.capitalize() if i > 0 else x for i, x in enumerate(re.split(r'[^a-zA-Z0-9]', string))) 
    
    elif args.version == 1.6:
        #Regex to make snake_case
        return re.sub(r'(?<!^)(?=[A-Z])', '_', string).lower() 

def find_key_breadcrumb(subkey: str, dictionary: dict, parent_key='', sep='.', version=1.5):
    # Create breadcrumb for the key in the dictionary
    for key, value in dictionary.items():
        if isinstance(value, dict):

            if parent_key:
                breadcrumb = find_key_breadcrumb(subkey, value, output_format(parent_key, version) + sep + output_format(key, version), sep=sep, version=version)
            else:
                breadcrumb = find_key_breadcrumb(subkey, value, output_format(key, version), sep=sep, version=version)

            if breadcrumb:
                return breadcrumb

        elif key == subkey:
            if parent_key:
                return parent_key + sep + output_format(key, version)
            else:
                return output_format(key, version)


def get_diff_lines(old_dict: dict, new_dict: dict) -> str:
    lines = difflib.ndiff(
        json.dumps(old_dict, indent=4).splitlines(keepends=True),
        json.dumps(new_dict, indent=4).splitlines(keepends=True)
    )
    return lines


def get_edits_string(old_dict: dict, new_dict: dict, short: bool = False) -> str:
    result = ""
    subkey = None
    lines = get_diff_lines(old_dict, new_dict)
    for line in lines:
        line = line.rstrip()
        if line.startswith("+"):
            parts = line.split(':', 1)
            key = parts[0].split()[-1].strip('"')  # Extracting subkey without quotes
            if subkey is None:  # If subkey is not yet set
                subkey = key
            elif subkey != key:  # If subkey changes, we stop looking
                break

        if subkey:  # Breaks if subkey is found
            break

    if subkey:
        subkey_breadcrumb = find_key_breadcrumb(subkey, new_dict)
        if subkey_breadcrumb:
            print("")
        else:
            print("Subkey '{}' not found in the dictionary.".format(subkey))
            return ""
    else:
        print("No subkey found in the diff.")
        return ""

    lines = get_diff_lines(old_dict, new_dict)

    for line in lines:
        line = line.rstrip()
        if line.startswith("+"):
            parts = line.split(':', 1)
            key = parts[0].split()[-1].strip('"')  # Extracting subkey without quotes
            if line.startswith("+"):
                breadcrumb = find_key_breadcrumb(key, new_dict)
                if breadcrumb:
                    result += Fore.GREEN + "+ " + breadcrumb + ": " + parts[1].strip() + Fore.RESET + "\n"
        elif line.startswith("-"):
            parts = line.split(':', 1)
            key = parts[0].split()[-1].strip('"')  # Extracting subkey without quotes
            if line.startswith("-"):
                breadcrumb = find_key_breadcrumb(key, old_dict)
                if breadcrumb:
                    result += Fore.RED + "- " + breadcrumb + ": " + parts[1].strip() + Fore.RESET + "\n"
        elif line.startswith("?"):
            continue

    if short:
        add = result.count("+")
        remove = result.count("-")
        print(Fore.GREEN + '\nAdded: ' + Fore.GREEN + str(add) +
      "     " + Fore.RED + "Removed: " + Fore.RED + str(remove), Fore.WHITE)

        return ""

    return result



if __name__ == "__main__":
    try:
        parser = ArgumentParser(
            description=f"A tool to find differences in brunvoll protobuf files")

        # Example usage
        parser.add_argument("file1", help="Path to the first file")
        parser.add_argument("file2", help="Path to the second file")

        parser.add_argument(
            "-v", "--version", help="Selects the protobuf 5 version", type=float)
        parser.add_argument(
            "-s", "--short", help=f"displays a short format with adds and removes ex: {Fore.GREEN + f'Added: 3' + '      ' + Fore.RED + f'Removed: 4'}" + Fore.WHITE, action="store_true")
        

        if len(sys.argv) == 1:
            print("\n")
            parser.print_help()
            print("")
            sys.exit(0)


        args: Namespace = parser.parse_args()

        parsed1 = MessageToDict(
            parse_file(
                str(args.file1), args.version))

        parsed2 = MessageToDict(
            parse_file(
                str(args.file2), args.version))
        print(
            get_edits_string(
                parsed1,
                parsed2,
                True if args.short else False
            ))
    except Exception as e:
        print(e, file=sys.stderr)