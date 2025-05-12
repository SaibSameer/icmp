#!/usr/bin/env python3
from pathlib import Path
import re

def fix_complex_headings(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    modified = False
    section_stack = []
    current_section = 0
    
    for i, line in enumerate(lines):
        if line.startswith('#'):
            current_level = len(re.match(r'^#+', line).group())
            heading_text = line[current_level:].strip()
            
            # Skip if it's a main title (h1)
            if current_level == 1:
                section_stack = [1]
                current_section = 1
                continue
            
            # Handle numbered sections (e.g., "1. Section Name")
            if re.match(r'^\d+\.', heading_text):
                current_section = int(re.match(r'^\d+', heading_text).group())
                lines[i] = '## ' + heading_text
                section_stack = [1, 2]
                modified = True
                continue
            
            # Handle subsections
            if current_level > 2:
                # If we're in a numbered section
                if current_section > 0:
                    if current_level == 3:
                        lines[i] = '### ' + heading_text
                        section_stack = [1, 2, 3]
                    elif current_level == 4:
                        lines[i] = '#### ' + heading_text
                        section_stack = [1, 2, 3, 4]
                    modified = True
                # If we're not in a numbered section
                else:
                    if current_level > 2:
                        lines[i] = '## ' + heading_text
                        section_stack = [1, 2]
                        modified = True
            else:
                section_stack.append(current_level)
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return True
    return False

def main():
    planning_dir = Path("planning")
    target_files = ['deployment.md', 'monitoring.md']
    fixed_files = []
    
    for file_name in target_files:
        file_path = planning_dir / file_name
        if file_path.exists():
            if fix_complex_headings(file_path):
                fixed_files.append(file_name)
    
    if fixed_files:
        print("\nFixed complex heading hierarchy in the following files:")
        for file in fixed_files:
            print(f"  - {file}")
    else:
        print("No files needed fixing.")

if __name__ == "__main__":
    main() 