#!/usr/bin/env python3
from pathlib import Path
import re

def enforce_hierarchy(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    modified = False
    current_section = 0
    current_subsection = 0
    
    for i, line in enumerate(lines):
        if line.startswith('#'):
            current_level = len(re.match(r'^#+', line).group())
            heading_text = line[current_level:].strip()
            
            # Level 1: Main title (keep as is)
            if current_level == 1:
                current_section = 0
                current_subsection = 0
                continue
            
            # Level 2: Main sections (##)
            if re.match(r'^\d+\.', heading_text):
                current_section = int(re.match(r'^\d+', heading_text).group())
                current_subsection = 0
                lines[i] = '## ' + heading_text
                modified = True
            # Level 3: Subsections (###)
            elif current_level == 3:
                if current_section > 0:
                    current_subsection += 1
                    lines[i] = '### ' + heading_text
                    modified = True
                else:
                    lines[i] = '## ' + heading_text
                    modified = True
            # Level 4: Sub-subsections (####)
            elif current_level == 4:
                if current_section > 0:
                    lines[i] = '#### ' + heading_text
                    modified = True
                else:
                    lines[i] = '### ' + heading_text
                    modified = True
            # Any other level: convert to appropriate level
            else:
                if current_section > 0:
                    if current_subsection > 0:
                        lines[i] = '#### ' + heading_text
                    else:
                        lines[i] = '### ' + heading_text
                else:
                    lines[i] = '## ' + heading_text
                modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return True
    return False

def main():
    planning_dir = Path("planning")
    target_files = ['deployment.md', 'monitoring.md']
    fixed_files = []
    
    # Define the expected hierarchy
    print("\nEnforcing heading hierarchy:")
    print("Level 1 (#): Main title")
    print("Level 2 (##): Main sections (numbered)")
    print("Level 3 (###): Subsections")
    print("Level 4 (####): Sub-subsections")
    
    for file_name in target_files:
        file_path = planning_dir / file_name
        if file_path.exists():
            if enforce_hierarchy(file_path):
                fixed_files.append(file_name)
    
    if fixed_files:
        print("\nFixed heading hierarchy in the following files:")
        for file in fixed_files:
            print(f"  - {file}")
    else:
        print("No files needed fixing.")

if __name__ == "__main__":
    main() 