import os

def show_structure(start_path='.'):
    for root, dirs, files in os.walk(start_path):
        # Get relative path from start_path
        relative_root = os.path.relpath(root, start_path)
        indent_level = relative_root.count(os.sep)
        indent = '    ' * indent_level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = '    ' * (indent_level + 1)
        for f in files:
            print(f"{sub_indent}{f}")

if __name__ == "__main__":
    # By default, . means "current directory"
    print(f"Walking folder: {os.path.abspath('.')}")
    show_structure('.')
