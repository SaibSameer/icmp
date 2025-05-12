#!/usr/bin/env python3
from pathlib import Path
import re

def fix_headings(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    prev_level = 0
    modified = False
    
    for i, line in enumerate(lines):
        if line.startswith('#'):
            current_level = len(re.match(r'^#+', line).group())
            if current_level - prev_level > 1 and prev_level != 0:
                # Fix the heading level
                new_level = prev_level + 1
                lines[i] = '#' * new_level + line[current_level:]
                modified = True
            prev_level = current_level
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return True
    return False

def main():
    planning_dir = Path("planning")
    fixed_files = []
    
    # Files with known issues
    target_files = [
        'code_patterns.md',
        'database_migration_guide.md',
        'deployment.md',
        'environment_variables.md',
        'monitoring.md',
        'troubleshooting.md'
    ]
    
    for file_name in target_files:
        file_path = planning_dir / file_name
        if file_path.exists():
            if fix_headings(file_path):
                fixed_files.append(file_name)
    
    if fixed_files:
        print("\nFixed heading hierarchy in the following files:")
        for file in fixed_files:
            print(f"  - {file}")
    else:
        print("No files needed fixing.")

if __name__ == "__main__":
    main() 