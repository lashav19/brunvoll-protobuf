
import json, difflib, sys, re
import google.protobuf.text_format as text_format
from google.protobuf.text_format import ParseError as textError
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
        print("No version specified\n", Fore.RESET)
        parser.print_help()
        sys.exit(0)
    try:
        if version == 1.5:
            from proto1_5 import thruster1_5 as protobuf 
        elif version == 1.6:
            from proto1_6 import thruster1_6 as protobuf
    
        with open(file, 'r') as f:
            return text_format.Parse(f.read(), protobuf.ThrusterParameters())        
    except textError:
        print(f"File {RED(file)} is invalid, inncorrect syntax or invalid version", file=sys.stderr)
    except FileNotFoundError:
        print(f"File {RED(file)} not found", file=sys.stderr)

    sys.exit(0)


def output_format(string):
    """
    Matches the keywords with the keyword standard in version 1.5 and 1.6
    1.5: everything is CamelCase
    1.6: everything is snake_case
    """
    if args.version == 1.5:
        # Regex to make everything CamelCase
        formatted_string = ''.join(x.capitalize() if i > 0 else x for i, x in enumerate(re.split(r'[^a-zA-Z0-9]', string))) 
    
    elif args.version == 1.6:
        # Regex to make snake_case
        formatted_string = re.sub(r'(?<!^)(?=[A-Z])', '_', string).lower() 

    # Regex to remove values without a comma at the end
    formatted_string = re.sub(r'([^,\n]+)(?=\n\1$)', '', formatted_string)


    return formatted_string


def find_key_breadcrumb(subkey: str, dictionary: dict, parent_key='', sep='.'):
    """
    Recursive function to create a breadcrumb path for the specified subkey in the dictionary.
    """
    # Create breadcrumb for the key in the dictionary
    for key, value in dictionary.items():
        if isinstance(value, dict):
            if parent_key:
                breadcrumb = find_key_breadcrumb(subkey, value, output_format(parent_key) + sep + output_format(key), sep=sep)
            else:
                breadcrumb = find_key_breadcrumb(subkey, value, output_format(key), sep=sep)

            if breadcrumb:
                return breadcrumb
        elif key == subkey:
            if parent_key:
                breadcrumb = parent_key + sep + output_format(key)
            else:
                breadcrumb = output_format(key)

            # Remove values without a comma at the end

            return breadcrumb


def validate(lines:str):
    modified_lines = ""
    for line in lines:
        if "{" in line or "}" in line or "," in line:
            modified_lines += line.replace(",","")
        else:
            modified_lines += line
    return modified_lines


def get_diff_lines(old_dict: dict, new_dict: dict) -> str:
    # abstraction for difflib to return the json dumps for the two files
    json1 = json.dumps(old_dict, indent=1).splitlines(keepends=True)
    json2 = json.dumps(new_dict, indent=1).splitlines(keepends=True)


    lines = difflib.ndiff(
        json.dumps(old_dict, indent=1).splitlines(keepends=True),
        json.dumps(new_dict, indent=1).splitlines(keepends=True)
    )



    # Split the string into lines and iterate over them

    return lines    


def get_edits_string(old_dict: dict, new_dict: dict, short: bool = False) -> str:
    result = ""
    subkey = None
    lines = get_diff_lines(old_dict, new_dict)

    for line in lines:
        line = line.rstrip()
    if subkey:
        subkey_breadcrumb = find_key_breadcrumb(subkey, new_dict)
        if subkey_breadcrumb:
            print("")
        else:
            print(subkey)

    else:
        print()
  

    lines = get_diff_lines(old_dict, new_dict)

    for line in lines:
        line = line.rstrip()

        if line.startswith("+"):
            if args.long:
                print(Fore.GREEN + line)
                continue
            parts = line.split(':', 1)
            key = parts[0].split()[-1].strip('"')  # Input has "" strips and forces to string

            breadcrumb = find_key_breadcrumb(key, new_dict)
            if breadcrumb:
                colorString = Fore.GREEN + "+ " + breadcrumb + ": " + parts[1].strip() + Fore.RESET + "\n"
                result += colorString
   

        elif line.startswith("-"):
            if args.long:
                print(Fore.RED + line) 
                continue

            parts = line.split(':', 1)
            key = parts[0].split()[-1].strip('"')  # Input has "" strips and forces to string

            breadcrumb = find_key_breadcrumb(key, old_dict)
            if breadcrumb:
                colorString = Fore.RED + "- " + breadcrumb.rstrip() + ": " + parts[1].strip() + Fore.RESET + "\n"
                result += colorString

        elif line.startswith("?"):
            if args.long:
                print(Fore.YELLOW + line)
                continue
        else:
            print(Fore.RESET+line) if args.long else None

    if short:
        add = result.count("+")
        remove = result.count("-")
        print(Fore.GREEN + '\nAdded: ' + Fore.GREEN + str(add) +"     " + Fore.RED + "Removed/Changed: " + Fore.RED + str(remove), Fore.RESET)

        sys.exit(0)
    lines = result.split('\n')
    # Remove any leading or trailing whitespace from each line and store them in a set
    return result


if __name__ == "__main__":

        parser = ArgumentParser(
            description=f"A tool to find differences in brunvoll protobuf files This is a test version {Fore.RED + 'NOT FOR PRODUCTION' + Fore.RESET}", prefix_chars="-+/")

        # Example usage
        parser.add_argument("file1", help="Path to the first file")
        parser.add_argument("file2", help="Path to the second file")

        parser.add_argument(
            "-v", "--version", choices=[1.5, 1.6], type=float, required=True)
        parser.add_argument(
            "-s", "--short", help=f"displays a short format with adds and removes ex: {Fore.GREEN + f'Added: 3' + '      ' + Fore.RED + f'Removed: 4'}" + Fore.WHITE, action="store_true")
        parser.add_argument(
            "-l", "--long", help="displays the whole file and the changes in it", action="store_true")
        


        if len(sys.argv) == 1: # prints the help screen if no arguments are passed
            parser.print_help()
            print("")
            sys.exit(0)


        args: Namespace = parser.parse_args() #the arguments
        parsed1 = MessageToDict(
            parse_file(
                str(args.file1), args.version))

        parsed2 = MessageToDict(
            parse_file(
                str(args.file2), args.version))
        returns = str(get_edits_string(
                parsed1,
                parsed2,
                True if args.short else False
            ))
        print(returns)