import os
import re
import hashlib
from datetime import datetime
import argparse
import sys
import time
import os.path

def restore_files(archive_file, output_dir):
    """
    Restores files from an archive file, recreating the original directory structure.

    Args:
        archive_file (str): Path to the archive file.
        output_dir (str): Root directory for restoring files, recreating structure from archive.
    """
    restored_count = 0
    failed_count = 0
    hash_mismatches = []

    try:
        with open(archive_file, 'r', encoding='utf-8') as f:
            archive_content = f.read()
    except FileNotFoundError:
        print(f"Error: Archive file not found: {archive_file}")
        return
    except Exception as e:
        print(f"Error: Failed to read archive file: {e}")
        return

    # Regular expression to capture file metadata and content
    file_pattern = re.compile(
        r"================================================================================\n"
        r"File: (.*)\n"
        r"Path: (.*)\n"
        r"Size: (.*)\n"
        r"Modified: (.*)\n"
        r"Created: (.*)\n"
        r"Hash: (.*)\n"
        r"Lines: (.*)\n"
        r"================================================================================\n"
        r"([\s\S]*?)(?=(?:\n================================================================================|\Z))"
    )

    for match in file_pattern.finditer(archive_content):
        filename = match.group(1).strip()  # Extract filename, strip whitespace
        original_path = match.group(2).strip() # Extract original path, strip whitespace
        try:
            size = int(match.group(3))
            modified_str = match.group(4).strip()
            created_str = match.group(5).strip()
            expected_hash = match.group(6).strip()
            content = match.group(8).strip()  # Extract content, strip whitespace

            # Sanitize the path (VERY IMPORTANT FOR SECURITY!)

            # Remove the ".\" prefix if present
            if original_path.startswith(".\\"):
                original_path = original_path[2:]

             # Use os.path.normpath to handle different path styles
            original_path = os.path.normpath(original_path)

            # Create the restored file path WITHOUT creating directories.
            restored_file_path = os.path.join(output_dir, original_path)

            # Create necessary directories
            try:
                os.makedirs(os.path.dirname(restored_file_path), exist_ok=True)
                print(f"Created directory or verified: {os.path.dirname(restored_file_path)}")
            except Exception as e:
                print(f"Error creating directory: {e}")
                failed_count += 1
                continue

            # Normalize line endings before writing content
            content = content.replace('\r\n', '\n').replace('\n', os.linesep)

            # Write the content to the restored file
            try:
                with open(restored_file_path, 'w', encoding='utf-8', newline='') as outfile:
                    outfile.write(content)
                print(f"Successfully wrote file: {filename} to {restored_file_path}")
            except Exception as e:
                print(f"Error writing to file {filename}: {e}")
                failed_count += 1
                continue

            # Verify the hash (optional but recommended)
            try:
                with open(restored_file_path, 'r', encoding='utf-8') as infile:
                    restored_content = infile.read()
                #removing line endings before hashing
                restored_content = restored_content.replace('\r\n', '\n').replace('\n', os.linesep)
                restored_hash = hashlib.sha256(restored_content.encode('utf-8')).hexdigest()

                if restored_hash != expected_hash:
                    hash_mismatches.append(filename)
                    print(f"Warning: Hash mismatch for {filename}")
            except Exception as e:
                print(f"Error verifying hash for {filename}: {e}")
                failed_count += 1
                continue

            restored_count += 1

        except Exception as e:
            print(f"Error processing entry for {filename}: {e}")
            failed_count += 1

    print(f"\n=== RESTORATION SUMMARY ===")
    print(f"Files restored: {restored_count}")
    print(f"Files failed to restore: {failed_count}")
    if hash_mismatches:
        print(f"Hash mismatches: {', '.join(hash_mismatches)}")

    print ("Output folder contents:")
    print (os.listdir(output_dir))

def main():
    parser = argparse.ArgumentParser(description="Restore files from an archive.")
    parser.add_argument("-i", "--input", required=True, help="Path to the archive file.")
    parser.add_argument("-o", "--output", required=True, help="Path to which folder the files are to be restored")
    args = parser.parse_args()
    restore_files(args.input, args.output)


if __name__ == "__main__":
    main()