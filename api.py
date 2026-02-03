from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from sdk import sdk, sdk_status, new_session_id, sdk_reset

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return FileResponse("index.html")

@app.post("/chat")
def chat(req: ChatRequest, request: Request):
    # pega session_id do cookie; se não existir, cria uma nova sessão
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = new_session_id()

    reply = sdk(req.message, session_id)

    # devolve JSON e também seta cookie para manter continuidade
    resp = JSONResponse({"reply": reply, "session_id": session_id})
    resp.set_cookie(
        key="session_id",
        value=session_id,
        httponly=False,   # se seu front lê via JS, deixe False
        samesite="lax"
    )
    return resp

@app.post("/reset")
def reset(request: Request):
    # reseta só a sessão atual
    session_id = request.cookies.get("session_id") or new_session_id()
    data = sdk_reset(session_id)

    resp = JSONResponse(data)
    resp.set_cookie(
        key="session_id",
        value=session_id,
        httponly=False,
        samesite="lax"
    )
    return resp

@app.get("/status")
def status():
    return sdk_status()
