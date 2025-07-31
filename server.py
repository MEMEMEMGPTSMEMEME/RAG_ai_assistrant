from flask import Flask, request, jsonify
from urllib.parse import urlparse
import subprocess
import os
import traceback
from crawler import collect_links
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_STORE_PATH = os.path.join(BASE_DIR, "vector_store", "doc_store.index")
DOCS_PATH = os.path.join(BASE_DIR, "vector_store", "doc_chunks.pkl")

# ▶ 임베딩 모델 로드
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route("/start_data_ingestion", methods=["POST"])
def start_data_ingestion():
    try:
        data = request.get_json()
        site_url = data.get("site_url")

        if not site_url:
            return jsonify({"error": "site_url is required"}), 400

        parsed = urlparse(site_url)
        domain = parsed.netloc

        print(f"[INFO] 📥 요청된 사이트: {site_url} (도메인: {domain})")
        print("[INFO] 🔎 링크 수집 중...")
        collect_links(start_url=site_url, allowed_domains=[domain])

        print("[INFO] ⬇ HTML 다운로드 실행...")
        subprocess.run(["python", os.path.join(BASE_DIR, "html_downloader.py")], check=True)

        print("[INFO] 📝 텍스트 추출 실행...")
        subprocess.run(["python", os.path.join(BASE_DIR, "parse_local_html.py")], check=True)

        print("[INFO] 🔍 문서 임베딩 실행...")
        subprocess.run(["python", os.path.join(BASE_DIR, "embed.py")], check=True)

        return jsonify({"status": "completed", "message": "문서 수집 및 임베딩 완료"}), 200

    except Exception as e:
        print(f"[ERROR] ❌ 오류 발생: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/ask", methods=["POST"])
def ask_question():
    try:
        data = request.get_json()
        query = data.get("query")

        if not query:
            return jsonify({"error": "query is required"}), 400

        if not os.path.exists(VECTOR_STORE_PATH) or not os.path.exists(DOCS_PATH):
            return jsonify({"error": "벡터 저장소가 존재하지 않습니다."}), 500

        print(f"[QUERY] 🤔 사용자 질문: {query}")
        query_vector = model.encode([query])
        query_vector = np.array(query_vector).astype("float32")

        # FAISS index 로드
        index = faiss.read_index(VECTOR_STORE_PATH)

        # 문서 chunk 로드
        with open(DOCS_PATH, "rb") as f:
            doc_chunks = pickle.load(f)

        D, I = index.search(query_vector, k=5)
        matched_docs = [doc_chunks[i] for i in I[0]]

        return jsonify({"documents": matched_docs}), 200

    except Exception as e:
        print(f"[ERROR] ❌ 질문 처리 중 오류: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
