
import google.protobuf.text_format as text_format
from google.protobuf.json_format import MessageToDict, ParseError
import json
import difflib
from deepdiff import DeepDiff
from typing import Callable

def parse_file(file):
    try:
        import proto5.thruster5 as proto5 
        with open(file, 'r') as f:
            return text_format.Parse(f.read(), proto5.ThrusterParameters())
    except ParseError:
        import proto6.thruster6 as proto6 
        with open(file, 'r') as f:
            return text_format.Parse(f.read(), proto6.ThrusterParameters())
    

RED: Callable[[str], str] = lambda text: f"\u001b[31m{text}\033\u001b[0m"
GREEN: Callable[[str], str] = lambda text: f"\u001b[32m{text}\033\u001b[0m"

def get_edits_string(old: str, new: str) -> str:
    result = ""

    lines = difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True))
    
    for line in lines:
        line = line.rstrip()
        if line.startswith("+"):
            result += GREEN(line) + "\n"
        elif line.startswith("-"):
            result += RED(line) + "\n"
        elif line.startswith("?"):
            continue

    return result



# Example usage
filepath1 = r"C:\Users\Utplassering\bv-protobuf\config\35042D\thruster_parameters_1.prototxt"
parsed1 = MessageToDict(parse_file(filepath1, True))

filepath2 = r"C:\Users\Utplassering\bv-protobuf\config\35042E\thruster_parameters_1.prototxt"
parsed2 = MessageToDict(parse_file(filepath2, True))

print(
    get_edits_string(
        json.dumps(parsed1, indent=4, sort_keys=True),
        json.dumps(parsed2, indent=4, sort_keys=True)
    )
)
