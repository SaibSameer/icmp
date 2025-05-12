-- Add stage transitions table
CREATE TABLE IF NOT EXISTS stage_transitions (
    transition_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_stage_id UUID REFERENCES stages(stage_id) ON DELETE CASCADE,
    to_stage_id UUID REFERENCES stages(stage_id) ON DELETE CASCADE,
    business_id UUID REFERENCES businesses(business_id) ON DELETE CASCADE,
    condition TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_transition CHECK (from_stage_id != to_stage_id)
);

-- Add audit log table
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(business_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    action_type VARCHAR(50) NOT NULL,
    action_data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_stage_transitions_business ON stage_transitions(business_id);
CREATE INDEX IF NOT EXISTS idx_stage_transitions_from_stage ON stage_transitions(from_stage_id);
CREATE INDEX IF NOT EXISTS idx_stage_transitions_to_stage ON stage_transitions(to_stage_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_business ON audit_logs(business_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- Add function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add trigger for stage_transitions
CREATE TRIGGER update_stage_transitions_updated_at
    BEFORE UPDATE ON stage_transitions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments
COMMENT ON TABLE stage_transitions IS 'Stores valid transitions between conversation stages';
COMMENT ON TABLE audit_logs IS 'Stores audit trail of system actions';
COMMENT ON COLUMN stage_transitions.condition IS 'Condition expression for stage transition';
COMMENT ON COLUMN audit_logs.action_data IS 'JSON data associated with the action';
COMMENT ON COLUMN audit_logs.metadata IS 'Additional metadata about the audit log entry'; 