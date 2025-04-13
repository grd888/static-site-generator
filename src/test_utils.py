import unittest

from textnode import TextNode, TextType

from utils import text_node_to_html_node, split_nodes_delimiter, extract_markdown_images

class TestUtils(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
    
    def test_split_nodes_delimiter_code(self):
        # Test for code blocks with backtick delimiter
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This is text with a ")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, "code block")
        self.assertEqual(new_nodes[1].text_type, TextType.CODE)
        self.assertEqual(new_nodes[2].text, " word")
        self.assertEqual(new_nodes[2].text_type, TextType.TEXT)
    
    def test_split_nodes_delimiter_bold(self):
        # Test for bold text with ** delimiter
        node = TextNode("This is text with a **bold** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This is text with a ")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, "bold")
        self.assertEqual(new_nodes[1].text_type, TextType.BOLD)
        self.assertEqual(new_nodes[2].text, " word")
        self.assertEqual(new_nodes[2].text_type, TextType.TEXT)
    
    def test_split_nodes_delimiter_italic(self):
        # Test for italic text with _ delimiter
        node = TextNode("This is text with an _italic_ word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This is text with an ")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, "italic")
        self.assertEqual(new_nodes[1].text_type, TextType.ITALIC)
        self.assertEqual(new_nodes[2].text, " word")
        self.assertEqual(new_nodes[2].text_type, TextType.TEXT)
    
    def test_split_nodes_delimiter_multiple_occurrences(self):
        # Test for multiple occurrences of the same delimiter
        node = TextNode("This `code` has `multiple` code blocks", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        
        self.assertEqual(len(new_nodes), 5)
        self.assertEqual(new_nodes[0].text, "This ")
        self.assertEqual(new_nodes[1].text, "code")
        self.assertEqual(new_nodes[1].text_type, TextType.CODE)
        self.assertEqual(new_nodes[2].text, " has ")
        self.assertEqual(new_nodes[3].text, "multiple")
        self.assertEqual(new_nodes[3].text_type, TextType.CODE)
        self.assertEqual(new_nodes[4].text, " code blocks")
    
    def test_split_nodes_delimiter_no_delimiter(self):
        # Test when no delimiter is found
        node = TextNode("This text has no delimiters", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text, "This text has no delimiters")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
    
    def test_split_nodes_delimiter_incomplete_pair(self):
        # Test when there's an incomplete pair of delimiters
        node = TextNode("This text has an incomplete ` delimiter", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        
        # The current implementation splits on the delimiter, resulting in 2 parts
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text, "This text has an incomplete ")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, " delimiter")
        self.assertEqual(new_nodes[1].text_type, TextType.TEXT)
    
    def test_split_nodes_delimiter_empty_content(self):
        # Test with empty content between delimiters
        node = TextNode("This has an empty `` code block", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text, "This has an empty ")
        self.assertEqual(new_nodes[1].text, " code block")
    
    def test_split_nodes_delimiter_multiple_nodes(self):
        # Test with multiple input nodes
        node1 = TextNode("This is `code`", TextType.TEXT)
        node2 = TextNode("This is normal text", TextType.TEXT)
        node3 = TextNode("This is more `code`", TextType.TEXT)
        
        new_nodes = split_nodes_delimiter([node1, node2, node3], "`", TextType.CODE)
        
        self.assertEqual(len(new_nodes), 5)
        self.assertEqual(new_nodes[0].text, "This is ")
        self.assertEqual(new_nodes[1].text, "code")
        self.assertEqual(new_nodes[1].text_type, TextType.CODE)
        self.assertEqual(new_nodes[2].text, "This is normal text")
        self.assertEqual(new_nodes[3].text, "This is more ")
        self.assertEqual(new_nodes[4].text, "code")
        self.assertEqual(new_nodes[4].text_type, TextType.CODE)
    
    def test_split_nodes_delimiter_non_text_nodes(self):
        # Test with non-TEXT type nodes
        node1 = TextNode("This is `code`", TextType.TEXT)
        node2 = TextNode("This is bold", TextType.BOLD)
        
        new_nodes = split_nodes_delimiter([node1, node2], "`", TextType.CODE)
        
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This is ")
        self.assertEqual(new_nodes[1].text, "code")
        self.assertEqual(new_nodes[1].text_type, TextType.CODE)
        self.assertEqual(new_nodes[2].text, "This is bold")
        self.assertEqual(new_nodes[2].text_type, TextType.BOLD)
    
    def test_extract_markdown_images(self):
        # Test with multiple images
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        images = extract_markdown_images(text)
        
        self.assertEqual(len(images), 2)
        self.assertEqual(images[0], ("rick roll", "https://i.imgur.com/aKaOqIh.gif"))
        self.assertEqual(images[1], ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"))
    
    def test_extract_markdown_images_no_images(self):
        # Test with no images
        text = "This is text with no markdown images"
        images = extract_markdown_images(text)
        
        self.assertEqual(len(images), 0)
    
    def test_extract_markdown_images_incomplete_syntax(self):
        # Test with incomplete markdown image syntax
        text = "This has an incomplete ![alt text](https://example.com and ![another](no closing parenthesis"
        images = extract_markdown_images(text)
        
        self.assertEqual(len(images), 0)
  
if __name__ == "__main__":
    unittest.main()