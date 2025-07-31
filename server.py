from flask import Flask, request, jsonify
from urllib.parse import urlparse
import subprocess
import os
import traceback
from crawler import collect_links

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ALLOWED_DOMAINS = ["docs.blender.org", "docs.python.org"]

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

        if domain not in ALLOWED_DOMAINS:
            return jsonify({"error": f"Domain '{domain}' not allowed."}), 403

        print(f"[INFO] 📥 요청된 사이트: {site_url}")
        print("[INFO] 🔎 링크 수집 중...")
        collect_links(start_url=site_url, allowed_domains=ALLOWED_DOMAINS)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
