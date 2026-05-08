import requests

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_VISION_MODEL = "llama-3.2-11b-vision-preview"


def get_groq_response(api_key: str, system_prompt: str, messages: list) -> str:
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "temperature": 0.3,
        "max_tokens": 2500,
    }
    res = requests.post(
        GROQ_ENDPOINT,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    if not res.ok:
        raise Exception(res.json().get("error", {}).get("message", f"HTTP {res.status_code}"))
    return res.json()["choices"][0]["message"]["content"]


def get_groq_vision_response(api_key: str, system_prompt: str, question: str, image_b64: str) -> str:
    payload = {
        "model": GROQ_VISION_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
            ]},
        ],
        "temperature": 0.3,
        "max_tokens": 2500,
    }
    res = requests.post(
        GROQ_ENDPOINT,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    if not res.ok:
        raise Exception(res.json().get("error", {}).get("message", f"HTTP {res.status_code}"))
    return res.json()["choices"][0]["message"]["content"]
