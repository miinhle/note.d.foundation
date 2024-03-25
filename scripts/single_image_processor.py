import os
import re
import urllib.parse
import sys


def process_markdown_file(file_path):
    """Processes a Markdown file, moving local images to an 'assets' folder and updating links.

    Args:
            file_path (str): Path to the Markdown file.
    """

    with open(file_path, "r") as file:
        content = file.read()

    file_dir = os.path.dirname(file_path)
    assets_dir = os.path.join(file_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    def replace_image_link(match):
        source_image_path = match.group(1) if match.group(1) else match.group(2)

        # Get the trailing image name from source_image_path
        image_name = os.path.basename(urllib.parse.urlparse(source_image_path).path)

        # Search for the image recursively
        for root, _, files in os.walk(file_dir):
            if image_name in files:
                image_path = os.path.join(root, image_name)
                break  # Stop if we find the image
        else:  # If the image is not found
            return match.group(0)  # Return the original link

        # Convert image_filename to lower kebab-case
        image_filename = os.path.basename(image_path)
        image_filename = image_filename.lower().replace(" ", "-")

        # Get the note filename
        note_filename = os.path.splitext(os.path.basename(file_path))[0]
        note_filename = note_filename.lower().replace(" ", "-")

        # Check if the image_filename already starts with the note_filename
        if image_filename.startswith(note_filename):
            new_filename = image_filename
        else:
            new_filename = note_filename + "_" + image_filename

        new_image_path = os.path.join(assets_dir, new_filename)

        # Check if the image is not in the assets folder
        if image_path != new_image_path:
            os.rename(image_path, new_image_path)
            print(f"Moved '{image_path}' to '{new_image_path}'")

        return "![](assets/" + new_filename + ")"

    # Update image links (both Obsidian and standard Markdown syntax)
    content = re.sub(
        r"!\[\[(.*?)\]\]|\!\[.*?\]\((.*?)\)", lambda x: replace_image_link(x), content
    )

    with open(file_path, "w") as file:
        file.write(content)


# Get the Markdown file path from the user (assuming it's the first argument)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        markdown_file_path = sys.argv[1]
        process_markdown_file(markdown_file_path)
    else:
        print("Please provide the path to the Markdown file as an argument.")
