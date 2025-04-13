import os
import shutil
import logging
from textnode import TextNode, TextType

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

def main():
    # Define source and destination directories relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_dir = os.path.join(project_root, "static")
    dest_dir = os.path.join(project_root, "public")
    
    logging.info(f"Starting directory copy from {source_dir} to {dest_dir}")
    copy_directory(source_dir, dest_dir)
    logging.info("Directory copy completed successfully")

if __name__ == "__main__":
    main()