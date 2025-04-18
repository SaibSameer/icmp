-- Migration: Add conversation_summary column to conversations table
-- Purpose: Store AI-generated summaries of conversations for better context and searchability

-- Add conversation_summary column
ALTER TABLE conversations 
ADD COLUMN IF NOT EXISTS conversation_summary JSONB;

-- Add index for faster searching
CREATE INDEX IF NOT EXISTS idx_conversations_summary 
ON conversations USING GIN (conversation_summary);

-- Add comment to explain the column
COMMENT ON COLUMN conversations.conversation_summary IS 
'Stores AI-generated summary of the conversation in JSON format with fields: overview, key_points, decisions, pending_items, next_steps, sentiment, confidence_score'; 