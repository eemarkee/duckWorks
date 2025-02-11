import os
import hashlib
import shutil
import json
import tkinter as tk
from tkinter import filedialog

def compare_file_contents(file_path_1, file_path_2):
    BLOCK_SIZE = 65536
    hash1 = hashlib.sha256()
    hash2 = hashlib.sha256()

    with open(file_path_1, "rb") as file1, open(file_path_2, "rb") as file2:
        while True:
            data1 = file1.read(BLOCK_SIZE)
            data2 = file2.read(BLOCK_SIZE)

            if not data1 and not data2:
                break

            hash1.update(data1)
            hash2.update(data2)

    return hash1.digest() == hash2.digest()


def find_identical_videos(directory, processed_files):
    file_sizes = {}
    duplicates = []

    for root, _, files in os.walk(directory):
        for filename in files:
            full_path = os.path.join(root, filename)

            # Skip processing files within the "duplicates" folder
            if not full_path.startswith(os.path.join(directory, "duplicates")):
                if os.path.isfile(full_path) and full_path not in processed_files:
                    file_size = os.path.getsize(full_path)

                    # Add the file to the processed_files set
                    processed_files.add(full_path)

                    if file_size in file_sizes:
                        file_path_1 = file_sizes[file_size]
                        file_path_2 = full_path

                        if compare_file_contents(file_path_1, file_path_2):
                            duplicates.append((file_path_1, file_path_2))
                    else:
                        file_sizes[file_size] = full_path

    return duplicates

def move_to_duplicates_folder(duplicates_list, duplicates_folder):
    if not os.path.exists(duplicates_folder):
        os.makedirs(duplicates_folder)

    for i, (file_path_1, file_path_2) in enumerate(duplicates_list, start=1):
        file_name_2 = os.path.basename(file_path_2)
        new_name_2 = f"{i}_{file_name_2}"

        new_path_2 = os.path.join(duplicates_folder, new_name_2)

        try:
            if file_path_1 != file_path_2:  # Move only duplicates, not the first occurrence
                shutil.move(file_path_2, new_path_2)
        except FileNotFoundError:
            print(f"Warning: Unable to move {file_path_2}")


def save_processed_files(processed_files, processed_file_path):
    with open(processed_file_path, "w") as file:
        json.dump(list(processed_files), file)

def load_processed_files(processed_file_path):
    if os.path.exists(processed_file_path):
        with open(processed_file_path, "r") as file:
            return set(json.load(file))
    return set()

def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select a folder")
    return folder_selected

# Example usage:
if __name__ == "__main__":
    directory_to_search = select_folder()
    if not directory_to_search:
        print("No folder selected. Exiting.")
        exit()

    processed_file_path = "processed_files.json"
    processed_files = load_processed_files(processed_file_path)

    # Find and move the duplicates (excluding first occurrences)
    duplicates_list = find_identical_videos(directory_to_search, processed_files)

    if duplicates_list:
        duplicates_folder = os.path.join(directory_to_search, "duplicates")
        move_to_duplicates_folder(duplicates_list, duplicates_folder)

        # Update the set of processed files
        processed_files.update(set(file_path for _, file_path in duplicates_list))
        save_processed_files(processed_files, processed_file_path)

        print(f"{len(duplicates_list)} sets of identical video files were moved to the duplicates folder.")
    else:
        print("No identical video files found in the directory and its subdirectories.")