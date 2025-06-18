import json
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load Discourse posts
with open("data/tds_topics.json", encoding="utf-8") as f:
    discourse_posts = json.load(f)

# Load TDS course content (links only)
with open("data/tds_course_content.json", encoding="utf-8") as f:
    tds_links = json.load(f)

# Build a unified corpus
corpus = []
sources = []

# 1. Add Discourse posts
for p in discourse_posts:
    title = p.get("title", "")
    content = p.get("content", "")
    link = p.get("link", "")

    combined_text = title + " " + content
    corpus.append(combined_text)
    sources.append({
        "type": "discourse",
        "link": link,
        "title": title,
        "content": content
    })

# 2. Add TDS course page links
for p in tds_links:
    title = p.get("title", "")
    href = p.get("href", "")

    text = title + " " + href
    corpus.append(text)
    sources.append({
        "type": "tds",
        "title": title,
        "link": href,
        "content": ""  # Placeholder for future scraping
    })

# Generate embeddings
corpus_embeddings = model.encode(corpus, convert_to_tensor=True)

# Create FAISS vector store
embedding_model = HuggingFaceEmbeddings(model_name="intfloat/e5-small")
search_engine = FAISS.from_texts(corpus, embedding_model)

# Search function
def find_answer(question: str):
    # Load model
    model = SentenceTransformer("all-MiniLM-L6-v2")
    hits = search_engine.similarity_search(question, k=3)

    if not hits:
        return "Sorry, I couldn't find any relevant answer.", []

    match_text = hits[0].page_content
    match_index = corpus.index(match_text)
    match_source = sources[match_index]

    if match_source["type"] == "discourse":
        # Safely extract and clean HTML content
        answer = BeautifulSoup(match_source.get("content", ""), "html.parser").get_text()
    else:
        answer = f"This seems to be from the course page: {match_source.get('title', '')}"

    links = [sources[corpus.index(hit.page_content)].get("link", "") for hit in hits]

    return answer, links