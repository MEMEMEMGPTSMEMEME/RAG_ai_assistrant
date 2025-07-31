# embed.py
import os
import pickle
from tqdm import tqdm
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

TXT_DIR = "parsed_docs"
VECTOR_DIR = "vector_store"
INDEX_FILE = os.path.join(VECTOR_DIR, "index.faiss")
ID_MAP_FILE = os.path.join(VECTOR_DIR, "doc_ids.pkl")

os.makedirs(VECTOR_DIR, exist_ok=True)

# ✅ 모델 로딩 (한국어/영어 모두 무난한 범용 모델)
model = SentenceTransformer("all-MiniLM-L6-v2")

# 📄 텍스트 파일 목록
files = [f for f in os.listdir(TXT_DIR) if f.endswith(".txt")]

embeddings = []
doc_ids = []

print(f"📚 {len(files)}개 문서 벡터화 중...")

for filename in tqdm(files, desc="🔍 임베딩 중"):
    with open(os.path.join(TXT_DIR, filename), "r", encoding="utf-8") as f:
        text = f.read()
    if len(text.strip()) < 30:
        continue  # 너무 짧은 문서는 제외

    embedding = model.encode(text, show_progress_bar=False)
    embeddings.append(embedding)
    doc_ids.append(filename)

# ▶ FAISS 저장
if embeddings:
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))
    faiss.write_index(index, INDEX_FILE)

    # ▶ 문서 ID 매핑 저장
    with open(ID_MAP_FILE, "wb") as f:
        pickle.dump(doc_ids, f)

    print(f"\n✅ 벡터 DB 저장 완료 → {INDEX_FILE}")
    print(f"🗂 문서 매핑 저장 완료 → {ID_MAP_FILE}")
else:
    print("⚠️ 유효한 문서가 없어 벡터 저장을 생략했습니다.")
