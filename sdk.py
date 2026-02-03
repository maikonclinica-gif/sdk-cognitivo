from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sdk import sdk, sdk_status, new_session_id, sdk_reset

app = FastAPI()

# 🔥 CORS correto para cookies no Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cognitivo.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return FileResponse("index.html")


@app.post("/chat")
def chat(req: ChatRequest, request: Request):
    # pega session_id do cookie; se não existir, cria nova sessão
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = new_session_id()

    reply = sdk(req.message, session_id)

    resp = JSONResponse({"reply": reply, "session_id": session_id})
    resp.set_cookie(
        key="session_id",
        value=session_id,
        httponly=False,
        samesite="none",   # necessário em produção
        secure=True        # obrigatório em HTTPS
    )
    return resp


@app.post("/reset")
def reset(request: Request):
    session_id = request.cookies.get("session_id") or new_session_id()
    data = sdk_reset(session_id)

    resp = JSONResponse(data)
    resp.set_cookie(
        key="session_id",
        value=session_id,
        httponly=False,
        samesite="none",
        secure=True
    )
    return resp


@app.get("/status")
def status():
    return sdk_status()
