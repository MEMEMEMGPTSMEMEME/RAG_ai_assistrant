# crawler.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, urljoin
import os
import time

SKIP_EXT = [".pdf", ".zip", ".js", ".css", ".ico", ".png", ".jpg", ".jpeg", ".svg"]
MAX_FAIL = 3
MAX_LINKS = 1000

def collect_links(start_url, allowed_domains=None, output_file="all_links.txt"):
    parsed_start = urlparse(start_url)
    if allowed_domains is None:
        allowed_domains = [parsed_start.netloc]

    visited = set()
    to_visit = [start_url]
    fail_counts = {}

    os.makedirs("html", exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)

    with open(output_file, "w", encoding="utf-8") as f:
        while to_visit and len(visited) < MAX_LINKS:
            url = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)

            try:
                driver.get(url)
                time.sleep(1.2)
                print(f"🔗 수집 중: {url}")
                anchors = driver.find_elements("tag name", "a")

                for a in anchors:
                    href = a.get_attribute("href")
                    if not href:
                        continue
                    joined = urljoin(url, href)
                    parsed = urlparse(joined)
                    if not parsed.netloc or parsed.netloc not in allowed_domains:
                        continue
                    if any(parsed.path.endswith(ext) for ext in SKIP_EXT):
                        continue
                    if joined not in visited and joined not in to_visit:
                        to_visit.append(joined)
                        f.write(joined + "\n")

            except Exception as e:
                print(f"[ERROR] 실패: {url} - {e}")
                fail_counts[urlparse(url).netloc] = fail_counts.get(urlparse(url).netloc, 0) + 1
                continue

    driver.quit()
    print(f"\n✅ 링크 수집 완료: {len(visited)}개 저장 → {output_file}")
