import unittest

from src.textnode import TextNode, TextType
from src.utils import text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, markdown_to_html_node, extract_title

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
    
    def test_extract_markdown_links(self):
        # Test with multiple links
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        links = extract_markdown_links(text)
        
        self.assertEqual(len(links), 2)
        self.assertEqual(links[0], ("to boot dev", "https://www.boot.dev"))
        self.assertEqual(links[1], ("to youtube", "https://www.youtube.com/@bootdotdev"))
    
    def test_extract_markdown_links_no_links(self):
        # Test with no links
        text = "This is text with no markdown links"
        links = extract_markdown_links(text)
        
        self.assertEqual(len(links), 0)
    
    def test_extract_markdown_links_incomplete_syntax(self):
        # Test with incomplete markdown link syntax
        text = "This has an incomplete [anchor text](https://example.com and [another](no closing parenthesis"
        links = extract_markdown_links(text)
        
        self.assertEqual(len(links), 0)
    
    def test_extract_markdown_links_with_images(self):
        # Test with both links and images
        text = "This has a [link](https://example.com) and an ![image](https://example.com/image.jpg)"
        links = extract_markdown_links(text)
        
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0], ("link", "https://example.com"))

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)
    
    def test_split_nodes_image_basic(self):
        # Test with a single image
        node = TextNode("This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text, "This is text with an ")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, "image")
        self.assertEqual(new_nodes[1].text_type, TextType.IMAGE)
        self.assertEqual(new_nodes[1].url, "https://i.imgur.com/zjjcJKZ.png")
    
    def test_split_nodes_image_multiple(self):
        # Test with multiple images
        node = TextNode(
            "This is text with an ![image1](https://example.com/image1.jpg) and another ![image2](https://example.com/image2.jpg)", 
            TextType.TEXT
        )
        new_nodes = split_nodes_image([node])
        
        self.assertEqual(len(new_nodes), 4)
        self.assertEqual(new_nodes[0].text, "This is text with an ")
        self.assertEqual(new_nodes[1].text, "image1")
        self.assertEqual(new_nodes[1].text_type, TextType.IMAGE)
        self.assertEqual(new_nodes[1].url, "https://example.com/image1.jpg")
        self.assertEqual(new_nodes[2].text, " and another ")
        self.assertEqual(new_nodes[3].text, "image2")
        self.assertEqual(new_nodes[3].text_type, TextType.IMAGE)
        self.assertEqual(new_nodes[3].url, "https://example.com/image2.jpg")
    
    def test_split_nodes_image_no_images(self):
        # Test with no images
        node = TextNode("This is text with no images", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text, "This is text with no images")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
    
    def test_split_nodes_image_non_text_node(self):
        # Test with non-TEXT type node
        node = TextNode("This is bold", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text, "This is bold")
        self.assertEqual(new_nodes[0].text_type, TextType.BOLD)
    
    def test_split_nodes_link_basic(self):
        # Test with a single link
        node = TextNode("This is text with a link [to boot dev](https://www.boot.dev)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text, "This is text with a link ")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, "to boot dev")
        self.assertEqual(new_nodes[1].text_type, TextType.LINK)
        self.assertEqual(new_nodes[1].url, "https://www.boot.dev")
    
    def test_split_nodes_link_multiple(self):
        # Test with multiple links
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)", 
            TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        
        self.assertEqual(len(new_nodes), 4)
        self.assertEqual(new_nodes[0].text, "This is text with a link ")
        self.assertEqual(new_nodes[1].text, "to boot dev")
        self.assertEqual(new_nodes[1].text_type, TextType.LINK)
        self.assertEqual(new_nodes[1].url, "https://www.boot.dev")
        self.assertEqual(new_nodes[2].text, " and ")
        self.assertEqual(new_nodes[3].text, "to youtube")
        self.assertEqual(new_nodes[3].text_type, TextType.LINK)
        self.assertEqual(new_nodes[3].url, "https://www.youtube.com/@bootdotdev")
    
    def test_split_nodes_link_no_links(self):
        # Test with no links
        node = TextNode("This is text with no links", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text, "This is text with no links")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
    
    def test_split_nodes_link_non_text_node(self):
        # Test with non-TEXT type node
        node = TextNode("This is bold", TextType.BOLD)
        new_nodes = split_nodes_link([node])
        
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text, "This is bold")
        self.assertEqual(new_nodes[0].text_type, TextType.BOLD)
    
    def test_split_nodes_link_empty_sections(self):
        # Test with empty sections between links
        node = TextNode("[link1](https://example.com/1)[link2](https://example.com/2)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text, "link1")
        self.assertEqual(new_nodes[0].text_type, TextType.LINK)
        self.assertEqual(new_nodes[0].url, "https://example.com/1")
        self.assertEqual(new_nodes[1].text, "link2")
        self.assertEqual(new_nodes[1].text_type, TextType.LINK)
        self.assertEqual(new_nodes[1].url, "https://example.com/2")

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
        [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.TEXT),
            TextNode(
                "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
            ),
        ],
        new_nodes,
    )
    
    def test_text_to_textnodes_all_elements(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        
        expected_nodes = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        
        self.assertEqual(len(nodes), len(expected_nodes))
        for i in range(len(nodes)):
            self.assertEqual(nodes[i].text, expected_nodes[i].text)
            self.assertEqual(nodes[i].text_type, expected_nodes[i].text_type)
            if hasattr(expected_nodes[i], 'url') and expected_nodes[i].url is not None:
                self.assertEqual(nodes[i].url, expected_nodes[i].url)
    
    def test_text_to_textnodes_plain_text(self):
        text = "This is just plain text with no markdown"
        nodes = text_to_textnodes(text)
        
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].text, text)
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
    
    def test_text_to_textnodes_nested_formatting(self):
        # Note: Our current implementation doesn't handle nested formatting correctly,
        # but we should test the actual behavior
        text = "This is **bold _and italic_**"
        nodes = text_to_textnodes(text)
        
        # The actual behavior with our current implementation
        # The bold markers are processed first, but the italic markers remain as text
        expected_nodes = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold _and italic_", TextType.BOLD),
        ]
        
        self.assertEqual(len(nodes), len(expected_nodes))
        for i in range(len(nodes)):
            self.assertEqual(nodes[i].text, expected_nodes[i].text)
            self.assertEqual(nodes[i].text_type, expected_nodes[i].text_type)
    
    def test_markdown_to_blocks_basic(self):
        markdown = "# This is a heading\n\nThis is a paragraph of text. It has some **bold** and _italic_ words inside of it.\n\n- This is the first list item in a list block\n- This is a list item\n- This is another list item"
        blocks = markdown_to_blocks(markdown)
        
        expected_blocks = [
            "# This is a heading",
            "This is a paragraph of text. It has some **bold** and _italic_ words inside of it.",
            "- This is the first list item in a list block\n- This is a list item\n- This is another list item"
        ]
        
        self.assertEqual(blocks, expected_blocks)
    
    def test_markdown_to_blocks_empty_blocks(self):
        # Test with excessive newlines that would create empty blocks
        markdown = "# Heading\n\n\n\nParagraph\n\n\n\n- List"
        blocks = markdown_to_blocks(markdown)
        
        expected_blocks = [
            "# Heading",
            "Paragraph",
            "- List"
        ]
        
        self.assertEqual(blocks, expected_blocks)
    
    def test_markdown_to_blocks_whitespace(self):
        # Test with blocks that have leading/trailing whitespace
        markdown = "  # Heading with space  \n\n  Paragraph with space  "
        blocks = markdown_to_blocks(markdown)
        
        expected_blocks = [
            "# Heading with space",
            "Paragraph with space"
        ]
        
        self.assertEqual(blocks, expected_blocks)
    
    def test_markdown_to_blocks_single_block(self):
        # Test with a single block (no double newlines)
        markdown = "This is just one block of text"
        blocks = markdown_to_blocks(markdown)
        
        expected_blocks = ["This is just one block of text"]
        
        self.assertEqual(blocks, expected_blocks)
    
    def test_markdown_to_blocks_code_blocks(self):
        # Test with code blocks that contain newlines
        markdown = "# Code Example\n\n```python\ndef hello():\n    print(\"Hello, world!\")\n```\n\nEnd of example"
        blocks = markdown_to_blocks(markdown)
        
        expected_blocks = [
            "# Code Example",
            "```python\ndef hello():\n    print(\"Hello, world!\")\n```",
            "End of example"
        ]
        
        self.assertEqual(blocks, expected_blocks)

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
            "- This is a list\n- with items",
        ],
    )
  
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )
        
    def test_heading(self):
        md = """
# Heading 1

## Heading 2 with **bold**

### Heading 3 with `code`
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Heading 1</h1><h2>Heading 2 with <b>bold</b></h2><h3>Heading 3 with <code>code</code></h3></div>",
        )
        
    def test_quote(self):
        md = """
> This is a quote
> with multiple lines
> and **bold** text
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a quote\nwith multiple lines\nand <b>bold</b> text</blockquote></div>",
        )
        
    def test_unordered_list(self):
        md = """
- Item 1 with **bold**
- Item 2 with _italic_
- Item 3 with `code`
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>Item 1 with <b>bold</b></li><li>Item 2 with <i>italic</i></li><li>Item 3 with <code>code</code></li></ul></div>",
        )
        
    def test_ordered_list(self):
        md = """
1. First item with **bold**
2. Second item with _italic_
3. Third item with `code`
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>First item with <b>bold</b></li><li>Second item with <i>italic</i></li><li>Third item with <code>code</code></li></ol></div>",
        )
        
    def test_mixed_content(self):
        md = """
# Main Heading

This is a paragraph with **bold** and _italic_ text.

```
code block
with multiple lines
```

> This is a quote
> with multiple lines

- List item 1
- List item 2

1. Ordered item 1
2. Ordered item 2
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Main Heading</h1><p>This is a paragraph with <b>bold</b> and <i>italic</i> text.</p><pre><code>code block\nwith multiple lines\n</code></pre><blockquote>This is a quote\nwith multiple lines</blockquote><ul><li>List item 1</li><li>List item 2</li></ul><ol><li>Ordered item 1</li><li>Ordered item 2</li></ol></div>",
        )
        
    def test_extract_title_basic(self):
        md = "# Hello, World!\n\nThis is some content."
        title = extract_title(md)
        self.assertEqual(title, "Hello, World!")
        
    def test_extract_title_with_formatting(self):
        md = "# This is a **bold** title\n\nWith content."
        title = extract_title(md)
        self.assertEqual(title, "This is a **bold** title")
        
    def test_extract_title_with_extra_whitespace(self):
        md = "#    Title with extra spaces    \n\nContent."
        title = extract_title(md)
        self.assertEqual(title, "Title with extra spaces")
        
    def test_extract_title_multiline_markdown(self):
        md = "Some text before\n\n# The Real Title\n\nMore content."
        title = extract_title(md)
        self.assertEqual(title, "The Real Title")
        
    def test_extract_title_no_h1(self):
        md = "## This is h2\n\nNo h1 here."
        with self.assertRaises(ValueError):
            extract_title(md)

if __name__ == "__main__":
    unittest.main()