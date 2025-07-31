# crawler.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
import time

SKIP_EXT = [".pdf", ".zip", ".js", ".css", ".ico", ".png", ".jpg", ".jpeg", ".svg"]
MAX_FAIL = 3

def collect_links(start_url, allowed_domains, output_file="all_links.txt", max_links=1000):
    fail_counts = {}
    visited = set()
    to_visit = [start_url]

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    with open(output_file, "w", encoding="utf-8") as f:
        while to_visit and len(visited) < max_links:
            url = to_visit.pop()
            if url in visited:
                continue
            visited.add(url)

            parsed = urlparse(url)
            domain = parsed.netloc
            if fail_counts.get(domain, 0) >= MAX_FAIL:
                print(f"⛔ 도메인 차단됨: {domain}")
                continue

            try:
                print(f"🔗 방문 중: {url}")
                driver.get(url)
                time.sleep(1.0)

                anchors = driver.find_elements("tag name", "a")
                for a in anchors:
                    href = a.get_attribute("href")
                    if not href:
                        continue

                    parsed_href = urlparse(href)
                    netloc = parsed_href.netloc
                    path = parsed_href.path
                    full_url = parsed_href.scheme + "://" + netloc + path

                    if not any(domain in netloc for domain in allowed_domains):
                        continue
                    if any(path.endswith(ext) for ext in SKIP_EXT):
                        continue
                    if full_url not in visited and full_url not in to_visit:
                        to_visit.append(full_url)
                        f.write(full_url + "\n")

            except Exception as e:
                print(f"[!] 실패: {url} ({e})")
                fail_counts[domain] = fail_counts.get(domain, 0) + 1

    driver.quit()
    print(f"\n✅ 수집 완료: {len(visited)}개 링크 → {output_file}")
