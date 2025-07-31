# html_downloader.py
import os
import requests
from urllib.parse import urlparse
from tqdm import tqdm

SAVE_DIR = "downloaded_html"
os.makedirs(SAVE_DIR, exist_ok=True)

with open("all_links.txt", "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

for url in tqdm(urls, desc="📥 다운로드 중"):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            parsed = urlparse(url)
            filename = parsed.path.strip("/").replace("/", "_")
            if not filename:
                filename = "index"
            full_path = os.path.join(SAVE_DIR, f"{filename}.html")
            with open(full_path, "w", encoding="utf-8") as out:
                out.write(r.text)
        else:
            print(f"[!] 실패: {url} ({r.status_code})")
    except Exception as e:
        print(f"[!] 에러: {url} ({e})")

print(f"\n✅ 저장 완료: {len(os.listdir(SAVE_DIR))}개 HTML → {SAVE_DIR}/")
