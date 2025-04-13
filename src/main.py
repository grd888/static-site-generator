import os
import shutil
import logging
from textnode import TextNode, TextType
from utils import markdown_to_html_node, extract_title

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def copy_directory(source_dir, dest_dir):
    """
    Recursively copy all contents from source_dir to dest_dir.
    First deletes all contents of dest_dir to ensure a clean copy.
    
    Args:
        source_dir: Path to the source directory
        dest_dir: Path to the destination directory
    """
    # Make sure source directory exists
    if not os.path.exists(source_dir):
        logging.error(f"Source directory does not exist: {source_dir}")
        return
    
    # Delete destination directory if it exists
    if os.path.exists(dest_dir):
        logging.info(f"Deleting existing destination directory: {dest_dir}")
        shutil.rmtree(dest_dir)
    
    # Create destination directory
    logging.info(f"Creating destination directory: {dest_dir}")
    os.makedirs(dest_dir)
    
    # Walk through the source directory and copy everything
    for root, dirs, files in os.walk(source_dir):
        # Get the relative path from source_dir
        rel_path = os.path.relpath(root, source_dir)
        
        # Create the corresponding directory in dest_dir
        if rel_path != '.':
            dest_path = os.path.join(dest_dir, rel_path)
            logging.info(f"Creating directory: {dest_path}")
            os.makedirs(dest_path, exist_ok=True)
        else:
            dest_path = dest_dir
        
        # Copy all files in the current directory
        for file in files:
            source_file = os.path.join(root, file)
            dest_file = os.path.join(dest_path, file)
            logging.info(f"Copying file: {source_file} -> {dest_file}")
            shutil.copy2(source_file, dest_file)

def generate_page(from_path, template_path, dest_path):
    """
    Generate an HTML page from a markdown file using a template.
    
    Args:
        from_path: Path to the markdown file
        template_path: Path to the HTML template file
        dest_path: Path where the generated HTML file will be saved
    """
    logging.info(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read the markdown file
    try:
        with open(from_path, 'r') as f:
            markdown_content = f.read()
    except FileNotFoundError:
        logging.error(f"Markdown file not found: {from_path}")
        return
    except Exception as e:
        logging.error(f"Error reading markdown file: {e}")
        return
    
    # Read the template file
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        logging.error(f"Template file not found: {template_path}")
        return
    except Exception as e:
        logging.error(f"Error reading template file: {e}")
        return
    
    # Convert markdown to HTML
    try:
        html_node = markdown_to_html_node(markdown_content)
        html_content = html_node.to_html()
    except Exception as e:
        logging.error(f"Error converting markdown to HTML: {e}")
        return
    
    # Extract title from markdown
    try:
        title = extract_title(markdown_content)
    except ValueError as e:
        logging.warning(f"No title found in markdown file, using default: {e}")
        title = "Untitled Page"
    except Exception as e:
        logging.error(f"Error extracting title: {e}")
        return
    
    # Replace placeholders in template
    try:
        final_html = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)
    except Exception as e:
        logging.error(f"Error replacing placeholders: {e}")
        return
    
    # Create destination directory if it doesn't exist
    dest_dir = os.path.dirname(dest_path)
    if not os.path.exists(dest_dir):
        try:
            os.makedirs(dest_dir)
            logging.info(f"Created directory: {dest_dir}")
        except Exception as e:
            logging.error(f"Error creating directory: {e}")
            return
    
    # Write the final HTML to the destination file
    try:
        with open(dest_path, 'w') as f:
            f.write(final_html)
        logging.info(f"Successfully generated page: {dest_path}")
    except Exception as e:
        logging.error(f"Error writing HTML file: {e}")
        return

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    """
    Recursively crawl a directory for markdown files and generate HTML pages.
    
    Args:
        dir_path_content: Path to the content directory containing markdown files
        template_path: Path to the HTML template file
        dest_dir_path: Path to the destination directory for generated HTML files
    """
    logging.info(f"Recursively generating pages from {dir_path_content} to {dest_dir_path}")
    
    # Make sure the content directory exists
    if not os.path.exists(dir_path_content):
        logging.error(f"Content directory does not exist: {dir_path_content}")
        return
    
    # Walk through the content directory
    for root, dirs, files in os.walk(dir_path_content):
        # Get the relative path from the content directory
        rel_path = os.path.relpath(root, dir_path_content)
        
        # Create the corresponding directory in the destination
        if rel_path != '.':
            dest_subdir = os.path.join(dest_dir_path, rel_path)
        else:
            dest_subdir = dest_dir_path
        
        # Process markdown files
        for file in files:
            # Check if the file is a markdown file
            if file.endswith('.md'):
                # Get the source and destination paths
                source_file = os.path.join(root, file)
                
                # If the file is named index.md, keep the directory structure
                # Otherwise, create an HTML file with the same name
                if file == 'index.md':
                    # For index.md, create index.html in the same relative directory
                    dest_file = os.path.join(dest_subdir, 'index.html')
                else:
                    # For other markdown files, replace .md with .html
                    dest_file = os.path.join(dest_subdir, file.replace('.md', '.html'))
                
                # Generate the HTML page
                generate_page(source_file, template_path, dest_file)

def main():
    # Define source and destination directories relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(project_root, "static")
    public_dir = os.path.join(project_root, "public")
    content_dir = os.path.join(project_root, "content")
    template_path = os.path.join(project_root, "template.html")
    
    # Step 1: Delete anything in the public directory
    if os.path.exists(public_dir):
        logging.info(f"Deleting existing public directory: {public_dir}")
        shutil.rmtree(public_dir)
        logging.info("Public directory deleted successfully")
    
    # Step 2: Copy all static files from static to public
    logging.info(f"Copying static files from {static_dir} to {public_dir}")
    copy_directory(static_dir, public_dir)
    logging.info("Static files copied successfully")
    
    # Step 3: Generate HTML pages from markdown files recursively
    logging.info("Recursively generating HTML pages from markdown files")
    generate_pages_recursive(content_dir, template_path, public_dir)
    logging.info("HTML pages generated successfully")

if __name__ == "__main__":
    main()