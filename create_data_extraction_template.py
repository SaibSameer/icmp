import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv
import uuid
import json

load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "icmp_db"),
    "user": os.environ.get("DB_USER", "icmp_user"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432")
}

def create_data_extraction_template(business_id, template_name, extraction_fields):
    """
    Create a new data extraction template.
    
    Args:
        business_id (str): The business ID
        template_name (str): Name of the template
        extraction_fields (dict): Dictionary of field names and their regex patterns
    """
    try:
        print("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Generate template content from extraction fields
        content = "Extract the following information from the message:\n"
        for field, pattern in extraction_fields.items():
            content += f"- {field}: {pattern}\n"
        
        # Create system prompt
        system_prompt = """You are a data extraction assistant. Extract the requested information from the user's message.
Return the data in JSON format with the specified field names.
If a field is not found in the message, set its value to null."""
        
        # Insert the template
        template_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO templates
            (template_id, business_id, template_name, template_type, content, system_prompt)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING template_id
            """,
            (
                template_id,
                business_id,
                template_name,
                'data_extraction',
                content,
                system_prompt
            )
        )
        
        # Commit the transaction
        conn.commit()
        
        print(f"Created data extraction template: {template_name}")
        print(f"Template ID: {template_id}")
        print("\nTemplate Content:")
        print(content)
        print("\nSystem Prompt:")
        print(system_prompt)
        
        return template_id
        
    except Exception as e:
        print(f"Error creating template: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def main():
    # Example usage
    business_id = "your_business_id"  # Replace with actual business ID
    
    # Define extraction fields and their patterns
    extraction_fields = {
        "name": "(?:name|call me|i am|this is) ([A-Za-z\\s]+)",
        "email": "([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,})",
        "phone": "(\\+\\d{1,3}[-.\\s]?\\(?\\d{3}\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4})",
        "address": "(?:address|location|live at|located at) ([A-Za-z0-9\\s,.-]+)",
        "order_number": "(?:order|order number|order #|order#) ([A-Z0-9-]+)",
        "product_name": "(?:product|item) ([A-Za-z0-9\\s-]+)",
        "quantity": "(?:quantity|qty|amount) (\\d+)"
    }
    
    try:
        template_id = create_data_extraction_template(
            business_id=business_id,
            template_name="Customer Information Extraction",
            extraction_fields=extraction_fields
        )
        print(f"\nTemplate created successfully with ID: {template_id}")
    except Exception as e:
        print(f"Failed to create template: {str(e)}")

if __name__ == "__main__":
    main() 