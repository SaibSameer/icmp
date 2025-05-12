-- Test database setup migration
-- This script creates a clean test database schema

-- Drop existing tables in test schema
DROP SCHEMA IF EXISTS test CASCADE;

-- Create test schema
CREATE SCHEMA test;

-- Create tables in test schema
CREATE TABLE test.users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    business_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test.businesses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test.stages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    business_id INTEGER REFERENCES test.businesses(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test.templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    stage_id INTEGER REFERENCES test.stages(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test.agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    business_id INTEGER REFERENCES test.businesses(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test.conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES test.users(id),
    agent_id INTEGER REFERENCES test.agents(id),
    stage_id INTEGER REFERENCES test.stages(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test.messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES test.conversations(id),
    content TEXT NOT NULL,
    sender_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test.llm_calls (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES test.messages(id),
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_test_users_business_id ON test.users(business_id);
CREATE INDEX idx_test_stages_business_id ON test.stages(business_id);
CREATE INDEX idx_test_templates_stage_id ON test.templates(stage_id);
CREATE INDEX idx_test_agents_business_id ON test.agents(business_id);
CREATE INDEX idx_test_conversations_user_id ON test.conversations(user_id);
CREATE INDEX idx_test_conversations_agent_id ON test.conversations(agent_id);
CREATE INDEX idx_test_conversations_stage_id ON test.conversations(stage_id);
CREATE INDEX idx_test_messages_conversation_id ON test.messages(conversation_id);
CREATE INDEX idx_test_llm_calls_message_id ON test.llm_calls(message_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION test.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_test_users_updated_at
    BEFORE UPDATE ON test.users
    FOR EACH ROW
    EXECUTE FUNCTION test.update_updated_at_column();

CREATE TRIGGER update_test_businesses_updated_at
    BEFORE UPDATE ON test.businesses
    FOR EACH ROW
    EXECUTE FUNCTION test.update_updated_at_column();

CREATE TRIGGER update_test_stages_updated_at
    BEFORE UPDATE ON test.stages
    FOR EACH ROW
    EXECUTE FUNCTION test.update_updated_at_column();

CREATE TRIGGER update_test_templates_updated_at
    BEFORE UPDATE ON test.templates
    FOR EACH ROW
    EXECUTE FUNCTION test.update_updated_at_column();

CREATE TRIGGER update_test_agents_updated_at
    BEFORE UPDATE ON test.agents
    FOR EACH ROW
    EXECUTE FUNCTION test.update_updated_at_column();

CREATE TRIGGER update_test_conversations_updated_at
    BEFORE UPDATE ON test.conversations
    FOR EACH ROW
    EXECUTE FUNCTION test.update_updated_at_column();

CREATE TRIGGER update_test_messages_updated_at
    BEFORE UPDATE ON test.messages
    FOR EACH ROW
    EXECUTE FUNCTION test.update_updated_at_column();

CREATE TRIGGER update_test_llm_calls_updated_at
    BEFORE UPDATE ON test.llm_calls
    FOR EACH ROW
    EXECUTE FUNCTION test.update_updated_at_column(); 