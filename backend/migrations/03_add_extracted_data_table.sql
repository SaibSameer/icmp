-- Migration to add extracted_data table
-- This table stores structured data extracted from messages

-- Create the extracted_data table
CREATE TABLE IF NOT EXISTS extracted_data (
    extraction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    stage_id UUID NOT NULL REFERENCES stages(stage_id) ON DELETE CASCADE,
    data_type VARCHAR(50) NOT NULL,
    extracted_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_extracted_data_conversation_id ON extracted_data (conversation_id);
CREATE INDEX IF NOT EXISTS idx_extracted_data_stage_id ON extracted_data (stage_id);
CREATE INDEX IF NOT EXISTS idx_extracted_data_data_type ON extracted_data (data_type);

-- Add a comment to the table
COMMENT ON TABLE extracted_data IS 'Stores structured data extracted from messages during conversation processing';

-- Add some example data extraction templates
INSERT INTO templates (template_id, business_id, template_name, template_type, content, system_prompt)
VALUES
    (gen_random_uuid(), '00000000-0000-0000-0000-000000000000', 'Contact Information Extraction', 'data_extraction', 
     'Extract the following information from the message:
- name: (?:name|call me|i am|this is) ([A-Za-z\s]+)
- email: ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})
- phone: (\+\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})
- address: (?:address|location|live at|located at) ([A-Za-z0-9\s,.-]+)',
     'You are a data extraction assistant. Extract the requested information from the user''s message.
Return the data in JSON format with the specified field names.
If a field is not found, set its value to null.'),
    
    (gen_random_uuid(), '00000000-0000-0000-0000-000000000000', 'Product Interest Extraction', 'data_extraction',
     'Extract the following information about product interest:
- product_name: (?:interested in|looking for|want|need) ([A-Za-z0-9\s,.-]+)
- budget: (?:budget|spend|cost|price|worth) (?:is|of|about|around)? (\$?\d+(?:\.\d{2})?(?:\s*(?:k|thousand|m|million))?)
- timeline: (?:when|timeline|by|before|after) ([A-Za-z0-9\s,.-]+)',
     'You are a data extraction assistant. Extract information about product interest from the user''s message.
Return the data in JSON format with the specified field names.
If a field is not found, set its value to null.'),
    
    (gen_random_uuid(), '00000000-0000-0000-0000-000000000000', 'Support Issue Extraction', 'data_extraction',
     'Extract the following information about the support issue:
- issue_type: (?:problem|issue|error|bug|not working) ([A-Za-z0-9\s,.-]+)
- error_message: (?:error|message|says|shows) (?:is|:)? ([A-Za-z0-9\s,.-]+)
- affected_feature: (?:feature|function|part|component) ([A-Za-z0-9\s,.-]+)',
     'You are a data extraction assistant. Extract information about the support issue from the user''s message.
Return the data in JSON format with the specified field names.
If a field is not found, set its value to null.')
ON CONFLICT (template_id) DO NOTHING; 