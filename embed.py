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

def load_texts_from_directory(directory):
    texts, metadata = [], []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content.strip():
                        texts.append(content)
                        metadata.append({"filename": filename})
            except Exception as e:
                print(f"[ERROR] 파일 열기 실패: {filename} ({e})")
    return texts, metadata

def save_embeddings(index, metadata):
    os.makedirs(VECTOR_STORE, exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)
    print(f"✅ 벡터 저장 완료 → {INDEX_PATH}")

def embed_and_store(texts, metadata):
    print("✅ 임베딩 모델 로딩 중...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("📊 임베딩 생성 중...")
    embeddings = model.encode(texts, show_progress_bar=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    save_embeddings(index, metadata)

if __name__ == "__main__":
    texts, metadata = load_texts_from_directory(TXT_DIR)
    if not texts:
        print("⚠️ 추출된 텍스트가 없습니다.")
    else:
        embed_and_store(texts, metadata)
