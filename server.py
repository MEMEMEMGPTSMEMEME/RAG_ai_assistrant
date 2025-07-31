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
    })


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@app.route("/start_data_ingestion", methods=["POST"])
def start_data_ingestion():
    try:
        data = request.get_json()
        site_url = data.get("site_url")
        if not site_url:
            return jsonify({"error": "site_url is required"}), 400

        parsed = urlparse(site_url)
        domain = parsed.netloc
        print(f"[INFO] 📥 수집 시작: {site_url}")

        collect_links(start_url=site_url, allowed_domains=[domain])

        subprocess.run(["python", os.path.join(BASE_DIR, "html_downloader.py")], check=True)
        subprocess.run(["python", os.path.join(BASE_DIR, "parse_local_html.py")], check=True)
        subprocess.run(["python", os.path.join(BASE_DIR, "embed.py")], check=True)

        return jsonify({"status": "completed", "message": f"{domain} 문서 수집 및 임베딩 완료"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        query = data.get("query")
        if not query:
            return jsonify({"error": "query is required"}), 400

        print(f"[ASK] 🙋 질문: {query}")

        model = SentenceTransformer("all-MiniLM-L6-v2")

        index_path = os.path.join(BASE_DIR, "vector_store", "faiss_index.index")
        metadata_path = os.path.join(BASE_DIR, "vector_store", "metadata.pkl")

        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            return jsonify({"error": "벡터 인덱스 또는 메타데이터가 존재하지 않습니다."}), 500

        index = faiss.read_index(index_path)
        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)

        query_embedding = model.encode([query])
        D, I = index.search(query_embedding, min(3, index.ntotal))

        results = []
        for idx in I[0]:
            if 0 <= idx < len(metadata):
                path = os.path.join(BASE_DIR, "parsed_docs", metadata[idx]["filename"])
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        results.append(f.read()[:1000])

        return jsonify({"results": results})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
