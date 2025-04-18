from typing import Dict, Any, Optional
from .base_update_service import BaseUpdateService
import logging
import uuid

log = logging.getLogger(__name__)

class UserUpdateService(BaseUpdateService):
    """Service for updating user information."""
    
    def __init__(self):
        super().__init__()
        self.table = "users"
        self.id_field = "user_id"
        self.allowed_fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "status",
            "preferences",
            "metadata"
        ]
        
    def create_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new user in the database.
        
        Args:
            user_id: UUID of the user to create
            user_data: Dictionary containing user data
            
        Returns:
            Created user data or None if creation fails
        """
        # Validate user ID
        if not self._validate_uuid(user_id):
            log.error(f"Invalid user ID format: {user_id}")
            return None
            
        # Set default values for required fields if not provided
        first_name = user_data.get('first_name', 'Guest')
        last_name = user_data.get('last_name', 'User')
        email = user_data.get('email', f"{user_id}@placeholder.com")
        
        # Prepare data for insertion
        insert_data = {
            self.id_field: user_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email
        }
        
        # Add any additional allowed fields that are present
        for field in self.allowed_fields:
            if field in user_data and field not in insert_data:
                insert_data[field] = user_data[field]
        
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Build insert query
                    fields = list(insert_data.keys())
                    placeholders = ", ".join(["%s"] * len(fields))
                    field_names = ", ".join(fields)
                    
                    # Execute insert
                    cursor.execute(
                        f"INSERT INTO {self.table} ({field_names}) VALUES ({placeholders}) RETURNING *",
                        list(insert_data.values())
                    )
                    
                    conn.commit()
                    new_user = cursor.fetchone()
                    return dict(new_user) if new_user else None
                    
        except Exception as e:
            log.error(f"Error creating user {user_id}: {str(e)}")
            return None
        
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update user information.
        
        Args:
            user_id: UUID of the user to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated user data or None if update fails
        """
        # Validate user ID
        if not self._validate_uuid(user_id):
            log.error(f"Invalid user ID format: {user_id}")
            return None
            
        # Filter allowed fields
        filtered_data = {k: v for k, v in update_data.items() if k in self.allowed_fields}
        if not filtered_data:
            log.warning("No valid fields to update")
            return None
            
        # Check if user exists
        existing_user = self._get_record(self.table, self.id_field, user_id)
        if not existing_user:
            log.info(f"User not found: {user_id}, creating new user")
            return self.create_user(user_id, filtered_data)
            
        # Execute update
        if self._execute_update(self.table, self.id_field, user_id, filtered_data):
            return self._get_record(self.table, self.id_field, user_id)
        return None
        
    def update_user_from_extracted_data(self, user_id: str, extracted_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update user information from extracted data.
        
        Args:
            user_id: UUID of the user to update
            extracted_data: Dictionary containing extracted data
            
        Returns:
            Updated user data or None if update fails
        """
        # Map extracted data fields to user fields
        field_mapping = {
            "user_name": "first_name",
            "user_email": "email",
            "user_phone": "phone",
            "user_address": "address"
        }
        
        update_data = {}
        for extracted_field, user_field in field_mapping.items():
            if extracted_field in extracted_data:
                update_data[user_field] = extracted_data[extracted_field]
                
        # Add preferences if present
        if "preferences" in extracted_data:
            update_data["preferences"] = extracted_data["preferences"]
            
        # Add metadata if present
        if "metadata" in extracted_data:
            update_data["metadata"] = extracted_data["metadata"]
            
        if update_data:
            return self.update_user(user_id, update_data)
        return None 