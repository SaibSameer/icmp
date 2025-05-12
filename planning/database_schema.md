# Database Schema Documentation

## Overview
This document outlines the canonical PostgreSQL database schema for the ICMP Events API. The schema is designed to support multi-tenant business operations, conversation management, and template-based message processing.

## Core Tables

### `businesses`
Stores information about registered businesses (tenants).

```sql
CREATE TABLE businesses (
    business_id UUID PRIMARY KEY NOT NULL,
    api_key TEXT NOT NULL UNIQUE,
    owner_id UUID NOT NULL,
    business_name TEXT NOT NULL UNIQUE,
    business_description TEXT,
    address TEXT,
    phone_number TEXT,
    website TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_businesses_owner_id ON businesses (owner_id);
```

### `templates`
Stores all prompt templates, including both active templates used by stages and default templates.

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

### `stages`
Defines the different stages within a business's conversation flow and stores their unique configurations.

```sql
CREATE TABLE stages (
    stage_id UUID PRIMARY KEY NOT NULL,
    business_id UUID NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
    agent_id UUID,
    stage_name TEXT NOT NULL,
    stage_description TEXT NOT NULL,
    stage_type TEXT NOT NULL,
    stage_selection_template_id UUID NOT NULL REFERENCES templates(template_id),
    data_extraction_template_id UUID NOT NULL REFERENCES templates(template_id),
    response_generation_template_id UUID NOT NULL REFERENCES templates(template_id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_stages_business_id ON stages (business_id);
CREATE INDEX idx_stages_agent_id ON stages (agent_id);
```

### `users`
Stores user information (customers, business owners, agents).

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users (email);
```

### `conversations`
Tracks ongoing or completed conversations.

```sql
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY NOT NULL,
    business_id UUID NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    agent_id UUID,
    stage_id UUID,
    session_id TEXT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'active'
);
CREATE INDEX idx_conversations_business_id ON conversations (business_id);
CREATE INDEX idx_conversations_user_id ON conversations (user_id);
CREATE INDEX idx_conversations_session_id ON conversations (session_id);
CREATE INDEX idx_conversations_status ON conversations (status);
```

### `messages`
Stores individual messages within conversations.

```sql
CREATE TABLE messages (
    message_id UUID PRIMARY KEY NOT NULL,
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    message_content TEXT NOT NULL,
    sender_type TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_messages_conversation_id ON messages (conversation_id);
CREATE INDEX idx_messages_created_at ON messages (created_at);
```

### `agents`
Stores information about AI or human agents.

```sql
CREATE TABLE agents (
    agent_id UUID PRIMARY KEY NOT NULL,
    business_id UUID NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_agents_business_id ON agents (business_id);
```

## Table Relationships

### Business Relationships
- A business has one owner (user)
- A business can have many stages
- A business can have many agents
- A business can have many conversations
- A business can have many templates

### User Relationships
- A user can participate in many conversations
- A user can own multiple businesses

### Stage Relationships
- A stage belongs to one business
- A stage links to three templates (selection, extraction, generation)
- A stage can optionally be linked to one agent

### Conversation Relationships
- A conversation belongs to one business and one user
- A conversation can optionally be handled by one agent
- A conversation can be associated with a stage
- A conversation contains many messages

### Template Relationships
- Templates belong to a business
- Templates can be used by multiple stages
- Each stage requires three specific templates

## Migration Notes

### Template System Migration
The system has transitioned from using the `prompt_templates` table to the more robust `templates` table, which includes:
- Business relationships
- Better template type support
- System prompt integration
- Improved versioning

### Table Dependencies
When working with templates, be aware of:
1. References in the stages table
2. Business ownership requirements
3. Template type constraints

## Related Documentation
- See `planning/api_documentation.md` for API endpoints
- See `planning/template_system.md` for template system details
- See `planning/code_patterns.md` for implementation patterns

Last Updated: 2025-05-12
