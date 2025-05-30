# backend/routes/agents.py
from flask import Blueprint, jsonify, request, g
import logging
import uuid
import json
import os
import sys
from psycopg2.extras import RealDictCursor

# Handle imports whether run as module or directly
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import get_db_connection, release_db_connection
from backend.auth import require_api_key, require_internal_key
from backend.routes.utils import is_valid_uuid

log = logging.getLogger(__name__)

agents_bp = Blueprint('agents', __name__, url_prefix='/api/agents')

@agents_bp.route('', methods=['GET'])
@require_api_key
def get_agents():
    """Lists agents, requires admin key. Optionally filter by business_id."""
    # Get optional business_id filter
    business_id_filter = request.args.get('business_id')
    if business_id_filter and not is_valid_uuid(business_id_filter):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format in query parameter"}), 400
        
    log_msg = "Fetching all agents (admin)"
    if business_id_filter:
        log_msg += f" filtered by business_id={business_id_filter}"
    log.info(log_msg)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        params = []
        query = """
            SELECT agent_id, business_id, agent_name, created_at, updated_at
            FROM agents
        """
        
        where_clauses = []
        if business_id_filter:
            where_clauses.append("business_id = %s")
            params.append(business_id_filter)
        
        if where_clauses:
             query += " WHERE " + " AND ".join(where_clauses)
             
        query += " ORDER BY created_at DESC;"
        
        cursor.execute(query, tuple(params))
        agents = cursor.fetchall()
        
        # Convert UUIDs and timestamps to strings
        for agent in agents:
            for key, value in agent.items():
                if isinstance(value, uuid.UUID):
                    agent[key] = str(value)
                elif hasattr(value, 'isoformat'):
                    agent[key] = value.isoformat()
            
        return jsonify(agents), 200

    except Exception as e:
        # Catch potential errors like table not existing if schema isn't confirmed
        error_detail = str(e)
        log.error(f"Error fetching agents (admin): {error_detail}", exc_info=True)
        if "relation \"agents\" does not exist" in error_detail.lower():
             return jsonify({"error_code": "SERVER_CONFIG_ERROR", "message": "Agents table not found. Please check database schema.", "details": error_detail}), 500
        return jsonify({"error_code": "SERVER_ERROR", "message": "Failed to fetch agents data", "details": error_detail}), 500
    finally:
        if conn:
            release_db_connection(conn)

@agents_bp.route('', methods=['POST'])
@require_api_key
def create_agent():
    """Creates a new agent for a business (admin access)."""
    data = request.get_json()
    if not data:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Request must be JSON"}), 400
        
    # Get business_id from payload - IT IS REQUIRED for admin creation
    business_id = data.get('business_id')
    agent_name = data.get('name') # Assuming 'name' is used based on update route
    
    if not business_id:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Missing required field in payload: business_id"}), 400
    if not is_valid_uuid(business_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format in payload"}), 400
    if not agent_name or not str(agent_name).strip():
         return jsonify({"error_code": "BAD_REQUEST", "message": "Missing or empty required field in payload: name"}), 400

    log.info(f"Admin creating agent '{agent_name}' for business {business_id}")

    agent_id = str(uuid.uuid4())
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify the target business_id exists before creating the agent
        cursor.execute("SELECT 1 FROM businesses WHERE business_id = %s", (business_id,))
        if not cursor.fetchone():
             return jsonify({"error_code": "NOT_FOUND", "message": f"Business with ID {business_id} not found"}), 404

        cursor.execute("""
            INSERT INTO agents (agent_id, business_id, agent_name)
            VALUES (%s, %s, %s)
            RETURNING agent_id, business_id, agent_name, created_at, updated_at;
        """, (
            agent_id,
            business_id,
            agent_name
        ))
        result = cursor.fetchone()
        conn.commit()
        
        # Convert UUIDs and timestamps to strings
        agent = {
            'agent_id': str(result[0]),
            'business_id': str(result[1]),
            'agent_name': result[2],
            'created_at': result[3].isoformat() if result[3] else None,
            'updated_at': result[4].isoformat() if result[4] else None
        }
        
        log.info(f"Agent {agent_id} created for business {business_id} by admin")
        return jsonify(agent), 201

    except Exception as e:
        if conn: conn.rollback()
        log.error(f"Error creating agent for business {business_id}: {str(e)}", exc_info=True)
        if "unique constraint" in str(e).lower() and "agents_business_id_agent_name_key" in str(e).lower():
             return jsonify({"error_code": "CONFLICT", "message": "Agent name already exists for this business"}), 409
        return jsonify({"error_code": "DB_ERROR", "message": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@agents_bp.route('/<agent_id>', methods=['PUT'])
@require_api_key
def update_agent(agent_id):
    """Updates an existing agent."""
    if not is_valid_uuid(agent_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid agent_id format"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Request must be JSON"}), 400

    business_id = data.get('business_id')
    if not business_id:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Missing required field: business_id"}), 400
    if not is_valid_uuid(business_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format"}), 400

    # Only allow updating agent_name for now
    agent_name = data.get('name')
    if not agent_name or not str(agent_name).strip():
        return jsonify({"error_code": "BAD_REQUEST", "message": "Missing or empty required field: name"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM agents WHERE agent_id = %s AND business_id = %s", 
                       (agent_id, business_id))
        if not cursor.fetchone():
            log.warning(f"Update attempted on non-existent or unauthorized agent {agent_id} for business {business_id}")
            return jsonify({"error_code": "NOT_FOUND", "message": "Agent not found or access denied"}), 404

        cursor.execute("""
            UPDATE agents 
            SET agent_name = %s, updated_at = NOW() 
            WHERE agent_id = %s AND business_id = %s
            RETURNING agent_id, business_id, agent_name, created_at, updated_at;
        """, (agent_name, agent_id, business_id))
        
        result = cursor.fetchone()
        if not result:
            log.warning(f"Update affected 0 rows for agent {agent_id}, business {business_id}")
            return jsonify({"error_code": "NOT_FOUND", "message": "Agent not found or access denied during update"}), 404
            
        conn.commit()
        
        # Convert UUIDs and timestamps to strings
        agent = {
            'agent_id': str(result[0]),
            'business_id': str(result[1]),
            'agent_name': result[2],
            'created_at': result[3].isoformat() if result[3] else None,
            'updated_at': result[4].isoformat() if result[4] else None
        }
        
        log.info(f"Agent {agent_id} updated successfully for business {business_id}")
        return jsonify(agent), 200

    except Exception as e:
        if conn: conn.rollback()
        log.error(f"Error updating agent {agent_id} for business {business_id}: {str(e)}", exc_info=True)
        if "unique constraint" in str(e).lower() and "agents_business_id_agent_name_key" in str(e).lower():
             return jsonify({"error_code": "CONFLICT", "message": "Agent name already exists for this business"}), 409
        return jsonify({"error_code": "DB_ERROR", "message": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@agents_bp.route('/<agent_id>', methods=['DELETE'])
@require_api_key
def delete_agent(agent_id):
    """Deletes an agent."""
    business_id = request.args.get('business_id')
    if not business_id:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Missing required query parameter: business_id"}), 400
    if not is_valid_uuid(business_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format"}), 400

    log.info(f"Deleting agent {agent_id} for business {business_id}")

    if not is_valid_uuid(agent_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid agent_id format"}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First verify the agent exists and belongs to the specified business
        query = """
            SELECT 1 FROM agents
            WHERE agent_id = %s AND business_id = %s;
        """
        cursor.execute(query, (agent_id, business_id))
        if cursor.fetchone() is None:
            return jsonify({"error_code": "NOT_FOUND", "message": "Agent not found or does not belong to the specified business"}), 404
        
        # Delete the agent
        query = """
            DELETE FROM agents
            WHERE agent_id = %s AND business_id = %s;
        """
        cursor.execute(query, (agent_id, business_id))
        conn.commit()
        
        return jsonify({"message": "Agent deleted successfully"}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        error_detail = str(e)
        log.error(f"Error deleting agent {agent_id} for business {business_id}: {error_detail}", exc_info=True)
        return jsonify({"error_code": "SERVER_ERROR", "message": "Failed to delete agent", "details": error_detail}), 500
    finally:
        if conn:
            release_db_connection(conn)

@agents_bp.route('/<agent_id>', methods=['GET'])
@require_api_key
def get_agent(agent_id):
    """Get a specific agent by ID using admin key."""
    if not is_valid_uuid(agent_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid agent_id format"}), 400
        
    log.info(f"Fetching agent {agent_id} via admin key")

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT agent_id, business_id, agent_name, created_at, updated_at
            FROM agents 
            WHERE agent_id = %s;
        """, (agent_id,))
        
        agent = cursor.fetchone()
        
        if not agent:
             return jsonify({"error_code": "NOT_FOUND", "message": "Agent not found"}), 404
        
        # Convert UUIDs and datetimes
        for key, value in agent.items():
            if isinstance(value, uuid.UUID):
                agent[key] = str(value)
            elif hasattr(value, 'isoformat'):
                agent[key] = value.isoformat()
        
        return jsonify(agent), 200

    except Exception as e:
        log.error(f"Error fetching agent {agent_id} (admin): {str(e)}", exc_info=True)
        return jsonify({"error_code": "SERVER_ERROR", "message": "Failed to fetch agent data", "details": str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)