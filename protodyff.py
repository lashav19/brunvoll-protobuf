


import json
import difflib
from deepdiff import DeepDiff
import re

data1 = """
thruster_name: "Bow"
thruster_type: FU63
plant_number: "12293"
position {
  x_position: 0
  y_position: 0
  z_position: 0
}
_has_controllable_pitch: true
is_combi_thruster: false
_has_remote_io: false
_has_angle_gear: false
hardwired_bridge_start_stop_type: CommandSignalToggle
map_external_bridge_azimuth_to_180: false
start_sequence_timeout_length: 180
stop_sequence_timeout_length: 30
local_control_selector: LocalControlSelectorGuiButton"""

data2 = """
thruster_name: "Bow"
thruster_type: FU53
plant_number: "12293"
position {
  x_position: 2
  y_position: 2
  z_position: 0
}
_has_controllable_pitch: true
is_combi_thruster: false
_has_remote_io: false
_has_angle_gear: false
hardwired_bridge_start_stop_type: CommandSignalToggle
map_external_bridge_azimuth_to_180: false
start_sequence_timeout_length: 180
stop_sequence_timeout_length: 30
local_control_selector: LocalControlSelectorGuiButton"""


def openFlat(filepath, key_value_pairs=None):
    import proto5.thruster5 as thruster5
    with open(fr"{filepath}", 'rb') as file:
        # Read the content and print it
        file_content = file.read()
        parser = thruster5.ThrusterParameters()
        serialized = parser.SerializeToString(file_content)

        # Parse the prototxt contents using the generated Python classes

    # Access and work with the parsed message

    lines = file_content.decode('utf-8')



    key_value_pairs = makeDict(lines)
    return key_value_pairs


def openv6(filepath):
    import proto6.thruster6 as thruster6
    with open(fr"{filepath}", 'rb') as file:
        # Read the content and print it
        file_content = file.read()
        parser = thruster6.ThrusterParameters()
        serialized = parser.SerializeToString(file_content)

        # Parse the prototxt contents using the generated Python classes
    # Access and work with the parsed message

    file_content_str = file_content.decode('utf-8')
    return makeDict(file_content_str)
    





def makeDict(lines, key_value_pairs=None):
    lines = lines.split('\n')
    if key_value_pairs is None:
        key_value_pairs = {}

    # Regular expression patterns to match key-value pairs and nested structures
    pattern_key_value = r'(?P<key>[a-zA-Z0-9_]+)\s*:\s*(?P<value>.+)$'
    pattern_nested_structure_start = r'(?P<key>[a-zA-Z0-9_]+)\s*{\s*$'
    pattern_nested_structure_end = r'^\s*}\s*$'

    # Helper function to parse nested structures recursively
    def parse_structure(lines_iter):
        nested_data = {}
        for line in lines_iter:
            # Check for nested structure start
            match_start = re.match(pattern_nested_structure_start, line)
            if match_start:
                key = match_start.group('key').strip()
                nested_data[key] = parse_structure(lines_iter)
            else:
                # Check for nested structure end
                match_end = re.match(pattern_nested_structure_end, line)
                if match_end:
                    return nested_data
                else:
                    # Match key-value pairs
                    match_kv = re.match(pattern_key_value, line)
                    if match_kv:
                        key = match_kv.group('key').strip()
                        value = match_kv.group('value').strip()
                        nested_data[key] = value
        return nested_data

    # Iterate over each line
    lines_iter = iter(lines)
    for line in lines_iter:
        # Match top-level key-value pairs
        match_kv = re.match(pattern_key_value, line)
        if match_kv:
            key = match_kv.group('key').strip()
            value = match_kv.group('value').strip()
            key_value_pairs[key] = value
        else:
            # Match nested structures
            match_start = re.match(pattern_nested_structure_start, line)
            if match_start:
                key = match_start.group('key').strip()
                key_value_pairs[key] = parse_structure(lines_iter)

    return key_value_pairs

one = openv6(r"config\35042D\thruster_parameters_1.prototxt")
two = openv6(r"config\35042E\thruster_parameters_1.prototxt")

print(makeDict(data1), makeDict(data2))

