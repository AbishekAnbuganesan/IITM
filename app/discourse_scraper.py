import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_discourse(start_date, end_date, output_path="data/discourse.json"):
    api_url = "https://discourse.onlinedegree.iitm.ac.in/latest.json"

    response = requests.get(api_url)
    data = response.json()

    posts = []
    for topic in data["topic_list"]["topics"]:
        created_at = datetime.strptime(topic["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        if start_date <= created_at <= end_date:
            topic_id = topic["id"]
            url = f"https://discourse.onlinedegree.iitm.ac.in/t/{topic_id}.json"
            topic_data = requests.get(url).json()
            posts.append({
                "id": topic_id,
                "title": topic_data["title"],
                "content": topic_data["post_stream"]["posts"][0]["cooked"],
                "url": f"https://discourse.onlinedegree.iitm.ac.in/t/{topic_id}"
            })

    with open(output_path, "w") as f:
        json.dump(posts, f, indent=2)
