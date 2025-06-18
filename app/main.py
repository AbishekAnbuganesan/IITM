from fastapi import FastAPI
from pydantic import BaseModel
from app.qa_engine import find_answer
from app.utils import extract_text_from_image
import os

app = FastAPI()

class Query(BaseModel):
    question: str
    image: str = None

@app.post("/")
async def answer_question(query: Query):
    question = query.question
    if query.image:
        extracted = extract_text_from_image(query.image)
        question += " " + extracted

    answer, links = find_answer(question)
    return {"answer": answer, "links": links}

# ── ADD THIS ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
