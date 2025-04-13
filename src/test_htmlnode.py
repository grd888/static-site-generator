import unittest

from htmlnode import HTMLNode, LeafNode


class TestHTMLNode(unittest.TestCase):
    def test_init(self):
        # Test initialization with default parameters
        node = HTMLNode()
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)
        
        # Test initialization with all parameters
        node = HTMLNode("div", "text", [HTMLNode("p")], {"class": "container"})
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.value, "text")
        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.props, {"class": "container"})
    
    def test_props_to_html(self):
        # Test with empty props
        node = HTMLNode(props={})
        self.assertEqual(node.props_to_html(), "")
        
        # Test with single prop
        node = HTMLNode(props={"class": "container"})
        self.assertEqual(node.props_to_html(), ' class="container"')
        
        # Test with multiple props
        node = HTMLNode(props={"class": "container", "id": "main", "data-test": "value"})
        # Since dict order is not guaranteed, check for each property separately
        props_html = node.props_to_html()
        self.assertIn(' class="container"', props_html)
        self.assertIn(' id="main"', props_html)
        self.assertIn(' data-test="value"', props_html)
    
    def test_repr(self):
        # Test __repr__ with default parameters
        node = HTMLNode()
        self.assertEqual(repr(node), "HTMLNode(None, None, None, None)")
        
        # Test __repr__ with all parameters
        node = HTMLNode("div", "text", [HTMLNode()], {"class": "container"})
        # We need to check parts of the string since the child's repr will be dynamic
        repr_str = repr(node)
        self.assertIn("HTMLNode(div, text, [", repr_str)
        self.assertIn("], {'class': 'container'}", repr_str)

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
        
    def test_leaf_to_html_no_tag(self):
        node = LeafNode(None, "Just some text")
        self.assertEqual(node.to_html(), "Just some text")
        
    def test_leaf_to_html_with_props(self):
        node = LeafNode("a", "Click me", {"href": "https://www.example.com", "target": "_blank"})
        self.assertEqual(node.to_html(), '<a href="https://www.example.com" target="_blank">Click me</a>')
        
    def test_leaf_to_html_none_value(self):
        node = LeafNode("div", None)
        with self.assertRaises(ValueError):
            node.to_html()


if __name__ == "__main__":
    unittest.main()
