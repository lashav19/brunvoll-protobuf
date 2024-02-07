import difflib
from colorama import init, Fore
import json


def find_key_breadcrumb(subkey: str, dictionary: dict, parent_key='', sep='.'):
    #lager en breadcrumb til pathen keyen er i
    for key, value in dictionary.items():
        if isinstance(value, dict):
            breadcrumb = find_key_breadcrumb(subkey, value, parent_key + sep + key if parent_key else key, sep=sep)
            if breadcrumb:
                return breadcrumb
        elif key == subkey:
            return parent_key + sep + key

def get_diff_lines(old_dict: dict, new_dict: dict) -> str:
    lines = difflib.ndiff(
        json.dumps(old_dict, indent=4).splitlines(keepends=True),
        json.dumps(new_dict, indent=4).splitlines(keepends=True)
    )
    return lines

def get_edits_dict(old_dict: dict, new_dict: dict, short: bool = False) -> str:
    result = ""
    subkey = None
    lines = get_diff_lines(old_dict, new_dict)
    for line in lines:
        line = line.rstrip()
        if line.startswith("+") or line.startswith("-"):
            parts = line.split(':', 1)
            key = parts[0].split()[-1].strip('"')  # Extracting subkey without quotes
            if subkey is None:  # If subkey is not yet set
                subkey = key
            elif subkey != key:  # If subkey changes, we stop looking
                break

        if subkey:  # If subkey is found
            break

    if subkey:
        subkey_breadcrumb = find_key_breadcrumb(subkey, new_dict)
        if subkey_breadcrumb:
            print("Breadcrumb to subkey '{}': {}".format(subkey, subkey_breadcrumb))
        else:
            print("Subkey '{}' not found in the dictionary.".format(subkey))
            return ""
    else:
        print("No subkey found in the diff.")
        return ""

    lines = get_diff_lines(old_dict, new_dict)

    for line in lines:
        line = line.rstrip()
        if line.startswith("+") or line.startswith("-"):
            parts = line.split(':', 1)
            key = parts[0].split()[-1].strip('"')  # Extracting subkey without quotes
            if line.startswith("+"):
                breadcrumb = find_key_breadcrumb(key, new_dict)
                if breadcrumb:
                    result += Fore.GREEN + "- " + breadcrumb + ": " + parts[1].strip() + Fore.RESET + "\n"
            elif line.startswith("-"):
                breadcrumb = find_key_breadcrumb(key, old_dict)
                if breadcrumb:
                    result += Fore.RED + "- " + breadcrumb + ": " + parts[1].strip() + Fore.RESET + "\n"
        elif line.startswith("?"):
            continue

    if short:
        add = result.count("+")
        remove = result.count("-")
        print(Fore.GREEN('\nAdded: '), Fore.GREEN(add) +
              "     " + Fore.RED("Removed: "), Fore.RED(remove))
        return ""

    return result

# Example usage:
old_dict = {"key1": {"subkey1": "value1", "subkey2": "value2"}}
new_dict = {"key1": {"subkey1": "new_value1", "subkey2": "value2", "subkey3": "value3"}}

print(get_edits_dict(old_dict, new_dict))
