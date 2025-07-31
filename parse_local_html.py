# parse_local_html.py
import os
from bs4 import BeautifulSoup
from tqdm import tqdm

HTML_DIR = "downloaded_html"
SAVE_DIR = "parsed_docs"
os.makedirs(SAVE_DIR, exist_ok=True)

def clean_text(text):
    return ' '.join(text.strip().split())

files = [f for f in os.listdir(HTML_DIR) if f.endswith(".html")]

for filename in tqdm(files, desc="📄 HTML → TXT 변환 중"):
    path = os.path.join(HTML_DIR, filename)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "html.parser")

    content = soup.find("main") or soup.find("body") or soup
    if content:
        text = clean_text(content.get_text())
        if len(text) > 50:
            txt_file = os.path.splitext(filename)[0] + ".txt"
            with open(os.path.join(SAVE_DIR, txt_file), "w", encoding="utf-8") as out:
                out.write(text)

print(f"\n✅ 총 {len(os.listdir(SAVE_DIR))}개 텍스트 문서 저장 완료 → {SAVE_DIR}/")
