import os
import re
import redis
import uuid
from typing import Dict, Any, Optional

# ===== REDIS =====
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise RuntimeError("REDIS_URL não encontrado nas variáveis de ambiente.")

r = redis.from_url(REDIS_URL, decode_responses=True)


def new_session_id() -> str:
    """Gera um ID de sessão novo."""
    return str(uuid.uuid4())


def sdk_status() -> Dict[str, Any]:
    """Status básico do SDK (para o Render/healthcheck e UI)."""
    return {"ok": True, "redis": True}


def sdk_reset(session_id: str) -> Dict[str, Any]:
    """Reseta memória daquela sessão."""
    key = f"name:{session_id}"
    r.delete(key)
    return {"ok": True, "message": "Sessão resetada."}


def sdk(message: str, session_id: str) -> str:
    """
    SDK cognitivo mínimo:
    - detecta 'meu nome é X' e persiste por sessão no Redis
    - responde 'qual é meu nome'
    """
    key = f"name:{session_id}"
    msg = (message or "").strip()
    message_lower = msg.lower()

    # Detectar "meu nome é X"
    match = re.search(r"meu nome é\s+([a-zA-ZÀ-ÿ]+)", message_lower)
    if match:
        name = match.group(1).strip().capitalize()
        r.set(key, name)
        return f"Prazer, {name}! Vou lembrar disso."

    # Pergunta do nome
    if "qual é meu nome" in message_lower:
        name: Optional[str] = r.get(key)
        if name:
            return f"Seu nome é {name}."
        return "Você ainda não me disse seu nome."

    return "Não entendi ainda, mas estou aprendendo 😉"
