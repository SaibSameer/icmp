-- Migration: Update llm_calls table schema
-- Purpose: Update the llm_calls table to match the current requirements

-- Create a temporary table with the new schema
CREATE TABLE llm_calls_new (
    call_id UUID PRIMARY KEY,
    business_id UUID NOT NULL,
    input_text TEXT NOT NULL,
    response TEXT NOT NULL,
    system_prompt TEXT,
    call_type VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Copy data from old table to new table
INSERT INTO llm_calls_new (call_id, input_text, response, timestamp)
SELECT call_id, prompt, response, created_at
FROM llm_calls;

-- Drop the old table
DROP TABLE llm_calls CASCADE;

-- Rename the new table to the original name
ALTER TABLE llm_calls_new RENAME TO llm_calls;

-- Create indexes
CREATE INDEX idx_llm_calls_business_id ON llm_calls (business_id);
CREATE INDEX idx_llm_calls_timestamp ON llm_calls (timestamp); 