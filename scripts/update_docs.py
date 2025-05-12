#!/usr/bin/env python3
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentationUpdater:
    def __init__(self, planning_dir: str = "planning"):
        self.planning_dir = Path(planning_dir).resolve()
        self.updated_files: Set[str] = set()
        self.fixed_links: Dict[str, List[str]] = {}
        
    def update_all(self) -> None:
        """Update all documentation files."""
        logger.info("Starting documentation update...")
        
        # Update last modified dates
        self._update_dates()
        
        # Update version numbers
        self._update_versions()
        
        # Update cross-references
        self._update_references()
        
        # Report results
        self._report_results()
    
    def _update_dates(self) -> None:
        """Update last modified dates in documentation files."""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        for file_path in self.planning_dir.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Update last modified date
                if "Last Updated:" in content:
                    content = re.sub(
                        r'Last Updated: \d{4}-\d{2}-\d{2}',
                        f'Last Updated: {current_date}',
                        content
                    )
                    self.updated_files.add(str(file_path.relative_to(self.planning_dir)))
                    
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
            except Exception as e:
                logger.error(f"Error updating {file_path}: {str(e)}")
    
    def _update_versions(self) -> None:
        """Update version numbers in documentation files."""
        for file_path in self.planning_dir.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Update version number if present
                if "Version:" in content:
                    content = re.sub(
                        r'Version: \d+\.\d+',
                        lambda m: f'Version: {self._increment_version(m.group(0))}',
                        content
                    )
                    self.updated_files.add(str(file_path.relative_to(self.planning_dir)))
                    
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
            except Exception as e:
                logger.error(f"Error updating {file_path}: {str(e)}")
    
    def _increment_version(self, version_str: str) -> str:
        """Increment version number."""
        version = version_str.split(': ')[1]
        major, minor = map(int, version.split('.'))
        return f"{major}.{minor + 1}"
    
    def _update_references(self) -> None:
        """Update cross-references between documentation files."""
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        
        for file_path in self.planning_dir.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content
                for match in link_pattern.finditer(content):
                    link_text, link_url = match.groups()
                    new_link = self._update_link(link_text, link_url, str(file_path))
                    if new_link:
                        new_content = new_content.replace(match.group(0), new_link)
                
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    self.updated_files.add(str(file_path.relative_to(self.planning_dir)))
            except Exception as e:
                logger.warning(f"Error updating references in {file_path}: {str(e)}")
    
    def _update_link(self, link_text, link_url, current_file_path):
        """Update a single link, handling relative paths and anchors."""
        # Skip external links and anchor-only links
        if link_url.startswith(('http://', 'https://', '#')):
            return None
            
        try:
            # Resolve the target path relative to the current file
            current_dir = Path(current_file_path).parent
            target_path = (current_dir / link_url).resolve()
            
            # Check if target exists
            if target_path.exists():
                # Get relative path from planning directory
                rel_path = target_path.relative_to(self.planning_dir)
                new_link = f"[{link_text}]({rel_path})"
                self.fixed_links[current_file_path] = self.fixed_links.get(current_file_path, []) + [new_link]
                return new_link
            else:
                # Try to find the target in the planning directory
                for root, _, files in os.walk(self.planning_dir):
                    for file in files:
                        if file.endswith('.md'):
                            if Path(file).stem == Path(link_url).stem:
                                rel_path = Path(root).relative_to(self.planning_dir) / file
                                new_link = f"[{link_text}]({rel_path})"
                                self.fixed_links[current_file_path] = self.fixed_links.get(current_file_path, []) + [new_link]
                                return new_link
        except Exception as e:
            logger.warning(f"Error updating link in {current_file_path}: {str(e)}")
        
        return None
    
    def _report_results(self) -> None:
        """Report update results."""
        if self.updated_files:
            logger.info("\nUpdated files:")
            for file in sorted(self.updated_files):
                logger.info(f"  - {file}")
                
        if self.fixed_links:
            logger.info("\nFixed links:")
            for file, links in sorted(self.fixed_links.items()):
                logger.info(f"  In {file}:")
                for link in links:
                    logger.info(f"    - {link}")
        else:
            logger.info("No files were updated.")

def main():
    updater = DocumentationUpdater()
    updater.update_all()
    logger.info("Documentation update completed!")

if __name__ == "__main__":
    main() 