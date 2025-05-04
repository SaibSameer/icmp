-- Create business_details table
CREATE TABLE IF NOT EXISTS business_details (
    business_id UUID PRIMARY KEY REFERENCES businesses(business_id) ON DELETE CASCADE,
    business_hours JSONB,
    additional_contact_info JSONB,
    social_media_links JSONB,
    business_categories TEXT[],
    payment_methods TEXT[],
    service_areas TEXT[],
    languages_spoken TEXT[],
    certifications TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on business_id
CREATE INDEX idx_business_details_business_id ON business_details(business_id);

-- Create trigger to update updated_at
CREATE TRIGGER update_business_details_updated_at
    BEFORE UPDATE ON business_details
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add new columns to businesses table
ALTER TABLE businesses
    ADD COLUMN IF NOT EXISTS business_hours JSONB,
    ADD COLUMN IF NOT EXISTS additional_contact_info JSONB,
    ADD COLUMN IF NOT EXISTS social_media_links JSONB,
    ADD COLUMN IF NOT EXISTS business_categories TEXT[],
    ADD COLUMN IF NOT EXISTS payment_methods TEXT[],
    ADD COLUMN IF NOT EXISTS service_areas TEXT[],
    ADD COLUMN IF NOT EXISTS languages_spoken TEXT[],
    ADD COLUMN IF NOT EXISTS certifications TEXT[]; 