from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import redis
import os
import re

app = FastAPI()

# ===== REDIS =====
REDIS_URL = os.getenv("REDIS_URL")

r = redis.from_url(
    REDIS_URL,
    decode_responses=True
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.get("/")
def root():
    return FileResponse("index.html")

def sdk(message: str, session_id: str):

    key = f"name:{session_id}"
    message_lower = message.lower()

    # Detectar "meu nome é X"
    match = re.search(r"meu nome é (\w+)", message_lower)
    if match:
        name = match.group(1).capitalize()
        r.set(key, name)
        return f"Prazer, {name}! Vou lembrar disso."

    # Pergunta do nome
    if "qual é meu nome" in message_lower:
        name = r.get(key)
        if name:
            return f"Seu nome é {name}."
        else:
            return "Você ainda não me disse seu nome."

    return "Não entendi ainda, mas estou aprendendo 😉"

@app.post("/chat")
def chat(req: ChatRequest):
    reply = sdk(req.message, req.session_id)
    return {"reply": reply}
