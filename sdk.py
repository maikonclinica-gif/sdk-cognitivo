# SDK Cognitivo — memória persistente por sessão (SQLite)

from typing import Optional
import memory_store  # <-- IMPORTA O MÓDULO, NÃO FUNÇÕES DIRETAS

memory_store.init_db()

def extract_name(text: str) -> Optional[str]:
    t = text.strip().lower()
    if "meu nome é" in t:
        name = t.split("meu nome é", 1)[-1].strip()
        name = name.replace(".", "").replace("!", "").replace("?", "")
        return name.title() if name else None
    return None

def sdk(session_id: str, message: str) -> str:
    memory_store.add_memory(session_id, message)

    name = extract_name(message)
    if name:
        memory_store.add_memory(session_id, f"nome:{name}")
        return f"Prazer, {name}. Vou lembrar disso."

    stored = memory_store.find_first_by_prefix(session_id, "nome:")
    stored_name = stored.split(":", 1)[1] if stored else None

    if "qual é meu nome" in message.lower():
        if stored_name:
            return f"Seu nome é {stored_name}."
        return "Você ainda não me disse seu nome."

    mem = memory_store.get_memories(session_id, limit=30)

    return (
        "[Intent:general | Emotion:neutral]\n"
        f"Session: {session_id}\n"
        f"Memórias: {' | '.join(mem)}\n"
        f"→ Entendi: {message}"
    )

def sdk_status(session_id: str):
    mem = memory_store.get_memories(session_id, limit=200)
    return {
        "status": "SDK running",
        "session_id": session_id,
        "memory_size": len(mem),
        "memory": mem
    }

def sdk_reset(session_id: str):
    memory_store.clear_session(session_id)
    return {"ok": True, "reset": "session", "session_id": session_id}
