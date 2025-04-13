import re
from textnode import TextNode, TextType
from htmlnode import LeafNode

def text_node_to_html_node(text_node):
  if text_node.text_type == TextType.TEXT:
    return LeafNode(None,text_node.text)
  elif text_node.text_type == TextType.BOLD:
    return LeafNode("b", text_node.text)
  elif text_node.text_type == TextType.ITALIC:
    return LeafNode("i", text_node.text)
  elif text_node.text_type == TextType.LINK:
    return LeafNode("a", text_node.text, {"href": text_node.url})
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
