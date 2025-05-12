#!/usr/bin/env python3
from pathlib import Path
import re
from collections import defaultdict, Counter

def analyze_file_structure(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    structure = defaultdict(list)
    current_section = None
    
    for i, line in enumerate(lines, 1):
        if line.startswith('#'):
            level = len(re.match(r'^#+', line).group())
            text = line[level:].strip()
            
            # Check if it's a numbered section
            number_match = re.match(r'^\d+\.', text)
            if number_match:
                current_section = text
                structure['numbered_sections'].append({
                    'line': i,
                    'level': level,
                    'text': text
                })
            else:
                structure['headings'].append({
                    'line': i,
                    'level': level,
                    'text': text,
                    'section': current_section
                })
    
    return structure

def main():
    planning_dir = Path("planning")
    target_files = ['deployment.md', 'monitoring.md']
    
    print("\nAnalyzing heading structure in documentation files:")
    
    for file_name in target_files:
        file_path = planning_dir / file_name
        if file_path.exists():
            print(f"\n{file_name}:")
            structure = analyze_file_structure(file_path)
            
            print("\nNumbered Sections:")
            for section in structure['numbered_sections']:
                print(f"  Line {section['line']}: Level {section['level']} - {section['text']}")
            
            print("\nOther Headings:")
            for heading in structure['headings']:
                section_info = f" (in section: {heading['section']})" if heading['section'] else ""
                print(f"  Line {heading['line']}: Level {heading['level']} - {heading['text']}{section_info}")
            
            # Analyze heading patterns
            levels = [h['level'] for h in structure['headings']]
            if levels:
                level_counts = Counter(levels)
                print(f"\nHeading Level Analysis:")
                print(f"  Min level: {min(levels)}")
                print(f"  Max level: {max(levels)}")
                print(f"  Level distribution: {dict(level_counts)}")

if __name__ == "__main__":
    main() 