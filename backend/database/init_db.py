import os
import logging
import psycopg2
from dotenv import load_dotenv
from db_config import get_db_config

load_dotenv()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def init_database():
    """Initialize the database with required tables."""
    config = get_db_config()
    log.info("Attempting to connect to database...")
    
    try:
        # Connect directly without connection pool
        conn = psycopg2.connect(**config)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create llm_calls table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS llm_calls (
            call_id UUID PRIMARY KEY,
            business_id UUID,
            input_text TEXT,
            response TEXT,
            system_prompt TEXT,
            call_type TEXT,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );''')
        
        # Create businesses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS businesses (
            business_id UUID PRIMARY KEY,
            api_key TEXT NOT NULL,
            owner_id UUID NOT NULL,
            business_name TEXT NOT NULL UNIQUE,
            business_description TEXT,
            address TEXT,
            phone_number TEXT,
            website TEXT,
            first_stage_id UUID,
            agent_list JSONB DEFAULT '[]',
            product_list JSONB DEFAULT '[]',
            service_list JSONB DEFAULT '[]',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );''')

        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id UUID PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);')

        # Create agents table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            agent_id UUID PRIMARY KEY NOT NULL,
            business_id UUID NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
            agent_name TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        );''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agents_business_id ON agents (business_id);')

        # Create stages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stages (
            stage_id UUID PRIMARY KEY,
            business_id UUID REFERENCES businesses(business_id),
            agent_id UUID REFERENCES agents(agent_id),
            stage_name TEXT NOT NULL,
            stage_description TEXT NOT NULL,
            stage_type TEXT NOT NULL,
            stage_selection_template_id UUID,
            data_extraction_template_id UUID,
            response_generation_template_id UUID,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stages_business_id ON stages (business_id);')

        # Create conversations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id UUID PRIMARY KEY,
            business_id UUID REFERENCES businesses(business_id),
            user_id UUID,
            agent_id UUID REFERENCES agents(agent_id),
            stage_id UUID REFERENCES stages(stage_id),
            session_id TEXT NOT NULL,
            start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'active'
        );''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_business_id ON conversations (business_id);')

        log.info("Database tables created successfully!")
        
    except Exception as e:
        log.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    init_database()