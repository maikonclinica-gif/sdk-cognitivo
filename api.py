from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sdk import sdk, sdk_status

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return FileResponse("index.html")

@app.post("/chat")
def chat(req: ChatRequest):
    reply = sdk(req.message)
    return {"reply": reply}

@app.get("/status")
def status():
    return sdk_status()
