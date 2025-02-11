import os
import sys

def create_directories_from_file(structure_file, base_path):
    """
    Reads a text file containing a directory structure and creates the directories.

    Args:
        structure_file (str): Path to the text file containing directory names.
        base_path (str): The root directory where the structure will be created.

    Example file structure.txt:
        utilities/python/scripts/ffmpeg
        utilities/python/scripts/filesystem
        utilities/python/tests
        utilities/batch/scripts
        utilities/excel/apps

    Example usage:
        python create_directory_structure.py structure.txt C:\Projects\Repo_location
    """
    if not os.path.exists(structure_file):
        print(f"❌ Error: Structure file '{structure_file}' not found.")
        return

    try:
        with open(structure_file, "r") as file:
            directories = [line.strip() for line in file if line.strip()]

        for directory in directories:
            full_path = os.path.join(base_path, directory)
            os.makedirs(full_path, exist_ok=True)
            print(f"✅ Created: {full_path}")

        print("\n🎉 Directory structure created successfully!")
    except Exception as e:
        print(f"❌ Error creating directories: {e}")

# Run script from command line
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_repo_structure.py <structure_file> <base_path>")
    else:
        structure_file = sys.argv[1]
        base_path = sys.argv[2]
        create_directories_from_file(structure_file, base_path)
