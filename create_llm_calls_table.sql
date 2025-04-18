-- Create the llm_calls table
CREATE TABLE IF NOT EXISTS llm_calls (
    call_id UUID PRIMARY KEY,
    business_id UUID NOT NULL,
    input_text TEXT NOT NULL,
    response TEXT NOT NULL,
    system_prompt TEXT,
    call_type VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on business_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_llm_calls_business_id ON llm_calls (business_id);

-- Create an index on timestamp for faster sorting
CREATE INDEX IF NOT EXISTS idx_llm_calls_timestamp ON llm_calls (timestamp); 