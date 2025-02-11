# use_media_organizer.py
from media_organizer import MediaOrganizer

def main():
    organizer = MediaOrganizer()
    
    while True:
        print("\nSelect an option:")
        print("1. Select directory")
        print("2. Organize files")
        print("3. Undo organization")
        print("4. Rename files")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            organizer.select_directory()
        elif choice == '2':
            organizer.organize_files_by_month()
        elif choice == '3':
            organizer.undo_organize_files()
        elif choice == '4':
            organizer.rename_files()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
