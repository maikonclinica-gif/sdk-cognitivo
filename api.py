from fastapi import FastAPI
from pydantic import BaseModel
from sdk import sdk, sdk_status

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    reply = sdk(req.message)
    return {"reply": reply}

@app.get("/")
def root():
    return {"status": "SDK API running"}

@app.get("/status")
def status():
    return sdk_status()
