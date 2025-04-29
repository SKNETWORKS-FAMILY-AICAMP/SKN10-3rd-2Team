import os
from dotenv import load_dotenv
from pathlib import Path

# .env 파일 로드
load_dotenv()

# API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")

# Ollama 설정
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma:2b")

# 벡터 스토어 설정
BASE_DIR = Path(__file__).parent.parent
VECTOR_STORE_PATH = BASE_DIR / os.getenv("VECTOR_STORE_PATH", "data/vector_store")
DATA_PATH = BASE_DIR / os.getenv("DATA_PATH", "data/documents")

# 검색 설정
TOP_K = int(os.getenv("TOP_K", 3))
THRESHOLD = float(os.getenv("THRESHOLD", 0.4))

# 디렉토리 생성
VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
DATA_PATH.mkdir(parents=True, exist_ok=True) 