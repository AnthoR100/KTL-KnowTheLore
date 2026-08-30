from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from knowthelore.rag.generator import answer, answer_stream

app = FastAPI(title="KnowTheLore API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class Question(BaseModel):
    question: str
    k: int = 5


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", responses={503: {"description": "LLM (Ollama) indisponible ou en erreur"}})
def ask(payload: Question):
    try:
        return answer(payload.question, k=payload.k)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/ask-stream")
def ask_stream(payload: Question):
    return StreamingResponse(
        answer_stream(payload.question, k=payload.k),
        media_type="text/plain",
    )