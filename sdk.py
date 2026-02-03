# SDK Cognitivo — memória por sessão

import uuid

# memória separada por sessão
sessions = {}

def new_session_id():
    return str(uuid.uuid4())

def get_session(session_id):
    if session_id not in sessions:
        sessions[session_id] = []
    return sessions[session_id]

def extract_name(text):
    text = text.lower()
    if "meu nome é" in text:
        return text.split("meu nome é")[-1].strip().title()
    return None

def sdk(message: str, session_id: str):
    memory = get_session(session_id)

    # salva mensagem
    memory.append(message)

    # detectar nome
    name = extract_name(message)
    if name:
        memory.append(f"nome:{name}")
        return f"Prazer, {name}. Vou lembrar disso."

    # recuperar nome salvo
    stored_name = None
    for item in memory:
        if item.startswith("nome:"):
            stored_name = item.split(":")[1]

    # pergunta do nome
    if "qual é meu nome" in message.lower():
        if stored_name:
            return f"Seu nome é {stored_name}."
        else:
            return "Você ainda não me disse seu nome."

    # resposta padrão
    return (
        "[Intent:general | Emotion:neutral]\n"
        f"Memórias: {' | '.join(memory)}\n"
        f"→ Entendi: {message}"
    )

def sdk_reset(session_id: str):
    sessions[session_id] = []
    return {"ok": True, "reset": "session", "session_id": session_id}

def sdk_status():
    return {
        "status": "SDK running",
        "sessions": len(sessions),
        "memory_preview": {k: v[-3:] for k, v in sessions.items()}
    }
