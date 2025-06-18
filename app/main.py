from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.qa_engine import find_answer
from app.utils import extract_text_from_image
import os

app = FastAPI()

# Define the request model
class Query(BaseModel):
    question: str
    image: str = None  # base64-encoded string (optional)

# Enable CORS to allow external requests (e.g., from Swagger UI or a frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to allowed domains
    allow_credentials=True,
    allow_methods=["*"],  # Includes GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)

# Root POST endpoint to answer questions
@app.post("/")
async def answer_question(query: Query):
    question = query.question
    if query.image:
        extracted = extract_text_from_image(query.image)
        question += " " + extracted

    answer, links = find_answer(question)
    return {"answer": answer, "links": links}

# Local dev only: Run app with uvicorn directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)