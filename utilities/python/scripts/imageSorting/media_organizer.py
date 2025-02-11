import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import re
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from pymediainfo import MediaInfo
import time

"""
Script to organize photos and video files by year and month into subfolders.
Supported file types: .jpg, .jpeg, .mts, .mkv, .mp4, .mov

Features:
1. Select a directory containing photos and video files.
2. Rename files from yyymmdd_num.jpg format to yyyy-mm-dd_num.jpg format.
3. Use "Media Created" metadata to rename files if date structure is not found in filename.
4. Organize the files into subfolders based on the year and month extracted from the filenames.
5. Undo the organization by moving the files back to the main directory and removing the created subfolders.

Usage:
- Create an instance of MediaOrganizer and call the methods as needed.
"""

class MediaOrganizer:
    def __init__(self):
        self.pattern = re.compile(r"(\d{2})(\d{2})(\d{2})_(.+)\.(jpg|jpeg|mts|mkv|mp4|mov)", re.IGNORECASE)
        self.correct_pattern = re.compile(r"(\d{4})-(\d{2})-(\d{2})_(.+)\.(jpg|jpeg|mts|mkv|mp4|mov)", re.IGNORECASE)
        self.source_directory = None

    def select_directory(self):
        # Open a file dialog to select the directory
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        selected_directory = filedialog.askdirectory(title="Select Directory Containing Files")
        
        if selected_directory:
            self.source_directory = Path(selected_directory)
            print(f"Selected directory: {self.source_directory}")
        else:
            print("No directory selected.")

    def get_media_created_date(self, file_path):
        try:
            if file_path.suffix.lower() in [".jpg", ".jpeg"]:
                with Image.open(file_path) as image:
                    exif_data = image._getexif()
                    if exif_data is not None:
                        for tag, value in exif_data.items():
                            decoded = TAGS.get(tag, tag)
                            if decoded == "DateTimeOriginal":
                                return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
            else:
                parser = createParser(str(file_path))
                if parser:
                    try:
                        metadata = extractMetadata(parser)
                        if metadata:
                            for data in metadata.exportPlaintext():
                                if "Creation date" in data:
                                    date_str = data.split(": ")[-1].strip()
                                    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    finally:
                        parser.close()
                media_info = MediaInfo.parse(file_path)
                for track in media_info.tracks:
                    if track.track_type == "General" and track.recorded_date:
                        return datetime.strptime(track.recorded_date, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"Error extracting date from {file_path.name}: {e}")
        return None

    def rename_files(self):
        if not self.source_directory:
            print("No directory selected.")
            return
        
        for file in self.source_directory.iterdir():
            if file.is_file():
                new_name = None

                # Skip files that already have the correct structure
                if self.correct_pattern.match(file.name):
                    continue

                match = self.pattern.match(file.name)
                if match:
                    year = f"20{match.group(1)}"
                    month = match.group(2)
                    day = match.group(3)
                    rest = match.group(4)
                    extension = match.group(5).lower()
                    new_name = f"{year}-{month}-{day}_{rest}.{extension}"
                else:
                    media_created_date = self.get_media_created_date(file)
                    if media_created_date:
                        new_name = media_created_date.strftime(f"%Y-%m-%d_{file.stem}.{file.suffix.lower()[1:]}")

                if new_name:
                    new_file_path = self.source_directory / new_name

                    # Retry mechanism for renaming files
                    for attempt in range(5):
                        try:
                            file.rename(new_file_path)
                            print(f"Renamed {file.name} to {new_name}")
                            break
                        except PermissionError:
                            print(f"PermissionError: Retrying renaming {file.name} to {new_name} (Attempt {attempt + 1}/5)")
                            time.sleep(1)
                    else:
                        print(f"Failed to rename {file.name} after 5 attempts.")

    def organize_files_by_month(self):
        if not self.source_directory:
            print("No directory selected.")
            return

        for file in self.source_directory.iterdir():
            if file.is_file() and file.suffix.lower() in [".jpg", ".jpeg", ".mts", ".mkv", ".mp4", ".mov"]:
                # Extract the year and month from the filename
                year = file.stem[:4]
                year_month = file.stem[:7].replace("-", "_")
                # Create the year directory
                year_directory = self.source_directory / year
                year_directory.mkdir(exist_ok=True)
                # Create the month directory within the year directory
                month_directory = year_directory / year_month
                month_directory.mkdir(exist_ok=True)
                # Move the file to the month directory
                shutil.move(str(file), str(month_directory / file.name))

    def undo_organize_files(self):
        if not self.source_directory:
            print("No directory selected.")
            return
        
        for year_dir in self.source_directory.iterdir():
            if year_dir.is_dir():
                for month_dir in year_dir.iterdir():
                    if month_dir.is_dir():
                        for file in month_dir.iterdir():
                            if file.is_file():
                                # Move the file back to the main directory
                                shutil.move(str(file), str(self.source_directory / file.name))
                        # Remove the empty month directory
                        month_dir.rmdir()
                # Remove the empty year directory
                year_dir.rmdir()

    def select_directory_and_rename_files(self):
        self.select_directory()
        self.rename_files()

# Example usage:
# organizer = MediaOrganizer()
# organizer.select_directory()
# organizer.organize_files_by_month()  # To organize files
# organizer.undo_organize_files()  # To undo the organization
# organizer.rename_files()  # To rename files
