# routes/transitions.py
from flask import Blueprint, request, jsonify
from db import get_db_connection
import uuid
import logging
from auth import require_business_api_key
from .utils import is_valid_uuid

log = logging.getLogger(__name__)

transitions_bp = Blueprint('transitions', __name__, url_prefix='/transitions')

@transitions_bp.route('', methods=['GET'])
@require_business_api_key
def get_transitions():
    business_id = request.args.get('business_id')
    agent_id = request.args.get('agent_id')  # Optional filter

    if not business_id:
        return jsonify({"error": "Missing business_id query parameter"}), 400
    
    # Validate business_id format
    if not is_valid_uuid(business_id):
        return jsonify({"error": "Invalid business_id format"}), 400

    # Validate agent_id format if provided
    if agent_id and agent_id.lower() != 'null' and not is_valid_uuid(agent_id):
        return jsonify({"error": "Invalid agent_id format"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Base query
        query = """
            SELECT 
                transition_id, business_id, agent_id, from_stage_id, to_stage_id,
                condition, priority, created_at
            FROM transitions 
            WHERE business_id = %s
        """
        params = [business_id]

        # Add agent_id filtering logic
        if agent_id:
            if agent_id.lower() == 'null':
                query += " AND agent_id IS NULL"
            else:
                query += " AND agent_id = %s"
                params.append(agent_id)

        query += " ORDER BY priority ASC, created_at DESC"
        
        cursor.execute(query, tuple(params))
        transitions = cursor.fetchall()
        
        # Define columns matching the SELECT statement order
        columns = [
            'transition_id', 'business_id', 'agent_id', 'from_stage_id', 'to_stage_id',
            'condition', 'priority', 'created_at'
        ]
        
        result_list = []
        for row in transitions:
            transition_dict = {}
            for i, col_name in enumerate(columns):
                value = row[i]
                # Ensure UUIDs and datetimes are strings for JSON
                if isinstance(value, uuid.UUID):
                    transition_dict[col_name] = str(value)
                elif hasattr(value, 'isoformat'):  # Check for datetime objects
                    transition_dict[col_name] = value.isoformat()
                else:
                    transition_dict[col_name] = value  # Handles None, strings, etc.
            result_list.append(transition_dict)
            
        return jsonify(result_list), 200

    except Exception as e:
        log.error(f"Error fetching transitions for business {business_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to fetch transition data", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

@transitions_bp.route('', methods=['POST'])
@require_business_api_key
def create_transition():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON and contain data"}), 400

    # Define required fields
    required_fields = ['business_id', 'from_stage_id', 'to_stage_id']

    # Check for missing or empty required fields
    missing_or_empty = [field for field in required_fields if field not in data or not data[field]]
    if missing_or_empty:
        return jsonify({"error": f"Missing or empty required fields: {', '.join(missing_or_empty)}"}), 400

    business_id = data.get('business_id')
    agent_id = data.get('agent_id')  # Optional, can be None
    from_stage_id = data.get('from_stage_id')
    to_stage_id = data.get('to_stage_id')
    condition = data.get('condition', '')
    priority = data.get('priority', 1)

    # Validate UUID formats
    if not is_valid_uuid(business_id):
        return jsonify({"error": "Invalid business_id format"}), 400
    if agent_id and not is_valid_uuid(agent_id):
        return jsonify({"error": "Invalid agent_id format"}), 400
    if not is_valid_uuid(from_stage_id):
        return jsonify({"error": "Invalid from_stage_id format"}), 400
    if not is_valid_uuid(to_stage_id):
        return jsonify({"error": "Invalid to_stage_id format"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # SQL INSERT statement
        sql = '''
            INSERT INTO transitions (
                transition_id, business_id, agent_id, from_stage_id, to_stage_id,
                condition, priority
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING transition_id;
        '''
        params = (
            str(uuid.uuid4()),
            business_id,
            agent_id,
            from_stage_id,
            to_stage_id,
            condition,
            priority
        )

        cursor.execute(sql, params)

        transition_id = cursor.fetchone()[0]
        conn.commit()
        
        # Fetch the newly created transition
        cursor.execute("""
            SELECT 
                transition_id, business_id, agent_id, from_stage_id, to_stage_id,
                condition, priority, created_at
            FROM transitions 
            WHERE transition_id = %s
        """, (transition_id,))
        
        result = cursor.fetchone()
        columns = [
            'transition_id', 'business_id', 'agent_id', 'from_stage_id', 'to_stage_id',
            'condition', 'priority', 'created_at'
        ]
        
        transition_dict = {}
        for i, col_name in enumerate(columns):
            value = result[i]
            if isinstance(value, uuid.UUID):
                transition_dict[col_name] = str(value)
            elif hasattr(value, 'isoformat'):
                transition_dict[col_name] = value.isoformat()
            else:
                transition_dict[col_name] = value
        
        log.info(f"Transition created successfully with ID: {transition_id}")
        return jsonify(transition_dict), 201

    except Exception as e:
        if conn: 
            conn.rollback()
        log.error(f"Error creating transition: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to create transition", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

@transitions_bp.route('/<transition_id>', methods=['DELETE'])
@require_business_api_key
def delete_transition(transition_id):
    # Validate transition_id format
    if not is_valid_uuid(transition_id):
        return jsonify({"error": "Invalid transition_id format"}), 400

    business_id = request.args.get('business_id')
    if not business_id:
        return jsonify({"error": "Missing business_id query parameter"}), 400
    
    # Validate business_id format
    if not is_valid_uuid(business_id):
        return jsonify({"error": "Invalid business_id format"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete the transition
        cursor.execute(
            "DELETE FROM transitions WHERE transition_id = %s AND business_id = %s RETURNING transition_id",
            (transition_id, business_id)
        )
        
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Transition not found or not owned by this business"}), 404
            
        conn.commit()
        return jsonify({"message": "Transition deleted successfully"}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        log.error(f"Error deleting transition {transition_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to delete transition", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()