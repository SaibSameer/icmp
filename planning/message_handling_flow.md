# ICMP Message Handling Flow Documentation

This document outlines the process by which incoming user messages are handled by the `MessageHandler` class located in `backend/message_processing/message_handler.py`.

## Overview

The goal is to process a user's message within the context of a conversation, determine the appropriate workflow (stage), potentially extract relevant data, generate an AI response, and update the database accordingly.

**Key Components:**

*   **MessageHandler:** Orchestrates the entire process.
*   **StageService:** Determines the current stage of the conversation.
*   **TemplateService:** Fetches and applies templates (prompts) for different steps.
*   **DataExtractionService:** Handles the extraction of structured data from messages.
*   **LLMService:** Interacts with the underlying Large Language Model (e.g., OpenAI) for stage selection, data extraction, and response generation.
*   **Database:** Stores information about businesses, users, conversations, stages, templates, messages, etc.
*   **Database Pool:** Manages database connections (`db_pool`).
*   **Redis Manager:** Manages state and caching (`redis_manager`).

## Core Processing Steps (`MessageHandler.process_message`)

1.  **Initialization & Logging:**
    *   A unique `log_id` is generated for the current request for tracing.
    *   Basic input validation occurs (checking for `business_id`, `user_id`, `content`).
    *   Redis connection is established for state management.

2.  **Database Connection & Transaction Start:**
    *   A database connection (`conn`) is acquired from the pool.
    *   **IMPORTANT:** All subsequent database operations within this request are part of a single **atomic transaction**. `autocommit` is turned off.

3.  **Conversation Management:**
    *   If a `conversation_id` is provided, it's verified.
    *   If no `conversation_id` exists or is provided, a new conversation record is created in the database.
    *   A unique `llm_call_id` is generated and associated with the conversation for this specific message interaction.
    *   Conversation state is cached in Redis for quick access.

4.  **Stage Determination (Initial):**
    *   The `StageService` determines the `current_stage` the conversation is in *before* processing this message.
    *   The initial template IDs are fetched and cached in Redis.
    *   Stage state is managed through Redis for performance.

5.  **Context Building:**
    *   A `context` dictionary is created containing relevant IDs, the user message, and stage information.
    *   The `TemplateVariableProvider` fetches dynamic data from the database and Redis cache.
    *   Context is cached in Redis for subsequent operations.

6.  **Stage Selection / Intent Detection (Optional):**
    *   If the current stage has a `selection_template_id`:
        *   The selection template is retrieved from Redis cache or database.
        *   The template is applied using the `context`.
        *   The resulting prompt is sent to the `LLMService`.
        *   If a new stage is detected:
            *   The `current_stage` is updated in both database and Redis.
            *   Stage transition is logged and cached.
        *   This step is logged.

7.  **Template Refresh (Post-Stage Selection):**
    *   After stage selection, template IDs are refreshed from Redis cache or database.
    *   Template cache is updated if needed.

8.  **Data Extraction (Optional):**
    *   If the stage has an `extraction_template_id`:
        *   The data extraction template is retrieved from cache.
        *   The `DataExtractionService` extracts structured data.
        *   Extracted data is cached in Redis.
        *   This step is logged.

9.  **Response Generation:**
    *   The response template is retrieved from cache.
    *   The template is applied using the final `context`.
    *   The response is generated using the `LLMService`.
    *   Response is cached in Redis.
    *   This step is logged.

10. **Save Messages:**
    *   The original message and AI response are saved to the database.
    *   Message state is cached in Redis.

11. **Update Conversation State:**
    *   The conversation timestamp is updated in the database.
    *   Conversation state is updated in Redis.

12. **Commit Transaction:**
    *   If all steps completed successfully, the transaction is committed.
    *   Redis cache is updated with final state.

13. **Return Success:**
    *   A success response is returned with the AI response and IDs.

14. **Error Handling & Rollback:**
    *   If any error occurs:
        *   The transaction is rolled back.
        *   Redis cache is cleared for the affected conversation.
        *   Error is logged and returned.

15. **Cleanup:**
    *   Database connection is released.
    *   Redis connections are properly closed.

## Redis Integration

### State Management
```python
# Cache conversation state
redis_manager.set_state(f"conv:{conversation_id}", {
    "stage_id": stage_id,
    "last_updated": timestamp,
    "context": context_data
})

# Cache stage templates
redis_manager.set_hash(f"stage:{stage_id}", {
    "selection_template": template_id,
    "extraction_template": template_id,
    "response_template": template_id
})

# Cache extracted data
redis_manager.set_state(f"data:{conversation_id}", extracted_data)
```

### Performance Optimization
1. **Caching Strategy**
   - Template caching
   - Context caching
   - State caching
   - Data caching

2. **Cache Invalidation**
   - Stage transitions
   - Template updates
   - Context changes
   - Data updates

## Enhanced Error Handling

### Error Categories
1. **Validation Errors**
   - Input validation failures
   - Template validation errors
   - Stage transition validation
   - Data extraction validation

2. **Processing Errors**
   - LLM service failures
   - Template rendering errors
   - Database operation failures
   - Redis operation failures
   - Rate limiting violations

3. **System Errors**
   - Connection failures
   - Resource exhaustion
   - Timeout errors
   - Configuration errors
   - Cache consistency errors

### Error Handling Strategy
1. **Immediate Response**
   - User-friendly error messages
   - Appropriate HTTP status codes
   - Detailed error logging
   - Transaction rollback
   - Cache cleanup

2. **Recovery Mechanisms**
   - Automatic retries for transient failures
   - Fallback templates
   - Graceful degradation
   - State recovery
   - Cache recovery

3. **Monitoring & Alerting**
   - Error rate tracking
   - Performance impact analysis
   - Alert thresholds
   - Error pattern detection
   - Cache hit/miss monitoring

## Related Documentation
- See `planning/template_system.md` for template details
- See `planning/stage_management.md` for stage management
- See `planning/code_patterns.md` for implementation patterns
- See `planning/testing_strategy.md` for testing guidelines

Last Updated: 2025-05-12
