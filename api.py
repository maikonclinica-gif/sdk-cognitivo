from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from sdk import sdk, sdk_status, sdk_reset, new_session_id

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return FileResponse("index.html")


@app.post("/chat")
def chat(req: ChatRequest, request: Request):
    # 1) Pega session_id do cookie (se existir)
    session_id = request.cookies.get("sdk_session")

    # 2) Se não existir, cria um novo
    created_new = False
    if not session_id:
        session_id = new_session_id()
        created_new = True

    # 3) Processa mensagem com sessão
    reply = sdk(req.message, session_id)

    # 4) Responde e garante cookie setado
    response = JSONResponse({"reply": reply})

    if created_new:
        # Cookie simples (demo). Depois dá pra endurecer.
        response.set_cookie(
            key="sdk_session",
            value=session_id,
            httponly=True,
            samesite="lax",
            secure=False,  # em HTTPS pode virar True; render geralmente é https
            max_age=60 * 60 * 24 * 30,  # 30 dias
        )

    return response


@app.get("/status")
def status():
    return sdk_status()


@app.post("/reset")
def reset(request: Request):
    """
    Reseta apenas a sessão atual (cookie).
    Se não tiver cookie, não faz nada.
    """
    session_id = request.cookies.get("sdk_session")
    result = sdk_reset(session_id=session_id) if session_id else {"ok": False, "error": "no session cookie"}
    return result


@app.post("/reset-all")
def reset_all():
    """
    Reseta tudo (todas as sessões).
    Use com cuidado.
    """
    return sdk_reset(session_id=None)
