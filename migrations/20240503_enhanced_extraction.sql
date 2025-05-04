-- Migration for enhanced data extraction features

-- Create table for extraction results
CREATE TABLE IF NOT EXISTS extraction_results (
    extraction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cluster_id VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    template_id UUID NOT NULL REFERENCES templates(template_id),
    extracted_data JSONB NOT NULL,
    success BOOLEAN NOT NULL DEFAULT false,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create table for pattern data
CREATE TABLE IF NOT EXISTS pattern_data (
    pattern_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cluster_id VARCHAR(255) NOT NULL,
    field VARCHAR(255) NOT NULL,
    pattern_values JSONB NOT NULL,
    weights JSONB NOT NULL,
    success_rate FLOAT NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cluster_id, field)
);

-- Create table for extraction feedback
CREATE TABLE IF NOT EXISTS extraction_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    extraction_id UUID NOT NULL REFERENCES extraction_results(extraction_id),
    feedback_data JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_extraction_results_cluster_id ON extraction_results(cluster_id);
CREATE INDEX IF NOT EXISTS idx_extraction_results_template_id ON extraction_results(template_id);
CREATE INDEX IF NOT EXISTS idx_extraction_results_success ON extraction_results(success);
CREATE INDEX IF NOT EXISTS idx_pattern_data_cluster_id ON pattern_data(cluster_id);
CREATE INDEX IF NOT EXISTS idx_pattern_data_field ON pattern_data(field);
CREATE INDEX IF NOT EXISTS idx_extraction_feedback_extraction_id ON extraction_feedback(extraction_id);

-- Add columns to templates table for enhanced extraction
ALTER TABLE templates ADD COLUMN IF NOT EXISTS extraction_methods JSONB DEFAULT '[]'::jsonb;
ALTER TABLE templates ADD COLUMN IF NOT EXISTS pattern_threshold FLOAT DEFAULT 0.7;
ALTER TABLE templates ADD COLUMN IF NOT EXISTS learning_enabled BOOLEAN DEFAULT true;

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_extraction_results_updated_at
    BEFORE UPDATE ON extraction_results
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pattern_data_updated_at
    BEFORE UPDATE ON pattern_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to calculate pattern success rate
CREATE OR REPLACE FUNCTION calculate_pattern_success_rate(
    p_cluster_id VARCHAR,
    p_field VARCHAR
) RETURNS FLOAT AS $$
DECLARE
    v_success_count INTEGER;
    v_total_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_success_count
    FROM extraction_results
    WHERE cluster_id = p_cluster_id
    AND success = true
    AND extracted_data->>p_field IS NOT NULL;

    SELECT COUNT(*)
    INTO v_total_count
    FROM extraction_results
    WHERE cluster_id = p_cluster_id
    AND extracted_data->>p_field IS NOT NULL;

    IF v_total_count = 0 THEN
        RETURN 0.0;
    END IF;

    RETURN v_success_count::FLOAT / v_total_count;
END;
$$ LANGUAGE plpgsql;

-- Create view for pattern statistics
CREATE OR REPLACE VIEW pattern_statistics AS
SELECT 
    p.cluster_id,
    p.field,
    p.success_rate,
    COUNT(DISTINCT er.extraction_id) as total_extractions,
    COUNT(DISTINCT CASE WHEN er.success THEN er.extraction_id END) as successful_extractions,
    jsonb_object_agg(p.pattern_values->>'value', p.weights->>'weight') as value_weights
FROM pattern_data p
LEFT JOIN extraction_results er ON p.cluster_id = er.cluster_id
GROUP BY p.cluster_id, p.field, p.success_rate;

-- Create function to get improved patterns
CREATE OR REPLACE FUNCTION get_improved_patterns(
    p_template_id UUID
) RETURNS TABLE (
    field VARCHAR,
    pattern_values JSONB,
    weights JSONB,
    success_rate FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pd.field,
        pd.pattern_values,
        pd.weights,
        pd.success_rate
    FROM pattern_data pd
    JOIN extraction_results er ON pd.cluster_id = er.cluster_id
    WHERE er.template_id = p_template_id
    AND er.success = true
    AND pd.success_rate > 0.7
    ORDER BY pd.success_rate DESC;
END;
$$ LANGUAGE plpgsql; 