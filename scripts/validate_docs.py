#!/usr/bin/env python3
import os
import re
from pathlib import Path
from typing import List, Dict, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentationValidator:
    def __init__(self, planning_dir: str = "planning"):
        self.planning_dir = Path(planning_dir)
        self.found_files: Set[str] = set()
        self.missing_files: Set[str] = set()
        self.broken_links: Dict[str, List[str]] = {}
        
    def validate_all(self) -> bool:
        """Validate all documentation files."""
        logger.info("Starting documentation validation...")
        
        # Find all markdown files
        self._find_all_files()
        
        # Validate each file
        for file_path in self.found_files:
            self._validate_file(file_path)
            
        # Report results
        self._report_results()
        
        return len(self.missing_files) == 0 and len(self.broken_links) == 0
    
    def _find_all_files(self) -> None:
        """Find all markdown files in the planning directory."""
        for file_path in self.planning_dir.rglob("*.md"):
            self.found_files.add(str(file_path.relative_to(self.planning_dir)))
    
    def _validate_file(self, file_path: str) -> None:
        """Validate a single documentation file."""
        full_path = self.planning_dir / file_path
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find all markdown links
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            
            for link_text, link_target in links:
                # Handle relative links
                if link_target.startswith('#'):
                    continue
                    
                # Handle external links
                if link_target.startswith(('http://', 'https://')):
                    continue
                    
                # Check if target file exists
                target_path = (full_path.parent / link_target).resolve()
                if not target_path.exists():
                    if file_path not in self.broken_links:
                        self.broken_links[file_path] = []
                    self.broken_links[file_path].append(link_target)
                    
        except Exception as e:
            logger.error(f"Error validating {file_path}: {str(e)}")
            self.missing_files.add(file_path)
    
    def _report_results(self) -> None:
        """Report validation results."""
        if self.missing_files:
            logger.warning("\nMissing files:")
            for file in sorted(self.missing_files):
                logger.warning(f"  - {file}")
                
        if self.broken_links:
            logger.warning("\nBroken links:")
            for file, links in sorted(self.broken_links.items()):
                logger.warning(f"  In {file}:")
                for link in links:
                    logger.warning(f"    - {link}")
                    
        if not self.missing_files and not self.broken_links:
            logger.info("All documentation files and links are valid!")

def main():
    validator = DocumentationValidator()
    success = validator.validate_all()
    
    if not success:
        logger.error("Documentation validation failed!")
        exit(1)
    else:
        logger.info("Documentation validation completed successfully!")

if __name__ == "__main__":
    main() 