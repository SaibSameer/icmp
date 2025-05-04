"""
Monitoring Routes

This module provides API routes for accessing monitoring data.
"""

from flask import Blueprint, jsonify, request, render_template
from backend.monitoring.enhanced_monitoring import EnhancedMonitoring
from backend.db import get_db_pool
import logging

log = logging.getLogger(__name__)

monitoring_bp = Blueprint('monitoring', __name__)

# Initialize monitoring system with database pool
db_pool = get_db_pool()
monitoring = EnhancedMonitoring(db_pool)

@monitoring_bp.route('/monitoring-dashboard')
def monitoring_dashboard():
    """Serve the enhanced monitoring dashboard."""
    return render_template('enhanced_dashboard.html')

@monitoring_bp.route('/api/monitoring/overview', methods=['GET'])
def get_overview():
    """Get overview statistics."""
    try:
        data = monitoring.get_overview_stats()
        return jsonify(data)
    except Exception as e:
        log.error(f"Error getting overview stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/api/monitoring/performance', methods=['GET'])
def get_performance():
    """Get performance trends."""
    try:
        days = request.args.get('days', default=7, type=int)
        data = monitoring.get_performance_trends(days)
        trend_plot = monitoring.get_trend_plot(days)
        return jsonify({
            'data': data,
            'trend_plot': trend_plot
        })
    except Exception as e:
        log.error(f"Error getting performance trends: {str(e)}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/api/monitoring/patterns', methods=['GET'])
def get_patterns():
    """Get pattern analysis."""
    try:
        data = monitoring.get_pattern_analysis()
        pattern_plot = monitoring.get_pattern_plot()
        return jsonify({
            'data': data,
            'pattern_plot': pattern_plot
        })
    except Exception as e:
        log.error(f"Error getting pattern analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/api/monitoring/errors', methods=['GET'])
def get_errors():
    """Get error analysis."""
    try:
        data = monitoring.get_error_analysis()
        error_plot = monitoring.get_error_plot()
        return jsonify({
            'data': data,
            'error_plot': error_plot
        })
    except Exception as e:
        log.error(f"Error getting error analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/api/monitoring/templates', methods=['GET'])
def get_templates():
    """Get template performance."""
    try:
        data = monitoring.get_template_performance()
        template_plot = monitoring.get_template_plot()
        return jsonify({
            'data': data,
            'template_plot': template_plot
        })
    except Exception as e:
        log.error(f"Error getting template performance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/api/monitoring/pipeline', methods=['GET'])
def get_pipeline():
    """Get processing pipeline metrics."""
    try:
        data = monitoring.get_processing_pipeline_metrics()
        pipeline_plot = monitoring.get_pipeline_plot()
        return jsonify({
            'data': data,
            'pipeline_plot': pipeline_plot
        })
    except Exception as e:
        log.error(f"Error getting pipeline metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/api/monitoring/ai', methods=['GET'])
def get_ai_performance():
    """Get AI performance metrics."""
    try:
        data = monitoring.get_ai_performance_metrics()
        ai_plot = monitoring.get_ai_performance_plot()
        return jsonify({
            'data': data,
            'ai_plot': ai_plot or '{}'  # Return empty JSON if plot is None
        })
    except Exception as e:
        log.error(f"Error getting AI performance metrics: {str(e)}")
        return jsonify({
            'data': {},
            'ai_plot': '{}'
        }), 500

@monitoring_bp.route('/api/monitoring/error-patterns', methods=['GET'])
def get_error_patterns():
    """Get error pattern analysis."""
    try:
        data = monitoring.get_error_pattern_analysis()
        error_pattern_plot = monitoring.get_error_pattern_plot()
        return jsonify({
            'data': data,
            'error_pattern_plot': error_pattern_plot
        })
    except Exception as e:
        log.error(f"Error getting error pattern analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/api/monitoring/all', methods=['GET'])
def get_all_metrics():
    """Get all monitoring data."""
    try:
        # Get all metrics with proper error handling
        overview = monitoring.get_overview_stats() or {}
        performance_trends = {
            'data': monitoring.get_performance_trends(7) or {},
            'trend_plot': monitoring.get_trend_plot(7) or '{}'
        }
        pattern_analysis = {
            'data': monitoring.get_pattern_analysis() or {},
            'pattern_plot': monitoring.get_pattern_plot() or '{}'
        }
        error_analysis = {
            'data': monitoring.get_error_analysis() or {},
            'error_plot': monitoring.get_error_plot() or '{}'
        }
        template_performance = {
            'data': monitoring.get_template_performance() or {},
            'template_plot': monitoring.get_template_plot() or '{}'
        }
        pipeline_metrics = {
            'data': monitoring.get_processing_pipeline_metrics() or {},
            'pipeline_plot': monitoring.get_pipeline_plot() or '{}'
        }
        ai_performance = {
            'data': monitoring.get_ai_performance_metrics() or {},
            'ai_plot': monitoring.get_ai_performance_plot() or '{}'
        }
        error_patterns = {
            'data': monitoring.get_error_pattern_analysis() or {},
            'error_pattern_plot': monitoring.get_error_pattern_plot() or '{}'
        }

        # Log the response for debugging
        log.info("Returning monitoring data")
        log.info(f"AI Performance Data: {ai_performance}")
        
        return jsonify({
            'overview': overview,
            'performance_trends': performance_trends,
            'pattern_analysis': pattern_analysis,
            'error_analysis': error_analysis,
            'template_performance': template_performance,
            'pipeline_metrics': pipeline_metrics,
            'ai_performance': ai_performance,
            'error_patterns': error_patterns
        })
    except Exception as e:
        log.error(f"Error getting all metrics: {str(e)}")
        # Return empty but valid JSON structure
        return jsonify({
            'overview': {},
            'performance_trends': {'data': {}, 'trend_plot': '{}'},
            'pattern_analysis': {'data': {}, 'pattern_plot': '{}'},
            'error_analysis': {'data': {}, 'error_plot': '{}'},
            'template_performance': {'data': {}, 'template_plot': '{}'},
            'pipeline_metrics': {'data': {}, 'pipeline_plot': '{}'},
            'ai_performance': {'data': {}, 'ai_plot': '{}'},
            'error_patterns': {'data': {}, 'error_pattern_plot': '{}'}
        }), 500 