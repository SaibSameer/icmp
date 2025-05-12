# Template Variables Documentation

This document provides detailed information about the available template variables in the system.

## Business Information Variables

### business_name
Returns the name of the business.
```python
# Example output
"Ask Samir"
```

### business_info
Returns detailed information about the business including name, description, contact details, and metadata.
```python
# Example output
=== Business Information ===
Name: Ask Samir
Description: a smart AI powerd Agent
Additional Information: wetvervrty u4ututr ertyreyeryrey
Address: amman jodran
Phone: 0777753704
Created: 2025-05-04T22:46:54.205059+03:00
Last Updated: 2025-05-08T13:22:24.823480+03:00
===========================
```

## Time and Date Variables

### current_time
Returns the current time in HH:MM:SS format.
```python
# Example output
"12:41:48"
```

### current_date
Returns the current date in YYYY-MM-DD format.
```python
# Example output
"2025-05-11"
```

## Stage Variables

### stage_list
Returns a list of available stages for the business.
```python
# Example output
['Default Conversation Stage', 'information', 'test']
```

### available_stages
Returns detailed information about each available stage.
```python
# Example output
Default Conversation Stage: Initial stage for new conversations
information: Select this stage if the user wants to know more about the business, or if any other user inquires that are not included in other stages
test: test
```

### agent_stages
Returns stages associated with a specific agent.
```python
# Example output
[{
    'stage_id': 'b3aaf83d-6a65-4db6-ae58-2aaac95c3563',
    'stage_name': 'test',
    'stage_description': 'test',
    'stage_type': 'conversation',
    'created_at': '2025-05-08T11:21:53.330545+03:00'
}]
```

## User Variables

### user_name
Returns the name of the user.
```python
# Example output
"User User"
```

## Conversation Variables

### user_messages
Returns all messages from the user in chronological order.
```python
# Example output
assistant: It seems like your message may have been a typo or not fully formed. How can I assist you today with your business management needs? Feel free to provide more details or ask any questions you have.
user: dsgsdg
assistant: I'm here and ready to assist you with any questions or tasks you have. How can I help you today?
user: how are you today
assistant: Hello! How can I assist you today?
user: hi
assistant: I'm here to help you with any questions you have related to business management. Please let me know how I can assist you today.
user: dgsdfsdf
assistant: I'm here to assist you with any questions you may have regarding business management. Feel free to let me know how I can help you today.
user: dsfdsfs
```

### all_conversation_history
Returns all conversations with their IDs.
```python
# Example output
[Conversation: 338d61d5-af18-45a4-9a4e-687f45bbb9ab] Assistant: It seems like your message may have been a typo or not fully formed. How can I assist you today with your business management needs? Feel free to provide more details or ask any questions you have.
[Conversation: 338d61d5-af18-45a4-9a4e-687f45bbb9ab] User: dsgsdg
[Conversation: b834e572-d6df-4b64-aaa7-fb043a9108f1] Assistant: I'm here and ready to assist you with any questions or tasks you have. How can I help you today?
[Conversation: b834e572-d6df-4b64-aaa7-fb043a9108f1] User: how are you today
[Conversation: b834e572-d6df-4b64-aaa7-fb043a9108f1] Assistant: Hello! How can I assist you today?
[Conversation: b834e572-d6df-4b64-aaa7-fb043a9108f1] User: hi
[Conversation: 98d5db41-c1c6-4447-91bf-576ee25e061d] Assistant: I'm here to help you with any questions you have related to business management. Please let me know how I can assist you today.
[Conversation: 98d5db41-c1c6-4447-91bf-576ee25e061d] User: dgsdfsdf
[Conversation: 98d5db41-c1c6-4447-91bf-576ee25e061d] Assistant: I'm here to assist you with any questions you may have regarding business management. Feel free to let me know how I can help you today.
[Conversation: 98d5db41-c1c6-4447-91bf-576ee25e061d] User: dsfdsfs
```

### conversation_history
Returns messages from a specific conversation.
```python
# Example output
User: hi
Assistant: Hello! How can I assist you today?
User: how are you today
Assistant: I'm here and ready to assist you with any questions or tasks you have. How can I help you today?
```

### last_10_messages
Returns the last 10 messages from a conversation in JSON format with timestamps.
```python
# Example output
[
  {
    "content": "hi",
    "sender": "user",
    "timestamp": "2025-05-11T11:29:12.472766+03:00"
  },
  {
    "content": "Hello! How can I assist you today?",
    "sender": "assistant",
    "timestamp": "2025-05-11T11:29:15.513403+03:00"
  },
  {
    "content": "how are you today",
    "sender": "user",
    "timestamp": "2025-05-11T11:30:13.120763+03:00"
  },
  {
    "content": "I'm here and ready to assist you with any questions or tasks you have. How can I help you today?",
    "sender": "assistant",
    "timestamp": "2025-05-11T11:30:15.222042+03:00"
  }
]
```

## Testing Template Variables

You can test any template variable using the test script:

```bash
python backend/message_processing/variables/test_variables.py --variable <variable_name> --business_id <business_id> --user_id <user_id> --conversation_id <conversation_id> [--agent_id <agent_id>]
```

Required parameters:
- `--variable`: Name of the variable to test
- `--business_id`: UUID of the business
- `--user_id`: UUID of the user
- `--conversation_id`: UUID of the conversation

Optional parameters:
- `--agent_id`: UUID of the agent (required for agent-specific variables)
- `--message_content`: Content of a message (for message-related variables)
- `--max_messages`: Maximum number of messages to retrieve (default: 10)
- `--include_timestamps`: Include timestamps in the output 