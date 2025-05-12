#!/usr/bin/env python3
from pathlib import Path
import re

def analyze_headings(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    heading_issues = []
    prev_level = 0
    
    for i, line in enumerate(lines, 1):
        if line.startswith('#'):
            current_level = len(re.match(r'^#+', line).group())
            if current_level - prev_level > 1 and prev_level != 0:
                heading_issues.append({
                    'line': i,
                    'content': line.strip(),
                    'current_level': current_level,
                    'prev_level': prev_level
                })
            prev_level = current_level
    
    return heading_issues

def main():
    planning_dir = Path("planning")
    files_with_issues = {}
    
    for md_file in planning_dir.glob("**/*.md"):
        issues = analyze_headings(md_file)
        if issues:
            files_with_issues[md_file] = issues
    
    if files_with_issues:
        print("\nFiles with heading hierarchy issues:")
        for file, issues in files_with_issues.items():
            print(f"\n{file}:")
            for issue in issues:
                print(f"  Line {issue['line']}: {issue['content']}")
                print(f"    - Current level: {issue['current_level']}")
                print(f"    - Previous level: {issue['prev_level']}")
                print(f"    - Suggested fix: Change to level {issue['prev_level'] + 1}")
    else:
        print("No heading hierarchy issues found.")

if __name__ == "__main__":
    main() 