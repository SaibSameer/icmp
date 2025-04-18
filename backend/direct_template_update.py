import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv
import uuid
import sys

load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "icmp_db"),
    "user": os.environ.get("DB_USER", "icmp_user"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432")
}

def update_all_templates():
    """Update all templates with new content"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        # Find all templates
        cursor.execute("SELECT template_id, template_name, template_text FROM prompt_templates")
        templates = cursor.fetchall()
        
        if not templates:
            print("No templates found in database")
            return
        
        print(f"Found {len(templates)} templates")
        
        # Update each template
        for template in templates:
            template_id = template['template_id']
            template_name = template['template_name'] or "Unnamed Template"
            template_text = template['template_text'] or ""
            
            # Create new text with a timestamp to ensure it's different
            new_text = template_text + f"\n\n# Updated at {uuid.uuid4()}"
            
            cursor.execute("""
                UPDATE prompt_templates
                SET template_text = %s
                WHERE template_id = %s
            """, (new_text, template_id))
            
            print(f"Updated template: {template_id} - {template_name}")
        
        conn.commit()
        print("\nAll templates updated successfully!")
        
        # Verify updates
        print("\nVerifying updates...")
        cursor.execute("SELECT template_id, template_name, template_text FROM prompt_templates")
        updated_templates = cursor.fetchall()
        
        for template in updated_templates:
            template_id = template['template_id']
            template_text = template['template_text'] or ""
            
            if "# Updated at" in template_text:
                print(f"Template {template_id} verified ✓")
            else:
                print(f"Template {template_id} update failed ✗")
    
    finally:
        conn.close()

def update_specific_template(template_id=None):
    """Update a specific template by ID"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        # If no template ID provided, list all and ask user to select
        if not template_id:
            cursor.execute("SELECT template_id, template_name, template_text FROM prompt_templates")
            templates = cursor.fetchall()
            
            if not templates:
                print("No templates found in database")
                return
            
            print("\nAvailable templates:")
            for i, template in enumerate(templates, 1):
                name = template['template_name'] or "Unnamed Template"
                text_preview = template['template_text'][:50] + "..." if template['template_text'] else "No text"
                print(f"{i}. {name} ({template['template_id']}) - {text_preview}")
            
            choice = input("\nEnter template number to update (or 'q' to quit): ")
            if choice.lower() == 'q':
                return
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(templates):
                    template_id = templates[index]['template_id']
                else:
                    print("Invalid selection")
                    return
            except ValueError:
                print("Invalid input")
                return
        
        # Get template details
        cursor.execute("""
            SELECT template_id, template_name, template_text 
            FROM prompt_templates
            WHERE template_id = %s
        """, (template_id,))
        
        template = cursor.fetchone()
        if not template:
            print(f"Template with ID {template_id} not found")
            return
        
        template_name = template['template_name'] or "Unnamed Template"
        template_text = template['template_text'] or ""
        
        print(f"\nSelected template: {template_name} ({template_id})")
        print(f"Current text:\n{template_text}\n")
        
        # Update template with new content
        print("Updating template...")
        new_text = template_text + f"\n\n# Updated at {uuid.uuid4()}"
        
        cursor.execute("""
            UPDATE prompt_templates
            SET template_text = %s
            WHERE template_id = %s
        """, (new_text, template_id))
        
        conn.commit()
        print(f"Template {template_id} updated successfully!")
        
        # Verify update
        cursor.execute("""
            SELECT template_text 
            FROM prompt_templates
            WHERE template_id = %s
        """, (template_id,))
        
        updated = cursor.fetchone()
        if updated and "# Updated at" in updated['template_text']:
            print("Verification successful - template was updated")
        else:
            print("Verification failed - template was not updated")
        
    finally:
        conn.close()

def main():
    print("Direct Template Update Tool")
    print("===========================")
    
    # Check if prompt_templates table exists
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'prompt_templates'
        );
    """)
    
    if not cursor.fetchone()[0]:
        print("prompt_templates table does not exist in the database")
        conn.close()
        return
    
    conn.close()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            update_all_templates()
            return
        elif sys.argv[1] == "--id" and len(sys.argv) > 2:
            update_specific_template(sys.argv[2])
            return
    
    print("\n1. Update all templates")
    print("2. Update a specific template")
    print("3. Exit")
    
    choice = input("\nSelect an option (1-3): ")
    
    if choice == '1':
        update_all_templates()
    elif choice == '2':
        update_specific_template()
    elif choice == '3':
        print("Exiting...")
    else:
        print("Invalid option")

if __name__ == "__main__":
    main()