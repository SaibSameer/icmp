"""
Dashboard Routes

This module provides the web interface routes for the extraction dashboard.
"""

from flask import Blueprint, render_template, jsonify
from backend.monitoring.extraction_dashboard import ExtractionDashboard
from backend.db import get_db_pool

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    """Render the main dashboard page."""
    return render_template('enhanced_dashboard.html')

@dashboard_bp.route('/api/dashboard/overview')
def get_overview():
    """Get overview statistics."""
    dashboard = ExtractionDashboard(get_db_pool())
    return jsonify(dashboard.get_overview_stats())

@dashboard_bp.route('/api/dashboard/trends')
def get_trends():
    """Get performance trends."""
    dashboard = ExtractionDashboard(get_db_pool())
    return jsonify(dashboard.get_performance_trends())

@dashboard_bp.route('/api/dashboard/patterns')
def get_patterns():
    """Get pattern analysis."""
    dashboard = ExtractionDashboard(get_db_pool())
    return jsonify(dashboard.get_pattern_analysis())

@dashboard_bp.route('/api/dashboard/errors')
def get_errors():
    """Get error analysis."""
    dashboard = ExtractionDashboard(get_db_pool())
    return jsonify(dashboard.get_error_analysis())

@dashboard_bp.route('/api/dashboard/templates')
def get_templates():
    """Get template performance."""
    dashboard = ExtractionDashboard(get_db_pool())
    return jsonify(dashboard.get_template_performance())

@dashboard_bp.route('/api/dashboard/all')
def get_all_data():
    """Get all dashboard data."""
    dashboard = ExtractionDashboard(get_db_pool())
    return jsonify(dashboard.get_dashboard_data()) 