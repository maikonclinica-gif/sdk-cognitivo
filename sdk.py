import json, os
from datetime import datetime

MEMORY_FILE = "sdk_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            print("⚠️ Memória corrompida. Criando nova.")
    return {"history": [], "insights": []}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

memory = load_memory()

def detect_intent(text):
    keywords = {
        "build": ["criar", "construir", "desenvolver", "sdk", "projeto"],
        "problem": ["problema", "erro", "falha", "bloqueou", "não consigo"],
        "money": ["dinheiro", "lucro", "ganhar", "vender"],
    }
    t = text.lower()
    for intent, words in keywords.items():
        if any(w in t for w in words):
            return intent
    return "general"

def detect_emotion(text):
    t = text.lower()
    if any(w in t for w in ["medo", "ansioso", "preocupado"]):
        return "fear"
    if any(w in t for w in ["feliz", "animado", "confiante"]):
        return "positive"
    if any(w in t for w in ["raiva", "ódio", "revoltado"]):
        return "anger"
    return "neutral"

def summarize(text, max_len=120):
    text = " ".join(text.split())
    return text[:max_len] + ("..." if len(text) > max_len else "")

def cognitive_layer(user_input, memory):
    insight = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "intent": detect_intent(user_input),
        "emotion": detect_emotion(user_input),
        "summary": summarize(user_input),
    }
    memory["insights"].append(insight)
    return insight

def retrieve_relevant_memories(query, memory, top_k=3):
    q = set(query.lower().split())
    scored = []
    for item in memory["history"]:
        text = item["user"]
        s = len(q.intersection(set(text.lower().split())))
        if s > 0:
            scored.append((s, text))
    scored.sort(reverse=True)
    return [t for _, t in scored[:top_k]]

def generate_response(user, insight):
    relevant = retrieve_relevant_memories(user, memory, top_k=3)
    if relevant:
        mem_txt = " | ".join(relevant)
        return (
            f"[Intent:{insight['intent']} | Emotion:{insight['emotion']}]\n"
            f"Memórias: {mem_txt}\n"
            f"→ Entendi: {insight['summary']}"
        )
    return f"[Intent:{insight['intent']} | Emotion:{insight['emotion']}] → Entendi: {insight['summary']}"

def sdk(user_text: str):
    user_text = (user_text or "").strip()
    if not user_text:
        return "⚠️ Envie um texto."

    insight = cognitive_layer(user_text, memory)
    memory["history"].append({"user": user_text, "insight": insight})
    save_memory(memory)
    return generate_response(user_text, insight)

def sdk_status():
    return {
        "history_count": len(memory["history"]),
        "insights_count": len(memory["insights"]),
        "memory_file": MEMORY_FILE,
    }

if __name__ == "__main__":
    print("SDK pronto. Digite algo:")
    while True:
        user = input("> ")
        print(sdk(user))
