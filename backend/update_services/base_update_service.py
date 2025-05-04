from typing import Dict, Any, Optional, List
import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv
import uuid
import logging

log = logging.getLogger(__name__)

class BaseUpdateService:
    """Base class for update services providing common database operations."""
    
    def __init__(self):
        load_dotenv()
        self.table = None  # To be set by child classes
        self.id_field = None  # To be set by child classes
        self.allowed_fields = []  # To be set by child classes
        
        # Database configuration
        self.db_config = {
            "dbname": os.getenv("DB_NAME", "icmp_db"),
            "user": os.getenv("DB_USER", "icmp_user"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432")
        }
        
    def _get_db_connection(self):
        """
        Create and return a database connection.
        
        Returns:
            A psycopg2 connection object
        """
        return psycopg2.connect(**self.db_config)
        
    def _validate_uuid(self, id_value: str) -> bool:
        """
        Validate if a string is a valid UUID.
        
        Args:
            id_value: String to validate
            
        Returns:
            True if valid UUID, False otherwise
        """
        try:
            uuid.UUID(str(id_value))
            return True
        except ValueError:
            return False
            
    def _get_record(self, table: str, id_field: str, id_value: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a record from the database.
        
        Args:
            table: Table name
            id_field: ID field name
            id_value: ID value
            
        Returns:
            Dictionary containing the record data or None if not found
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(
                        f"SELECT * FROM {table} WHERE {id_field} = %s",
                        (id_value,)
                    )
                    result = cur.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            log.error(f"Error retrieving record from {table}: {str(e)}")
            return None
                
    def _execute_update(self, table: str, id_field: str, id_value: str, update_data: Dict[str, Any]) -> bool:
        """
        Execute an update operation on the database.
        
        Args:
            table: Table name
            id_field: ID field name
            id_value: ID value
            update_data: Dictionary containing fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        if not update_data:
            return False
            
        set_clause = ", ".join([f"{k} = %s" for k in update_data.keys()])
        values = list(update_data.values())
        values.append(id_value)
        
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"UPDATE {table} SET {set_clause} WHERE {id_field} = %s",
                        values
                    )
                    conn.commit()
                    return True
        except Exception as e:
            log.error(f"Error updating record in {table}: {str(e)}")
            return False

    def _validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """
        Validate required fields in the data.
        
        Args:
            data: Dictionary containing the data to validate
            required_fields: List of field names that are required
            
        Returns:
            List of missing required fields
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)
        return missing_fields
        
    def _create_record(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new record in the database.
        
        Args:
            table: Table name
            data: Dictionary containing the data to insert
            
        Returns:
            Dictionary containing the created record or None if creation fails
        """
        if not data:
            return None
            
        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    # Build insert query
                    fields = list(data.keys())
                    placeholders = ", ".join(["%s"] * len(fields))
                    field_names = ", ".join(fields)
                    
                    # Execute insert
                    cur.execute(
                        f"INSERT INTO {table} ({field_names}) VALUES ({placeholders}) RETURNING *",
                        list(data.values())
                    )
                    
                    conn.commit()
                    result = cur.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            log.error(f"Error creating record in {table}: {str(e)}")
            return None