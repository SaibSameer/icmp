"""
Enhanced Monitoring System

This module provides advanced monitoring capabilities for the data extraction system,
building upon the existing ExtractionDashboard functionality.
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
from backend.monitoring.extraction_dashboard import ExtractionDashboard
import plotly.express as px

log = logging.getLogger(__name__)

class EnhancedMonitoring(ExtractionDashboard):
    """
    Enhanced monitoring system that extends the basic ExtractionDashboard with
    additional features for better debugging and analysis.
    """
    
    def __init__(self, db_pool):
        super().__init__(db_pool)
        self.performance_metrics = {}
        self.error_patterns = {}
        self.template_analysis = {}
        self.logger = logging.getLogger(__name__)
    
    def get_processing_pipeline_metrics(self) -> Dict[str, Any]:
        """
        Get detailed metrics about the processing pipeline.
        
        Returns:
            Dictionary containing pipeline metrics
        """
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            
            # Get stage-wise performance
            cursor.execute("""
                SELECT stage,
                       COUNT(*) as total,
                       COUNT(CASE WHEN success THEN 1 END) as successful,
                       AVG(processing_time) as avg_time,
                       MAX(processing_time) as max_time,
                       MIN(processing_time) as min_time
                FROM processing_stages
                GROUP BY stage
                ORDER BY total DESC
            """)
            
            rows = cursor.fetchall()
            
            # Create pipeline visualization
            fig = make_subplots(rows=2, cols=1, subplot_titles=("Stage Performance", "Processing Time"))
            
            # Add stage performance bars
            fig.add_trace(
                go.Bar(
                    x=[row[0] for row in rows],
                    y=[row[2]/row[1] if row[1] > 0 else 0 for row in rows],
                    name="Success Rate"
                ),
                row=1, col=1
            )
            
            # Add processing time scatter
            fig.add_trace(
                go.Scatter(
                    x=[row[0] for row in rows],
                    y=[row[3] for row in rows],
                    name="Average Time",
                    mode='lines+markers'
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title="Processing Pipeline Metrics",
                height=800
            )
            
            return {
                'stage_metrics': [
                    {
                        'stage': row[0],
                        'total': row[1],
                        'successful': row[2],
                        'success_rate': row[2]/row[1] if row[1] > 0 else 0,
                        'avg_time': float(row[3]) if row[3] else 0,
                        'max_time': float(row[4]) if row[4] else 0,
                        'min_time': float(row[5]) if row[5] else 0
                    }
                    for row in rows
                ],
                'pipeline_plot': fig.to_json()
            }
            
        except Exception as e:
            log.error(f"Error getting pipeline metrics: {str(e)}")
            return {}
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def get_ai_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics specific to AI components.
        
        Returns:
            Dictionary containing AI performance metrics
        """
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            
            # Get AI model performance
            cursor.execute("""
                SELECT call_type as model_name,
                       COUNT(*) as total_calls,
                       AVG(completion_time) as avg_response_time,
                       AVG(tokens_used) as avg_tokens,
                       COUNT(*) as successful_calls
                FROM llm_calls
                GROUP BY call_type
                ORDER BY total_calls DESC
            """)
            
            rows = cursor.fetchall()
            
            if not rows:
                return {
                    'model_metrics': [],
                    'ai_plot': '{}'
                }
            
            # Create AI performance visualization
            fig = make_subplots(rows=2, cols=1, subplot_titles=("Model Usage", "Performance Metrics"))
            
            # Add model usage bars
            fig.add_trace(
                go.Bar(
                    x=[row[0] for row in rows],
                    y=[row[1] for row in rows],
                    name="Total Calls"
                ),
                row=1, col=1
            )
            
            # Add performance metrics
            fig.add_trace(
                go.Scatter(
                    x=[row[0] for row in rows],
                    y=[row[2] for row in rows],
                    name="Avg Response Time",
                    mode='lines+markers'
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title="AI Performance Metrics",
                height=800
            )
            
            return {
                'model_metrics': [
                    {
                        'model_name': row[0],
                        'total_calls': row[1],
                        'avg_response_time': float(row[2]) if row[2] else 0,
                        'avg_tokens': float(row[3]) if row[3] else 0,
                        'success_rate': row[4]/row[1] if row[1] > 0 else 0
                    }
                    for row in rows
                ],
                'ai_plot': fig.to_json()
            }
            
        except Exception as e:
            log.error(f"Error getting AI performance metrics: {str(e)}")
            return {
                'model_metrics': [],
                'ai_plot': '{}'
            }
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def get_error_pattern_analysis(self) -> Dict[str, Any]:
        """
        Get detailed analysis of error patterns.
        
        Returns:
            Dictionary containing error pattern analysis
        """
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            
            # Get detailed error patterns
            cursor.execute("""
                SELECT error_type,
                       stage,
                       COUNT(*) as error_count,
                       AVG(processing_time) as avg_time,
                       MAX(processing_time) as max_time
                FROM error_logs
                GROUP BY error_type, stage
                ORDER BY error_count DESC
                LIMIT 20
            """)
            
            rows = cursor.fetchall()
            
            # Create error pattern visualization
            fig = go.Figure()
            
            # Add error type bars
            fig.add_trace(go.Bar(
                x=[f"{row[0]} ({row[1]})" for row in rows],
                y=[row[2] for row in rows],
                name="Error Count"
            ))
            
            # Add processing time scatter
            fig.add_trace(go.Scatter(
                x=[f"{row[0]} ({row[1]})" for row in rows],
                y=[row[3] for row in rows],
                name="Average Time",
                mode='lines+markers'
            ))
            
            fig.update_layout(
                title="Error Pattern Analysis",
                xaxis_title="Error Type (Stage)",
                yaxis_title="Count/Time"
            )
            
            return {
                'error_patterns': [
                    {
                        'error_type': row[0],
                        'stage': row[1],
                        'error_count': row[2],
                        'avg_time': float(row[3]) if row[3] else 0,
                        'max_time': float(row[4]) if row[4] else 0
                    }
                    for row in rows
                ],
                'error_pattern_plot': fig.to_json()
            }
            
        except Exception as e:
            log.error(f"Error getting error pattern analysis: {str(e)}")
            return {}
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def get_enhanced_dashboard_data(self) -> Dict[str, Any]:
        """
        Get all enhanced dashboard data.
        
        Returns:
            Dictionary containing all enhanced dashboard data
        """
        return {
            'overview': self.get_overview_stats(),
            'performance_trends': self.get_performance_trends(),
            'pattern_analysis': self.get_pattern_analysis(),
            'error_analysis': self.get_error_analysis(),
            'template_performance': self.get_template_performance(),
            'pipeline_metrics': self.get_processing_pipeline_metrics(),
            'ai_performance': self.get_ai_performance_metrics(),
            'error_patterns': self.get_error_pattern_analysis()
        }

    def get_trend_plot(self, days=7):
        """Generate a plot showing performance trends over time."""
        try:
            data = self.get_performance_trends(days)
            if not data or not data.get('trend_data'):
                # Create empty plot with message
                fig = go.Figure()
                fig.add_annotation(
                    text="No data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=20)
                )
                fig.update_layout(
                    title='Performance Trends',
                    xaxis_title='Date',
                    yaxis_title='Success Rate (%)',
                    template='plotly_white'
                )
                return fig.to_json()
            
            df = pd.DataFrame(data['trend_data'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['success_rate'] * 100,  # Convert to percentage
                mode='lines+markers',
                name='Success Rate',
                line=dict(color='#28a745')
            ))
            
            fig.update_layout(
                title='Performance Trends',
                xaxis_title='Date',
                yaxis_title='Success Rate (%)',
                template='plotly_white'
            )
            
            return fig.to_json()
        except Exception as e:
            self.logger.error(f"Error generating trend plot: {str(e)}")
            return None

    def get_pipeline_plot(self):
        """Generate a plot showing processing pipeline metrics."""
        try:
            data = self.get_processing_pipeline_metrics()
            if not data or not data.get('stage_metrics'):
                # Create empty plot with message
                fig = go.Figure()
                fig.add_annotation(
                    text="No data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=20)
                )
                fig.update_layout(
                    title='Processing Pipeline Performance',
                    xaxis_title='Stage',
                    yaxis_title='Value',
                    barmode='group',
                    template='plotly_white'
                )
                return fig.to_json()
            
            df = pd.DataFrame(data['stage_metrics'])
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['stage'],
                y=df['success_rate'] * 100,  # Convert to percentage
                name='Success Rate',
                marker_color='#28a745'
            ))
            
            fig.update_layout(
                title='Processing Pipeline Performance',
                xaxis_title='Stage',
                yaxis_title='Success Rate (%)',
                barmode='group',
                template='plotly_white'
            )
            
            return fig.to_json()
        except Exception as e:
            self.logger.error(f"Error generating pipeline plot: {str(e)}")
            return None

    def get_ai_performance_plot(self):
        """Generate a plot showing AI performance metrics."""
        try:
            data = self.get_ai_performance_metrics()
            if not data or not data.get('model_metrics'):
                # Create empty plot with message
                fig = go.Figure()
                fig.add_annotation(
                    text="No data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=20)
                )
                fig.update_layout(
                    title='AI Performance Metrics',
                    xaxis_title='Model',
                    yaxis_title='Success Rate (%)',
                    template='plotly_white'
                )
                return fig.to_json()
            
            df = pd.DataFrame(data['model_metrics'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['model_name'],
                y=df['success_rate'] * 100,  # Convert to percentage
                mode='lines+markers',
                name='Success Rate',
                line=dict(color='#28a745')
            ))
            
            fig.update_layout(
                title='AI Performance Metrics',
                xaxis_title='Model',
                yaxis_title='Success Rate (%)',
                template='plotly_white'
            )
            
            return fig.to_json()
        except Exception as e:
            self.logger.error(f"Error generating AI performance plot: {str(e)}")
            # Return a valid empty plot JSON instead of None
            fig = go.Figure()
            fig.add_annotation(
                text="Error loading data",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20)
            )
            fig.update_layout(
                title='AI Performance Metrics',
                xaxis_title='Model',
                yaxis_title='Success Rate (%)',
                template='plotly_white'
            )
            return fig.to_json()

    def get_pattern_plot(self):
        """Generate a plot showing pattern analysis."""
        try:
            data = self.get_pattern_analysis()
            if not data or not data.get('pattern_stats'):
                # Create empty plot with message
                fig = go.Figure()
                fig.add_annotation(
                    text="No data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=20)
                )
                fig.update_layout(
                    title='Pattern Analysis',
                    xaxis_title='Pattern Type',
                    yaxis_title='Value',
                    barmode='group',
                    template='plotly_white'
                )
                return fig.to_json()
            
            df = pd.DataFrame(data['pattern_stats'])
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['field'],
                y=df['success_rate'],
                name='Success Rate',
                marker_color='#28a745'
            ))
            fig.add_trace(go.Bar(
                x=df['field'],
                y=df['usage_count'],
                name='Usage Count',
                marker_color='#007bff'
            ))
            
            fig.update_layout(
                title='Pattern Analysis',
                xaxis_title='Field',
                yaxis_title='Value',
                barmode='group',
                template='plotly_white'
            )
            
            return fig.to_json()
        except Exception as e:
            self.logger.error(f"Error generating pattern plot: {str(e)}")
            return None

    def get_error_plot(self):
        """Generate a plot showing error analysis."""
        try:
            data = self.get_error_analysis()
            if not data or not data.get('error_stats'):
                # Create empty plot with message
                fig = go.Figure()
                fig.add_annotation(
                    text="No data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=20)
                )
                fig.update_layout(
                    title='Error Analysis',
                    xaxis_title='Error Type',
                    yaxis_title='Count',
                    template='plotly_white'
                )
                return fig.to_json()
            
            df = pd.DataFrame(data['error_stats'])
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['error_type'],
                y=df['count'],
                name='Error Count',
                marker_color='#dc3545'
            ))
            
            fig.update_layout(
                title='Error Analysis',
                xaxis_title='Error Type',
                yaxis_title='Count',
                template='plotly_white'
            )
            
            return fig.to_json()
        except Exception as e:
            self.logger.error(f"Error generating error plot: {str(e)}")
            return None

    def get_error_pattern_plot(self):
        """Generate a plot showing error patterns."""
        try:
            data = self.get_error_pattern_analysis()
            if not data or not data.get('error_patterns'):
                # Create empty plot with message
                fig = go.Figure()
                fig.add_annotation(
                    text="No data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=20)
                )
                fig.update_layout(
                    title='Error Patterns',
                    xaxis_title='Error Pattern',
                    yaxis_title='Occurrence Count',
                    template='plotly_white'
                )
                return fig.to_json()
            
            df = pd.DataFrame(data['error_patterns'])
            
            # Ensure required columns exist
            if 'error_pattern' not in df.columns:
                df['error_pattern'] = 'Unknown Error'
            if 'occurrence_count' not in df.columns:
                df['occurrence_count'] = 0
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['error_pattern'],
                y=df['occurrence_count'],
                name='Occurrence Count',
                marker_color='#dc3545'
            ))
            
            fig.update_layout(
                title='Error Patterns',
                xaxis_title='Error Pattern',
                yaxis_title='Occurrence Count',
                template='plotly_white'
            )
            
            return fig.to_json()
        except Exception as e:
            self.logger.error(f"Error generating error pattern plot: {str(e)}")
            return None

    def get_template_plot(self):
        """Generate a plot showing template performance."""
        try:
            data = self.get_template_performance()
            if not data or not data.get('template_stats'):
                # Create empty plot with message
                fig = go.Figure()
                fig.add_annotation(
                    text="No data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=20)
                )
                fig.update_layout(
                    title='Template Performance',
                    xaxis_title='Template',
                    yaxis_title='Value',
                    barmode='group',
                    template='plotly_white'
                )
                return fig.to_json()
            
            df = pd.DataFrame(data['template_stats'])
            
            # Ensure required columns exist
            if 'template_name' not in df.columns:
                df['template_name'] = 'Unknown Template'
            if 'success_rate' not in df.columns:
                df['success_rate'] = 0
            if 'usage_count' not in df.columns:
                df['usage_count'] = 0
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['template_name'],
                y=df['success_rate'],
                name='Success Rate',
                marker_color='#28a745'
            ))
            fig.add_trace(go.Bar(
                x=df['template_name'],
                y=df['usage_count'],
                name='Usage Count',
                marker_color='#007bff'
            ))
            
            fig.update_layout(
                title='Template Performance',
                xaxis_title='Template',
                yaxis_title='Value',
                barmode='group',
                template='plotly_white'
            )
            
            return fig.to_json()
        except Exception as e:
            self.logger.error(f"Error generating template plot: {str(e)}")
            return None 