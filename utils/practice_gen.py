import json
import requests

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

def generate_practice_questions(api_key: str, topic: str) -> list:
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": 
             "You are a math question generator. Return ONLY a valid JSON array of exactly 5 strings. No markdown, no backticks, no explanation."},
            {"role": "user", "content": 
             f"Generate 5 {topic} practice questions of mixed difficulty (2 easy, 2 medium, 1 hard). JSON array only."},
        ],
        "temperature": 0.7,
        "max_tokens": 600,
    }
    try:
        res = requests.post(
            GROQ_ENDPOINT,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload, timeout=30,
        )
        text = res.json()["choices"][0]["message"]["content"].strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        return [f"Error: {e}. API key check karein."]
