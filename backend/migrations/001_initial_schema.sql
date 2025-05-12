-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables
CREATE TABLE IF NOT EXISTS default_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_text TEXT NOT NULL,
    variables TEXT[] NOT NULL,
    template_type VARCHAR(50) NOT NULL DEFAULT 'default',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agents (
    agent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    agent_role VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(business_id, agent_name)
);

CREATE TABLE IF NOT EXISTS stages (
    stage_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL,
    agent_id UUID REFERENCES agents(agent_id) ON DELETE CASCADE,
    stage_name VARCHAR(255) NOT NULL,
    stage_order INTEGER NOT NULL,
    template_id UUID REFERENCES default_templates(template_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(business_id, agent_id, stage_name)
);

CREATE TABLE IF NOT EXISTS llm_calls (
    call_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL,
    agent_id UUID REFERENCES agents(agent_id) ON DELETE SET NULL,
    stage_id UUID REFERENCES stages(stage_id) ON DELETE SET NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_agents_business_id ON agents(business_id);
CREATE INDEX IF NOT EXISTS idx_stages_business_id ON stages(business_id);
CREATE INDEX IF NOT EXISTS idx_stages_agent_id ON stages(agent_id);
CREATE INDEX IF NOT EXISTS idx_llm_calls_business_id ON llm_calls(business_id);
CREATE INDEX IF NOT EXISTS idx_llm_calls_agent_id ON llm_calls(agent_id);
CREATE INDEX IF NOT EXISTS idx_llm_calls_stage_id ON llm_calls(stage_id);
CREATE INDEX IF NOT EXISTS idx_llm_calls_created_at ON llm_calls(created_at);

-- Create functions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_agents_updated_at
    BEFORE UPDATE ON agents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stages_updated_at
    BEFORE UPDATE ON stages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_templates_updated_at
    BEFORE UPDATE ON default_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 