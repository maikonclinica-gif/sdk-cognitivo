# SDK Cognitivo — memória básica com continuidade

memory = []

def extract_name(text):
    text = text.lower()
    if "meu nome é" in text:
        return text.split("meu nome é")[-1].strip().title()
    return None

def sdk(message: str):
    global memory

    msg = message.lower().strip()

    # salva mensagem
    memory.append(message)

    # captura nome
    name = extract_name(message)
    if name:
        memory.append(f"nome:{name}")
        return f"Prazer, {name}. Vou lembrar disso."

    # recuperar nome salvo
    stored_name = None
    for item in memory:
        if item.startswith("nome:"):
            stored_name = item.split(":")[1]

    # pergunta sobre o nome (mais robusto)
    if "qual é meu nome" in msg or "qual e meu nome" in msg:
        if stored_name:
            return f"Seu nome é {stored_name}."
        return "Você ainda não me disse seu nome."

    # resposta padrão
    return (
        "[Intent:general | Emotion:neutral]\n"
        f"Memórias: {' | '.join(memory)}\n"
        f"→ Entendi: {message}"
    )

def sdk_status():
    return {
        "status": "SDK running",
        "memory_size": len(memory),
        "memory": memory
    }
