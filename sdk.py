memory = []

def extract_name(text):
    text = text.lower()
    if "meu nome é" in text:
        return text.split("meu nome é")[-1].strip().title()
    return None

def sdk(message: str):
    global memory

    memory.append(message)

    name = extract_name(message)
    if name:
        memory.append(f"nome:{name}")
        return f"Prazer, {name}. Vou lembrar disso."

    stored_name = None
    for item in memory:
        if item.startswith("nome:"):
            stored_name = item.split(":")[1]

    if "qual é meu nome" in message.lower():
        if stored_name:
            return f"Seu nome é {stored_name}."
        else:
            return "Você ainda não me disse seu nome."

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
