import unittest

from blocktype import BlockType, block_to_block_type

class TestBlockType(unittest.TestCase):
    def test_paragraph(self):
        block = "This is a regular paragraph with some text."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
        
        block = "This is a paragraph\nwith multiple lines\nbut no special formatting."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_heading(self):
        # Test all heading levels
        for i in range(1, 7):
            heading = "#" * i + " Heading level " + str(i)
            self.assertEqual(block_to_block_type(heading), BlockType.HEADING)
        
        # Test invalid heading (too many #)
        heading = "#" * 7 + " Invalid heading"
        self.assertEqual(block_to_block_type(heading), BlockType.PARAGRAPH)
        
        # Test invalid heading (no space after #)
        heading = "##No space after hash"
        self.assertEqual(block_to_block_type(heading), BlockType.PARAGRAPH)
    
    def test_code(self):
        block = "```\ncode block\nwith multiple lines\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)
        
        block = "```python\ndef hello():\n    print('Hello, world!')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)
        
        # Test invalid code block (doesn't end with ```)
        block = "```\ncode block without closing backticks"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
        
        # Test invalid code block (doesn't start with ```)
        block = "code block\n```"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_quote(self):
        block = "> This is a quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)
        
        block = "> This is a quote\n> with multiple lines"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)
        
        # Test invalid quote (not all lines start with >)
        block = "> This is a quote\nThis line doesn't start with >"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_unordered_list(self):
        block = "- Item 1"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)
        
        block = "- Item 1\n- Item 2\n- Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)
        
        # Test invalid unordered list (not all lines start with -)
        block = "- Item 1\nItem 2 without dash"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
        
        # Test invalid unordered list (no space after -)
        block = "-Item without space"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_ordered_list(self):
        block = "1. Item 1"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)
        
        block = "1. Item 1\n2. Item 2\n3. Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)
        
        # Test invalid ordered list (doesn't start with 1)
        block = "2. Starting with 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
        
        # Test invalid ordered list (numbers not sequential)
        block = "1. Item 1\n3. Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
        
        # Test invalid ordered list (no space after number)
        block = "1.Item without space"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

if __name__ == "__main__":
    unittest.main()
