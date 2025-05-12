"""
Test Suite for Enhanced Data Extraction

This module provides comprehensive tests for the enhanced data extraction system,
including pattern learning, multi-strategy extraction, and monitoring capabilities.
"""

import unittest
from unittest.mock import Mock, patch
import json
from datetime import datetime, timedelta
import numpy as np
from backend.message_processing.services.data_extraction_service import DataExtractionService
from backend.message_processing.data_extraction.extractor import DataExtractor
from backend.message_processing.data_extraction.rule_validator import ExtractionRuleValidator
from backend.message_processing.data_extraction.processor import DataProcessor
from backend.message_processing.pattern_learning import PatternLearningService
from backend.monitoring.extraction_dashboard import ExtractionDashboard

class TestEnhancedDataExtraction(unittest.TestCase):
    """Test cases for EnhancedDataExtraction class."""
    
    def setUp(self):
        """Set up test environment."""
        self.db_pool = Mock()
        self.llm_service = Mock()
        self.extraction_service = DataExtractionService(self.db_pool, self.llm_service)
        
        # Sample template
        self.template = {
            'template_id': 'test_template',
            'patterns': {
                'amount': r'\$(\d+\.?\d*)',
                'date': r'(\d{2}/\d{2}/\d{4})'
            },
            'business_rules': [
                {
                    'conditions': [
                        {'type': 'contains', 'value': 'payment'}
                    ],
                    'extract': {'type': 'payment'}
                }
            ],
            'categories': [
                {
                    'name': 'payment_type',
                    'keywords': ['credit', 'debit', 'cash']
                }
            ]
        }
        
        # Sample context
        self.context = {
            'message_content': 'Payment of $100.50 made on 01/01/2023 via credit card',
            'conversation_history': 'Previous message about payment',
            'user_preferences': {'preferred_currency': 'USD'}
        }
    
    def test_extract_with_patterns(self):
        """Test pattern-based extraction."""
        result = self.extraction_service._extract_with_patterns(
            self.context['message_content'],
            self.template
        )
        
        self.assertEqual(result['amount'], '100.50')
        self.assertEqual(result['date'], '01/01/2023')
    
    def test_extract_with_llm(self):
        """Test LLM-based extraction."""
        self.llm_service.generate.return_value = json.dumps({
            'amount': '100.50',
            'date': '01/01/2023',
            'payment_type': 'credit'
        })
        
        result = self.extraction_service._extract_with_llm(
            self.context['message_content'],
            self.template,
            self.context
        )
        
        self.assertEqual(result['amount'], '100.50')
        self.assertEqual(result['date'], '01/01/2023')
        self.assertEqual(result['payment_type'], 'credit')
    
    def test_extract_with_rules(self):
        """Test rule-based extraction."""
        result = self.extraction_service._extract_with_rules(
            self.context['message_content'],
            self.template
        )
        
        self.assertEqual(result['type'], 'payment')
    
    def test_extract_with_statistics(self):
        """Test statistical extraction."""
        result = self.extraction_service._extract_with_statistics(
            self.context['message_content'],
            self.template
        )
        
        self.assertEqual(result['payment_type'], 'credit')
        self.assertEqual(result['numerical_values'], [100.50])
    
    def test_combine_results(self):
        """Test result combination with confidence scoring."""
        results = [
            ('pattern', {'amount': '100.50', 'date': '01/01/2023'}),
            ('llm', {'amount': '100.50', 'date': '01/01/2023', 'payment_type': 'credit'}),
            ('rule', {'type': 'payment'}),
            ('statistical', {'payment_type': 'credit', 'numerical_values': [100.50]})
        ]
        
        combined = self.extraction_service._combine_results(
            results,
            self.context['message_content']
        )
        
        self.assertEqual(combined['amount'], '100.50')
        self.assertEqual(combined['date'], '01/01/2023')
        self.assertEqual(combined['payment_type'], 'credit')
        self.assertEqual(combined['type'], 'payment')
        self.assertIn('_confidence_scores', combined)
    
    def test_store_successful_pattern(self):
        """Test pattern storage."""
        result = {
            'amount': '100.50',
            'date': '01/01/2023',
            'payment_type': 'credit'
        }
        
        self.extraction_service._store_successful_pattern(
            self.context['message_content'],
            self.template,
            result
        )
        
        # Verify pattern was stored
        self.assertIn(
            self.extraction_service._create_pattern_signature(
                self.context['message_content'],
                self.template
            ),
            self.extraction_service.pattern_database
        )

class TestPatternLearningService(unittest.TestCase):
    """Test cases for PatternLearningService class."""
    
    def setUp(self):
        """Set up test environment."""
        self.db_pool = Mock()
        self.learning_service = PatternLearningService(self.db_pool)
        
        # Sample data
        self.message = "Payment of $100.50 made on 01/01/2023"
        self.template = {'template_id': 'test_template'}
        self.extracted_data = {
            'amount': '100.50',
            'date': '01/01/2023'
        }
    
    def test_learn_from_extraction(self):
        """Test learning from successful extraction."""
        self.learning_service.learn_from_extraction(
            self.message,
            self.template,
            self.extracted_data,
            success=True
        )
        
        # Verify cluster was created
        cluster_id = self.learning_service._get_cluster_id(
            self.message,
            self.template
        )
        self.assertIn(cluster_id, self.learning_service.pattern_clusters)
    
    def test_get_improved_patterns(self):
        """Test getting improved patterns."""
        # First learn from some extractions
        self.learning_service.learn_from_extraction(
            self.message,
            self.template,
            self.extracted_data,
            success=True
        )
        
        improved_patterns = self.learning_service.get_improved_patterns(
            self.template['template_id']
        )
        
        self.assertIsInstance(improved_patterns, dict)
    
    def test_add_feedback(self):
        """Test adding user feedback."""
        extraction_id = 'test_extraction'
        feedback = {
            'correct': True,
            'notes': 'Good extraction'
        }
        
        self.learning_service.add_feedback(extraction_id, feedback)
        
        self.assertIn(extraction_id, self.learning_service.feedback_history)
        self.assertEqual(
            self.learning_service.feedback_history[extraction_id][-1]['feedback'],
            feedback
        )

class TestExtractionDashboard(unittest.TestCase):
    """Test cases for ExtractionDashboard class."""
    
    def setUp(self):
        """Set up test environment."""
        self.db_pool = Mock()
        self.dashboard = ExtractionDashboard(self.db_pool)
        
        # Mock database cursor
        self.cursor = Mock()
        self.db_pool.getconn.return_value.cursor.return_value = self.cursor
    
    def test_get_overview_stats(self):
        """Test getting overview statistics."""
        # Mock database results
        self.cursor.fetchone.side_effect = [
            (100, 80, 20),  # Total extractions
            (50, 0.85, 40),  # Pattern statistics
            (10, 8, 2)  # Recent performance
        ]
        
        stats = self.dashboard.get_overview_stats()
        
        self.assertEqual(stats['total_extractions'], 100)
        self.assertEqual(stats['successful_extractions'], 80)
        self.assertEqual(stats['success_rate'], 0.8)
        self.assertEqual(stats['total_patterns'], 50)
        self.assertEqual(stats['avg_success_rate'], 0.85)
    
    def test_get_performance_trends(self):
        """Test getting performance trends."""
        # Mock database results
        dates = [
            datetime.now() - timedelta(days=i)
            for i in range(7)
        ]
        self.cursor.fetchall.return_value = [
            (date, 10, 8, 2)
            for date in dates
        ]
        
        trends = self.dashboard.get_performance_trends()
        
        self.assertIn('trend_data', trends)
        self.assertIn('trend_plot', trends)
        self.assertEqual(len(trends['trend_data']), 7)
    
    def test_get_pattern_analysis(self):
        """Test getting pattern analysis."""
        # Mock database results
        self.cursor.fetchall.return_value = [
            ('amount', 50, 0.9, 1.0, 0.8),
            ('date', 40, 0.85, 0.95, 0.75)
        ]
        
        analysis = self.dashboard.get_pattern_analysis()
        
        self.assertIn('pattern_stats', analysis)
        self.assertIn('pattern_plot', analysis)
        self.assertEqual(len(analysis['pattern_stats']), 2)
    
    def test_get_error_analysis(self):
        """Test getting error analysis."""
        # Mock database results
        self.cursor.fetchall.return_value = [
            ('pattern_not_found', 10),
            ('invalid_format', 5)
        ]
        
        analysis = self.dashboard.get_error_analysis()
        
        self.assertIn('error_stats', analysis)
        self.assertIn('error_plot', analysis)
        self.assertEqual(len(analysis['error_stats']), 2)
    
    def test_get_template_performance(self):
        """Test getting template performance."""
        # Mock database results
        self.cursor.fetchall.return_value = [
            ('template1', 'Test Template 1', 100, 80, 0.85),
            ('template2', 'Test Template 2', 50, 40, 0.8)
        ]
        
        performance = self.dashboard.get_template_performance()
        
        self.assertIn('template_stats', performance)
        self.assertIn('template_plot', performance)
        self.assertEqual(len(performance['template_stats']), 2)

if __name__ == '__main__':
    unittest.main() 