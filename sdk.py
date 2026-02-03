# sdk.py
# SDK Cognitivo — memória persistente e por sessão (cookie/session_id)

import json
import os
import uuid
from typing import Dict, Any, List, Optional

MEMORY_FILE = "memory.json"

# Limites simples pra não deixar crescer infinito
MAX_HISTORY_PER_SESSION = 50   # últimas mensagens do usuário
MAX_FACTS_PER_SESSION = 50     # fatos (ex.: nome)


def _safe_read_json(path: str) -> Dict[str, Any]:
    """Lê JSON com segurança. Se não existir ou estiver corrompido, volta vazio."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _safe_write_json(path: str, data: Dict[str, Any]) -> None:
    """Escreve JSON com segurança (gravação atômica)."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def load_memory_store() -> Dict[str, Any]:
    return _safe_read_json(MEMORY_FILE)


def save_memory_store(store: Dict[str, Any]) -> None:
    _safe_write_json(MEMORY_FILE, store)


def ensure_session(store: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    """Garante estrutura da sessão."""
    if "sessions" not in store or not isinstance(store["sessions"], dict):
        store["sessions"] = {}
    if session_id not in store["sessions"] or not isinstance(store["sessions"][session_id], dict):
        store["sessions"][session_id] = {"history": [], "facts": {}}
    if "history" not in store["sessions"][session_id] or not isinstance(store["sessions"][session_id]["history"], list):
        store["sessions"][session_id]["history"] = []
    if "facts" not in store["sessions"][session_id] or not isinstance(store["sessions"][session_id]["facts"], dict):
        store["sessions"][session_id]["facts"] = {}
    return store["sessions"][session_id]


def extract_name(text: str) -> Optional[str]:
    t = text.strip()

    # pega "meu nome é X"
    lower = t.lower()
    if "meu nome é" in lower:
        name = t.lower().split("meu nome é", 1)[-1].strip()
        if name:
            # limpa pontuação final comum
            name = name.rstrip(".!?,;:")
            # Title case simples (Maikon)
            return name.title()

    # pega "eu me chamo X"
    if "eu me chamo" in lower:
        name = t.lower().split("eu me chamo", 1)[-1].strip()
        if name:
            name = name.rstrip(".!?,;:")
            return name.title()

    return None


def remember_fact(session: Dict[str, Any], key: str, value: str) -> None:
    """Salva fato em facts."""
    session["facts"][key] = value

    # controle simples de tamanho (caso cresça com muitos fatos)
    if len(session["facts"]) > MAX_FACTS_PER_SESSION:
        # remove chaves antigas (ordem não garantida em dict antigo, mas ok para demo)
        keys = list(session["facts"].keys())
        for k in keys[:-MAX_FACTS_PER_SESSION]:
            session["facts"].pop(k, None)


def add_history(session: Dict[str, Any], message: str) -> None:
    session["history"].append(message)
    if len(session["history"]) > MAX_HISTORY_PER_SESSION:
        session["history"] = session["history"][-MAX_HISTORY_PER_SESSION:]


def get_fact(session: Dict[str, Any], key: str) -> Optional[str]:
    val = session["facts"].get(key)
    return val if isinstance(val, str) else None


def sdk(message: str, session_id: str) -> str:
    """
    Função principal do SDK.
    Recebe message e session_id.
    Persiste memória em memory.json
    """
    store = load_memory_store()
    session = ensure_session(store, session_id)

    # guarda histórico
    add_history(session, message)

    # detecta nome
    name = extract_name(message)
    if name:
        remember_fact(session, "nome", name)
        save_memory_store(store)
        return f"Prazer, {name}. Vou lembrar disso."

    # pergunta do nome
    if "qual é meu nome" in message.lower():
        stored_name = get_fact(session, "nome")
        save_memory_store(store)
        if stored_name:
            return f"Seu nome é {stored_name}."
        return "Você ainda não me disse seu nome."

    # resposta padrão (mostra um resumo bem simples)
    stored_name = get_fact(session, "nome")
    mem_line = []
    if stored_name:
        mem_line.append(f"nome:{stored_name}")
    # mostra só as últimas 5 mensagens pra não poluir
    last_msgs = session["history"][-5:]
    mem_line.extend(last_msgs)

    save_memory_store(store)

    return (
        "[Intent:general | Emotion:neutral]\n"
        f"Memórias: {' | '.join(mem_line)}\n"
        f"→ Entendi: {message}"
    )


def sdk_status() -> Dict[str, Any]:
    store = load_memory_store()
    sessions = store.get("sessions", {})
    return {
        "status": "SDK running",
        "sessions_count": len(sessions) if isinstance(sessions, dict) else 0,
        "memory_file": MEMORY_FILE,
    }


def sdk_reset(session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Se session_id for None, limpa tudo.
    Se session_id vier, limpa só aquela sessão.
    """
    store = load_memory_store()
    if "sessions" not in store or not isinstance(store["sessions"], dict):
        store["sessions"] = {}

    if session_id:
        store["sessions"].pop(session_id, None)
        save_memory_store(store)
        return {"ok": True, "reset": "session", "session_id": session_id}

    store["sessions"] = {}
    save_memory_store(store)
    return {"ok": True, "reset": "all"}


def new_session_id() -> str:
    return str(uuid.uuid4())
