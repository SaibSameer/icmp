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

## Core Processing Steps (`MessageHandler.process_message`)

1.  **Initialization & Logging:**
    *   A unique `log_id` is generated for the current request for tracing.
    *   Basic input validation occurs (checking for `business_id`, `user_id`, `content`).

2.  **Database Connection & Transaction Start:**
    *   A database connection (`conn`) is acquired from the pool.
    *   **IMPORTANT:** All subsequent database operations within this request are part of a single **atomic transaction**. `autocommit` is turned off.

3.  **Conversation Management:**
    *   If a `conversation_id` is provided, it's verified.
    *   If no `conversation_id` exists or is provided, a new conversation record is created in the database.
    *   A unique `llm_call_id` is generated and associated with the conversation for this specific message interaction (helps maintain context isolation for LLM calls).

4.  **Stage Determination (Initial):**
    *   The `StageService` determines the `current_stage` the conversation is in *before* processing this message.
    *   The initial template IDs (`selection_template_id`, `extraction_template_id`, `response_template_id`) associated with this *initial* stage are fetched.

5.  **Context Building:**
    *   A `context` dictionary is created containing relevant IDs, the user message, and stage information.
    *   The `TemplateVariableProvider` fetches dynamic data (e.g., user name, business details) from the database and adds it to the `context`.

6.  **Stage Selection / Intent Detection (Optional):**
    *   If the current stage has a `selection_template_id`:
        *   The selection template is retrieved and applied using the `context`.
        *   The resulting prompt is sent to the `LLMService` to determine the most appropriate *next* stage based on the user's message content.
        *   The LLM response is parsed to detect a target stage name.
        *   If a new stage is detected:
            *   The `current_stage` variable is updated locally.
            *   The `stage_id` in the `conversations` table is updated in the database.
        *   This step is logged.

7.  **Template Refresh (Post-Stage Selection):**
    *   **IMPORTANT:** After step 6 potentially updates the `current_stage`, the code **re-queries the database** to fetch the `extraction_template_id` and `response_template_id` associated with this **newly determined stage**. This ensures subsequent steps use the correct templates immediately.

8.  **Data Extraction (Optional):**
    *   If the (potentially new) stage has an `extraction_template_id`:
        *   The data extraction template is retrieved and applied using the latest `context`.
        *   The `DataExtractionService` (which may involve the `LLMService`) is called to extract structured data.
        *   The extracted data is added back to the `context`.
        *   This step is logged.

9.  **Response Generation:**
    *   The `response_generation_template_id` for the (potentially new) stage is retrieved.
    *   The response template is applied using the final `context` (including any extracted data).
    *   The resulting prompt is sent to the `LLMService` to generate the final AI response to the user.
    *   This step is logged.

10. **Save Messages:**
    *   The original incoming user message is saved to the `messages` table.
    *   The generated AI response is saved to the `messages` table.

11. **Update Conversation Timestamp:**
    *   The `last_updated` timestamp in the `conversations` table is updated.

12. **Commit Transaction:**
    *   If *all* preceding steps (including all database writes and LLM calls) completed without error, `conn.commit()` is called. This makes all database changes for this message permanent.

13. **Return Success:**
    *   A success JSON response is returned to the caller, including the AI response, IDs, and the `process_log_id`.

14. **Error Handling & Rollback:**
    *   If *any* error occurs during steps 3-11:
        *   The `except` block is triggered.
        *   `conn.rollback()` is called, undoing *all* database changes made during this request.
        *   An error is logged, including any processing steps completed before the error.
        *   An error JSON response is returned to the caller.

15. **Release Connection:**
    *   In the `finally` block (executed regardless of success or error), the database connection (`conn`) is returned to the pool.

## Key Takeaways

*   **Atomic Transactions:** The entire process is wrapped in a single database transaction, ensuring data consistency.
*   **Immediate Stage Transition:** The system now uses the templates for the *newly selected* stage within the same message processing cycle.
*   **Centralized Orchestration:** `MessageHandler` acts as the central coordinator.
*   **Modularity:** Uses dedicated services (`StageService`, `TemplateService`, etc.) for specific tasks. 