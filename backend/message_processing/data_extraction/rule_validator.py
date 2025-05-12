"""
Extraction rule validator system.

This module handles the validation of data extraction rules,
ensuring they are properly formatted and contain all required fields.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Set, Union
from ..errors import DataExtractionError

logger = logging.getLogger(__name__)

class ExtractionRuleValidator:
    """Validates data extraction rules."""
    
    def __init__(self):
        """Initialize the rule validator."""
        self.required_fields = {
            'regex': {'pattern', 'field'},
            'keyword': {'keywords', 'field'},
            'pattern': {'pattern_type', 'field'},
            'custom': {'custom_logic', 'field'}
        }
        
    def validate_rule(
        self,
        rule: Dict[str, Any]
    ) -> bool:
        """Validate an extraction rule.
        
        Args:
            rule: Extraction rule to validate
            
        Returns:
            True if rule is valid
            
        Raises:
            DataExtractionError: If rule is invalid
        """
        try:
            # Check required fields
            method = rule.get('method', 'regex')
            if method not in self.required_fields:
                raise DataExtractionError(f"Unknown extraction method: {method}")
                
            required = self.required_fields[method]
            missing = required - set(rule.keys())
            if missing:
                raise DataExtractionError(f"Missing required fields for {method}: {missing}")
                
            # Validate method-specific fields
            if method == 'regex':
                self._validate_regex_rule(rule)
            elif method == 'keyword':
                self._validate_keyword_rule(rule)
            elif method == 'pattern':
                self._validate_pattern_rule(rule)
            elif method == 'custom':
                self._validate_custom_rule(rule)
                
            return True
            
        except DataExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error validating rule: {str(e)}")
            raise DataExtractionError(f"Failed to validate rule: {str(e)}")
            
    def _validate_regex_rule(
        self,
        rule: Dict[str, Any]
    ) -> None:
        """Validate a regex extraction rule.
        
        Args:
            rule: Regex extraction rule
            
        Raises:
            DataExtractionError: If rule is invalid
        """
        try:
            pattern = rule['pattern']
            
            # Check if pattern is a valid regex
            try:
                re.compile(pattern)
            except re.error as e:
                raise DataExtractionError(f"Invalid regex pattern: {str(e)}")
                
            # Check group field mappings
            for key in rule.keys():
                if key.startswith('group_') and key.endswith('_field'):
                    try:
                        group_num = int(key.split('_')[1])
                        if group_num < 1:
                            raise DataExtractionError(f"Invalid group number in {key}")
                    except ValueError:
                        raise DataExtractionError(f"Invalid group field mapping: {key}")
                        
        except Exception as e:
            logger.error(f"Error validating regex rule: {str(e)}")
            raise DataExtractionError(f"Regex rule validation failed: {str(e)}")
            
    def _validate_keyword_rule(
        self,
        rule: Dict[str, Any]
    ) -> None:
        """Validate a keyword extraction rule.
        
        Args:
            rule: Keyword extraction rule
            
        Raises:
            DataExtractionError: If rule is invalid
        """
        try:
            keywords = rule['keywords']
            
            # Check if keywords is a non-empty list
            if not isinstance(keywords, list):
                raise DataExtractionError("Keywords must be a list")
            if not keywords:
                raise DataExtractionError("Keywords list cannot be empty")
                
            # Check if all keywords are strings
            for keyword in keywords:
                if not isinstance(keyword, str):
                    raise DataExtractionError("All keywords must be strings")
                if not keyword.strip():
                    raise DataExtractionError("Keywords cannot be empty strings")
                    
        except Exception as e:
            logger.error(f"Error validating keyword rule: {str(e)}")
            raise DataExtractionError(f"Keyword rule validation failed: {str(e)}")
            
    def _validate_pattern_rule(
        self,
        rule: Dict[str, Any]
    ) -> None:
        """Validate a pattern extraction rule.
        
        Args:
            rule: Pattern extraction rule
            
        Raises:
            DataExtractionError: If rule is invalid
        """
        try:
            pattern_type = rule['pattern_type']
            
            # Check if pattern type is valid
            valid_types = {'email', 'phone', 'date', 'url', 'number'}
            if pattern_type not in valid_types:
                raise DataExtractionError(f"Invalid pattern type: {pattern_type}")
                
        except Exception as e:
            logger.error(f"Error validating pattern rule: {str(e)}")
            raise DataExtractionError(f"Pattern rule validation failed: {str(e)}")
            
    def _validate_custom_rule(
        self,
        rule: Dict[str, Any]
    ) -> None:
        """Validate a custom extraction rule.
        
        Args:
            rule: Custom extraction rule
            
        Raises:
            DataExtractionError: If rule is invalid
        """
        try:
            custom_logic = rule['custom_logic']
            
            # Check if custom logic is callable
            if not callable(custom_logic):
                raise DataExtractionError("Custom logic must be callable")
                
        except Exception as e:
            logger.error(f"Error validating custom rule: {str(e)}")
            raise DataExtractionError(f"Custom rule validation failed: {str(e)}")
            
    def validate_rules(
        self,
        rules: List[Dict[str, Any]]
    ) -> bool:
        """Validate multiple extraction rules.
        
        Args:
            rules: List of extraction rules
            
        Returns:
            True if all rules are valid
            
        Raises:
            DataExtractionError: If any rule is invalid
        """
        try:
            if not isinstance(rules, list):
                raise DataExtractionError("Rules must be a list")
            if not rules:
                raise DataExtractionError("Rules list cannot be empty")
                
            for rule in rules:
                self.validate_rule(rule)
                
            return True
            
        except DataExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error validating rules: {str(e)}")
            raise DataExtractionError(f"Failed to validate rules: {str(e)}")
            
    def get_required_fields(
        self,
        method: str
    ) -> Set[str]:
        """Get required fields for an extraction method.
        
        Args:
            method: Extraction method name
            
        Returns:
            Set of required field names
            
        Raises:
            DataExtractionError: If method is unknown
        """
        if method not in self.required_fields:
            raise DataExtractionError(f"Unknown extraction method: {method}")
            
        return self.required_fields[method].copy() 