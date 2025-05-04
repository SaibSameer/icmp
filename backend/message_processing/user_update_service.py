# -*- coding: utf-8 -*-"""
from typing import Dict, Any, Optional
import logging
import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv

log = logging.getLogger(__name__)

class UserUpdateService:
    """Service for updating user information from extracted data."""
    
    def __init__(self):
        load_dotenv()
        self.db_config = {
            "dbname": os.getenv("DB_NAME", "icmp_db"),
            "user": os.getenv("DB_USER", "icmp_user"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432")
        }
    
    def _get_db_connection(self):
        """Create and return a database connection."""
        return psycopg2.connect(**self.db_config)
    
    def create_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new user in the database.
        
        Args:
            user_id: UUID of the user to create
            user_data: Dictionary containing user data
            
        Returns:
            Created user data or None if creation fails
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    # Set default values for required fields if not provided
                    first_name = user_data.get('first_name', 'Guest')
                    last_name = user_data.get('last_name', 'User')
                    email = user_data.get('email', f"{user_id}@placeholder.com")
                    
                    # Insert the new user
                    cursor.execute(
                        """
                        INSERT INTO users (user_id, first_name, last_name, email)
                        VALUES (%s, %s, %s, %s)
                        RETURNING *
                        """,
                        (user_id, first_name, last_name, email)
                    )
                    
                    conn.commit()
                    new_user = cursor.fetchone()
                    return dict(new_user) if new_user else None
                    
        except Exception as e:
            log.error(f"Error creating user {user_id}: {str(e)}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update user information in the database. Creates user if does not exist.
        
        Args:
            user_id: UUID of the user to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated user data or None if update fails
        """
        if not update_data:
            log.warning("No data provided for update")
            return None
        
        allowed_fields = ["first_name", "last_name", "email", "phone", "address"]
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        if not filtered_data:
            log.warning("No valid fields to update")
            return None
            
        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    # Check if user exists
                    cursor.execute(
                        "SELECT * FROM users WHERE user_id = %s",
                        (user_id,)
                    )
                    user_exists = cursor.fetchone() is not None
                    
                    if not user_exists:
                        log.info(f"User {user_id} not found, creating new user")
                        return self.create_user(user_id, filtered_data)
                    
                    # Build update query
                    set_clause = ", ".join([f"{k} = %s" for k in filtered_data.keys()])
                    values = list(filtered_data.values())
                    values.append(user_id)
                    
                    # Execute update
                    cursor.execute(
                        f"UPDATE users SET {set_clause} WHERE user_id = %s RETURNING *",
                        values
                    )
                    
                    conn.commit()
                    updated_user = cursor.fetchone()
                    return dict(updated_user) if updated_user else None
                    
        except Exception as e:
            # Log the error safely before re-raising
            log.error(f"Error during update_user for {user_id}: {e!r}") 
            # Re-raise the original exception to be caught by the caller
            raise e