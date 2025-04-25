import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "icmp_db"),
    "user": os.environ.get("DB_USER", "icmp_user"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432")
}

def main():
    try:
        print("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Find templates with NULL names
        cursor.execute("SELECT template_id FROM prompt_templates WHERE template_name IS NULL")
        templates_needing_names = cursor.fetchall()
        
        if not templates_needing_names:
            print("No templates found with NULL names.")
            return
            
        print(f"Found {len(templates_needing_names)} templates with NULL names.")
        
        # For each template, find linked stage and update template name
        for template_row in templates_needing_names:
            template_id = template_row[0]
            print(f"Processing template: {template_id}")
            
            # Check if it's linked to a stage
            cursor.execute("""
                SELECT 
                    stage_id, stage_name, 
                    CASE 
                        WHEN stage_selection_template_id = %s THEN 'Stage Selection'
                        WHEN data_extraction_template_id = %s THEN 'Data Extraction'
                        WHEN response_generation_template_id = %s THEN 'Response Generation'
                        ELSE NULL
                    END as template_type
                FROM 
                    stages 
                WHERE 
                    stage_selection_template_id = %s OR 
                    data_extraction_template_id = %s OR 
                    response_generation_template_id = %s
                LIMIT 1
            """, [template_id, template_id, template_id, template_id, template_id, template_id])
            
            stage_row = cursor.fetchone()
            
            if stage_row:
                stage_id = stage_row[0]
                stage_name = stage_row[1] or "Unnamed Stage"
                template_type = stage_row[2]
                
                # Create a new template name
                template_name = f"{stage_name} - {template_type}"
                
                # Update the template name
                cursor.execute(
                    "UPDATE prompt_templates SET template_name = %s WHERE template_id = %s",
                    (template_name, template_id)
                )
                
                print(f"  Updated template with name: {template_name}")
            else:
                # Standalone template, use a generic name
                cursor.execute(
                    "UPDATE prompt_templates SET template_name = %s WHERE template_id = %s",
                    (f"Standalone Template {template_id[:8]}", template_id)
                )
                print(f"  Updated with generic name (not linked to a stage)")
        
        # Commit all updates
        conn.commit()
        print("All template names have been updated successfully.")
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()