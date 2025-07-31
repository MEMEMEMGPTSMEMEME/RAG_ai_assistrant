# server.py
from flask import Flask, request, jsonify
from urllib.parse import urlparse
import subprocess
import os
import traceback
from crawler import collect_links
from sentence_transformers import SentenceTransformer
import faiss
import pickle

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "✅ RAG Assistant 서버 실행 중입니다.",
        "available_endpoints": [
            "/health",
            "/start_data_ingestion",
            "/ask"
        ]
    }), 200

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

        domain = urlparse(site_url).netloc
        print(f"[INFO] 수집 시작 → 도메인: {domain}, URL: {site_url}")

        collect_links(start_url=site_url)

        for script in ["html_downloader.py", "parse_local_html.py", "embed.py"]:
            print(f"[INFO] 실행 중: {script}")
            subprocess.run(["python", os.path.join(BASE_DIR, script)], check=True)

        return jsonify({"status": "completed", "message": f"{domain} 문서 수집 및 벡터화 완료"}), 200

    except Exception as e:
        print(f"[ERROR] ❌ 인제스트 실패: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        query = data.get("query")

        if not query:
            return jsonify({"error": "query is required"}), 400

        model = SentenceTransformer("all-MiniLM-L6-v2")
        index_path = os.path.join(BASE_DIR, "vector_store", "faiss_index.index")
        metadata_path = os.path.join(BASE_DIR, "vector_store", "metadata.pkl")

        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            return jsonify({"error": "벡터 인덱스 또는 메타데이터 없음"}), 500

        index = faiss.read_index(index_path)
        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)

        query_embedding = model.encode([query])
        k = min(3, index.ntotal)
        _, I = index.search(query_embedding, k)

        results = []
        for idx in I[0]:
            if 0 <= idx < len(metadata):
                file = metadata[idx]["filename"]
                file_path = os.path.join(BASE_DIR, "parsed_docs", file)
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        results.append(f.read()[:1000])

        return jsonify({"results": results}), 200

    except Exception as e:
        print(f"[ERROR] ❌ 질문 처리 중 오류: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
