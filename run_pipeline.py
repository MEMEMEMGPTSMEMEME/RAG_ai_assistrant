# run_pipeline.py
import subprocess
import os

print("🔗 [1/4] selenium_link_collector.py - 링크 수집 중...")
subprocess.run(["python", "selenium_link_collector.py"], check=True)

print("🌐 [2/4] html_downloader.py - HTML 다운로드 중...")
subprocess.run(["python", "html_downloader.py"], check=True)

print("📝 [3/4] parse_local_html.py - 텍스트 추출 중...")
subprocess.run(["python", "parse_local_html.py"], check=True)

print("🧠 [4/4] embed.py - 문서 임베딩 중...")
subprocess.run(["python", "embed.py"], check=True)

print("\n✅ 파이프라인 실행 완료!")
