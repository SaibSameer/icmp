#!/usr/bin/env python3
from pathlib import Path
import re

def is_code_block(line):
    """Check if the line is likely a code block or command"""
    code_indicators = [
        '```', '#!/', '.py', '.sh', '.yml', '.ini', '.conf',
        'sudo', 'pip', 'python', 'git', 'cp', 'mv', 'rm',
        'postgres=#', 'mysql>', 'redis>', '!/bin/bash',
        'Check ', 'Install ', 'Configure ', 'Update ',
        'backend/', '/etc/', '/usr/local/bin/'
    ]
    return any(indicator in line for indicator in code_indicators)

def fix_document_structure(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    modified = False
    current_section = None
    in_code_block = False
    
    for i, line in enumerate(lines):
        # Track code blocks
        if line.startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            continue
            
        if line.startswith('#'):
            current_level = len(re.match(r'^#+', line).group())
            heading_text = line[current_level:].strip()
            
            # Skip if it's a code block or command
            if is_code_block(heading_text):
                continue
            
            # Handle main document title
            if heading_text.endswith(('Guide', 'Setup Guide')):
                if current_level != 1:
                    lines[i] = '# ' + heading_text
                    modified = True
                continue
            
            # Handle numbered sections
            if re.match(r'^\d+\.', heading_text):
                current_section = heading_text
                if current_level != 2:
                    lines[i] = '## ' + heading_text
                    modified = True
            # Handle main sections
            elif current_level == 1:
                lines[i] = '## ' + heading_text
                modified = True
            # Handle subsections
            elif current_level > 2:
                if current_section:
                    lines[i] = '### ' + heading_text
                    modified = True
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
    
    print("\nFixing document structure while maintaining existing organization:")
    print("1. Preserving main document titles as level 1 (#)")
    print("2. Preserving numbered sections as level 2 (##)")
    print("3. Converting all subsections to level 3 (###)")
    print("4. Preserving code blocks and commands")
    
    for file_name in target_files:
        file_path = planning_dir / file_name
        if file_path.exists():
            if fix_document_structure(file_path):
                fixed_files.append(file_name)
    
    if fixed_files:
        print("\nFixed document structure in the following files:")
        for file in fixed_files:
            print(f"  - {file}")
    else:
        print("No files needed fixing.")

if __name__ == "__main__":
    main() 