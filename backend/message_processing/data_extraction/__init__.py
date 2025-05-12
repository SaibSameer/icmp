"""
Data extraction package.

This package provides a modular system for data extraction, including
extraction rules, validation, and processing.
"""

from .extractor import DataExtractor
from .rule_validator import ExtractionRuleValidator
from .processor import DataProcessor

__all__ = ['DataExtractor', 'ExtractionRuleValidator', 'DataProcessor'] 