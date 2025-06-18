from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import json

# 1. Load model
model = SentenceTransformer("intfloat/e5-small")
hf_embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-small")

# 2. Load data
with open("data/tds_topics.json", encoding="utf-8") as f:
    discourse_posts = json.load(f)

with open("data/tds_course_content.json", encoding="utf-8") as f:
    tds_links = json.load(f)

# 3. Prepare corpus and sources
corpus = []
sources = []

for p in discourse_posts:
    title = p.get("title", "")
    content = p.get("content", "")
    link = p.get("link", "")
    corpus.append(f"{title} {content}")
    sources.append({
        "type": "discourse",
        "title": title,
        "content": content,
        "link": link
    })

for p in tds_links:
    title = p.get("title", "")
    href = p.get("href", "")
    corpus.append(f"{title} {href}")
    sources.append({
        "type": "tds",
        "title": title,
        "content": "",
        "link": href
    })

# 4. Create the search engine
search_engine = FAISS.from_texts(corpus, hf_embeddings)

# 5. Define the function AFTER the search engine is available
def find_answer(question: str):
    hits = search_engine.similarity_search(question, k=3)
    if not hits:
        return "Sorry, I couldn't find any relevant answer.", []

    links = []
    for hit in hits:
        idx = corpus.index(hit.page_content)
        src = sources[idx]
        title = src.get("title", "Untitled")
        url = src.get("link") or "https://tds.s-anand.net/#/"
        links.append({"url": url, "text": title})

    best = sources[corpus.index(hits[0].page_content)]
    if best["type"] == "discourse":
        raw_content = best.get("content", "")
        answer = BeautifulSoup(raw_content, "html.parser").get_text().strip()
        if not answer:
            answer = f"(No detailed content found, but related to: {best.get('title', 'Untitled')})"
    else:
        answer = f"This is from the course content page: {best.get('title', 'Untitled')}"

    return answer, links
