import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv
import uuid
import requests
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

def get_test_stage():
    """Find an existing stage to use for testing"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        # Find a stage with associated templates
        cursor.execute("""
            SELECT 
                s.stage_id, s.business_id, s.stage_name,
                s.stage_selection_template_id, s.data_extraction_template_id, s.response_generation_template_id
            FROM stages s
            WHERE s.stage_selection_template_id IS NOT NULL
            LIMIT 1
        """)
        
        stage = cursor.fetchone()
        if not stage:
            print("No suitable stage found for testing")
            return None
        
        print(f"Found stage: {stage['stage_id']}, name: {stage['stage_name']}")
        
        # Get API key for this business
        cursor.execute("SELECT api_key FROM businesses WHERE business_id = %s", (stage['business_id'],))
        business = cursor.fetchone()
        
        if not business:
            print(f"No business found with ID {stage['business_id']}")
            return None
        
        # Get template details
        template_ids = [
            stage['stage_selection_template_id'],
            stage['data_extraction_template_id'],
            stage['response_generation_template_id']
        ]
        
        template_ids = [tid for tid in template_ids if tid]
        if not template_ids:
            print("No template IDs found for this stage")
            return None
        
        # Get template details
        placeholders = ', '.join(['%s'] * len(template_ids))
        cursor.execute(f"""
            SELECT template_id, template_name, template_text
            FROM prompt_templates
            WHERE template_id IN ({placeholders})
        """, template_ids)
        
        templates = cursor.fetchall()
        
        return {
            'stage_id': stage['stage_id'],
            'business_id': stage['business_id'],
            'api_key': business['api_key'],
            'stage_name': stage['stage_name'],
            'templates': [
                {'id': t['template_id'], 'name': t['template_name'], 'text': t['template_text']} 
                for t in templates
            ]
        }
    finally:
        conn.close()

def update_template_via_api(stage_data):
    """Update a template using the API"""
    api_url = 'http://localhost:8000'  # Change if using a different host/port
    
    stage_id = stage_data['stage_id']
    api_key = stage_data['api_key']
    
    # Prepare update data
    template = stage_data['templates'][0]  # Use the first template
    new_text = template['text'] + "\n\n# This is a test update " + str(uuid.uuid4())
    
    # Determine which config field to use
    cursor = psycopg2.connect(**DB_CONFIG).cursor(cursor_factory=DictCursor)
    cursor.execute("""
        SELECT 
            CASE 
                WHEN stage_selection_template_id = %s THEN 'stage_selection_config'
                WHEN data_extraction_template_id = %s THEN 'data_extraction_config'
                WHEN response_generation_template_id = %s THEN 'response_generation_config'
                ELSE NULL
            END as config_field
        FROM stages 
        WHERE stage_id = %s
    """, (template['id'], template['id'], template['id'], stage_id))
    
    result = cursor.fetchone()
    config_field = result[0] if result else 'stage_selection_config'
    
    # Create update payload
    update_data = {
        'business_id': stage_data['business_id'],
        'stage_name': stage_data['stage_name'] + ' (updated)',
        config_field: {
            'template_text': new_text
        }
    }
    
    print(f"Updating stage {stage_id} with data: {json.dumps(update_data, indent=2)}")
    
    # Make API request
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'businessApiKey={api_key}'
    }
    
    response = requests.put(
        f"{api_url}/stages/{stage_id}",
        data=json.dumps(update_data),
        headers=headers
    )
    
    print(f"API Response: {response.status_code}")
    print(response.text)
    
    # Check if update was successful
    if response.status_code == 200:
        print("Template update successful!")
        
        # Verify update in database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("""
            SELECT template_text FROM prompt_templates
            WHERE template_id = %s
        """, (template['id'],))
        
        updated_template = cursor.fetchone()
        if updated_template and updated_template['template_text'] == new_text:
            print("Database verification successful - template text was updated")
        else:
            print("Database verification failed - template text was not updated")
            if updated_template:
                print(f"Current text: {updated_template['template_text'][:100]}...")
        
        conn.close()
    else:
        print("Template update failed!")

def update_template_directly():
    """Update a template directly in the database"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        # Find a template
        cursor.execute("SELECT template_id, template_name, template_text FROM prompt_templates LIMIT 1")
        template = cursor.fetchone()
        
        if not template:
            print("No templates found in database")
            return
        
        # Update the template
        template_id = template['template_id']
        new_text = template['template_text'] + "\n\n# This is a direct database update " + str(uuid.uuid4())
        
        cursor.execute("""
            UPDATE prompt_templates
            SET template_text = %s
            WHERE template_id = %s
        """, (new_text, template_id))
        
        conn.commit()
        
        # Verify update
        cursor.execute("SELECT template_text FROM prompt_templates WHERE template_id = %s", (template_id,))
        updated = cursor.fetchone()
        
        if updated and updated['template_text'] == new_text:
            print(f"Direct database update successful for template {template_id}")
        else:
            print(f"Direct database update failed for template {template_id}")
    finally:
        conn.close()

def main():
    print("Template Update Test Tool")
    print("========================")
    
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
    
    print("\n1. Test API Update")
    print("2. Test Direct Database Update")
    print("3. Run Both Tests")
    
    choice = input("\nSelect a test to run (1-3): ")
    
    if choice in ('1', '3'):
        print("\nRunning API Update Test...")
        stage_data = get_test_stage()
        if stage_data:
            update_template_via_api(stage_data)
    
    if choice in ('2', '3'):
        print("\nRunning Direct Database Update Test...")
        update_template_directly()

if __name__ == "__main__":
    main()