import os
import datetime

def create_file_list(start_dir=".", output_file="file_list.txt"):
    """
    Creates a text file containing a listing of all files and directories
    within the specified directories ("backend", "front-end", "schemas") and their subdirectories,
    excluding the "node_modules" directory.

    Args:
        start_dir (str): The root directory to start the listing from. Defaults to the current directory.
        output_file (str): The name of the output text file. Defaults to "file_list.txt".
    """

    included_dirs = ["backend", "front-end", "schemas"]

    try:
        with open(output_file, "w") as f:
            f.write(f"File and Directory Listing - {datetime.datetime.now()}\n")
            f.write("-" * 40 + "\n")

            for top_level_dir in included_dirs:
                full_path = os.path.join(start_dir, top_level_dir)
                if not os.path.isdir(full_path):
                    print(f"Warning: Directory '{full_path}' not found. Skipping.")
                    continue  # Skip to the next directory if it doesn't exist

                for root, dirs, files in os.walk(full_path):
                    # Exclude "node_modules" directory
                    if "node_modules" in root.split(os.sep):  # Check if node_modules is in the path
                        continue

                    # Write the directory name
                    f.write(f"Directory: {root}\n")

                    # Write the files in the directory
                    for file in files:
                        f.write(f"  - File: {file}\n")

                    # Add a separator after each directory (optional)
                    f.write("-" * 20 + "\n")

        print(f"File list created successfully: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Get the directory from the user (optional - can be hardcoded if needed)
    dir_to_list = input("Enter the base directory to list (or press Enter for current directory): ")
    if not dir_to_list:
        dir_to_list = "." #Current Directory
    output_filename = input("Enter the output filename (or press Enter for 'file_list.txt'): ")
    if not output_filename:
        output_filename = "file_list.txt"
    create_file_list(dir_to_list, output_filename)