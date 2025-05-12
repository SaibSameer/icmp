#!/usr/bin/env python
"""
Utility Module: Health Check Endpoint

This module provides the health check endpoint for monitoring system status.
It checks database connectivity and schema loading status.

Location: backend/utils/health_check.py
"""

from flask import jsonify
from backend.db import get_db_connection, release_db_connection
from datetime import datetime
import psycopg2
import logging

log = logging.getLogger(__name__)

def register(app, require_api_key, limiter, schemas):
    @app.route('/health', methods=['GET'])
    @require_api_key
    #@limiter.limit("100 per minute")  # Added rate limiting
    def health_check():
        status = {"status": "healthy", "date": datetime.now().isoformat()}
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            status["database"] = "connected"
            release_db_connection(conn)
        except psycopg2.Error as e:  # Narrowed exception
            status["status"] = "unhealthy"
            status["database"] = "disconnected"
            log.error(f"Database health check failed: {str(e)}", exc_info=True)
        status["schemas_loaded"] = len(schemas) > 0
        return jsonify(status), 200 if status["status"] == "healthy" else 503