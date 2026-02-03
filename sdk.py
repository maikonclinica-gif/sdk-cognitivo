import os
import uuid
import redis
import json

REDIS_URL = os.getenv("REDIS_URL")
TTL = int(os.getenv("SDK_SESSION_TTL_SECONDS", "86400"))

r = redis.from_url(REDIS_URL, decode_responses=True)

def new_session_id() -> str:
    return str(uuid.uuid4())

def _key(session_id: str):
    return f"sdk:session:{session_id}"

def _get_memory(session_id: str):
    key = _key(session_id)
    data = r.get(key)
    if data:
        return json.loads(data)
    return []

def _save_memory(session_id: str, memory):
    key = _key(session_id)
    r.setex(key, TTL, json.dumps(memory))

def sdk_reset(session_id: str):
    r.delete(_key(session_id))
    return {"ok": True, "reset": "session", "session_id": session_id}

def extract_name(text: str):
    t = (text or "").strip()
    low = t.lower()
    if "meu nome é" in low:
        name_part = t[low.index("meu nome é") + len("meu nome é"):].strip()
        if name_part:
            return " ".join([p.capitalize() for p in name_part.split()])
    return None

def sdk(message: str, session_id: str):
    memory = _get_memory(session_id)

    memory.append(message)

    name = extract_name(message)
    if name:
        memory = [m for m in memory if not str(m).startswith("nome:")]
        memory.append(f"nome:{name}")
        _save_memory(session_id, memory)
        return f"Prazer, {name}. Vou lembrar disso."

    stored_name = None
    for item in memory:
        if isinstance(item, str) and item.startswith("nome:"):
            stored_name = item.split(":", 1)[1].strip()

    if "qual é meu nome" in (message or "").lower():
        if stored_name:
            _save_memory(session_id, memory)
            return f"Seu nome é {stored_name}."
        return "Você ainda não me disse seu nome."

    _save_memory(session_id, memory)

    return (
        "[Intent:general | Emotion:neutral]\n"
        f"Session: {session_id}\n"
        f"Memórias: {' | '.join([str(x) for x in memory])}\n"
        f"→ Entendi: {message}"
    )

def sdk_status():
    return {"status": "SDK running (Redis mode)"}
