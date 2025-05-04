from typing import Dict, Any, Optional
from .base_update_service import BaseUpdateService
import logging
import uuid

log = logging.getLogger(__name__)

class BusinessUpdateService(BaseUpdateService):
    """Service for updating business information."""
    
    def __init__(self):
        super().__init__()
        self.table = "businesses"
        self.id_field = "business_id"
        self.allowed_fields = [
            "business_name",
            "business_description",
            "email",
            "phone",
            "address",
            "status",
            "metadata"
        ]
        
    def create_business(self, business_id: str, business_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new business in the database.
        
        Args:
            business_id: UUID of the business to create
            business_data: Dictionary containing business data
            
        Returns:
            Created business data or None if creation fails
        """
        # Validate business ID
        if not self._validate_uuid(business_id):
            log.error(f"Invalid business ID format: {business_id}")
            return None
            
        # Set default values for required fields if not provided
        business_name = business_data.get('business_name', 'New Business')
        business_description = business_data.get('business_description', '')
        email = business_data.get('email', f"{business_id}@placeholder.com")
        
        # Prepare data for insertion
        insert_data = {
            self.id_field: business_id,
            'business_name': business_name,
            'business_description': business_description,
            'email': email
        }
        
        # Add any additional allowed fields that are present
        for field in self.allowed_fields:
            if field in business_data and field not in insert_data:
                insert_data[field] = business_data[field]
        
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
                    new_business = cursor.fetchone()
                    return dict(new_business) if new_business else None
                    
        except Exception as e:
            log.error(f"Error creating business {business_id}: {str(e)}")
            return None
        
    def update_business(self, business_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update business information.
        
        Args:
            business_id: UUID of the business to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated business data or None if update fails
        """
        # Validate business ID
        if not self._validate_uuid(business_id):
            log.error(f"Invalid business ID format: {business_id}")
            return None
            
        # Filter allowed fields
        filtered_data = {k: v for k, v in update_data.items() if k in self.allowed_fields}
        if not filtered_data:
            log.warning("No valid fields to update")
            return None
            
        # Check if business exists
        existing_business = self._get_record(self.table, self.id_field, business_id)
        if not existing_business:
            log.info(f"Business not found: {business_id}, creating new business")
            return self.create_business(business_id, filtered_data)
            
        # Execute update
        if self._execute_update(self.table, self.id_field, business_id, filtered_data):
            return self._get_record(self.table, self.id_field, business_id)
        return None
        
    def update_business_from_extracted_data(self, business_id: str, extracted_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update business information from extracted data.
        
        Args:
            business_id: UUID of the business to update
            extracted_data: Dictionary containing extracted data
            
        Returns:
            Updated business data or None if update fails
        """
        # Map extracted data fields to business fields
        field_mapping = {
            "business_name": "business_name",
            "business_description": "business_description",
            "business_email": "email",
            "business_phone": "phone",
            "business_address": "address"
        }
        
        update_data = {}
        for extracted_field, business_field in field_mapping.items():
            if extracted_field in extracted_data:
                update_data[business_field] = extracted_data[extracted_field]
                
        # Add metadata if present
        if "metadata" in extracted_data:
            update_data["metadata"] = extracted_data["metadata"]
            
        if update_data:
            return self.update_business(business_id, update_data)
        return None