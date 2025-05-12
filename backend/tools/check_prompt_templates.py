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

def main():
    try:
        print("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Check prompt_templates table structure
        print("\nChecking prompt_templates table structure:")
        cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'prompt_templates';")
        columns = cursor.fetchall()
        for col in columns:
            print(f"- {col[0]}: {col[1]}")
        
        # Count templates
        cursor.execute("SELECT COUNT(*) FROM prompt_templates;")
        count = cursor.fetchone()[0]
        print(f"\nTotal templates in prompt_templates: {count}")
        
        # Check for empty template text
        cursor.execute("SELECT COUNT(*) FROM prompt_templates WHERE template_text IS NULL OR template_text = '';")
        empty_count = cursor.fetchone()[0]
        print(f"Empty templates: {empty_count}")
        
        # Show some template records
        if count > 0:
            print("\nTemplate records (max 10):")
            cursor.execute("SELECT template_id, template_name, template_text FROM prompt_templates LIMIT 10;")
            templates = cursor.fetchall()
            for template in templates:
                print(f"ID: {template[0]}")
                print(f"Name: {template[1]}")
                if template[2]:
                    print(f"Text preview: {template[2][:50]}{'...' if len(template[2]) > 50 else ''}")
                else:
                    print("Text: None or empty")
                print("-" * 50)
        
        # Check stages with template references
        print("\nChecking stages with template references:")
        cursor.execute("""
            SELECT stage_id, stage_name, 
                   stage_selection_template_id, data_extraction_template_id, response_generation_template_id,
                   selection_template_id, extraction_template_id, response_template_id
            FROM stages
            LIMIT 5;
        """)
        stages = cursor.fetchall()
        for stage in stages:
            print(f"Stage ID: {stage['stage_id']}")
            print(f"Name: {stage['stage_name']}")
            print(f"New template IDs:")
            print(f"  - Selection: {stage['stage_selection_template_id']}")
            print(f"  - Extraction: {stage['data_extraction_template_id']}")
            print(f"  - Response: {stage['response_generation_template_id']}")
            print(f"Old template IDs:")
            print(f"  - Selection: {stage['selection_template_id']}")
            print(f"  - Extraction: {stage['extraction_template_id']}")
            print(f"  - Response: {stage['response_template_id']}")
            
            # Check template details
            template_ids = []
            if stage['stage_selection_template_id']:
                template_ids.append(stage['stage_selection_template_id'])
            elif stage['selection_template_id']:
                template_ids.append(stage['selection_template_id'])
                
            if stage['data_extraction_template_id']:
                template_ids.append(stage['data_extraction_template_id'])
            elif stage['extraction_template_id']:
                template_ids.append(stage['extraction_template_id'])
                
            if stage['response_generation_template_id']:
                template_ids.append(stage['response_generation_template_id'])
            elif stage['response_template_id']:
                template_ids.append(stage['response_template_id'])
            
            if template_ids:
                print("\nTemplate details for this stage:")
                placeholders = ', '.join(['%s'] * len(template_ids))
                try:
                    cursor.execute(f"SELECT template_id, template_name, template_text FROM prompt_templates WHERE template_id IN ({placeholders})", template_ids)
                    stage_templates = cursor.fetchall()
                    
                    for template in stage_templates:
                        print(f"  Template ID: {template[0]}")
                        print(f"  Name: {template[1]}")
                        if template[2]:
                            print(f"  Text preview: {template[2][:50]}{'...' if len(template[2]) > 50 else ''}")
                        else:
                            print(f"  Text: None or empty")
                        print("  " + "-" * 40)
                except Exception as e:
                    print(f"  Error retrieving templates: {str(e)}")
            
            print("-" * 50)
            
        # Option to check a specific stage or template
        print("\nWould you like to check a specific template? Enter template ID or press Enter to skip:")
        template_id_input = input()
        
        if template_id_input:
            try:
                cursor.execute("SELECT * FROM prompt_templates WHERE template_id = %s", (template_id_input,))
                template = cursor.fetchone()
                
                if template:
                    print(f"\nTemplate details for {template['template_id']}:")
                    for key, value in template.items():
                        if key == 'template_text':
                            print(f"{key}: {value}")
                        else:
                            print(f"{key}: {value}")
                else:
                    print(f"No template found with ID: {template_id_input}")
            except Exception as e:
                print(f"Error retrieving template: {str(e)}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()