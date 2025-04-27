# backend/routes/agents.py
from flask import Blueprint, jsonify, request
import logging
import uuid

from db import get_db_connection, release_db_connection
from auth import require_business_api_key
from routes.utils import is_valid_uuid

log = logging.getLogger(__name__)

agents_bp = Blueprint('agents', __name__, url_prefix='/agents')

@agents_bp.route('', methods=['GET'])
@require_business_api_key
def get_agents():
    """Lists agents associated with a given business_id."""
    business_id = request.args.get('business_id')

    if not business_id:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Missing business_id query parameter"}), 400
    
    if not is_valid_uuid(business_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Match actual agents table schema without agent_role
        query = """
            SELECT agent_id, business_id, agent_name, created_at
            FROM agents
            WHERE business_id = %s
            ORDER BY created_at DESC;
        """
        cursor.execute(query, (business_id,))
        agents = cursor.fetchall()

        columns = ['agent_id', 'business_id', 'agent_name', 'created_at']
        result_list = []
        for row in agents:
            agent_dict = {}
            for i, col_name in enumerate(columns):
                value = row[i]
                if isinstance(value, uuid.UUID):
                    agent_dict[col_name] = str(value)
                elif hasattr(value, 'isoformat'):
                    agent_dict[col_name] = value.isoformat()
                else:
                    agent_dict[col_name] = value
            result_list.append(agent_dict)
            
        return jsonify(result_list), 200

    except Exception as e:
        # Catch potential errors like table not existing if schema isn't confirmed
        error_detail = str(e)
        log.error(f"Error fetching agents for business {business_id}: {error_detail}", exc_info=True)
        if "relation \"agents\" does not exist" in error_detail.lower():
             return jsonify({"error_code": "SERVER_CONFIG_ERROR", "message": "Agents table not found. Please check database schema.", "details": error_detail}), 500
        return jsonify({"error_code": "SERVER_ERROR", "message": "Failed to fetch agents data", "details": error_detail}), 500
    finally:
        if conn:
            release_db_connection(conn)

@agents_bp.route('', methods=['POST'])
@require_business_api_key
def create_agent():
    """Creates a new agent for a business."""
    if not request.is_json:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Request must be JSON"}), 400
    
    data = request.json
    business_id = data.get('business_id')
    agent_name = data.get('agent_name')
    
    # Validate required fields
    if not business_id or not agent_name:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Missing required fields: business_id and agent_name are required"}), 400
    
    if not is_valid_uuid(business_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format"}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate a new UUID for the agent
        agent_id = str(uuid.uuid4())
        
        # Insert the new agent
        query = """
            INSERT INTO agents (agent_id, business_id, agent_name)
            VALUES (%s, %s, %s)
            RETURNING agent_id, business_id, agent_name, created_at;
        """
        cursor.execute(query, (agent_id, business_id, agent_name))
        conn.commit()
        
        # Get the created agent data
        new_agent = cursor.fetchone()
        columns = ['agent_id', 'business_id', 'agent_name', 'created_at']
        
        # Format the response
        agent_dict = {}
        for i, col_name in enumerate(columns):
            value = new_agent[i]
            if isinstance(value, uuid.UUID):
                agent_dict[col_name] = str(value)
            elif hasattr(value, 'isoformat'):
                agent_dict[col_name] = value.isoformat()
            else:
                agent_dict[col_name] = value
                
        return jsonify(agent_dict), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
        error_detail = str(e)
        log.error(f"Error creating agent for business {business_id}: {error_detail}", exc_info=True)
        return jsonify({"error_code": "SERVER_ERROR", "message": "Failed to create agent", "details": error_detail}), 500
    finally:
        if conn:
            release_db_connection(conn)

@agents_bp.route('/<agent_id>', methods=['PUT'])
@require_business_api_key
def update_agent(agent_id):
    """Updates an existing agent."""
    if not is_valid_uuid(agent_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid agent_id format"}), 400
    
    if not request.is_json:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Request must be JSON"}), 400
    
    data = request.json
    business_id = data.get('business_id')
    agent_name = data.get('agent_name')
    
    # Validate required fields
    if not business_id or not agent_name:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Missing required fields: business_id and agent_name are required"}), 400
    
    if not is_valid_uuid(business_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format"}), 400
    
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
        
        # Update the agent
        query = """
            UPDATE agents
            SET agent_name = %s
            WHERE agent_id = %s AND business_id = %s
            RETURNING agent_id, business_id, agent_name, created_at;
        """
        cursor.execute(query, (agent_name, agent_id, business_id))
        conn.commit()
        
        # Get the updated agent data
        updated_agent = cursor.fetchone()
        columns = ['agent_id', 'business_id', 'agent_name', 'created_at']
        
        # Format the response
        agent_dict = {}
        for i, col_name in enumerate(columns):
            value = updated_agent[i]
            if isinstance(value, uuid.UUID):
                agent_dict[col_name] = str(value)
            elif hasattr(value, 'isoformat'):
                agent_dict[col_name] = value.isoformat()
            else:
                agent_dict[col_name] = value
                
        return jsonify(agent_dict), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        error_detail = str(e)
        log.error(f"Error updating agent {agent_id} for business {business_id}: {error_detail}", exc_info=True)
        return jsonify({"error_code": "SERVER_ERROR", "message": "Failed to update agent", "details": error_detail}), 500
    finally:
        if conn:
            release_db_connection(conn)

@agents_bp.route('/<agent_id>', methods=['DELETE'])
@require_business_api_key
def delete_agent(agent_id):
    """Deletes an agent."""
    if not is_valid_uuid(agent_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid agent_id format"}), 400
    
    business_id = request.args.get('business_id')
    if not business_id:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Missing business_id query parameter"}), 400
    
    if not is_valid_uuid(business_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format"}), 400
    
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
@require_business_api_key
def get_agent(agent_id):
    """Get a specific agent by ID."""
    if not is_valid_uuid(agent_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid agent_id format"}), 400
        
    business_id = request.args.get('business_id')
    if not business_id:
        return jsonify({"error_code": "BAD_REQUEST", "message": "business_id parameter is required"}), 400
        
    if not is_valid_uuid(business_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format"}), 400
        
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT agent_id, agent_name, business_id,
                   created_at 
            FROM agents
            WHERE agent_id = %s AND business_id = %s
            """,
            (agent_id, business_id)
        )
        
        row = cursor.fetchone()
        if not row:
            return jsonify({"error_code": "NOT_FOUND", "message": f"Agent with ID {agent_id} not found"}), 404
            
        # Convert UUIDs to strings and handle JSON fields
        agent = {
            "agent_id": str(row[0]) if isinstance(row[0], uuid.UUID) else row[0],
            "agent_name": row[1],
            "business_id": str(row[2]) if isinstance(row[2], uuid.UUID) else row[2],
            "created_at": row[3].isoformat() if row[3] else None
        }
        
        return jsonify(agent), 200
        
    except Exception as e:
        error_detail = str(e)
        log.error(f"Error fetching agent {agent_id} for business {business_id}: {error_detail}", exc_info=True)
        return jsonify({"error_code": "SERVER_ERROR", "message": "Failed to fetch agent", "details": error_detail}), 500
    finally:
        if conn:
            release_db_connection(conn)