import os
import json
import time
import pickle
import logging
import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import List, Dict, Optional, Union, Any, Tuple
from pathlib import Path
from rank_bm25 import BM25Okapi
from collections import defaultdict
from sentence_transformers import SentenceTransformer
import warnings
import csv
import re
from langchain.schema import Document
from common.document_processor import Document

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn을 찾을 수 없습니다. 기본 임베딩을 사용합니다.")

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('VectorStore')

# MeCab 임포트 시도 (한국어 형태소 분석기)
try:
    from konlpy.tag import Mecab
    MECAB_AVAILABLE = True
except:
    MECAB_AVAILABLE = False
    logger.warning("MeCab을 로드할 수 없습니다. 기본 토큰화 방식을 사용합니다.")

# Gemma 임베딩 클래스 정의 (TF-IDF 기반)
class GemmaEmbedder:
    def __init__(self):
        """
        Gemma 스타일 임베딩 클래스 - TF-IDF와 랜덤 프로젝션을 사용
        """
        logger.info("GemmaEmbedder 초기화 중")
        self.vector_size = 256
        self.vocab = {}  # vocab 속성 추가 - 폴백 메커니즘에서 사용
        
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                max_features=5000,  # 최대 5000개의 특성 사용
                min_df=1,           # 최소 1회 이상 등장하는 단어만 사용 (수정됨)
                max_df=1.0,         # 최대 빈도 제한 없음 (수정됨)
                sublinear_tf=True   # tf에 로그 스케일 적용
            )
            self.use_fallback = False
            logger.info("TF-IDF 벡터라이저 초기화 성공")
        else:
            self.use_fallback = True
            logger.warning("scikit-learn을 찾을 수 없어 기본 임베딩 사용")
        
        # 랜덤 프로젝션 행렬 (5000 -> 256 차원으로 축소)
        self.projection = np.random.normal(0, 1/np.sqrt(self.vector_size), (5000, self.vector_size))
        
    def _tokenize(self, text):
        """간단한 토큰화"""
        # 기본 토큰화: 공백으로 분리하고 소문자로 변환
        return text.lower().split()
        
    def encode(self, sentences, convert_to_tensor=False, show_progress_bar=False):
        """
        문장을 임베딩 벡터로 변환
        """
        if isinstance(sentences, str):
            sentences = [sentences]
            
        # 진행 상황 표시
        if show_progress_bar:
            sentences_iter = tqdm(sentences, desc="임베딩 생성")
        else:
            sentences_iter = sentences
            
        # 기본 임베딩 사용
        if self.use_fallback:
            result = []
            for sentence in sentences_iter:
                vector = np.zeros(self.vector_size, dtype=np.float32)
                tokens = self._tokenize(sentence)
                
                for i, token in enumerate(tokens):
                    if token not in self.vocab:
                        self.vocab[token] = np.random.rand(self.vector_size).astype(np.float32) * 2 - 1
                        
                    position_weight = 1.0 / (1 + i * 0.1)
                    vector += self.vocab[token] * position_weight
                    
                # 벡터 정규화
                norm = np.linalg.norm(vector)
                if norm > 0:
                    vector = vector / norm
                    
                result.append(vector)
            return np.array(result)
        else:
            # TF-IDF 임베딩 사용
            try:
                # 문장이 하나만 있을 경우 최소 2개의 문서가 필요한 문제 처리
                if len(sentences) == 1:
                    # 임시로 같은 문장을 두 번 사용
                    temp_sentences = sentences + sentences
                    logger.info("문장이 하나뿐이라 임시로 복제하여 처리합니다.")
                else:
                    temp_sentences = sentences
                
                # 첫 번째 호출에서 vectorizer를 fit
                if not hasattr(self.vectorizer, 'vocabulary_'):
                    logger.info("TF-IDF 벡터라이저 학습 중...")
                    try:
                        sparse_vectors = self.vectorizer.fit_transform(temp_sentences)
                    except Exception as e:
                        logger.error(f"TF-IDF 벡터라이저 학습 실패: {str(e)}")
                        self.use_fallback = True
                        return self.encode(sentences, convert_to_tensor, show_progress_bar)
                else:
                    try:
                        sparse_vectors = self.vectorizer.transform(sentences)
                    except Exception as e:
                        logger.error(f"TF-IDF 변환 실패: {str(e)}")
                        self.use_fallback = True
                        return self.encode(sentences, convert_to_tensor, show_progress_bar)
                
                # 밀집 벡터 변환
                dense_vectors = sparse_vectors.toarray()
                
                # 차원이 5000보다 작을 경우 패딩
                if dense_vectors.shape[1] < 5000:
                    padded = np.zeros((dense_vectors.shape[0], 5000))
                    padded[:, :dense_vectors.shape[1]] = dense_vectors
                    dense_vectors = padded
                
                # 차원이 5000보다 크면 잘라내기
                if dense_vectors.shape[1] > 5000:
                    dense_vectors = dense_vectors[:, :5000]
                
                # 랜덤 프로젝션으로 차원 축소
                projected = dense_vectors @ self.projection
                
                # 정규화
                norms = np.linalg.norm(projected, axis=1, keepdims=True)
                norms[norms < 1e-10] = 1.0  # 매우 작은 값도 1로 설정하여 나눗셈 오류 방지
                normalized = projected / norms
                
                # 문장이 하나만 있었을 경우 첫 번째 벡터만 반환
                if len(sentences) == 1 and len(temp_sentences) > 1:
                    return normalized[:1]
                    
                return normalized
                
            except Exception as e:
                logger.error(f"TF-IDF 임베딩 생성 오류: {str(e)}")
                # 오류 발생 시 폴백 모드로 전환
                self.use_fallback = True
                logger.warning("기본 임베딩으로 폴백합니다.")
                return self.encode(sentences, convert_to_tensor, show_progress_bar)

class VectorStore:
    """벡터 저장소 클래스"""
    
    def __init__(self, embedding_model):
        """벡터 저장소 초기화
        
        Args:
            embedding_model: 임베딩 모델 객체
        """
        self.embedding_model = embedding_model
        self.documents = []
        self.embeddings = []
        self.bm25 = None
        self.tokenized_corpus = []
        self.vector_store_path = Path("vector_store")
        self.vector_store_file = self.vector_store_path / "vector_store.pkl"
    
    def create_index(self, documents: List[Dict[str, Any]]) -> bool:
        """문서를 임베딩하여 인덱스 생성
        
        Args:
            documents: 문서 목록
            
        Returns:
            bool: 인덱스 생성 성공 여부
        """
        try:
            # 문서 저장
            self.documents = documents
            
            # 토큰화된 코퍼스 생성 (BM25용)
            self.tokenized_corpus = [self._tokenize(doc.get("question", "")) for doc in documents]
            
            # BM25 모델 생성
            self.bm25 = BM25Okapi(self.tokenized_corpus)
            
            # 모든 문서의 임베딩 계산
            texts = [doc.get("question", "") for doc in documents]
            self.embeddings = self.embedding_model.embed_documents(texts)
            
            logger.info(f"{len(documents)}개 문서의 인덱스를 생성했습니다.")
            return True
        
        except Exception as e:
            logger.error(f"인덱스 생성 중 오류 발생: {str(e)}")
            return False
    
    def _tokenize(self, text: str) -> List[str]:
        """텍스트를 토큰화
        
        Args:
            text: 토큰화할 텍스트
            
        Returns:
            List[str]: 토큰 목록
        """
        # 간단한 공백 기반 토큰화 
        return text.split()
    
    def similarity_search(self, query: str, top_k: int = 3) -> List[Dict]:
        """쿼리와 유사한 문서 검색
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 문서 수
            
        Returns:
            List[Dict]: 유사도 점수와 함께 문서 반환
        """
        if not self.documents or not self.embeddings:
            logger.warning("문서나 임베딩이 로드되지 않았습니다")
            return []
            
        try:
            # 쿼리 임베딩
            query_embedding = self.embedding_model.embed_query(query)
            
            # 문서와의 유사도 계산
            similarities = []
            for idx, doc_embedding in enumerate(self.embeddings):
                # 코사인 유사도 계산 (값이 클수록 유사도가 높음)
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                similarities.append((idx, similarity))
            
            # 유사도 기준 내림차순 정렬 (높은 값이 더 유사함)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # top_k 결과 반환
            results = []
            for idx, score in similarities[:top_k]:
                doc = self.documents[idx].copy()
                doc['score'] = float(score)
                results.append(doc)
                
            logger.info(f"검색 결과: {len(results)}개")
            return results
            
        except Exception as e:
            logger.error(f"유사도 검색 중 오류 발생: {str(e)}")
            return []
            
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """두 벡터 간의 코사인 유사도 계산
        
        Args:
            vec1: 첫 번째 벡터
            vec2: 두 번째 벡터
            
        Returns:
            float: 코사인 유사도 (값이 클수록 유사도가 높음)
        """
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        
        # 0으로 나누기 방지
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0
            
        return dot_product / (norm_vec1 * norm_vec2)
    
    def save(self) -> bool:
        """벡터 저장소를 파일로 저장
        
        Returns:
            bool: 저장 성공 여부
        """
        try:
            # 벡터 저장소 디렉토리 생성
            os.makedirs(self.vector_store_path, exist_ok=True)
            
            # 벡터 저장소 상태 저장
            data = {
                "documents": self.documents,
                "embeddings": self.embeddings,
                "tokenized_corpus": self.tokenized_corpus
            }
            
            with open(self.vector_store_file, "wb") as f:
                pickle.dump(data, f)
            
            logger.info(f"벡터 저장소가 {self.vector_store_file}에 저장되었습니다.")
            return True
        
        except Exception as e:
            logger.error(f"벡터 저장소 저장 중 오류 발생: {str(e)}")
            return False
    
    def load(self) -> bool:
        """파일에서 벡터 저장소 로드
        
        Returns:
            bool: 로드 성공 여부
        """
        try:
            # 벡터 저장소 파일이 없으면 실패
            if not os.path.exists(self.vector_store_file):
                logger.warning(f"벡터 저장소 파일이 존재하지 않습니다: {self.vector_store_file}")
                return False
            
            # 벡터 저장소 상태 로드
            with open(self.vector_store_file, "rb") as f:
                data = pickle.load(f)
            
            self.documents = data.get("documents", [])
            self.embeddings = data.get("embeddings", [])
            self.tokenized_corpus = data.get("tokenized_corpus", [])
            
            # BM25 재초기화
            if self.tokenized_corpus:
                self.bm25 = BM25Okapi(self.tokenized_corpus)
            
            logger.info(f"{len(self.documents)}개 문서가 {self.vector_store_file}에서 로드되었습니다.")
            return True
        
        except Exception as e:
            logger.error(f"벡터 저장소 로드 중 오류 발생: {str(e)}")
            return False

    def get_response(self, query):
        """사용자 질문에 대한 응답 생성"""
        try:
            # 유사 문서 검색
            docs = self.similarity_search(query, top_k=1)
            
            if not docs:
                return "관련 정보를 찾을 수 없습니다. 다른 질문을 해보세요."
            
            # 가장 관련성 높은 답변 반환
            best_match = docs[0]
            answer = best_match.get("answer", "")
            
            # 로그 기록
            logger.info(f"응답 생성 완료 - 쿼리: '{query}', 매칭 질문: '{best_match.get('question', '')}'")
            
            return answer
            
        except Exception as e:
            logger.error(f"응답 생성 중 오류 발생: {str(e)}")
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"

    def load_from_csv(self, csv_path: Optional[str] = None) -> bool:
        """CSV 파일에서 문서 로드
        
        Args:
            csv_path: CSV 파일 경로
            
        Returns:
            bool: 로드 성공 여부
        """
        if not csv_path:
            csv_path = str(Path("./data") / "campusfaq.csv")
        
        logger.info(f"CSV 파일에서 데이터 로드: {csv_path}")
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"CSV 로드 완료: {len(df)}개 행")
            
            # 컬럼 이름 확인 및 조정
            question_col = None
            answer_col = None
            
            for col in df.columns:
                if col.lower() in ['question', 'q']:
                    question_col = col
                if col.lower() in ['answer', 'a']:
                    answer_col = col
            
            if not question_col or not answer_col:
                logger.error(f"CSV 파일에 필요한 열이 없음: {df.columns}")
                return False
                
            self.documents = []
            for _, row in df.iterrows():
                self.documents.append({
                    "question": row[question_col],
                    "answer": row[answer_col]
                })
                
            logger.info(f"{len(self.documents)}개 문서 로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"CSV 로드 중 오류 발생: {str(e)}")
            return False

    def load_data(self, csv_path: str) -> bool:
        """CSV 파일에서 데이터 로드하고 인덱스 생성
        
        Args:
            csv_path: CSV 파일 경로
            
        Returns:
            bool: 로드 성공 여부
        """
        try:
            # CSV 파일에서 문서 로드
            success = self.load_from_csv(csv_path)
            if not success:
                return False
            
            # 토큰화된 코퍼스 생성 (BM25용)
            self.tokenized_corpus = [self._tokenize(doc.get("question", "")) for doc in self.documents]
            
            # BM25 모델 생성
            self.bm25 = BM25Okapi(self.tokenized_corpus)
            
            # 모든 문서의 임베딩 계산 (임베딩 모델이 있는 경우)
            if self.embedding_model:
                texts = [doc.get("question", "") for doc in self.documents]
                self.embeddings = self.embedding_model.embed_documents(texts)
            
            logger.info(f"{len(self.documents)}개 문서의 인덱스를 생성했습니다.")
            return True
            
        except Exception as e:
            logger.error(f"데이터 로드 중 오류 발생: {str(e)}")
            return False 