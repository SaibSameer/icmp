"""
API routes for data extraction functionality.

This module provides endpoints for accessing and managing extracted data.
"""

import logging
from flask import Blueprint, jsonify, request, g
from typing import Dict, Any, List, Optional
import traceback # For detailed error logging

from backend.db import get_db_connection, release_db_connection
from backend.message_processing.services.data_extraction_service import DataExtractionService
from backend.message_processing.data_extraction.extractor import DataExtractor
from backend.message_processing.data_extraction.rule_validator import ExtractionRuleValidator
from backend.message_processing.data_extraction.processor import DataProcessor
from backend.auth import require_internal_key

log = logging.getLogger(__name__)

# Create a Blueprint for data extraction routes
data_extraction_bp = Blueprint('data_extraction', __name__)

@data_extraction_bp.route('/api/v1/conversations/<conversation_id>/extracted_data', methods=['GET'])
@require_internal_key
def get_conversation_extracted_data(conversation_id: str):
    """
    Get all extracted data for a conversation.
    
    Args:
        conversation_id: ID of the conversation
        
    Returns:
        JSON response with extracted data
    """
    try:
        business_id = g.business_id
        user_id = g.user_id
        
        # Get query parameters
        data_type = request.args.get('data_type')
        limit = int(request.args.get('limit', 10))
        
        # Verify the conversation belongs to the business
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT conversation_id FROM conversations 
            WHERE conversation_id = %s AND business_id = %s
            """,
            (conversation_id, business_id)
        )
        
        if not cursor.fetchone():
            return jsonify({
                'success': False,
                'error': 'Conversation not found or access denied'
            }), 404
        
        # Create data extraction service
        from backend.db import get_db_pool
        db_pool = get_db_pool()
        data_extraction_service = DataExtractionService(db_pool)
        
        # Get extracted data
        extracted_data = data_extraction_service.get_extracted_data(
            conversation_id, data_type, limit
        )
        
        return jsonify({
            'success': True,
            'extracted_data': extracted_data
        })
        
    except Exception as e:
        log.error(f"Error retrieving extracted data: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()

@data_extraction_bp.route('/api/v1/extracted_data/<extraction_id>', methods=['GET'])
@require_internal_key
def get_extraction_by_id(extraction_id: str):
    """
    Get a specific extraction by ID.
    
    Args:
        extraction_id: ID of the extraction
        
    Returns:
        JSON response with extraction data
    """
    try:
        business_id = g.business_id
        
        # Verify the extraction belongs to a conversation of the business
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ed.extraction_id, ed.stage_id, ed.data_type, 
                   ed.extracted_data, ed.created_at, s.stage_name,
                   c.conversation_id, c.business_id
            FROM extracted_data ed
            JOIN stages s ON ed.stage_id = s.stage_id
            JOIN conversations c ON ed.conversation_id = c.conversation_id
            WHERE ed.extraction_id = %s AND c.business_id = %s
            """,
            (extraction_id, business_id)
        )
        
        result = cursor.fetchone()
        if not result:
            return jsonify({
                'success': False,
                'error': 'Extraction not found or access denied'
            }), 404
        
        # Format the result
        extraction = {
            'extraction_id': result['extraction_id'],
            'conversation_id': result['conversation_id'],
            'stage_id': result['stage_id'],
            'stage_name': result['stage_name'],
            'data_type': result['data_type'],
            'data': result['extracted_data'],
            'created_at': result['created_at'].isoformat()
        }
        
        return jsonify({
            'success': True,
            'extraction': extraction
        })
        
    except Exception as e:
        log.error(f"Error retrieving extraction: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()

@data_extraction_bp.route('/api/v1/businesses/<business_id>/extraction_templates', methods=['GET'])
@require_internal_key
def get_extraction_templates(business_id: str):
    """
    Get all data extraction templates for a business.
    
    Args:
        business_id: ID of the business
        
    Returns:
        JSON response with extraction templates
    """
    try:
        # Verify the business ID matches the authenticated user
        if business_id != g.business_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Get extraction templates
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT template_id, template_name, template_type, content, 
                   system_prompt, created_at, updated_at
            FROM templates
            WHERE business_id = %s AND template_type = 'data_extraction'
            ORDER BY template_name
            """,
            (business_id,)
        )
        
        templates = cursor.fetchall()
        
        # Format the results
        result = []
        for template in templates:
            result.append({
                'template_id': template['template_id'],
                'template_name': template['template_name'],
                'template_type': template['template_type'],
                'content': template['content'],
                'system_prompt': template['system_prompt'],
                'created_at': template['created_at'].isoformat(),
                'updated_at': template['updated_at'].isoformat() if template['updated_at'] else None
            })
        
        return jsonify({
            'success': True,
            'templates': result
        })
        
    except Exception as e:
        log.error(f"Error retrieving extraction templates: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()

@data_extraction_bp.route('/api/v1/businesses/<business_id>/extraction_templates', methods=['POST'])
@require_internal_key
def create_extraction_template(business_id: str):
    """
    Create a new data extraction template.
    
    Args:
        business_id: ID of the business
        
    Returns:
        JSON response with the created template
    """
    try:
        # Verify the business ID matches the authenticated user
        if business_id != g.business_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Get template data from request
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['template_name', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create the template
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO templates 
            (template_id, business_id, template_name, template_type, content, system_prompt)
            VALUES (gen_random_uuid(), %s, %s, 'data_extraction', %s, %s)
            RETURNING template_id, template_name, template_type, content, 
                      system_prompt, created_at, updated_at
            """,
            (business_id, data['template_name'], data['content'], data.get('system_prompt', ''))
        )
        
        template = cursor.fetchone()
        conn.commit()
        
        # Format the result
        result = {
            'template_id': template['template_id'],
            'template_name': template['template_name'],
            'template_type': template['template_type'],
            'content': template['content'],
            'system_prompt': template['system_prompt'],
            'created_at': template['created_at'].isoformat(),
            'updated_at': template['updated_at'].isoformat() if template['updated_at'] else None
        }
        
        return jsonify({
            'success': True,
            'template': result
        }), 201
        
    except Exception as e:
        log.error(f"Error creating extraction template: {str(e)}\n{traceback.format_exc()}")
        if conn:
            conn.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()

@data_extraction_bp.route('/api/extract', methods=['POST'])
@require_internal_key
def extract_data():
    if not hasattr(g, 'business_id'):
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id
    log.info(f"Data extraction request for business {business_id}")

    data = request.get_json()
    if not data:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Request must be JSON"}), 400

    template_id = data.get('template_id')
    text_content = data.get('text_content')
    # Optional: allow passing context variables for the template
    context_vars = data.get('context_variables', {})

    if not template_id or not text_content:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Missing required fields: template_id and text_content"}), 400
    
    # TODO: Validate template_id format (is_valid_uuid?)

    conn = None
    try:
        # Fetch the template content AND verify it belongs to the business
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT content, system_prompt FROM templates 
                          WHERE template_id = %s AND business_id = %s 
                          AND template_type = 'data_extraction'""", 
                       (template_id, business_id))
        template_row = cursor.fetchone()

        if not template_row:
            log.warning(f"Data extraction template {template_id} not found or invalid type/access for business {business_id}")
            return jsonify({"error_code": "NOT_FOUND", "message": "Data extraction template not found or access denied"}), 404
        
        template_content = template_row[0]
        system_prompt = template_row[1]
        release_db_connection(conn) # Release connection before potentially long LLM call
        conn = None 

        # Placeholder for the actual extraction logic
        # This would likely involve formatting the prompt with text_content & context_vars,
        # then calling the LLM.
        log.info(f"TODO: Implement data extraction using template {template_id} for business {business_id}")
        # Example call:
        # extracted_data = extract_data_using_template(
        #     template_content=template_content, 
        #     system_prompt=system_prompt,
        #     text_content=text_content, 
        #     context_vars=context_vars
        # )
        extracted_data = {"placeholder": "extracted data would be here", "input_text": text_content[:50] + "..."}

        return jsonify({"success": True, "extracted_data": extracted_data}), 200

    except Exception as e:
        log.error(f"Error during data extraction for business {business_id}: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error_code": "EXTRACTION_FAILED", "message": "Failed to extract data"}), 500
    finally:
        if conn: # Ensure connection is released if error occurred before LLM call
            release_db_connection(conn)