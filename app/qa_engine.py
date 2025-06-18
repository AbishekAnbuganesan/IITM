import json
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# 1. Load/initialize the embedding model once
model = SentenceTransformer("intfloat/e5-small")

# 2. Load Discourse posts
with open("data/tds_topics.json", encoding="utf-8") as f:
    discourse_posts = json.load(f)

# 3. Load TDS course content (links only)
with open("data/tds_course_content.json", encoding="utf-8") as f:
    tds_links = json.load(f)

# 4. Build a unified corpus & metadata
corpus = []
sources = []

for p in discourse_posts:
    title   = p.get("title", "")
    content = p.get("content", "")
    link    = p.get("link", "")
    corpus.append(f"{title} {content}")
    sources.append({
        "type":    "discourse",
        "title":   title,
        "content": content,
        "link":    link
    })

for p in tds_links:
    title = p.get("title", "")
    href  = p.get("href", "")
    corpus.append(f"{title} {href}")
    sources.append({
        "type":    "tds",
        "title":   title,
        "content": "",     # optional
        "link":    href
    })

# 5. Generate embeddings for the whole corpus
# (Not needed here since FAISS does it internally via HuggingFaceEmbeddings)
hf_embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-small")

# 6. Build FAISS vector store
search_engine = FAISS.from_texts(corpus, hf_embeddings)

# 7. Exposed search function
def find_answer(question: str):
    # Top 3 matching docs
    hits = search_engine.similarity_search(question, k=3)

    if not hits:
        return "Sorry, I couldn't find any relevant answer.", []

    # Get best match
    match_text  = hits[0].page_content
    match_index = corpus.index(match_text)
    src         = sources[match_index]

    # Prepare answer text
    if src["type"] == "discourse":
        answer = BeautifulSoup(src["content"], "html.parser").get_text().strip()
    else:
        answer = f"This comes from the course content page: {src['title']}"

    # Prepare links with proper schema
    links = []
    for hit in hits:
        idx = corpus.index(hit.page_content)
        links.append({
            "url": sources[idx]["link"],
            "text": sources[idx]["title"]
        })

    return answer, links
