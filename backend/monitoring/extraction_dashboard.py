"""
Monitoring Dashboard for Enhanced Data Extraction

This module provides a dashboard for monitoring and analyzing the performance
of the enhanced data extraction system.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from backend.db import get_db_connection, release_db_connection

log = logging.getLogger(__name__)

class ExtractionDashboard:
    """
    Dashboard for monitoring and analyzing data extraction performance.
    """
    
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    def get_overview_stats(self) -> Dict[str, Any]:
        """
        Get overview statistics for the extraction system.
        
        Returns:
            Dictionary containing overview statistics
        """
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            
            # Get total extractions
            cursor.execute("""
                SELECT COUNT(*) as total_extractions,
                       COUNT(CASE WHEN success THEN 1 END) as successful_extractions,
                       COUNT(CASE WHEN NOT success THEN 1 END) as failed_extractions
                FROM extraction_results
            """)
            row = cursor.fetchone()
            
            # Get pattern statistics
            cursor.execute("""
                SELECT COUNT(*) as total_patterns,
                       AVG(success_rate) as avg_success_rate,
                       COUNT(CASE WHEN success_rate > 0.7 THEN 1 END) as high_confidence_patterns
                FROM pattern_data
            """)
            pattern_stats = cursor.fetchone()
            
            # Get recent performance
            cursor.execute("""
                SELECT COUNT(*) as recent_extractions,
                       COUNT(CASE WHEN success THEN 1 END) as recent_successes,
                       COUNT(CASE WHEN NOT success THEN 1 END) as recent_failures
                FROM extraction_results
                WHERE timestamp > NOW() - INTERVAL '24 hours'
            """)
            recent_stats = cursor.fetchone()
            
            return {
                'total_extractions': row[0],
                'successful_extractions': row[1],
                'failed_extractions': row[2],
                'success_rate': row[1] / row[0] if row[0] > 0 else 0,
                'total_patterns': pattern_stats[0],
                'avg_success_rate': float(pattern_stats[1]) if pattern_stats[1] else 0,
                'high_confidence_patterns': pattern_stats[2],
                'recent_extractions': recent_stats[0],
                'recent_success_rate': recent_stats[1] / recent_stats[0] if recent_stats[0] > 0 else 0
            }
            
        except Exception as e:
            log.error(f"Error getting overview stats: {str(e)}")
            return {}
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def get_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """
        Get performance trends over time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary containing performance trends
        """
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            
            # Get daily performance
            cursor.execute("""
                SELECT DATE_TRUNC('day', timestamp) as date,
                       COUNT(*) as total,
                       COUNT(CASE WHEN success THEN 1 END) as successful,
                       COUNT(CASE WHEN NOT success THEN 1 END) as failed
                FROM extraction_results
                WHERE timestamp > NOW() - INTERVAL '%s days'
                GROUP BY date
                ORDER BY date
            """, (days,))
            
            rows = cursor.fetchall()
            
            # Convert to DataFrame for easier processing
            df = pd.DataFrame(rows, columns=['date', 'total', 'successful', 'failed'])
            df['success_rate'] = df['successful'] / df['total']
            
            # Create trend visualization
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['total'], name="Total Extractions"),
                secondary_y=False
            )
            
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['success_rate'], name="Success Rate"),
                secondary_y=True
            )
            
            fig.update_layout(
                title="Extraction Performance Trends",
                xaxis_title="Date",
                yaxis_title="Number of Extractions",
                yaxis2_title="Success Rate"
            )
            
            return {
                'trend_data': df.to_dict('records'),
                'trend_plot': fig.to_json()
            }
            
        except Exception as e:
            log.error(f"Error getting performance trends: {str(e)}")
            return {}
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def get_pattern_analysis(self) -> Dict[str, Any]:
        """
        Get analysis of extraction patterns.
        
        Returns:
            Dictionary containing pattern analysis
        """
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            
            # Get pattern statistics
            cursor.execute("""
                SELECT field, 
                       COUNT(*) as usage_count,
                       AVG(success_rate) as avg_success,
                       MAX(success_rate) as max_success,
                       MIN(success_rate) as min_success
                FROM pattern_data
                GROUP BY field
                ORDER BY usage_count DESC
            """)
            
            rows = cursor.fetchall()
            
            # Create pattern analysis visualization
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=[row[0] for row in rows],
                y=[row[1] for row in rows],
                name="Usage Count"
            ))
            
            fig.add_trace(go.Scatter(
                x=[row[0] for row in rows],
                y=[row[2] for row in rows],
                name="Average Success",
                mode='lines+markers'
            ))
            
            fig.update_layout(
                title="Pattern Analysis",
                xaxis_title="Field",
                yaxis_title="Count/Success Rate"
            )
            
            return {
                'pattern_stats': [
                    {
                        'field': row[0],
                        'usage_count': row[1],
                        'avg_success': float(row[2]) if row[2] else 0,
                        'max_success': float(row[3]) if row[3] else 0,
                        'min_success': float(row[4]) if row[4] else 0
                    }
                    for row in rows
                ],
                'pattern_plot': fig.to_json()
            }
            
        except Exception as e:
            log.error(f"Error getting pattern analysis: {str(e)}")
            return {}
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """
        Get analysis of extraction errors.
        
        Returns:
            Dictionary containing error analysis
        """
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            
            # Get error patterns
            cursor.execute("""
                SELECT extracted_data->>'error' as error_type,
                       COUNT(*) as error_count
                FROM extraction_results
                WHERE NOT success
                GROUP BY error_type
                ORDER BY error_count DESC
                LIMIT 10
            """)
            
            rows = cursor.fetchall()
            
            # Create error analysis visualization
            fig = go.Figure(data=[
                go.Pie(
                    labels=[row[0] for row in rows],
                    values=[row[1] for row in rows],
                    hole=.3
                )
            ])
            
            fig.update_layout(
                title="Error Distribution"
            )
            
            return {
                'error_stats': [
                    {
                        'error_type': row[0],
                        'count': row[1]
                    }
                    for row in rows
                ],
                'error_plot': fig.to_json()
            }
            
        except Exception as e:
            log.error(f"Error getting error analysis: {str(e)}")
            return {}
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def get_template_performance(self) -> Dict[str, Any]:
        """
        Get performance analysis by template.
        
        Returns:
            Dictionary containing template performance analysis
        """
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            
            # Get template performance
            cursor.execute("""
                SELECT t.template_id,
                       t.template_name,
                       COUNT(er.extraction_id) as total_extractions,
                       COUNT(CASE WHEN er.success THEN 1 END) as successful_extractions,
                       AVG(pd.success_rate) as avg_pattern_success
                FROM templates t
                LEFT JOIN extraction_results er ON t.template_id = er.template_id
                LEFT JOIN pattern_data pd ON er.cluster_id = pd.cluster_id
                GROUP BY t.template_id, t.template_name
                ORDER BY total_extractions DESC
            """)
            
            rows = cursor.fetchall()
            
            # Create template performance visualization
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=[row[1] for row in rows],
                y=[row[2] for row in rows],
                name="Total Extractions"
            ))
            
            fig.add_trace(go.Bar(
                x=[row[1] for row in rows],
                y=[row[3] for row in rows],
                name="Successful Extractions"
            ))
            
            fig.update_layout(
                title="Template Performance",
                xaxis_title="Template",
                yaxis_title="Number of Extractions",
                barmode='group'
            )
            
            return {
                'template_stats': [
                    {
                        'template_id': row[0],
                        'template_name': row[1],
                        'total_extractions': row[2],
                        'successful_extractions': row[3],
                        'success_rate': row[3] / row[2] if row[2] > 0 else 0,
                        'avg_pattern_success': float(row[4]) if row[4] else 0
                    }
                    for row in rows
                ],
                'template_plot': fig.to_json()
            }
            
        except Exception as e:
            log.error(f"Error getting template performance: {str(e)}")
            return {}
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get all dashboard data in one call.
        
        Returns:
            Dictionary containing all dashboard data
        """
        return {
            'overview': self.get_overview_stats(),
            'performance_trends': self.get_performance_trends(),
            'pattern_analysis': self.get_pattern_analysis(),
            'error_analysis': self.get_error_analysis(),
            'template_performance': self.get_template_performance()
        } 