import re
from src.textnode import TextNode, TextType
from src.htmlnode import LeafNode, ParentNode
from src.blocktype import BlockType, block_to_block_type

def text_node_to_html_node(text_node):
  if text_node.text_type == TextType.TEXT:
    return LeafNode(None, text_node.text)
  elif text_node.text_type == TextType.BOLD:
    return LeafNode("b", text_node.text)
  elif text_node.text_type == TextType.ITALIC:
    return LeafNode("i", text_node.text)
  elif text_node.text_type == TextType.CODE:
    return LeafNode("code", text_node.text)
  elif text_node.text_type == TextType.LINK:
    return LeafNode("a", text_node.text, {"href": text_node.url})
  elif text_node.text_type == TextType.IMAGE:
    return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
  else:
    raise ValueError(f"Unknown text type: {text_node.text_type}")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
  result = []
  
  for old_node in old_nodes:
    # Only process TextNode with TEXT type
    if not isinstance(old_node, TextNode) or old_node.text_type != TextType.TEXT:
      result.append(old_node)
      continue
    
    # Split the text by delimiter
    splits = old_node.text.split(delimiter)
    
    # If no delimiter found, keep the node as is
    if len(splits) <= 1:
      result.append(old_node)
      continue
      
    # Check if we have an even number of splits (complete delimiter pairs)
    # If odd number of splits, we have incomplete delimiter pairs
    has_complete_pairs = len(splits) % 2 == 1
    
    # Process text with delimiters
    for i in range(len(splits)):
      # Skip empty splits
      if not splits[i]:
        continue
      
      # For complete pairs: even indices are TEXT, odd indices are special text_type
      # For incomplete pairs: only properly enclosed text gets the special text_type
      if has_complete_pairs:
        if i % 2 == 0:
          result.append(TextNode(splits[i], TextType.TEXT))
        else:
          result.append(TextNode(splits[i], text_type))
      else:
        # For incomplete pairs, only text between complete delimiter pairs gets the special type
        # This means odd indices less than the last index get the special type
        if i % 2 == 1 and i < len(splits) - 1:
          result.append(TextNode(splits[i], text_type))
        else:
          result.append(TextNode(splits[i], TextType.TEXT))
  
  return result

def extract_markdown_images(text):
  """Extract markdown images from text and return a list of tuples with alt text and URL.
  
  Args:
    text: A string containing markdown text
    
  Returns:
    A list of tuples, each containing (alt_text, url) for each markdown image found
  
  Example:
    text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif)"
    extract_markdown_images(text) # [("rick roll", "https://i.imgur.com/aKaOqIh.gif")]
  """
  # Regular expression pattern for markdown images: ![alt text](url)
  # The pattern captures two groups: the alt text and the URL
  pattern = r"!\[(.*?)\]\((.*?)\)"
  
  # Find all matches in the text
  matches = re.findall(pattern, text)
  
  # Each match is a tuple of (alt_text, url)
  return matches

def extract_markdown_links(text):
  """Extract markdown links from text and return a list of tuples with anchor text and URL.
  
  Args:
    text: A string containing markdown text
    
  Returns:
    A list of tuples, each containing (anchor_text, url) for each markdown link found
  
  Example:
    text = "This is text with a link [to boot dev](https://www.boot.dev)"
    extract_markdown_links(text) # [("to boot dev", "https://www.boot.dev")]
  """
  # Regular expression pattern for markdown links: [anchor text](url)
  # The pattern captures two groups: the anchor text and the URL
  # The negative lookbehind (?<!!)) ensures we don't match image syntax (which has ! before [)
  pattern = r"(?<!!)\[(.*?)\]\((.*?)\)"
  
  # Find all matches in the text
  matches = re.findall(pattern, text)
  
  # Each match is a tuple of (anchor_text, url)
  return matches

def split_nodes_image(old_nodes):
  """Split text nodes that contain markdown image syntax into multiple nodes.
  
  Args:
    old_nodes: A list of TextNode objects
    
  Returns:
    A list of TextNode objects where any markdown images have been converted to image nodes
  
  Example:
    node = TextNode("This is text with an ![image](https://example.com/image.jpg)", TextType.TEXT)
    split_nodes_image([node]) # [TextNode("This is text with an ", TextType.TEXT), TextNode("image", TextType.IMAGE, "https://example.com/image.jpg")]
  """
  result = []
  
  for old_node in old_nodes:
    # Only process TextNode with TEXT type
    if not isinstance(old_node, TextNode) or old_node.text_type != TextType.TEXT:
      result.append(old_node)
      continue
    
    # Extract all images from the text
    images = extract_markdown_images(old_node.text)
    
    # If no images found, keep the original node
    if not images:
      result.append(old_node)
      continue
    
    # Process the text, splitting on each image
    remaining_text = old_node.text
    
    for image_alt, image_url in images:
      # Split the text at the image markdown
      image_markdown = f"![{image_alt}]({image_url})"
      sections = remaining_text.split(image_markdown, 1)
      
      # Add the text before the image if it's not empty
      if sections[0]:
        result.append(TextNode(sections[0], TextType.TEXT))
      
      # Add the image node
      result.append(TextNode(image_alt, TextType.IMAGE, image_url))
      
      # Update the remaining text
      if len(sections) > 1:
        remaining_text = sections[1]
      else:
        remaining_text = ""
    
    # Add any remaining text after the last image
    if remaining_text:
      result.append(TextNode(remaining_text, TextType.TEXT))
  
  return result

def split_nodes_link(old_nodes):
  """Split text nodes that contain markdown link syntax into multiple nodes.
  
  Args:
    old_nodes: A list of TextNode objects
    
  Returns:
    A list of TextNode objects where any markdown links have been converted to link nodes
  
  Example:
    node = TextNode("This is text with a link [to boot dev](https://www.boot.dev)", TextType.TEXT)
    split_nodes_link([node]) # [TextNode("This is text with a link ", TextType.TEXT), TextNode("to boot dev", TextType.LINK, "https://www.boot.dev")]
  """
  result = []
  
  for old_node in old_nodes:
    # Only process TextNode with TEXT type
    if not isinstance(old_node, TextNode) or old_node.text_type != TextType.TEXT:
      result.append(old_node)
      continue
    
    # Extract all links from the text
    links = extract_markdown_links(old_node.text)
    
    # If no links found, keep the original node
    if not links:
      result.append(old_node)
      continue
    
    # Process the text, splitting on each link
    remaining_text = old_node.text
    
    for link_text, link_url in links:
      # Split the text at the link markdown
      link_markdown = f"[{link_text}]({link_url})"
      sections = remaining_text.split(link_markdown, 1)
      
      # Add the text before the link if it's not empty
      if sections[0]:
        result.append(TextNode(sections[0], TextType.TEXT))
      
      # Add the link node
      result.append(TextNode(link_text, TextType.LINK, link_url))
      
      # Update the remaining text
      if len(sections) > 1:
        remaining_text = sections[1]
      else:
        remaining_text = ""
    
    # Add any remaining text after the last link
    if remaining_text:
      result.append(TextNode(remaining_text, TextType.TEXT))
  
  return result

def text_to_textnodes(text):
  """Convert markdown text to a list of TextNode objects.
  
  Args:
    text: A string containing markdown text
    
  Returns:
    A list of TextNode objects representing the parsed markdown text
  
  Example:
    text = "This is **text** with an _italic_ word and a `code block`"
    text_to_textnodes(text) # [TextNode("This is ", TextType.TEXT), TextNode("text", TextType.BOLD), ...]
  """
  # Start with a single text node containing the entire text
  nodes = [TextNode(text, TextType.TEXT)]
  
  # Apply each splitting function in sequence
  # Order matters here - we want to process delimiters first, then images and links
  nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
  nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
  nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
  nodes = split_nodes_image(nodes)
  nodes = split_nodes_link(nodes)
  
  return nodes

def markdown_to_blocks(markdown):
  """Split a markdown string into blocks based on double newlines.
  
  Args:
    markdown: A string containing markdown text
    
  Returns:
    A list of strings, each representing a block of markdown
  
  Example:
    markdown = "# Heading\n\nParagraph text\n\n- List item"
    markdown_to_blocks(markdown) # ["# Heading", "Paragraph text", "- List item"]
  """
  # Split the markdown by double newlines
  blocks = markdown.split("\n\n")
  
  # Process each block
  result = []
  for block in blocks:
    # Strip leading/trailing whitespace
    stripped_block = block.strip()
    
    # Only add non-empty blocks
    if stripped_block:
      result.append(stripped_block)
  
  return result

def text_to_children(text):
  """Convert text to a list of HTMLNode children by processing inline markdown.
  
  Args:
    text: A string containing markdown text
    
  Returns:
    A list of HTMLNode objects representing the inline markdown elements
  """
  text_nodes = text_to_textnodes(text)
  return [text_node_to_html_node(text_node) for text_node in text_nodes]

def extract_title_level(heading_block):
  """Extract the heading level from a heading block.
  
  Args:
    heading_block: A string containing a heading block
    
  Returns:
    A tuple of (level, content) where level is an integer 1-6 and content is the heading text
  """
  # Split by the first space to separate the # markers from the content
  parts = heading_block.split(" ", 1)
  level = len(parts[0])  # Count the number of # characters
  content = parts[1] if len(parts) > 1 else ""
  return level, content

def extract_code_content(code_block):
  """Extract the content from a code block, removing the triple backticks.
  
  Args:
    code_block: A string containing a code block with triple backticks
    
  Returns:
    The content of the code block without the triple backticks
  """
  # Remove the first and last line (which contain the triple backticks)
  lines = code_block.split("\n")
  if len(lines) <= 2:  # Just the opening and closing backticks
    return ""
  
  # Check if the first line has a language specifier after the backticks
  if lines[0].startswith("```") and len(lines[0]) > 3:
    # Remove the opening line with language specifier and the closing line
    return "\n".join(lines[1:-1]) + "\n"
  else:
    # Remove the opening and closing backtick lines
    return "\n".join(lines[1:-1]) + "\n"

def extract_quote_content(quote_block):
  """Extract the content from a quote block, removing the > markers.
  
  Args:
    quote_block: A string containing a quote block where each line starts with >
    
  Returns:
    The content of the quote block without the > markers
  """
  lines = quote_block.split("\n")
  result = []
  
  for line in lines:
    # Remove the > and the space after it (if present)
    if line.startswith("> "):
      result.append(line[2:])
    elif line.startswith(">"):
      result.append(line[1:])
    else:
      result.append(line)  # Shouldn't happen if properly formatted
  
  return "\n".join(result)

def extract_list_items(list_block, ordered=False):
  """Extract items from a list block.
  
  Args:
    list_block: A string containing a list block
    ordered: Boolean indicating if this is an ordered list
    
  Returns:
    A list of strings, each representing a list item without the marker
  """
  lines = list_block.split("\n")
  items = []
  
  for i, line in enumerate(lines):
    if ordered:
      # For ordered lists, remove the number, period, and space
      prefix = f"{i+1}. "
      if line.startswith(prefix):
        items.append(line[len(prefix):])
    else:
      # For unordered lists, remove the dash and space
      if line.startswith("- "):
        items.append(line[2:])
  
  return items

def markdown_to_html_node(markdown):
  """Convert a markdown string to an HTML node.
  
  Args:
    markdown: A string containing markdown text
    
  Returns:
    An HTMLNode object representing the markdown document
  """
  # Split the markdown into blocks
  blocks = markdown_to_blocks(markdown)
  
  # Process each block and create HTML nodes
  children = []
  for block in blocks:
    # Determine the block type
    block_type = block_to_block_type(block)
    
    if block_type == BlockType.PARAGRAPH:
      # Replace newlines with spaces in paragraphs
      block_text = block.replace("\n", " ")
      # Create paragraph node with inline markdown processing
      children.append(ParentNode("p", text_to_children(block_text)))
    
    elif block_type == BlockType.HEADING:
      # Extract the heading level and content
      level, content = extract_title_level(block)
      # Create heading node with inline markdown processing
      children.append(ParentNode(f"h{level}", text_to_children(content)))
    
    elif block_type == BlockType.CODE:
      # Extract code content without the backticks
      code_content = extract_code_content(block)
      # Create code block without inline markdown processing
      code_node = TextNode(code_content, TextType.TEXT)
      # Wrap in pre and code tags
      code_html_node = text_node_to_html_node(code_node)
      children.append(ParentNode("pre", [ParentNode("code", [code_html_node])]))
    
    elif block_type == BlockType.QUOTE:
      # Extract quote content without the > markers
      quote_content = extract_quote_content(block)
      # Create quote node with inline markdown processing
      children.append(ParentNode("blockquote", text_to_children(quote_content)))
    
    elif block_type == BlockType.UNORDERED_LIST:
      # Extract list items
      items = extract_list_items(block, ordered=False)
      # Create list items with inline markdown processing
      list_items = [ParentNode("li", text_to_children(item)) for item in items]
      # Create unordered list node
      children.append(ParentNode("ul", list_items))
    
    elif block_type == BlockType.ORDERED_LIST:
      # Extract list items
      items = extract_list_items(block, ordered=True)
      # Create list items with inline markdown processing
      list_items = [ParentNode("li", text_to_children(item)) for item in items]
      # Create ordered list node
      children.append(ParentNode("ol", list_items))
  
  # Create parent div node containing all block nodes
  return ParentNode("div", children)
