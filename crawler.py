# crawler.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import re

SKIP_EXT = [".pdf", ".zip", ".js", ".css", ".ico", ".png", ".jpg", ".jpeg", ".svg"]
visited = set()

def collect_links(start_url, allowed_domains=None, output_file="all_links.txt", max_links=1000):
    if allowed_domains is None:
        parsed = urlparse(start_url)
        allowed_domains = [parsed.netloc]

    to_visit = [start_url]
    os.makedirs("html", exist_ok=True)
    collected = 0

    with open(output_file, "w", encoding="utf-8") as f:
        while to_visit and collected < max_links:
            url = to_visit.pop()
            if url in visited:
                continue
            visited.add(url)

            try:
                print(f"🔗 요청 중: {url}")
                response = requests.get(url, timeout=5)
                if response.status_code != 200:
                    continue
            except Exception as e:
                print(f"[ERROR] 요청 실패: {url} ({e})")
                continue

            parsed_url = urlparse(url)
            if not any(domain in parsed_url.netloc for domain in allowed_domains):
                continue
            if any(parsed_url.path.endswith(ext) for ext in SKIP_EXT):
                continue

            filename = re.sub(r"[^a-zA-Z0-9]", "_", url) + ".html"
            filepath = os.path.join("html", filename)
            with open(filepath, "w", encoding="utf-8") as html_file:
                html_file.write(response.text)
            collected += 1

            soup = BeautifulSoup(response.text, "html.parser")
            for link_tag in soup.find_all("a", href=True):
                href = link_tag["href"]
                full_url = urljoin(url, href)
                if full_url.startswith("http") and full_url not in visited and full_url not in to_visit:
                    to_visit.append(full_url)
                    f.write(full_url + "\n")

    print(f"\n✅ 수집 완료: {collected}개 링크 저장됨 → {output_file}")
