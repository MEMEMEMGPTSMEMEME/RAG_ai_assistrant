# parse_local_html.py

import os
from bs4 import BeautifulSoup

INPUT_DIR = "downloaded_html"
OUTPUT_DIR = "parsed_docs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "header", "footer", "nav"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)

def parse_all_html_files():
    if not os.path.exists(INPUT_DIR):
        print(f"[ERROR] ❌ 입력 디렉토리 없음: {INPUT_DIR}")
        return

    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith(".html"):
            continue
        in_path = os.path.join(INPUT_DIR, filename)
        out_path = os.path.join(OUTPUT_DIR, filename.replace(".html", ".txt"))

        try:
            with open(in_path, "r", encoding="utf-8") as f:
                html = f.read()
            cleaned = clean_text(html)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            print(f"✅ 텍스트 추출 완료: {filename}")
        except Exception as e:
            print(f"[ERROR] {filename} 처리 실패: {e}")

if __name__ == "__main__":
    parse_all_html_files()
