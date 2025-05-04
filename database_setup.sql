-- Drop dependent tables first if they exist
DROP TABLE IF EXISTS llm_calls CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS users CASCADE; -- Drop users too if messages references it
-- Add drops for other tables like stages, conversations, businesses etc. 
-- if you want a completely clean setup each time.
DROP TABLE IF EXISTS stages CASCADE;
DROP TABLE IF EXISTS stage_transitions CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS templates CASCADE;
DROP TABLE IF EXISTS agents CASCADE;
DROP TABLE IF EXISTS businesses CASCADE;
DROP TABLE IF EXISTS users CASCADE;


-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    message_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create llm_calls table
CREATE TABLE IF NOT EXISTS llm_calls (
    call_id UUID PRIMARY KEY,
    message_id UUID REFERENCES messages(message_id),
    prompt TEXT,
    response TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completion_time FLOAT,
    tokens_used INTEGER,
    FOREIGN KEY (message_id) REFERENCES messages(message_id)
);

-- Create function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);
CREATE INDEX IF NOT EXISTS idx_llm_calls_message_id ON llm_calls(message_id);

-- Create businesses table
CREATE TABLE IF NOT EXISTS businesses (
    business_id UUID PRIMARY KEY NOT NULL,
    api_key TEXT NOT NULL, -- Legacy/Old businessApiKey, consider renaming/removing if unused
    internal_api_key TEXT UNIQUE, -- Added: For internal service/webhook auth
    owner_id UUID NOT NULL, -- Consider linking to a proper users table if one exists
    business_name TEXT NOT NULL UNIQUE,
    business_description TEXT,
    address TEXT,
    phone_number TEXT,
    website TEXT,
    first_stage_id UUID, -- Added based on schema search
    facebook_page_id TEXT UNIQUE, -- Added: For mapping Facebook webhooks
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- Assuming standard timestamp handling
);

-- Add indexes if they aren't already present
CREATE INDEX IF NOT EXISTS idx_businesses_owner_id ON businesses (owner_id);
CREATE INDEX IF NOT EXISTS idx_businesses_internal_key ON businesses (internal_api_key);
CREATE INDEX IF NOT EXISTS idx_businesses_facebook_page ON businesses (facebook_page_id);

-- Create trigger for businesses updated_at
CREATE TRIGGER update_businesses_updated_at
    BEFORE UPDATE ON businesses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create stages table (ensure FK references businesses.business_id)
CREATE TABLE IF NOT EXISTS stages (
    stage_id UUID PRIMARY KEY NOT NULL,
    business_id UUID NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
    -- Add the rest of the columns for the stages table here 
    -- Example columns (check other files like schemas.py or routes/stages.py for actual definition):
    agent_id UUID, -- REFERENCES agents(agent_id) ?
    stage_name TEXT NOT NULL,
    stage_description TEXT,
    stage_type VARCHAR(50),
    stage_selection_template_id UUID, -- REFERENCES templates(template_id)?
    data_extraction_template_id UUID, -- REFERENCES templates(template_id)?
    response_generation_template_id UUID, -- REFERENCES templates(template_id)?
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add trigger for stages updated_at
-- CREATE TRIGGER update_stages_updated_at
--    BEFORE UPDATE ON stages
--    FOR EACH ROW
--    EXECUTE FUNCTION update_updated_at_column();

-- Create templates table (ensure FK references businesses.business_id)
CREATE TABLE IF NOT EXISTS templates (
    template_id UUID PRIMARY KEY NOT NULL,
    business_id UUID NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
    template_name VARCHAR(255) NOT NULL,
    template_type VARCHAR(50) NOT NULL, -- e.g., stage_selection, data_extraction, response_generation
    content TEXT,
    system_prompt TEXT,
    is_default BOOLEAN DEFAULT FALSE, -- Added based on routes/templates.py
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create trigger for templates updated_at
CREATE TRIGGER update_templates_updated_at
    BEFORE UPDATE ON templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create agents table (ensure FK references businesses.business_id)
CREATE TABLE IF NOT EXISTS agents (
    agent_id UUID PRIMARY KEY NOT NULL,
    business_id UUID NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL, -- Match column used in agents.py route
    -- Add other agent config fields if needed (description, system_prompt, etc.)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add Unique Constraint for Agent Name per Business
ALTER TABLE agents
ADD CONSTRAINT agents_business_id_agent_name_key UNIQUE (business_id, agent_name);

-- Create trigger for agents updated_at
CREATE TRIGGER update_agents_updated_at
    BEFORE UPDATE ON agents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id UUID PRIMARY KEY NOT NULL,
    business_id UUID NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(agent_id) ON DELETE SET NULL, -- Link to agent handling
    stage_id UUID, -- Current or last stage (FK added below if stages created first)
    session_id TEXT, -- Identifier for a user's session (might be platform specific)
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active', -- e.g., 'active', 'paused', 'completed', 'error'
    conversation_summary TEXT,
    message_history JSONB
);

-- Add FK for stage_id if stages table exists
-- ALTER TABLE conversations ADD CONSTRAINT fk_conversations_stage_id FOREIGN KEY (stage_id) REFERENCES stages(stage_id) ON DELETE SET NULL;

-- Add trigger for conversations updated_at
CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add other tables (e.g., stage_transitions) if they are defined in this file. 