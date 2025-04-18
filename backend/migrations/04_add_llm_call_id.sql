-- Migration: Add llm_call_id column to conversations table
-- Purpose: Store a tracking ID for LLM calls within a conversation

-- Add llm_call_id column
ALTER TABLE conversations 
ADD COLUMN IF NOT EXISTS llm_call_id UUID;

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_conversations_llm_call_id 
ON conversations (llm_call_id);

-- Add comment to explain the column
COMMENT ON COLUMN conversations.llm_call_id IS 
'Stores a tracking ID for LLM calls within a conversation to maintain context across multiple calls'; 