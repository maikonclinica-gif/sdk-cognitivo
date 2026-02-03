# SDK Cognitivo — memória básica com continuidade

memory = []

def extract_name(text):
    text = text.lower()
    if "meu nome é" in text:
        return text.split("meu nome é")[-1].strip().title()
    return None

def sdk(message: str):
    global memory

    # salva mensagem na memória
    memory.append(message)

    # verifica se o usuário falou o nome
    name = extract_name(message)
    if name:
        memory.append(f"nome:{name}")
        return f"Prazer, {name}. Vou lembrar disso."

    # tenta recuperar nome da memória
    stored_name = None
    for item in memory:
        if item.startswith("nome:"):
            stored_name = item.split(":")[1]

    # se perguntar o nome
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

def sdk_status():
    return {
        "status": "SDK running",
        "memory_size": len(memory),
        "memory": memory
    }
