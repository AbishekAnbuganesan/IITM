from fastapi import FastAPI
from pydantic import BaseModel
from app.qa_engine import find_answer
from app.utils import extract_text_from_image

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

    return {
        "answer": answer,
        "links": links
    }
if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # default fallback
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)