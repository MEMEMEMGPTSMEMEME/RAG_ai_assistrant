from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException
from urllib.parse import urlparse
import time

visited = set()
max_depth = 2
output_file = "all_links.txt"

def collect_links(start_url, depth=0):
    if depth > max_depth or start_url in visited:
        return
    visited.add(start_url)

    try:
        print(f"🔎 수집 시작: {start_url}")
        driver.get(start_url)
        time.sleep(1.0)
        anchors = driver.find_elements("tag name", "a")
        for a in anchors:
            try:
                href = a.get_attribute("href")
            except StaleElementReferenceException:
                continue
            if href and href.startswith("http") and urlparse(href).netloc == urlparse(start_url).netloc:
                if href not in visited:
                    collect_links(href, depth + 1)
    except Exception as e:
        print(f"[!] 실패: {start_url} ({e})")

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)

seed_urls = [
    "https://docs.jangafx.com/docs/EmberGen/4.3/getting-started",
    "https://docs.blender.org/manual/en/4.0/index.html",
    "https://helpx.adobe.com/photoshop/user-guide.html",
    "https://www.blender.org/manual/en/4.0/addons/index.html",
]

for url in seed_urls:
    collect_links(url)

with open(output_file, "w", encoding="utf-8") as f:
    for link in sorted(visited):
        f.write(link + "\n")

driver.quit()
print(f"\n✅ 링크 수집 완료: {len(visited)}개 → {output_file}")
