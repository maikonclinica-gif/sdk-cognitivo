# SDK Cognitivo — memória básica com continuidade por sessão (cookie)

import uuid

# Memória por sessão:
# { "session_id": ["msg1", "msg2", "nome:Maikon", ...] }
_sessions = {}

def new_session_id() -> str:
    return str(uuid.uuid4())

def _get_memory(session_id: str):
    if session_id not in _sessions:
        _sessions[session_id] = []
    return _sessions[session_id]

def sdk_reset(session_id: str):
    _sessions[session_id] = []
    return {"ok": True, "reset": "session", "session_id": session_id}

def extract_name(text: str):
    t = (text or "").strip()
    low = t.lower()
    if "meu nome é" in low:
        # pega tudo depois de "meu nome é"
        name_part = t[low.index("meu nome é") + len("meu nome é"):].strip()
        if name_part:
            # title-case simples
            return " ".join([p.capitalize() for p in name_part.split()])
    return None

def sdk(message: str, session_id: str):
    memory = _get_memory(session_id)

    # salva mensagem na memória
    memory.append(message)

    # verifica se o usuário falou o nome
    name = extract_name(message)
    if name:
        # remove nomes antigos (se quiser manter histórico, comente esse bloco)
        memory[:] = [m for m in memory if not str(m).startswith("nome:")]
        memory.append(f"nome:{name}")
        return f"Prazer, {name}. Vou lembrar disso."

    # tenta recuperar nome da memória
    stored_name = None
    for item in memory:
        if isinstance(item, str) and item.startswith("nome:"):
            stored_name = item.split(":", 1)[1].strip()

    # se perguntar o nome
    if "qual é meu nome" in (message or "").lower():
        if stored_name:
            return f"Seu nome é {stored_name}."
        return "Você ainda não me disse seu nome."

    # resposta padrão
    return (
        "[Intent:general | Emotion:neutral]\n"
        f"Session: {session_id}\n"
        f"Memórias: {' | '.join([str(x) for x in memory])}\n"
        f"→ Entendi: {message}"
    )

def sdk_status():
    # status geral (quantas sessões existem e tamanhos)
    sessions_info = {sid: len(mem) for sid, mem in _sessions.items()}
    return {
        "status": "SDK running",
        "sessions_count": len(_sessions),
        "sessions": sessions_info
    }
