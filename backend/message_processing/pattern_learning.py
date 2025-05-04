"""
Pattern Learning Service for Data Extraction

This module provides functionality to learn and improve extraction patterns
over time based on successful extractions and user feedback.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict

log = logging.getLogger(__name__)

class PatternLearningService:
    """
    Service for learning and improving extraction patterns over time.
    """
    
    def __init__(self, db_pool):
        self.db_pool = db_pool
        self.vectorizer = TfidfVectorizer()
        self.pattern_clusters = {}
        self.feedback_history = defaultdict(list)
        self.learning_rate = 0.1  # Rate at which patterns are updated
        
    def learn_from_extraction(self, message: str, template: Dict[str, Any], 
                            extracted_data: Dict[str, Any], success: bool = True):
        """
        Learn from a successful or failed extraction.
        
        Args:
            message: The message that was processed
            template: The template used for extraction
            extracted_data: The data that was extracted
            success: Whether the extraction was successful
        """
        try:
            # Get or create pattern cluster
            cluster_id = self._get_cluster_id(message, template)
            
            # Update pattern statistics
            self._update_pattern_stats(cluster_id, message, template, extracted_data, success)
            
            # Update pattern weights
            self._update_pattern_weights(cluster_id, success)
            
            # Store in database
            self._store_learning_data(cluster_id, message, template, extracted_data, success)
            
        except Exception as e:
            log.error(f"Error in pattern learning: {str(e)}")
    
    def get_improved_patterns(self, template_id: str) -> Dict[str, Any]:
        """
        Get improved patterns for a template based on learning.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary of improved patterns
        """
        try:
            # Get successful patterns for this template
            successful_patterns = self._get_successful_patterns(template_id)
            
            # Generate improved patterns
            improved_patterns = self._generate_improved_patterns(successful_patterns)
            
            return improved_patterns
            
        except Exception as e:
            log.error(f"Error getting improved patterns: {str(e)}")
            return {}
    
    def add_feedback(self, extraction_id: str, feedback: Dict[str, Any]):
        """
        Add user feedback about an extraction.
        
        Args:
            extraction_id: ID of the extraction
            feedback: Dictionary containing feedback data
        """
        try:
            # Store feedback
            self.feedback_history[extraction_id].append({
                'feedback': feedback,
                'timestamp': datetime.now()
            })
            
            # Update patterns based on feedback
            self._update_patterns_from_feedback(extraction_id, feedback)
            
        except Exception as e:
            log.error(f"Error adding feedback: {str(e)}")
    
    def _get_cluster_id(self, message: str, template: Dict[str, Any]) -> str:
        """Get or create a cluster ID for similar messages."""
        # Vectorize message
        message_vector = self.vectorizer.fit_transform([message])
        
        # Find similar clusters
        for cluster_id, cluster_data in self.pattern_clusters.items():
            if cluster_data['template_id'] == template.get('template_id'):
                # Calculate similarity with cluster center
                similarity = np.dot(message_vector, cluster_data['center'].T).mean()
                if similarity > 0.7:  # Similarity threshold
                    return cluster_id
        
        # Create new cluster
        new_cluster_id = f"cluster_{len(self.pattern_clusters)}"
        self.pattern_clusters[new_cluster_id] = {
            'template_id': template.get('template_id'),
            'center': message_vector,
            'messages': [message],
            'success_count': 0,
            'total_count': 0,
            'patterns': {}
        }
        
        return new_cluster_id
    
    def _update_pattern_stats(self, cluster_id: str, message: str, 
                            template: Dict[str, Any], extracted_data: Dict[str, Any], 
                            success: bool):
        """Update pattern statistics for a cluster."""
        cluster = self.pattern_clusters[cluster_id]
        cluster['total_count'] += 1
        
        if success:
            cluster['success_count'] += 1
            
            # Update patterns
            for field, value in extracted_data.items():
                if field not in cluster['patterns']:
                    cluster['patterns'][field] = {
                        'values': [],
                        'weights': {},
                        'success_rate': 0.0
                    }
                
                pattern_data = cluster['patterns'][field]
                pattern_data['values'].append(value)
                
                # Update weights based on value frequency
                if value not in pattern_data['weights']:
                    pattern_data['weights'][value] = 1
                else:
                    pattern_data['weights'][value] += 1
                
                # Update success rate
                pattern_data['success_rate'] = (
                    pattern_data.get('success_rate', 0) * 0.9 +  # Decay old rate
                    (1 if success else 0) * 0.1  # Add new result
                )
    
    def _update_pattern_weights(self, cluster_id: str, success: bool):
        """Update pattern weights based on success/failure."""
        cluster = self.pattern_clusters[cluster_id]
        
        for field, pattern_data in cluster['patterns'].items():
            # Adjust weights based on success
            weight_adjustment = self.learning_rate * (1 if success else -1)
            
            for value in pattern_data['weights']:
                pattern_data['weights'][value] *= (1 + weight_adjustment)
            
            # Normalize weights
            total_weight = sum(pattern_data['weights'].values())
            if total_weight > 0:
                pattern_data['weights'] = {
                    k: v/total_weight 
                    for k, v in pattern_data['weights'].items()
                }
    
    def _store_learning_data(self, cluster_id: str, message: str, 
                           template: Dict[str, Any], extracted_data: Dict[str, Any], 
                           success: bool):
        """Store learning data in the database."""
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            
            # Store extraction result
            cursor.execute(
                """
                INSERT INTO extraction_results 
                (cluster_id, message, template_id, extracted_data, success, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (cluster_id, message, template.get('template_id'), 
                 json.dumps(extracted_data), success, datetime.now())
            )
            
            # Store pattern data
            for field, value in extracted_data.items():
                if field not in self.pattern_clusters[cluster_id]['patterns']:
                    self.pattern_clusters[cluster_id]['patterns'][field] = {
                        'values': [],
                        'weights': {},
                        'success_rate': 0.0
                    }
                
                pattern_data = self.pattern_clusters[cluster_id]['patterns'][field]
                pattern_data['values'].append(value)
                
                # Update weights based on value frequency
                if value not in pattern_data['weights']:
                    pattern_data['weights'][value] = 1
                else:
                    pattern_data['weights'][value] += 1
                
                # Update success rate
                pattern_data['success_rate'] = (
                    pattern_data.get('success_rate', 0) * 0.9 +  # Decay old rate
                    (1 if success else 0) * 0.1  # Add new result
                )
                
                # Store in database
                cursor.execute(
                    """
                    INSERT INTO pattern_data 
                    (cluster_id, field, pattern_values, weights, success_rate)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (cluster_id, field) 
                    DO UPDATE SET 
                        pattern_values = %s,
                        weights = %s,
                        success_rate = %s
                    """,
                    (cluster_id, field, 
                     json.dumps(pattern_data['values']),
                     json.dumps(pattern_data['weights']),
                     pattern_data['success_rate'],
                     json.dumps(pattern_data['values']),
                     json.dumps(pattern_data['weights']),
                     pattern_data['success_rate'])
                )
            
            conn.commit()
            
        except Exception as e:
            log.error(f"Error storing learning data: {str(e)}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def _get_successful_patterns(self, template_id: str) -> List[Dict[str, Any]]:
        """Get successful patterns for a template."""
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT cluster_id, field, pattern_values, weights, success_rate
                FROM pattern_data
                WHERE cluster_id IN (
                    SELECT cluster_id 
                    FROM extraction_results 
                    WHERE template_id = %s AND success = true
                )
                AND success_rate > 0.7
                """,
                (template_id,)
            )
            
            patterns = []
            for row in cursor.fetchall():
                patterns.append({
                    'cluster_id': row[0],
                    'field': row[1],
                    'values': json.loads(row[2]),
                    'weights': json.loads(row[3]),
                    'success_rate': row[4]
                })
            
            return patterns
            
        except Exception as e:
            log.error(f"Error getting successful patterns: {str(e)}")
            return []
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def _generate_improved_patterns(self, successful_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate improved patterns from successful extractions."""
        improved_patterns = {}
        
        # Group patterns by field
        field_patterns = defaultdict(list)
        for pattern in successful_patterns:
            field_patterns[pattern['field']].append(pattern)
        
        # Generate improved patterns for each field
        for field, patterns in field_patterns.items():
            # Combine patterns with high success rates
            combined_pattern = self._combine_patterns(patterns)
            if combined_pattern:
                improved_patterns[field] = combined_pattern
        
        return improved_patterns
    
    def _combine_patterns(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine multiple patterns into an improved pattern."""
        if not patterns:
            return None
        
        # Calculate weighted average of success rates
        total_weight = sum(p['success_rate'] for p in patterns)
        if total_weight == 0:
            return None
        
        # Combine values based on weights
        combined_values = defaultdict(float)
        for pattern in patterns:
            weight = pattern['success_rate'] / total_weight
            for value, value_weight in pattern['weights'].items():
                combined_values[value] += value_weight * weight
        
        # Normalize weights
        total_weight = sum(combined_values.values())
        if total_weight > 0:
            combined_values = {
                k: v/total_weight 
                for k, v in combined_values.items()
            }
        
        return {
            'values': list(combined_values.keys()),
            'weights': combined_values,
            'success_rate': sum(p['success_rate'] for p in patterns) / len(patterns)
        }
    
    def _update_patterns_from_feedback(self, extraction_id: str, feedback: Dict[str, Any]):
        """Update patterns based on user feedback."""
        try:
            # Get the extraction result
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT cluster_id, message, template_id, extracted_data
                FROM extraction_results
                WHERE extraction_id = %s
                """,
                (extraction_id,)
            )
            
            row = cursor.fetchone()
            if not row:
                return
            
            cluster_id, message, template_id, extracted_data = row
            extracted_data = json.loads(extracted_data)
            
            # Update patterns based on feedback
            for field, feedback_data in feedback.items():
                if field in extracted_data:
                    # Adjust pattern weights
                    if feedback_data.get('correct', False):
                        self._update_pattern_stats(cluster_id, message, 
                                                {'template_id': template_id},
                                                {field: extracted_data[field]},
                                                True)
                    else:
                        # If incorrect, reduce weight of the incorrect value
                        self._update_pattern_stats(cluster_id, message,
                                                {'template_id': template_id},
                                                {field: feedback_data.get('correct_value', '')},
                                                True)
            
        except Exception as e:
            log.error(f"Error updating patterns from feedback: {str(e)}")
        finally:
            if conn:
                self.db_pool.putconn(conn) 