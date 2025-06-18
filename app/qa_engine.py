import json
from sentence_transformers import SentenceTransformer, util
from bs4 import BeautifulSoup

model = SentenceTransformer('all-MiniLM-L6-v2')

with open("data/discourse.json") as f:
    posts = json.load(f)

corpus = [p["title"] + " " + p["content"] for p in posts]
corpus_embeddings = model.encode(corpus, convert_to_tensor=True)

def find_answer(question):
    question_embedding = model.encode(question, convert_to_tensor=True)
    hits = util.semantic_search(question_embedding, corpus_embeddings, top_k=3)[0]

    response_links = []
    for hit in hits:
        post = posts[hit['corpus_id']]
        response_links.append({
            "url": post["url"],
            "text": BeautifulSoup(post["content"], "html.parser").get_text()[:100]
        })

    best_answer = BeautifulSoup(posts[hits[0]['corpus_id']]["content"], "html.parser").get_text()
    return best_answer, response_links
