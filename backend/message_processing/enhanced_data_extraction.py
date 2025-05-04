"""
Enhanced Data Extraction Service with Multi-Layer Extraction Strategy

This module provides a robust and versatile data extraction system that combines
multiple extraction methods and learns from past extractions.
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.ai.llm_service import LLMService
from backend.db import get_db_connection, release_db_connection

log = logging.getLogger(__name__)

class EnhancedDataExtraction:
    """
    Advanced data extraction service with multiple extraction strategies
    and learning capabilities.
    """
    
    def __init__(self, db_pool, llm_service: Optional[LLMService] = None):
        self.db_pool = db_pool
        self.llm_service = llm_service
        self.extraction_patterns = {}
        self.success_rates = {}
        self.vectorizer = TfidfVectorizer()
        self.pattern_database = {}
        
    def extract_data(self, conn, extraction_template_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced data extraction with multiple strategies and confidence scoring.
        """
        try:
            # Get template and process it
            template = self._get_extraction_template(conn, extraction_template_id)
            if not template:
                return {"error": "Template not found"}
            
            processed_template = self._process_template(conn, template, context)
            
            # Get message content
            message_content = context.get('message_content', '')
            
            # Try multiple extraction methods
            results = []
            
            # 1. Pattern-based extraction - Commented out
            # pattern_result = self._extract_with_patterns(message_content, processed_template)
            # results.append(('pattern', pattern_result))
            
            # 2. LLM-based extraction - Only this one is active
            if self.llm_service:
                llm_result = self._extract_with_llm(message_content, processed_template, context)
                results.append(('llm', llm_result))
            
            # 3. Rule-based extraction - Commented out
            # rule_result = self._extract_with_rules(message_content, processed_template)
            # results.append(('rule', rule_result))
            
            # 4. Statistical extraction - Commented out
            # stat_result = self._extract_with_statistics(message_content, processed_template)
            # results.append(('statistical', stat_result))
            
            # Score and combine results
            final_result = self._combine_results(results, message_content)
            
            # Store successful patterns
            if not isinstance(final_result, dict) or 'error' not in final_result:
                self._store_successful_pattern(message_content, processed_template, final_result)
            
            return final_result
            
        except Exception as e:
            log.error(f"Error in enhanced extraction: {str(e)}")
            return {"error": f"Extraction failed: {str(e)}"}
    
    def _extract_with_patterns(self, message: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """Pattern-based extraction with learned patterns."""
        result = {}
        
        # Check pattern database for similar messages
        similar_patterns = self._find_similar_patterns(message)
        if similar_patterns:
            # Use successful patterns from similar messages
            for pattern in similar_patterns:
                if pattern['pattern'] in message:
                    result.update(pattern['extracted_data'])
        
        # Use template-defined patterns
        if 'patterns' in template:
            for field, pattern in template['patterns'].items():
                matches = re.findall(pattern, message)
                if matches:
                    result[field] = matches[0]
        
        return result
    
    def _extract_with_llm(self, message: str, template: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """LLM-based extraction with context awareness."""
        if not self.llm_service:
            return {}
            
        # Add context to the prompt
        prompt = self._build_context_aware_prompt(message, template, context)
        
        try:
            response = self.llm_service.generate(prompt)
            return self._parse_llm_response(response)
        except Exception as e:
            log.error(f"LLM extraction failed: {str(e)}")
            return {}
    
    def _extract_with_rules(self, message: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based extraction using predefined rules."""
        result = {}
        
        # Apply business-specific rules
        if 'business_rules' in template:
            for rule in template['business_rules']:
                if self._evaluate_rule(message, rule):
                    result.update(rule['extract'])
        
        # Apply general rules
        for field, rules in template.get('rules', {}).items():
            for rule in rules:
                if self._evaluate_rule(message, rule):
                    result[field] = rule['value']
                    break
        
        return result
    
    def _extract_with_statistics(self, message: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """Statistical extraction for numerical and categorical data."""
        result = {}
        
        # Extract numerical values
        numbers = re.findall(r'\d+\.?\d*', message)
        if numbers:
            result['numerical_values'] = [float(n) for n in numbers]
        
        # Extract categorical data using frequency analysis
        words = message.lower().split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Find most frequent words that match template categories
        for category in template.get('categories', []):
            matches = [word for word, freq in word_freq.items() 
                      if word in category['keywords']]
            if matches:
                result[category['name']] = max(matches, key=lambda x: word_freq[x])
        
        return result
    
    def _combine_results(self, results: List[Tuple[str, Dict[str, Any]]], message: str) -> Dict[str, Any]:
        """Combine results from different extraction methods with confidence scoring."""
        combined = {}
        confidence_scores = {}
        
        for method, result in results:
            if not result or isinstance(result, dict) and 'error' in result:
                continue
                
            # Calculate confidence score
            confidence = self._calculate_confidence(method, result, message)
            
            # Update combined result with highest confidence values
            for key, value in result.items():
                if key not in combined or confidence > confidence_scores.get(key, 0):
                    combined[key] = value
                    confidence_scores[key] = confidence
        
        # Add confidence scores to result
        combined['_confidence_scores'] = confidence_scores
        
        return combined
    
    def _calculate_confidence(self, method: str, result: Dict[str, Any], message: str) -> float:
        """Calculate confidence score for an extraction result."""
        # Base confidence by method
        method_weights = {
            'llm': 0.8,
            'pattern': 0.7,
            'rule': 0.6,
            'statistical': 0.5
        }
        
        # Adjust based on result quality
        quality_score = 1.0
        if isinstance(result, dict):
            # More fields = higher confidence
            field_count = len(result)
            quality_score *= min(1.0, field_count / 5)
            
            # Check for empty or invalid values
            for value in result.values():
                if not value or str(value).strip() == '':
                    quality_score *= 0.8
        
        return method_weights.get(method, 0.5) * quality_score
    
    def _store_successful_pattern(self, message: str, template: Dict[str, Any], result: Dict[str, Any]):
        """Store successful extraction patterns for future use."""
        try:
            # Create pattern signature
            pattern = self._create_pattern_signature(message, template)
            
            # Store in pattern database
            self.pattern_database[pattern] = {
                'message': message,
                'template': template,
                'extracted_data': result,
                'timestamp': datetime.now(),
                'success_count': 1
            }
            
            # Update success rates
            template_id = template.get('template_id', 'unknown')
            self.success_rates[template_id] = self.success_rates.get(template_id, 0) + 1
            
        except Exception as e:
            log.error(f"Error storing pattern: {str(e)}")
    
    def _find_similar_patterns(self, message: str) -> List[Dict[str, Any]]:
        """Find similar patterns from the pattern database."""
        if not self.pattern_database:
            return []
        
        # Vectorize messages
        messages = [data['message'] for data in self.pattern_database.values()]
        messages.append(message)
        
        try:
            vectors = self.vectorizer.fit_transform(messages)
            similarities = cosine_similarity(vectors[-1:], vectors[:-1])[0]
            
            # Get top similar patterns
            similar_indices = np.argsort(similarities)[-3:]  # Top 3 matches
            return [list(self.pattern_database.values())[i] for i in similar_indices 
                   if similarities[i] > 0.7]  # Similarity threshold
            
        except Exception as e:
            log.error(f"Error finding similar patterns: {str(e)}")
            return []
    
    def _create_pattern_signature(self, message: str, template: Dict[str, Any]) -> str:
        """Create a unique signature for a message pattern."""
        # Extract key features
        words = message.lower().split()
        key_features = [word for word in words if len(word) > 3]  # Ignore short words
        
        # Add template features
        template_features = [str(v) for v in template.values() if isinstance(v, (str, int, float))]
        
        # Combine and hash
        signature = ' '.join(sorted(key_features + template_features))
        return hash(signature)
    
    def _build_context_aware_prompt(self, message: str, template: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build a context-aware prompt for LLM extraction."""
        # Include conversation history
        history = context.get('conversation_history', '')
        
        # Include user preferences
        preferences = context.get('user_preferences', {})
        
        # Build prompt
        prompt = f"""
        Extract information from the following message with context:
        
        Conversation History:
        {history}
        
        User Preferences:
        {json.dumps(preferences, indent=2)}
        
        Template Requirements:
        {json.dumps(template, indent=2)}
        
        Message to Extract From:
        {message}
        
        Please extract the requested information in JSON format.
        """
        
        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured data."""
        try:
            # Try to find JSON in response
            json_str = re.search(r'\{.*\}', response, re.DOTALL)
            if json_str:
                return json.loads(json_str.group())
            return {}
        except Exception as e:
            log.error(f"Error parsing LLM response: {str(e)}")
            return {}
    
    def _evaluate_rule(self, message: str, rule: Dict[str, Any]) -> bool:
        """Evaluate if a rule applies to a message."""
        try:
            # Check conditions
            for condition in rule.get('conditions', []):
                if not self._check_condition(message, condition):
                    return False
            return True
        except Exception as e:
            log.error(f"Error evaluating rule: {str(e)}")
            return False
    
    def _check_condition(self, message: str, condition: Dict[str, Any]) -> bool:
        """Check if a condition is met in the message."""
        condition_type = condition.get('type', 'contains')
        value = condition.get('value', '')
        
        if condition_type == 'contains':
            return value.lower() in message.lower()
        elif condition_type == 'starts_with':
            return message.lower().startswith(value.lower())
        elif condition_type == 'ends_with':
            return message.lower().endswith(value.lower())
        elif condition_type == 'regex':
            return bool(re.search(value, message))
        
        return False 