# SDK Cognitivo — memória básica com continuidade (robusto)

memory = []

def normalize(text: str) -> str:
    """
    Normaliza texto para comparação:
    - lowercase
    - remove acentos comuns
    - tira espaços extras
    """
    text = text.lower().strip()
    # remoção simples de acentos (sem libs externas)
    text = (
        text.replace("á", "a").replace("à", "a").replace("ã", "a").replace("â", "a")
            .replace("é", "e").replace("ê", "e")
            .replace("í", "i")
            .replace("ó", "o").replace("ô", "o").replace("õ", "o")
            .replace("ú", "u")
            .replace("ç", "c")
    )
    # normaliza espaços
    while "  " in text:
        text = text.replace("  ", " ")
    return text

def extract_name(text: str):
    t = normalize(text)
    if "meu nome e" in t:
        # pega tudo depois de "meu nome e"
        name_part = t.split("meu nome e")[-1].strip()
        # pega só a primeira "frase" (até ponto, exclamação, interrogação)
        for sep in [".", "!", "?", ",", ";", ":"]:
            name_part = name_part.split(sep)[0].strip()
        # Title Case simples
        return name_part.title() if name_part else None
    return None

def get_stored_name():
    stored = None
    for item in memory:
        if isinstance(item, str) and item.startswith("nome:"):
            stored = item.split(":", 1)[1]
    return stored

def is_asking_name(msg_norm: str) -> bool:
    # cobre:
    # "qual é meu nome"
    # "qual é o meu nome"
    # "qual e meu nome"
    # "qual e o meu nome"
    return ("qual" in msg_norm) and ("meu nome" in msg_norm)

def sdk(message: str):
    global memory

    msg_norm = normalize(message)

    # salva mensagem na memória
    memory.append(message)

    # se o usuário falou o nome
    name = extract_name(message)
    if name:
        memory.append(f"nome:{name}")
        return f"Prazer, {name}. Vou lembrar disso."

    # se perguntar o nome
    if is_asking_name(msg_norm):
        stored_name = get_stored_name()
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
