from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uuid

from sdk import sdk, sdk_status, sdk_reset

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

def get_or_set_session_id(request: Request, response: JSONResponse) -> str:
    sid = request.cookies.get("sdk_session_id")
    if not sid:
        sid = str(uuid.uuid4())
        # cookie simples (pode melhorar depois com secure/samesite)
        response.set_cookie("sdk_session_id", sid, httponly=False, samesite="lax")
    return sid

@app.get("/")
def root():
    return FileResponse("index.html")

@app.post("/chat")
def chat(req: ChatRequest, request: Request):
    response = JSONResponse(content={"reply": ""})
    sid = get_or_set_session_id(request, response)

    reply = sdk(sid, req.message)
    response.body = JSONResponse(content={"reply": reply}).body
    return response

@app.get("/status")
def status(request: Request):
    response = JSONResponse(content={})
    sid = get_or_set_session_id(request, response)

    payload = sdk_status(sid)
    response.body = JSONResponse(content=payload).body
    return response

@app.post("/reset")
def reset(request: Request):
    response = JSONResponse(content={})
    sid = get_or_set_session_id(request, response)

    payload = sdk_reset(sid)
    response.body = JSONResponse(content=payload).body
    return response
