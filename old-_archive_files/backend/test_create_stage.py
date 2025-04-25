import requests
import json
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your actual API endpoint and authentication
BASE_URL = "http://localhost:5000"  # Adjust if your server runs on a different port
API_KEY = "your_api_key_here"  # Replace with your actual API key
BUSINESS_ID = "7ae167a0-d864-43b9-bdaf-fcba35b33f27"  # Replace with your actual business ID
AGENT_ID = "f731ec2a-a68d-4e56-8a27-d77a9ad4978a"  # Optional, can be None

def test_create_stage():
    """Test creating a stage with the correct field structure"""
    
    # This is the proper structure for creating a new stage
    stage_data = {
        "business_id": BUSINESS_ID,
        "agent_id": AGENT_ID,  # Optional
        "stage_name": "Test Stage",
        "stage_description": "A test stage created via API",
        "stage_type": "information",
        
        # These three config objects are required
        "stage_selection_config": {
            "template_text": "This is the stage selection prompt template. It helps determine which stage to use based on user input."
        },
        "data_extraction_config": {
            "template_text": "This is the data extraction prompt template. It helps extract key information from user messages."
        },
        "response_generation_config": {
            "template_text": "This is the response generation prompt template. It helps generate appropriate responses based on the extracted data."
        }
    }
    
    # Print the request body for debugging
    print("\nRequest Body:")
    print(json.dumps(stage_data, indent=2))
    
    # Make the API request
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-KEY": API_KEY
        }
        
        response = requests.post(
            f"{BASE_URL}/stages",
            json=stage_data,
            headers=headers
        )
        
        # Print the response for debugging
        print(f"\nStatus Code: {response.status_code}")
        print("Response Body:")
        if response.text:
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
        
        if response.status_code == 201:
            print("\nStage created successfully!")
            return response.json().get("stage_id")
        else:
            print("\nFailed to create stage")
            return None
            
    except Exception as e:
        logger.error(f"Error making API request: {e}")
        return None

if __name__ == "__main__":
    print("Testing stage creation...")
    stage_id = test_create_stage()
    if stage_id:
        print(f"Created stage with ID: {stage_id}")
    else:
        print("Stage creation failed")