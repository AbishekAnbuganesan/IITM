import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DISCOURSE_URL = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "tds_topics.json")

def init_driver():
    print("[INFO] Connecting to existing Chrome session...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    print("[INFO] Connected to Chrome successfully.")
    return driver

def wait_for_topic_titles(driver):
    print("[INFO] Waiting for topic links to load...")
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.raw-topic-link"))
        )
        print("[INFO] Topic links loaded.")
    except Exception as e:
        print("[ERROR] Timeout: a.raw-topic-link elements not found.")
        raise e

def scrape_topic_links(driver):
    wait_for_topic_titles(driver)
    print("[INFO] Collecting topic links...")
    titles = driver.find_elements(By.CSS_SELECTOR, "a.raw-topic-link")
    links = []

    for title in titles:
        href = title.get_attribute("href")
        text = title.text.strip()
        print(f"[DEBUG] Title: {text} | Link: {href}")
        links.append({"title": text, "url": href})

    print(f"[INFO] Collected {len(links)} topics.")
    return links

def save_links(links):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(links, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Saved {len(links)} links to {OUTPUT_FILE}")

def main():
    driver = init_driver()

    print(f"[INFO] Navigating to {DISCOURSE_URL} ...")
    driver.get(DISCOURSE_URL)

    links = scrape_topic_links(driver)

    print("\n=== Summary of Topics ===")
    for i, link in enumerate(links, start=1):
        print(f"{i:02d}. {link['title']} → {link['url']}")

    save_links(links)

    print("\n[INFO] Done. Not closing browser to preserve session.")

if __name__ == "__main__":
    main()
