#!/usr/bin/env python3
import os
import re
from datetime import datetime
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
import sys

class DocumentationChecker:
    def __init__(self, planning_dir="planning"):
        self.planning_dir = Path(planning_dir)
        self.broken_links = []
        self.outdated_files = []
        self.missing_updates = []
        
    def check_all(self):
        """Run all documentation checks"""
        print("Starting documentation health check...")
        self.check_broken_links()
        self.check_last_updates()
        self.check_formatting()
        self.report_results()
        
    def check_broken_links(self):
        """Check for broken links in markdown files"""
        for md_file in self.planning_dir.glob("**/*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Convert markdown to HTML to parse links
                html = markdown.markdown(content)
                soup = BeautifulSoup(html, 'html.parser')
                
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href and not href.startswith(('http://', 'https://')):
                        target_path = self.planning_dir / href
                        if not target_path.exists():
                            self.broken_links.append(f"{md_file}: {href}")
    
    def check_last_updates(self):
        """Check for files that haven't been updated recently"""
        current_date = datetime.now()
        for md_file in self.planning_dir.glob("**/*.md"):
            last_modified = datetime.fromtimestamp(md_file.stat().st_mtime)
            days_since_update = (current_date - last_modified).days
            
            if days_since_update > 30:  # Files not updated in 30 days
                self.outdated_files.append(f"{md_file}: {days_since_update} days old")
    
    def check_formatting(self):
        """Check for basic formatting consistency"""
        for md_file in self.planning_dir.glob("**/*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for missing last updated date
                if not re.search(r"Last Updated:", content):
                    self.missing_updates.append(f"{md_file}: Missing last updated date")
                
                # Check for proper heading hierarchy
                lines = content.split('\n')
                prev_level = 0
                for line in lines:
                    if line.startswith('#'):
                        current_level = len(re.match(r'^#+', line).group())
                        if current_level - prev_level > 1:
                            self.missing_updates.append(f"{md_file}: Inconsistent heading hierarchy")
                        prev_level = current_level
    
    def report_results(self):
        """Print the results of all checks"""
        print("\n=== Documentation Health Check Results ===")
        
        if self.broken_links:
            print("\nBroken Links Found:")
            for link in self.broken_links:
                print(f"  - {link}")
        
        if self.outdated_files:
            print("\nOutdated Files:")
            for file in self.outdated_files:
                print(f"  - {file}")
        
        if self.missing_updates:
            print("\nFormatting Issues:")
            for issue in self.missing_updates:
                print(f"  - {issue}")
        
        if not any([self.broken_links, self.outdated_files, self.missing_updates]):
            print("\nAll checks passed! Documentation is in good health.")

if __name__ == "__main__":
    checker = DocumentationChecker()
    checker.check_all() 