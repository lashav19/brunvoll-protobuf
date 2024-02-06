
import proto5.thruster5 as thruster5
import json

import proto5

def openFlat(filepath, key_value_pairs=None):
    with open(fr"{filepath}", 'rb') as file:
        # Read the content and print it
        file_content = file.read()
        parser = thruster5.ThrusterParameters()
        serialized = parser.SerializeToString(file_content)
        print("File content:")
        # Parse the prototxt contents using the generated Python classes
        
        parsed_message = parser.SerializeToString(file_content)

    # Access and work with the parsed message
    print("Parsed message:")
    file_content_str = file_content.decode('utf-8')

    lines = file_content_str.split('\n')


    # Initialize an empty dictionary to store key-value pairs
    key_value_pairs = {}

    # Iterate over each line
    for line in lines:
        # Check if the line contains a colon
        if ':' in line:
            # Split the line by colon
            parts = line.split(':')
            # Strip leading and trailing whitespace from the key
            key = parts[0].strip()
            # Get the value, stripping leading and trailing whitespace
            value = parts[1].strip()
            # Add the key-value pair to the dictionary
            key_value_pairs[key] = value

    # Print the key-value pairs
    return key_value_pairs
print(openFlat(r"config\35042B\thruster_parameters_1.prototxt")['MaxPiRefRetrPos1'])