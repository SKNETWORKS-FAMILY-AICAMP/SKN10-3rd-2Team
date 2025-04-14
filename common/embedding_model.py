import os
import logging
import numpy as np
from typing import List, Optional
from pathlib import Path

# GemmaEmbedder 클래스 임포트
from common.vector_store import GemmaEmbedder

# 로깅 설정
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmbeddingModel:
    def __init__(self, model_name: Optional[str] = None, cache_dir: Optional[str] = None):
        """임베딩 모델 초기화"""
        logger.info("GemmaEmbedder 임베딩 모델 초기화...")
        self.embeddings = GemmaEmbedder()
        logger.info("GemmaEmbedder 임베딩 모델 로드 완료")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """문서 임베딩"""
        try:
            # 입력 검증
            if not texts:
                logger.warning("임베딩할 텍스트가 없습니다.")
                return []
            
            # 텍스트 전처리
            processed_texts = [self._preprocess_text(text) for text in texts]
            
            # 임베딩 생성
            embeddings = self.embeddings.encode(processed_texts, show_progress_bar=True)
            
            # numpy 배열을 리스트로 변환
            embeddings = [embedding.tolist() for embedding in embeddings]
            
            logger.info(f"문서 {len(texts)}개 임베딩 완료")
            return embeddings
        
        except Exception as e:
            logger.error(f"문서 임베딩 중 오류 발생: {str(e)}")
            # 오류 발생 시 빈 리스트 반환
            return []
    
    def embed_query(self, text: str) -> List[float]:
        """쿼리 임베딩"""
        try:
            # 입력 검증
            if not text:
                logger.warning("임베딩할 쿼리 텍스트가 없습니다.")
                return []
            
            # 텍스트 전처리
            processed_text = self._preprocess_text(text)
            
            # 임베딩 생성
            embedding = self.embeddings.encode(processed_text)[0].tolist()
            logger.info(f"쿼리 임베딩 완료: {text[:50]}...")
            return embedding
        
        except Exception as e:
            logger.error(f"쿼리 임베딩 중 오류 발생: {str(e)}")
            # 오류 발생 시 빈 리스트 반환
            return []
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        if not text:
            return ""
        
        # 텍스트 정규화 - 공백 제거 및 특수 문자 처리
        text = text.strip()
        
        # 추가 전처리 로직은 필요에 따라 구현
        return text 

    def embed_document(self, text: str) -> List[float]:
        """단일 문서 임베딩"""
        return self.embed_query(text) 