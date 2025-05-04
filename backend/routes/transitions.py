# routes/transitions.py
from flask import Blueprint, request, jsonify, g
from db import get_db_connection, release_db_connection
import uuid
import logging
from auth import require_internal_key
from .utils import is_valid_uuid
import json

log = logging.getLogger(__name__)

transitions_bp = Blueprint('transitions', __name__, url_prefix='/transitions')

@transitions_bp.route('/by-stage/<stage_id>', methods=['GET'])
@require_internal_key
def get_transitions_for_stage(stage_id):
    if not hasattr(g, 'business_id'):
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id
    log.info(f"Fetching transitions for stage {stage_id} in business {business_id}")

    if not is_valid_uuid(stage_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid stage_id format"}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Verify stage belongs to business first
        cursor.execute("SELECT 1 FROM stages WHERE stage_id = %s AND business_id = %s", (stage_id, business_id))
        if not cursor.fetchone():
            return jsonify({"error_code": "NOT_FOUND", "message": "Stage not found or access denied"}), 404
        
        # Fetch transitions
        cursor.execute("""
            SELECT transition_id, from_stage_id, to_stage_id, conditions, priority 
            FROM stage_transitions 
            WHERE from_stage_id = %s 
            ORDER BY priority ASC
            """, (stage_id,))
        transitions = cursor.fetchall()
        transition_list = [
            {
                "transition_id": str(row[0]),
                "from_stage_id": str(row[1]),
                "to_stage_id": str(row[2]),
                "conditions": row[3], # Assuming JSONB or TEXT
                "priority": row[4]
            } for row in transitions
        ]
        return jsonify(transition_list), 200

    except Exception as e:
        log.error(f"Error fetching transitions for stage {stage_id}: {str(e)}", exc_info=True)
        return jsonify({"error_code": "DB_ERROR", "message": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@transitions_bp.route('', methods=['POST'])
@require_internal_key
def create_transition():
    if not hasattr(g, 'business_id'):
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id
    log.info(f"Creating transition for business {business_id}")

    data = request.get_json()
    if not data:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Request must be JSON"}), 400

    # Basic Validation
    required = ['from_stage_id', 'to_stage_id', 'conditions', 'priority']
    if not all(field in data for field in required):
        return jsonify({"error_code": "BAD_REQUEST", "message": f"Missing required fields: {required}"}), 400
    if not is_valid_uuid(data['from_stage_id']) or not is_valid_uuid(data['to_stage_id']):
         return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid stage ID format"}), 400
    if not isinstance(data['priority'], int):
         return jsonify({"error_code": "BAD_REQUEST", "message": "Priority must be an integer"}), 400
    # TODO: Add validation for conditions format (JSON?)

    from_stage_id = data['from_stage_id']
    to_stage_id = data['to_stage_id']
    conditions = data['conditions'] # Consider json.dumps if storing as TEXT
    priority = data['priority']
    transition_id = str(uuid.uuid4())
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify both stages belong to the authenticated business
        cursor.execute("SELECT 1 FROM stages WHERE stage_id = %s AND business_id = %s", (from_stage_id, business_id))
        if not cursor.fetchone():
            return jsonify({"error_code": "NOT_FOUND", "message": f"From stage {from_stage_id} not found or access denied"}), 404
        cursor.execute("SELECT 1 FROM stages WHERE stage_id = %s AND business_id = %s", (to_stage_id, business_id))
        if not cursor.fetchone():
            return jsonify({"error_code": "NOT_FOUND", "message": f"To stage {to_stage_id} not found or access denied"}), 404

        # Insert the transition
        cursor.execute("""
            INSERT INTO stage_transitions (transition_id, from_stage_id, to_stage_id, conditions, priority)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING transition_id;
        """, (
            transition_id,
            from_stage_id,
            to_stage_id,
            json.dumps(conditions) if isinstance(conditions, dict) else conditions, # Store as JSON string if dict
            priority
        ))
        result = cursor.fetchone()
        conn.commit()
        log.info(f"Transition {result[0]} created from {from_stage_id} to {to_stage_id} for business {business_id}")
        return jsonify({"message": "Transition created successfully", "transition_id": result[0]}), 201

    except Exception as e:
        if conn: conn.rollback()
        log.error(f"Error creating transition for business {business_id}: {str(e)}", exc_info=True)
        return jsonify({"error_code": "DB_ERROR", "message": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@transitions_bp.route('/<transition_id>', methods=['DELETE'])
@require_internal_key
def delete_transition(transition_id):
    if not hasattr(g, 'business_id'):
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id
    log.info(f"Deleting transition {transition_id} for business {business_id}")

    if not is_valid_uuid(transition_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid transition_id format"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify the transition belongs to a stage within the authenticated business
        cursor.execute("""
            DELETE FROM stage_transitions st
            USING stages s
            WHERE st.transition_id = %s 
            AND st.from_stage_id = s.stage_id 
            AND s.business_id = %s
        """, (transition_id, business_id))
        conn.commit()

        if cursor.rowcount == 0:
             log.warning(f"Delete attempted on non-existent or unauthorized transition {transition_id} for business {business_id}")
             return jsonify({"error_code": "NOT_FOUND", "message": "Transition not found or access denied"}), 404
        
        log.info(f"Transition {transition_id} deleted successfully for business {business_id}")
        return jsonify({"message": "Transition deleted successfully"}), 200

    except Exception as e:
        if conn: conn.rollback()
        log.error(f"Error deleting transition {transition_id} for business {business_id}: {str(e)}", exc_info=True)
        return jsonify({"error_code": "DB_ERROR", "message": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            release_db_connection(conn)