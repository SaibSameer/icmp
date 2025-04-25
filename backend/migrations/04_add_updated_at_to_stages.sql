-- Migration: Add updated_at column to stages table
-- Purpose: Add updated_at timestamp column to track when stages are modified

-- Add updated_at column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'stages' 
        AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE stages 
        ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        
        -- Create a trigger to automatically update the updated_at column
        CREATE OR REPLACE FUNCTION update_stages_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';

        CREATE TRIGGER update_stages_updated_at
            BEFORE UPDATE ON stages
            FOR EACH ROW
            EXECUTE FUNCTION update_stages_updated_at();
            
        RAISE NOTICE 'Added updated_at column and trigger to stages table';
    ELSE
        RAISE NOTICE 'updated_at column already exists in stages table';
    END IF;
END $$; 