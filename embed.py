# embed.py
import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

TXT_DIR = "parsed_docs"
VECTOR_STORE = "vector_store"
INDEX_PATH = os.path.join(VECTOR_STORE, "faiss_index.index")
METADATA_PATH = os.path.join(VECTOR_STORE, "metadata.pkl")

def load_texts():
    texts = []
    metadata = []
    for filename in os.listdir(TXT_DIR):
        if filename.endswith(".txt"):
            with open(os.path.join(TXT_DIR, filename), "r", encoding="utf-8") as f:
                content = f.read()
                texts.append(content)
                metadata.append({"filename": filename})
    return texts, metadata

def embed_and_store(texts, metadata):
    print("✅ 임베딩 모델 로딩 중...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    print("📊 임베딩 생성 중...")
    embeddings = model.encode(texts, show_progress_bar=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    print("💾 벡터 저장 중...")
    os.makedirs(VECTOR_STORE, exist_ok=True)
    faiss.write_index(index, INDEX_PATH)

    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print(f"✅ 완료! 저장 위치: {INDEX_PATH}")

if __name__ == "__main__":
    texts, metadata = load_texts()
    if not texts:
        print("⚠️ 추출된 텍스트가 없습니다.")
    else:
        embed_and_store(texts, metadata)
