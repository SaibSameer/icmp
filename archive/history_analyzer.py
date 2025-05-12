import psycopg2
from psycopg2.pool import SimpleConnectionPool
import os
from dotenv import load_dotenv
import openai
import json

load_dotenv()

# Database connection
pool = SimpleConnectionPool(1, 20,
    dbname=os.environ.get("DB_NAME"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    host=os.environ.get("DB_HOST"),
    port=os.environ.get("DB_PORT")
)

# OpenAI setup
openai.api_key = os.environ.get("OPENAI_API_KEY")

def fetch_chat_history(business_id, limit=100):
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT user_message, agent_response, extracted_entities, current_stage
                FROM chat_history
                WHERE business_id = %s
                ORDER BY timestamp DESC
                LIMIT %s;
            """, (business_id, limit))
            return cur.fetchall()
    finally:
        pool.putconn(conn)

def fetch_available_stages(business_id):
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM stages WHERE business_id = %s;", (business_id,))
            return [row[0] for row in cur.fetchall()]
    finally:
        pool.putconn(conn)

def fetch_available_templates(business_id):
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name, fields FROM templates WHERE business_id = %s;", (business_id,))
            return [{"name": row[0], "fields": row[1]} for row in cur.fetchall()]
    finally:
        pool.putconn(conn)

def analyze_history_for_suggestions(business_id):
    history = fetch_chat_history(business_id)
    stages = fetch_available_stages(business_id)
    templates = fetch_available_templates(business_id)
    
    with open("suggestion_template.txt", "r") as f:
        prompt_template = f.read()
    
    history_str = json.dumps([{
        "user_message": row[0],
        "agent_response": row[1],
        "entities": row[2],
        "stage": row[3]
    } for row in history], indent=2)
    
    prompt = prompt_template.replace("{{user_messages}}", history_str)\
                           .replace("{{available_stages}}", json.dumps(stages))\
                           .replace("{{available_templates}}", json.dumps(templates))
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert in conversational AI design."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return json.loads(response.choices[0].message.content)

def suggest_stages_and_templates(business_id):
    suggestions = analyze_history_for_suggestions(business_id)
    return suggestions

if __name__ == "__main__":
    suggestions = suggest_stages_and_templates("example_business_id")
    print(json.dumps(suggestions, indent=2))