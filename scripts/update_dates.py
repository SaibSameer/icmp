#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import re

def add_last_updated(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if Last Updated already exists
    if "Last Updated:" in content:
        return False
    
    # Add Last Updated at the end of the file
    current_date = datetime.now().strftime("%Y-%m-%d")
    updated_content = f"{content.rstrip()}\n\nLast Updated: {current_date}\n"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    return True

def main():
    planning_dir = Path("planning")
    updated_files = []
    
    for md_file in planning_dir.glob("**/*.md"):
        if add_last_updated(md_file):
            updated_files.append(md_file)
    
    if updated_files:
        print(f"Added Last Updated date to {len(updated_files)} files:")
        for file in updated_files:
            print(f"  - {file}")
    else:
        print("No files needed updating.")

if __name__ == "__main__":
    main() 