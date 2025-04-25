import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "icmp_db"),
    "user": os.environ.get("DB_USER", "icmp_user"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432")
}

# Default template texts
DEFAULT_TEMPLATES = {
    "stage_selection": """You are the Stage Selection Engine.

User request: {user_message}

Your task is to select the appropriate stage to handle this request based on its content.
Analyze the message carefully and select the most appropriate stage.

Stage options:
{stage_options}

Return only the stage ID that should handle this message.""",

    "data_extraction": """Extract key information from the following user message.

User message: {user_message}

Extract the following details (return as JSON):
- Main request type
- Specific entities mentioned
- Any time constraints or deadlines
- Priority level (if mentioned)
- Any additional relevant details""",

    "response_generation": """Generate a professional and helpful response to the user's query.

User query: {user_message}

Context information: {context}

Instructions:
- Be concise and directly address the user's query
- Include relevant information from the context provided
- Maintain a professional but friendly tone
- If you need more information, politely ask follow-up questions
- Format your response for readability"""
}

def main():
    try:
        print("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Check if default_templates table exists
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'default_templates')")
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("The default_templates table doesn't exist. Creating it...")
            cursor.execute("""
                CREATE TABLE default_templates (
                    template_id UUID PRIMARY KEY,
                    template_name VARCHAR(255) NOT NULL,
                    template_text TEXT NOT NULL,
                    variables TEXT[] DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            conn.commit()
            print("Table created successfully.")
        
        # Find empty templates
        cursor.execute("SELECT template_id, template_name FROM default_templates WHERE template_text IS NULL OR template_text = ''")
        empty_templates = cursor.fetchall()
        
        if empty_templates:
            print(f"Found {len(empty_templates)} empty templates. Fixing them...")
            
            for template in empty_templates:
                template_id = template[0]
                template_name = template[1].lower()
                template_text = None
                
                # Determine which default template to use based on name
                if "selection" in template_name:
                    template_text = DEFAULT_TEMPLATES["stage_selection"]
                elif "extraction" in template_name:
                    template_text = DEFAULT_TEMPLATES["data_extraction"]
                elif "response" in template_name or "generation" in template_name:
                    template_text = DEFAULT_TEMPLATES["response_generation"]
                else:
                    # Generic template if we can't determine the type
                    template_text = "Default template text. Please update with appropriate content."
                
                # Update the template
                cursor.execute(
                    "UPDATE default_templates SET template_text = %s WHERE template_id = %s",
                    (template_text, template_id)
                )
                print(f"Fixed template: {template_id} - {template_name}")
            
            conn.commit()
            print("All empty templates have been fixed.")
        else:
            print("No empty templates found.")
        
        # Check stages with missing template references
        cursor.execute("""
            SELECT stage_id, stage_name 
            FROM stages 
            WHERE stage_selection_template_id IS NULL 
               OR data_extraction_template_id IS NULL 
               OR response_generation_template_id IS NULL
        """)
        stages_with_missing_templates = cursor.fetchall()
        
        if stages_with_missing_templates:
            print(f"\nFound {len(stages_with_missing_templates)} stages with missing template references.")
            
            fix_stages = input("Do you want to fix these stages by creating missing templates? (y/n): ")
            if fix_stages.lower() == 'y':
                for stage in stages_with_missing_templates:
                    stage_id = stage[0]
                    stage_name = stage[1]
                    
                    # Get current template IDs
                    cursor.execute("""
                        SELECT stage_selection_template_id, data_extraction_template_id, response_generation_template_id
                        FROM stages
                        WHERE stage_id = %s
                    """, (stage_id,))
                    template_ids = cursor.fetchone()
                    
                    # Create missing templates
                    template_fields = ['stage_selection_template_id', 'data_extraction_template_id', 'response_generation_template_id']
                    template_types = ['stage_selection', 'data_extraction', 'response_generation']
                    template_names = [f"{stage_name} - Stage Selection", f"{stage_name} - Data Extraction", f"{stage_name} - Response Generation"]
                    
                    updates = {}
                    
                    for i, field in enumerate(template_fields):
                        if template_ids[i] is None:
                            # Create new template
                            new_template_id = str(uuid.uuid4())
                            cursor.execute(
                                """
                                INSERT INTO default_templates (template_id, template_name, template_text, variables)
                                VALUES (%s, %s, %s, %s)
                                """,
                                (new_template_id, template_names[i], DEFAULT_TEMPLATES[template_types[i]], ['user_message'])
                            )
                            updates[field] = new_template_id
                            print(f"Created new {template_types[i]} template for stage {stage_name}")
                    
                    # Update stage if needed
                    if updates:
                        set_clause = ", ".join([f"{field} = %s" for field in updates.keys()])
                        query = f"UPDATE stages SET {set_clause} WHERE stage_id = %s"
                        params = list(updates.values()) + [stage_id]
                        cursor.execute(query, params)
                        print(f"Updated stage {stage_name} with new template references")
                
                conn.commit()
                print("All stages have been fixed with proper template references.")
        else:
            print("All stages have valid template references.")
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()