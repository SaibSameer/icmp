import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv
import uuid
import json
import requests

load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "icmp_db"),
    "user": os.environ.get("DB_USER", "icmp_user"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432")
}

def get_stage_and_templates(stage_id=None):
    """Get a stage and its associated templates"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    try:
        # List stages if no ID provided
        if not stage_id:
            cursor.execute("""
                SELECT stage_id, stage_name, business_id, 
                       stage_selection_template_id, data_extraction_template_id, response_generation_template_id 
                FROM stages 
                WHERE stage_selection_template_id IS NOT NULL
                   OR data_extraction_template_id IS NOT NULL
                   OR response_generation_template_id IS NOT NULL
                LIMIT 10
            """)
            
            stages = cursor.fetchall()
            if not stages:
                print("No stages with templates found")
                return None
                
            print("\nAvailable stages:")
            for i, stage in enumerate(stages, 1):
                print(f"{i}. {stage['stage_name']} ({stage['stage_id']})")
                
            choice = input("\nSelect a stage (1-10): ")
            try:
                index = int(choice) - 1
                if 0 <= index < len(stages):
                    stage_id = stages[index]['stage_id']
                else:
                    print("Invalid selection")
                    return None
            except ValueError:
                print("Invalid input")
                return None
        
        # Get stage details
        cursor.execute("""
            SELECT *
            FROM stages
            WHERE stage_id = %s
        """, (stage_id,))
        
        stage = cursor.fetchone()
        if not stage:
            print(f"Stage {stage_id} not found")
            return None
            
        # Get template details
        template_ids = []
        template_mappings = {}
        
        if stage['stage_selection_template_id']:
            template_ids.append(stage['stage_selection_template_id'])
            template_mappings[stage['stage_selection_template_id']] = 'stage_selection_config'
            
        if stage['data_extraction_template_id']:
            template_ids.append(stage['data_extraction_template_id'])
            template_mappings[stage['data_extraction_template_id']] = 'data_extraction_config'
            
        if stage['response_generation_template_id']:
            template_ids.append(stage['response_generation_template_id'])
            template_mappings[stage['response_generation_template_id']] = 'response_generation_config'
            
        if not template_ids:
            print(f"Stage {stage_id} has no associated templates")
            return None
            
        # Get template content
        placeholders = ', '.join(['%s'] * len(template_ids))
        cursor.execute(f"""
            SELECT template_id, template_name, template_text
            FROM prompt_templates
            WHERE template_id IN ({placeholders})
        """, template_ids)
        
        templates = cursor.fetchall()
        templates_dict = {t['template_id']: t for t in templates}
        
        # Get business API key
        cursor.execute("""
            SELECT api_key 
            FROM businesses
            WHERE business_id = %s
        """, (stage['business_id'],))
        
        business = cursor.fetchone()
        api_key = business['api_key'] if business else None
        
        result = {
            'stage': dict(stage),
            'api_key': api_key,
            'templates': templates_dict,
            'template_mappings': template_mappings
        }
        
        return result
        
    finally:
        conn.close()

def simulate_frontend_update(stage_data, api_port=5000):
    """Simulate a frontend request to update a stage with templates"""
    stage = stage_data['stage']
    templates = stage_data['templates']
    template_mappings = stage_data['template_mappings']
    api_key = stage_data['api_key']
    
    if not api_key:
        print("No API key available for this business")
        return
    
    # Create update payload that represents frontend form submission
    update_data = {
        'business_id': stage['business_id'],
        'stage_name': stage['stage_name'],
        'stage_description': stage['stage_description'],
        'stage_type': stage['stage_type'],
        'agent_id': stage['agent_id']
    }
    
    # Add template configs
    for template_id, config_field in template_mappings.items():
        if template_id in templates:
            template = templates[template_id]
            # Add a unique marker to the template text to verify update
            new_text = template['template_text'] + f"\n\n# Frontend update test {uuid.uuid4()}"
            
            update_data[config_field] = {
                'template_text': new_text,
                'template_id': template_id
            }
    
    print(f"\nUpdate payload prepared:")
    print(json.dumps(update_data, indent=2))
    
    # Make API request
    try:
        url = f"http://localhost:{api_port}/stages/{stage['stage_id']}"
        print(f"\nSending PUT request to: {url}")
        
        headers = {
            'Content-Type': 'application/json',
            'Cookie': f'businessApiKey={api_key}'
        }
        
        response = requests.put(
            url,
            data=json.dumps(update_data),
            headers=headers
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print("\nVerifying template updates in database...")
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor(cursor_factory=DictCursor)
            
            for template_id in templates:
                cursor.execute("""
                    SELECT template_text
                    FROM prompt_templates
                    WHERE template_id = %s
                """, (template_id,))
                
                updated = cursor.fetchone()
                if updated and "# Frontend update test" in updated['template_text']:
                    print(f"Template {template_id} successfully updated ✓")
                else:
                    print(f"Template {template_id} update failed ✗")
                    
            conn.close()
        
    except Exception as e:
        print(f"Error making API request: {str(e)}")

def main():
    print("Frontend Update Simulation Tool")
    print("===============================")
    
    # Get stage and template data
    stage_data = get_stage_and_templates()
    if not stage_data:
        return
        
    # Ask for API port
    port_input = input("\nEnter API port (default: 5000): ")
    api_port = int(port_input) if port_input.isdigit() else 5000
    
    # Simulate update
    simulate_frontend_update(stage_data, api_port)

if __name__ == "__main__":
    main()