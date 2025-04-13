from enum import Enum

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(block):
    """Determine the type of a markdown block.
    
    Args:
        block: A string containing a block of markdown text (with whitespace already stripped)
        
    Returns:
        A BlockType enum value representing the type of the block
    """
    # Check if it's a heading (starts with 1-6 # characters followed by a space)
    if block.startswith("#"):
        # Extract the potential heading marker
        heading_marker = block.split(" ", 1)[0]
        # Check if it's a valid heading (1-6 # characters)
        if 1 <= len(heading_marker) <= 6 and all(char == '#' for char in heading_marker):
            return BlockType.HEADING
    
    # Check if it's a code block (starts and ends with 3 backticks)
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    
    # Check if it's a quote block (every line starts with >)
    lines = block.split("\n")
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    
    # Check if it's an unordered list (every line starts with - followed by a space)
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST
    
    # Check if it's an ordered list
    # Every line must start with a number followed by . and a space
    # Numbers must start at 1 and increment by 1 for each line
    if len(lines) > 0 and lines[0].startswith("1. "):
        is_ordered_list = True
        for i, line in enumerate(lines, 1):
            expected_prefix = f"{i}. "
            if not line.startswith(expected_prefix):
                is_ordered_list = False
                break
        if is_ordered_list:
            return BlockType.ORDERED_LIST
    
    # If none of the above conditions are met, it's a paragraph
    return BlockType.PARAGRAPH