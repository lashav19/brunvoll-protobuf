# Example text
text = """Line ends with a comma,
Line ends with a curly brace: }
Line doesn't end with a comma or curly brace: } ...
Another line without a comma or curly brace
Line with only curly braces: {}
Line with a mix of characters and curly braces: } abc {"""

def validatemultistring(lines):
    modified_lines = []
    for line in lines:
        if "{" in line or "}" in line or "," in line:
            modified_lines.append(line)
        else:
            print("valid"+ line)
            modified_lines.append(line + ",")
    return '\n'.join(modified_lines)

print(validatemultistring(text.split("\n")))