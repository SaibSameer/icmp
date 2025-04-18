# Database Schema (PostgreSQL)

This document outlines the canonical database schema. 
**Note:** Ensure the actual database reflects these definitions, including table renames and column updates from recent refactoring.

## Tables

### `businesses`

*   **Purpose:** Stores information about registered businesses (tenants).
*   **Schema:**
    ```sql
    CREATE TABLE businesses (
        business_id UUID PRIMARY KEY NOT NULL,
        api_key TEXT NOT NULL UNIQUE, -- Unique API key for the business (ensure encryption at rest)
        owner_id UUID NOT NULL, -- Link to the user who owns the business (references users table? Needs users table definition)
        business_name TEXT NOT NULL UNIQUE,
        business_description TEXT,
        address TEXT,
        phone_number TEXT,
        website TEXT,
        -- agent_list JSONB, -- Consider a separate business_agents table for many-to-many
        -- product_list JSONB, -- Consider a separate business_products table
        -- service_list JSONB, -- Consider normalization
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    );
    CREATE INDEX idx_businesses_owner_id ON businesses (owner_id);
    ```

### `templates`

*   **Purpose:** Stores all prompt templates, including both active templates used by stages and default templates.
*   **Schema:**
    ```sql
    CREATE TABLE templates (
        template_id UUID PRIMARY KEY NOT NULL,
        business_id UUID NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
        template_name VARCHAR(255) NOT NULL,
        template_type VARCHAR(50) NOT NULL,
        content TEXT NOT NULL,
        system_prompt TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX idx_templates_business_id ON templates (business_id);
    CREATE INDEX idx_templates_template_type ON templates (template_type);
    ```

### `prompt_templates` (Deprecated)

*   **Purpose:** Legacy table for storing prompt templates. Being phased out in favor of the `templates` table.
*   **Migration:** A migration script is available at `backend/migrations/01_cleanup_template_tables.sql` to move any remaining data from this table to the `templates` table.
*   **Schema:**
    ```sql
    CREATE TABLE prompt_templates (
        template_id CHARACTER VARYING(255) PRIMARY KEY NOT NULL,
        template_text TEXT NOT NULL,
        description TEXT,
        variables TEXT[] NOT NULL DEFAULT '{}',
        template_name CHARACTER VARYING(255),
        template_type CHARACTER VARYING(50) DEFAULT 'stage_selection'
    );
    ```

### `stages`

*   **Purpose:** Defines the different stages within a business's conversation flow and stores their unique configurations.
*   **Schema:**
    ```sql
    CREATE TABLE stages (
        stage_id UUID PRIMARY KEY NOT NULL,
        business_id UUID NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
        agent_id UUID, -- Optional link to a specific agent
        stage_name TEXT NOT NULL,
        stage_description TEXT NOT NULL,
        stage_type TEXT NOT NULL, -- e.g., 'conversation', 'response', 'form'
        stage_selection_template_id UUID NOT NULL REFERENCES templates(template_id),
        data_extraction_template_id UUID NOT NULL REFERENCES templates(template_id),
        response_generation_template_id UUID NOT NULL REFERENCES templates(template_id),
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    );
    CREATE INDEX idx_stages_business_id ON stages (business_id);
    CREATE INDEX idx_stages_agent_id ON stages (agent_id);
    ```

### `users`

*   **Purpose:** Stores user information (customers, business owners, agents).
*   **Schema:**
    ```sql
    CREATE TABLE users (
        user_id UUID PRIMARY KEY NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        -- Add password_hash TEXT NOT NULL for user authentication
        -- Add role TEXT NOT NULL DEFAULT 'customer' (e.g., 'customer', 'admin', 'agent')
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    );
    CREATE INDEX idx_users_email ON users (email);
    ```

### `conversations`

*   **Purpose:** Tracks ongoing or completed conversations.
*   **Schema:**
    ```sql
    CREATE TABLE conversations (
        conversation_id UUID PRIMARY KEY NOT NULL,
        business_id UUID NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
        user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
        agent_id UUID, -- REFERENCES agents(agent_id), -- Link to agent handling (Needs agents table)
        stage_id UUID, -- REFERENCES stages(stage_id), -- Current or last stage
        session_id TEXT NOT NULL, -- Identifier for a user's session
        start_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        status TEXT NOT NULL DEFAULT 'active', -- e.g., 'active', 'paused', 'completed', 'error'
        -- Add conversation_summary TEXT -- For context in future messages?
        -- Add message_history JSONB -- Potentially store recent messages?
    );
    CREATE INDEX idx_conversations_business_id ON conversations (business_id);
    CREATE INDEX idx_conversations_user_id ON conversations (user_id);
    CREATE INDEX idx_conversations_session_id ON conversations (session_id);
    CREATE INDEX idx_conversations_status ON conversations (status);
    ```

### `messages`

*   **Purpose:** Stores individual messages within conversations.
*   **Schema:**
    ```sql
    CREATE TABLE messages (
        message_id UUID PRIMARY KEY NOT NULL,
        conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
        message_content TEXT NOT NULL,
        sender_type TEXT NOT NULL, -- 'user' or 'assistant'
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    );
    CREATE INDEX idx_messages_conversation_id ON messages (conversation_id);
    CREATE INDEX idx_messages_created_at ON messages (created_at);
    ```

### `agents`

*   **Purpose:** Stores information about AI or human agents.
*   **Schema:**
    ```sql
    CREATE TABLE agents (
        agent_id UUID PRIMARY KEY NOT NULL,
        business_id UUID NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
        agent_name TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    );
    CREATE INDEX idx_agents_business_id ON agents (business_id);
    ```

## Relationships (Summary)

*   A `business` has one `owner` (a `user`).
*   A `business` can have many `stages`.
*   A `business` can have many `agents`.
*   A `business` can have many `conversations`.
*   A `business` can have many `templates`.
*   A `user` can participate in many `conversations`.
*   A `stage` belongs to one `business`.
*   A `stage` links to three `templates` (selection, extraction, generation).
*   A `stage` can optionally be linked to one `agent`.
*   A `conversation` belongs to one `business` and one `user`.
*   A `conversation` can optionally be handled by one `agent`.
*   A `conversation` can be associated with a `stage`.
*   `templates` belong to a business and can be used by multiple stages.

## Migration Notes

Some parts of the database schema are undergoing migration:

1. **Template System Migration**: The system is transitioning from using the `prompt_templates` table to the more robust `templates` table, which includes business relationships and better supports the template system features.

2. **Table Dependencies**: When migrating templates, care must be taken to update references in the `stages` table, which links to templates for stage selection, data extraction, and response generation.

For more information on database migrations, see [DATABASE_MIGRATION_GUIDE.md](DATABASE_MIGRATION_GUIDE.md) and [TEMPLATE_SYSTEM.md](TEMPLATE_SYSTEM.md).