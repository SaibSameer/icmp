-- Migration: Add template_variables table
-- Purpose: Add a table to store template variable definitions for better management and documentation

-- Create table for template variables
CREATE TABLE IF NOT EXISTS template_variables (
    variable_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variable_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    default_value TEXT,
    example_value TEXT,
    category VARCHAR(50) NOT NULL,  -- e.g., 'stage', 'user', 'conversation', 'system'
    is_dynamic BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_template_variables_name ON template_variables (variable_name);
CREATE INDEX IF NOT EXISTS idx_template_variables_category ON template_variables (category);

-- Insert standard variables
INSERT INTO template_variables 
    (variable_name, description, default_value, example_value, category, is_dynamic)
VALUES
    ('stage_list', 'List of all available stage names for the business', '[]', '["Greet", "Assist", "Close"]', 'stage', true),
    ('available_stages', 'Detailed information about available stages with descriptions', 'No stages available', 'Greet: Welcome the customer\nAssist: Help with customer needs', 'stage', true),
    ('conversation_history', 'Full history of the conversation', 'No conversation history', 'User: Hello\nAssistant: How can I help?', 'conversation', true),
    ('summary_of_last_conversations', 'Brief summary of recent messages', 'No previous conversations', 'User: Hello... | Assistant: How can I help?', 'conversation', true),
    ('N', 'Number of recent messages to consider', '3', '5', 'conversation', true),
    ('user_name', 'Full name of the user', 'Guest', 'John Smith', 'user', true),
    ('business_name', 'Name of the business', 'Our Business', 'Acme Corporation', 'business', true),
    ('current_time', 'Current time in HH:MM:SS format', '', '14:30:22', 'system', true),
    ('current_date', 'Current date in YYYY-MM-DD format', '', '2023-09-15', 'system', true)
ON CONFLICT (variable_name) DO UPDATE
SET 
    description = EXCLUDED.description,
    default_value = EXCLUDED.default_value,
    example_value = EXCLUDED.example_value,
    category = EXCLUDED.category,
    updated_at = CURRENT_TIMESTAMP;

-- Create junction table for tracking variables used in specific templates
CREATE TABLE IF NOT EXISTS template_variable_usage (
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(template_id) ON DELETE CASCADE,
    variable_id UUID NOT NULL REFERENCES template_variables(variable_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(template_id, variable_id)
);

-- Add function to automatically update usage table when scanning templates
CREATE OR REPLACE FUNCTION update_template_variable_usage() RETURNS TRIGGER AS $$
DECLARE
    var_name TEXT;
    var_id UUID;
    var_exists BOOLEAN;
BEGIN
    -- First, delete existing usage records for this template
    DELETE FROM template_variable_usage WHERE template_id = NEW.template_id;
    
    -- Scan content for variables using regex
    FOR var_name IN 
        SELECT DISTINCT m[1] 
        FROM regexp_matches(NEW.content, '{([^{}]+)}', 'g') AS m
    LOOP
        -- Check if this variable exists in template_variables
        SELECT EXISTS(SELECT 1 FROM template_variables WHERE variable_name = var_name) INTO var_exists;
        
        -- If variable doesn't exist in registry, add it with minimal info
        IF NOT var_exists THEN
            INSERT INTO template_variables (
                variable_name, description, category, is_dynamic
            ) VALUES (
                var_name, 'Auto-detected variable', 'unknown', false
            )
            RETURNING variable_id INTO var_id;
        ELSE
            SELECT variable_id INTO var_id FROM template_variables WHERE variable_name = var_name;
        END IF;
        
        -- Record the usage
        INSERT INTO template_variable_usage (template_id, variable_id)
        VALUES (NEW.template_id, var_id)
        ON CONFLICT (template_id, variable_id) DO NOTHING;
    END LOOP;
    
    -- Also scan system_prompt if it exists
    IF NEW.system_prompt IS NOT NULL AND NEW.system_prompt != '' THEN
        FOR var_name IN 
            SELECT DISTINCT m[1] 
            FROM regexp_matches(NEW.system_prompt, '{([^{}]+)}', 'g') AS m
        LOOP
            -- Check if this variable exists
            SELECT EXISTS(SELECT 1 FROM template_variables WHERE variable_name = var_name) INTO var_exists;
            
            -- If variable doesn't exist in registry, add it with minimal info
            IF NOT var_exists THEN
                INSERT INTO template_variables (
                    variable_name, description, category, is_dynamic
                ) VALUES (
                    var_name, 'Auto-detected variable', 'unknown', false
                )
                RETURNING variable_id INTO var_id;
            ELSE
                SELECT variable_id INTO var_id FROM template_variables WHERE variable_name = var_name;
            END IF;
            
            -- Record the usage
            INSERT INTO template_variable_usage (template_id, variable_id)
            VALUES (NEW.template_id, var_id)
            ON CONFLICT (template_id, variable_id) DO NOTHING;
        END LOOP;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update usage on template insert/update
CREATE TRIGGER update_template_variables_on_change
AFTER INSERT OR UPDATE OF content, system_prompt ON templates
FOR EACH ROW
EXECUTE FUNCTION update_template_variable_usage();

-- Initial population for existing templates
DO $$
BEGIN
    -- Add usage records for all existing templates
    PERFORM update_template_variable_usage() 
    FROM templates;
    
    RAISE NOTICE 'Variable usage populated for existing templates';
END $$; 