import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://tds.s-anand.net/#/2025-01/"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "tds_course_content.json")

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

def wait_for_sidebar(driver):
    print("[INFO] Waiting for sidebar to load...")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
    )
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".sidebar-nav a"))
    )
    print("[INFO] Sidebar loaded.")

def extract_links(driver):
    print("[INFO] Extracting sidebar links...")
    links = driver.find_elements(By.CSS_SELECTOR, ".sidebar-nav a")
    print(f"[DEBUG] Found {len(links)} links.")

    items = []
    for link in links:
        title = link.text.strip()
        href = link.get_attribute("href")
        if title and href:
            items.append({"title": title, "href": href})

    print(f"[INFO] Extracted {len(items)} items.")
    return items

def save_to_file(data):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Saved to {OUTPUT_FILE}")

def main():
    driver = setup_driver()
    try:
        print(f"[INFO] Opening {BASE_URL}")
        driver.get(BASE_URL)
        wait_for_sidebar(driver)
        time.sleep(1.5)  # Slight extra wait to ensure JS is done
        data = extract_links(driver)
        save_to_file(data)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
