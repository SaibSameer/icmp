import json

# This script demonstrates the correct structure for creating and updating stages

# Example of correct request format for creating a new stage
create_stage_example = {
    "business_id": "7ae167a0-d864-43b9-bdaf-fcba35b33f27",  # Required
    "agent_id": "f731ec2a-a68d-4e56-8a27-d77a9ad4978a",     # Optional
    "stage_name": "Customer Greeting",                      # Required
    "stage_description": "Initial greeting stage for customers", # Required
    "stage_type": "greeting",                               # Required
    
    # All three of these config objects are REQUIRED
    "stage_selection_config": {
        "template_text": "This is the prompt template for stage selection."
        # variables field is optional
    },
    "data_extraction_config": {
        "template_text": "This is the prompt template for data extraction."
        # variables field is optional
    },
    "response_generation_config": {
        "template_text": "This is the prompt template for response generation."
        # variables field is optional
    }
}

# Example of correct request format for updating an existing stage
update_stage_example = {
    "business_id": "7ae167a0-d864-43b9-bdaf-fcba35b33f27",  # Required
    # Only include fields you want to update
    "stage_name": "Updated Customer Greeting",              # Optional for update
    
    # Any of these template configs can be included if you want to update them
    "stage_selection_config": {
        "template_text": "Updated prompt template for stage selection."
    }
    # You don't need to include all config objects, only those you want to update
}

# Example of what the response structure looks like for a stage
stage_response_example = {
    "stage_id": "12345678-1234-5678-1234-567812345678",
    "business_id": "7ae167a0-d864-43b9-bdaf-fcba35b33f27",
    "agent_id": "f731ec2a-a68d-4e56-8a27-d77a9ad4978a",
    "stage_name": "Customer Greeting",
    "stage_description": "Initial greeting stage for customers",
    "stage_type": "greeting",
    "created_at": "2023-04-01T12:34:56.789Z",
    
    # Template configs in response
    "stage_selection_config": {
        "template_text": "This is the prompt template for stage selection.",
        "variables": []
    },
    "data_extraction_config": {
        "template_text": "This is the prompt template for data extraction.",
        "variables": []
    },
    "response_generation_config": {
        "template_text": "This is the prompt template for response generation.",
        "variables": []
    }
}

if __name__ == "__main__":
    print("\n=== STAGE CREATION REQUEST FORMAT ===")
    print(json.dumps(create_stage_example, indent=2))
    
    print("\n=== STAGE UPDATE REQUEST FORMAT ===")
    print(json.dumps(update_stage_example, indent=2))
    
    print("\n=== STAGE RESPONSE FORMAT ===")
    print(json.dumps(stage_response_example, indent=2))