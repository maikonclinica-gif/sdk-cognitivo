# SDK Cognitivo — memória básica com continuidade por sessão (cookie)
# Versão com persistência simples em arquivo + lock (mais estável em deploys)

import uuid
import json
import os
from pathlib import Path
from threading import Lock
from typing import Dict, List, Any, Optional

# =========================
# Config
# =========================

# Onde salvar as sessões.
# Em Render, /tmp existe e é gravável. (Não é "eterno", mas evita perder a cada request/worker reload.)
_STORE_PATH = Path(os.getenv("SDK_STORE_PATH", "/tmp/sdk_sessions.json"))

# Limites para não estourar memória
MAX_MESSAGES_PER_SESSION = int(os.getenv("SDK_MAX_MESSAGES_PER_SESSION", "60"))
MAX_SESSIONS = int(os.getenv("SDK_MAX_SESSIONS", "500"))

_lock = Lock()

# Memória por sessão:
# { "session_id": ["msg1", "msg2", "nome:Maikon", ...] }
_sessions: Dict[str, List[Any]] = {}


# =========================
# Persistência
# =========================

def _load_store() -> None:
    global _sessions
    try:
        if _STORE_PATH.exists():
            data = json.loads(_STORE_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                # garante formato {sid: list}
                cleaned = {}
                for sid, mem in data.items():
                    if isinstance(sid, str) and isinstance(mem, list):
                        cleaned[sid] = mem
                _sessions = cleaned
    except Exception:
        # Se der erro de leitura/corrupção, não derruba o app
        _sessions = {}

def _save_store() -> None:
    try:
        _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _STORE_PATH.write_text(json.dumps(_sessions, ensure_ascii=False), encoding="utf-8")
    except Exception:
        # Se não conseguir gravar, segue em RAM
        pass

# carrega na inicialização do módulo
with _lock:
    _load_store()


# =========================
# Sessão / Memória
# =========================

def new_session_id() -> str:
    return str(uuid.uuid4())

def _prune_limits() -> None:
    """
    Evita crescer infinito:
    - limita sessões
    - limita tamanho de memória por sessão
    """
    # Limita sessões (remove as mais antigas por ordem de inserção)
    if len(_sessions) > MAX_SESSIONS:
        # remove o excedente no começo
        excess = len(_sessions) - MAX_SESSIONS
        for sid in list(_sessions.keys())[:excess]:
            _sessions.pop(sid, None)

    # Limita mensagens por sessão
    for sid, mem in list(_sessions.items()):
        if isinstance(mem, list) and len(mem) > MAX_MESSAGES_PER_SESSION:
            _sessions[sid] = mem[-MAX_MESSAGES_PER_SESSION:]


def _get_memory(session_id: str) -> List[Any]:
    if session_id not in _sessions:
        _sessions[session_id] = []
    return _sessions[session_id]

def sdk_reset(session_id: str):
    with _lock:
        _sessions[session_id] = []
        _prune_limits()
        _save_store()
    return {"ok": True, "reset": "session", "session_id": session_id}


# =========================
# NLP simples (nome)
# =========================

def extract_name(text: str) -> Optional[str]:
    t = (text or "").strip()
    low = t.lower()

    if "meu nome é" in low:
        # pega tudo depois de "meu nome é"
        name_part = t[low.index("meu nome é") + len("meu nome é"):].strip()

        # limpa pontuação comum no final
        name_part = name_part.strip(" .!?,;:")

        if name_part:
            # Title-case simples
            return " ".join([p.capitalize() for p in name_part.split()])

    return None


# =========================
# SDK principal
# =========================

def sdk(message: str, session_id: str):
    with _lock:
        memory = _get_memory(session_id)

        # salva mensagem na memória
        memory.append(message)

        # verifica se o usuário falou o nome
        name = extract_name(message)
        if name:
            # remove nomes antigos
            memory[:] = [m for m in memory if not (isinstance(m, str) and m.startswith("nome:"))]
            memory.append(f"nome:{name}")

            _prune_limits()
            _save_store()
            return f"Prazer, {name}. Vou lembrar disso."

        # tenta recuperar nome da memória
        stored_name = None
        for item in memory:
            if isinstance(item, str) and item.startswith("nome:"):
                stored_name = item.split(":", 1)[1].strip()

        # se perguntar o nome
        if "qual é meu nome" in (message or "").lower():
            _prune_limits()
            _save_store()
            if stored_name:
                return f"Seu nome é {stored_name}."
            return "Você ainda não me disse seu nome."

        _prune_limits()
        _save_store()

        # resposta padrão
        return (
            "[Intent:general | Emotion:neutral]\n"
            f"Session: {session_id}\n"
            f"Memórias: {' | '.join([str(x) for x in memory])}\n"
            f"→ Entendi: {message}"
        )


def sdk_status():
    with _lock:
        sessions_info = {sid: len(mem) for sid, mem in _sessions.items()}
        return {
            "status": "SDK running",
            "sessions_count": len(_sessions),
            "sessions": sessions_info,
            "store_path": str(_STORE_PATH),
            "limits": {
                "max_messages_per_session": MAX_MESSAGES_PER_SESSION,
                "max_sessions": MAX_SESSIONS,
            },
        }
