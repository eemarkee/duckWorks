import subprocess
import time
import pygetwindow as gw
import json
import argparse
import win32gui
import win32com.client


"""
Explorer Window Layout Manager
==============================
This script provides utilities for managing the layout of Windows File Explorer windows, 
including saving and restoring their positions, sizes, and directory paths.

Features:
---------
1. Save the layout of all open File Explorer windows to a JSON file.
2. Restore File Explorer windows to a saved layout, including size, position, and directory path.
3. Add a new window configuration to an existing layout.

Usage:
------
Run the script with the following command-line arguments:

1. Save the layout of all open File Explorer windows:
    ```
    python script_name.py --store layout.json
    ```

2. Load and restore a saved layout:
    ```
    python script_name.py --load layout.json
    ```

3. Add a new window to a saved layout:
    ```
    python script_name.py --store layout.json --add "C:\\Path\\To\\Folder" 100 100 800 600
    ```
    Parameters for `--add`:
        - `DIR`: The directory path to open in the File Explorer.
        - `X`, `Y`: The screen coordinates of the top-left corner of the window.
        - `WIDTH`, `HEIGHT`: The width and height of the window.

Dependencies:
-------------
- `subprocess`: Used for opening Explorer windows.
- `time`: Used for introducing delays to ensure Explorer windows are ready.
- `pygetwindow`: Provides window management utilities (optional for advanced features).
- `json`: For saving and loading layout data.
- `argparse`: For parsing command-line arguments.
- `win32gui`, `win32com.client`: Required for interacting with Windows GUI and File Explorer.

Example:
--------
Save the current Explorer window layout to `layout.json`:
    python script_name.py --store layout.json

Restore the saved layout from `layout.json`:
    python script_name.py --load layout.json

Add a specific window to the layout:
    python script_name.py --store layout.json --add "C:\\Users\\Documents" 100 100 1024 768
"""

# Function to open Explorer in a specific directory
def open_explorer(directory):
    subprocess.Popen(f'explorer \"{directory}\"')


# Function to move and resize a window by its handle
def move_and_resize_window(hwnd, x, y, width, height):
    win32gui.MoveWindow(hwnd, x, y, width, height, True)


# Function to get the directory of an Explorer window
def get_explorer_directories():
    shell = win32com.client.Dispatch("Shell.Application")
    directories = []
    for window in shell.Windows():
        if window.Name == "File Explorer" or "Explorer" in window.Name:
            try:
                path = window.Document.Folder.Self.Path
                hwnd = window.HWND
                rect = win32gui.GetWindowRect(hwnd)
                directories.append({
                    "directory": path,
                    "x": rect[0],
                    "y": rect[1],
                    "width": rect[2] - rect[0],
                    "height": rect[3] - rect[1],
                })
            except Exception as e:
                print(f"Error processing window: {e}")
    return directories


# Function to save all open Explorer windows to a JSON file
def save_open_windows_to_layout(layout_file):
    layout = {"windows": get_explorer_directories()}
    with open(layout_file, "w") as file:
        json.dump(layout, file)
    print(f"Layout saved to {layout_file}.")


# Function to load and apply a layout from a JSON file
def load_and_apply_layout(layout_file):
    with open(layout_file, "r") as file:
        layouts = json.load(file)
        for layout in layouts.get("windows", []):
            directory = layout["directory"]
            x, y, width, height = layout["x"], layout["y"], layout["width"], layout["height"]

            # Open the Explorer window
            open_explorer(directory)
            time.sleep(1)  # Wait for the window to open

            # Find the newly opened window and resize it
            shell = win32com.client.Dispatch("Shell.Application")
            for window in shell.Windows():
                if window.Document.Folder.Self.Path == directory:
                    hwnd = window.HWND
                    move_and_resize_window(hwnd, x, y, width, height)
                    break


# Main function to handle arguments
def main():
    parser = argparse.ArgumentParser(description="Manage Explorer window layouts.")
    parser.add_argument("--load", metavar="LAYOUT_FILE", help="Load and apply a window layout from a JSON file.")
    parser.add_argument("--store", metavar="LAYOUT_FILE", help="Store the current window layout to a JSON file.")
    parser.add_argument("--add", nargs=5, metavar=("DIR", "X", "Y", "WIDTH", "HEIGHT"),
                        help="Add a new window to the layout (used with --store).")

    args = parser.parse_args()

    if args.load:
        load_and_apply_layout(args.load)

    if args.store:
        if args.add:
            layout = {"windows": []}
            try:
                with open(args.store, "r") as file:
                    layout = json.load(file)
            except FileNotFoundError:
                pass  # No existing layout, create a new one

            dir_path, x, y, width, height = args.add
            layout["windows"].append({
                "directory": dir_path,
                "x": int(x),
                "y": int(y),
                "width": int(width),
                "height": int(height)
            })
            save_open_windows_to_layout(args.store)
        else:
            save_open_windows_to_layout(args.store)


if __name__ == "__main__":
    main()
    
