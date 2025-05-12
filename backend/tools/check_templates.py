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
        
        # List all tables in the database
        print("\nListing all tables:")
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"- {table[0]}")
        
        # Check if prompt_templates table exists
        if any(table[0] == 'prompt_templates' for table in tables):
            print("\nChecking prompt_templates table:")
            cursor.execute("SELECT COUNT(*) FROM prompt_templates;")
            count = cursor.fetchone()[0]
            print(f"Total templates: {count}")
            
            # Count templates by type
            cursor.execute("SELECT template_type, COUNT(*) FROM prompt_templates GROUP BY template_type;")
            type_counts = cursor.fetchall()
            print("\nTemplates by type:")
            for type_count in type_counts:
                print(f"- {type_count[0]}: {type_count[1]}")
            
            # Check for empty template text
            cursor.execute("SELECT COUNT(*) FROM prompt_templates WHERE template_text IS NULL OR template_text = '';")
            empty_count = cursor.fetchone()[0]
            print(f"\nEmpty templates: {empty_count}")
            
            if empty_count > 0:
                print("\nEmpty template records:")
                cursor.execute("SELECT template_id, template_name, template_type FROM prompt_templates WHERE template_text IS NULL OR template_text = '';")
                empty_templates = cursor.fetchall()
                for template in empty_templates:
                    print(f"ID: {template[0]}")
                    print(f"Name: {template[1]}")
                    print(f"Type: {template[2]}")
                    print("-" * 50)
            
            # Show regular template samples
            cursor.execute("SELECT COUNT(*) FROM prompt_templates WHERE template_type NOT LIKE 'default_%';")
            regular_count = cursor.fetchone()[0]
            if regular_count > 0:
                print("\nRegular Template samples (max 5):")
                cursor.execute("SELECT template_id, template_name, template_type, template_text FROM prompt_templates WHERE template_type NOT LIKE 'default_%' LIMIT 5;")
                templates = cursor.fetchall()
                for template in templates:
                    print(f"ID: {template[0]}")
                    print(f"Name: {template[1]}")
                    print(f"Type: {template[2]}")
                    print(f"Text preview: {template[3][:50]}{'...' if len(template[3]) > 50 else ''}")
                    print("-" * 50)
            
            # Show default template samples
            cursor.execute("SELECT COUNT(*) FROM prompt_templates WHERE template_type LIKE 'default_%';")
            default_count = cursor.fetchone()[0]
            if default_count > 0:
                print("\nDefault Template samples (max 5):")
                cursor.execute("SELECT template_id, template_name, template_type, template_text FROM prompt_templates WHERE template_type LIKE 'default_%' LIMIT 5;")
                templates = cursor.fetchall()
                for template in templates:
                    print(f"ID: {template[0]}")
                    print(f"Name: {template[1]}")
                    print(f"Type: {template[2]}")
                    print(f"Text preview: {template[3][:50]}{'...' if len(template[3]) > 50 else ''}")
                    print("-" * 50)
        else:
            print("\nprompt_templates table does not exist!")
            
        # Check if stages table exists and how it's structured
        if any(table[0] == 'stages' for table in tables):
            print("\nChecking stages table structure:")
            cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'stages';")
            columns = cursor.fetchall()
            for col in columns:
                print(f"- {col[0]}: {col[1]}")
                
            # Check a sample of stages data
            print("\nSample stages data (max 5):")
            cursor.execute("SELECT stage_id, stage_name, stage_selection_template_id, data_extraction_template_id, response_generation_template_id FROM stages LIMIT 5;")
            stages = cursor.fetchall()
            for stage in stages:
                print(f"Stage ID: {stage[0]}")
                print(f"Name: {stage[1]}")
                print(f"Selection Template ID: {stage[2]}")
                print(f"Extraction Template ID: {stage[3]}")
                print(f"Response Template ID: {stage[4]}")
                
                # Check template details for this stage
                print("\nTemplate details for this stage:")
                template_ids = [stage[2], stage[3], stage[4]]
                valid_ids = [tid for tid in template_ids if tid is not None]
                
                if valid_ids:
                    # Convert to string format for SQL placeholders
                    placeholders = ', '.join(['%s'] * len(valid_ids))
                    cursor.execute(f"SELECT template_id, template_name, template_type, template_text FROM prompt_templates WHERE template_id IN ({placeholders})", valid_ids)
                    stage_templates = cursor.fetchall()
                    
                    for template in stage_templates:
                        print(f"  Template ID: {template[0]}")
                        print(f"  Name: {template[1]}")
                        print(f"  Type: {template[2]}")
                        if template[3]:
                            print(f"  Text preview: {template[3][:50]}{'...' if len(template[3]) > 50 else ''}")
                        else:
                            print(f"  Text: None or empty")
                        print("  " + "-" * 40)
                else:
                    print("  No template IDs found for this stage")
                
                print("-" * 50)
                
            # Option to check a specific stage
            print("\nWould you like to check a specific stage? Enter stage ID or press Enter to skip:")
            stage_id_input = input()
            
            if stage_id_input:
                try:
                    # Validate UUID format
                    stage_id = uuid.UUID(stage_id_input)
                    cursor.execute("SELECT stage_id, stage_name, stage_selection_template_id, data_extraction_template_id, response_generation_template_id FROM stages WHERE stage_id = %s", (str(stage_id),))
                    stage = cursor.fetchone()
                    
                    if stage:
                        print(f"\nStage details for {stage[0]}:")
                        print(f"Name: {stage[1]}")
                        print(f"Selection Template ID: {stage[2]}")
                        print(f"Extraction Template ID: {stage[3]}")
                        print(f"Response Template ID: {stage[4]}")
                        
                        # Check linked templates
                        print("\nLinked template details:")
                        template_types = ["Selection", "Extraction", "Response"]
                        template_ids = [stage[2], stage[3], stage[4]]
                        
                        for i, template_id in enumerate(template_ids):
                            template_type = template_types[i]
                            if template_id:
                                cursor.execute("SELECT template_id, template_name, template_type, template_text FROM prompt_templates WHERE template_id = %s", (template_id,))
                                template = cursor.fetchone()
                                
                                if template:
                                    print(f"\n{template_type} Template:")
                                    print(f"  ID: {template[0]}")
                                    print(f"  Name: {template[1]}")
                                    print(f"  Type: {template[2]}")
                                    if template[3]:
                                        print(f"  Text: {template[3]}")
                                    else:
                                        print(f"  Text: None or empty")
                                else:
                                    print(f"\n{template_type} Template: ID exists in stage but no matching template found!")
                            else:
                                print(f"\n{template_type} Template: No template ID set")
                    else:
                        print(f"No stage found with ID: {stage_id}")
                except ValueError:
                    print("Invalid UUID format")
    
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()