import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain_openai import ChatOpenAI
from common.vector_store import VectorStore
import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Retriever')

# 현재 디렉토리를 모듈 검색 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

class Retriever:
    """
    하이브리드 검색 기반 텍스트 검색기
    SentenceTransformer 임베딩과 BM25를 결합하여 효과적인 검색 결과 제공
    """
    
    def __init__(
        self,
        model_name: str = "snunlp/KR-SBERT-V40K-klueNLI-augSTS",
        data_path: Optional[str] = None,
        top_k: int = 3,
        threshold: float = 0.1
    ):
        """
        Retriever 초기화
        
        Args:
            model_name: 사용할 SentenceTransformer 모델 이름
            data_path: 데이터 파일 경로, None이면 기존 저장된 스토어 로드 시도
            top_k: 반환할 최대 결과 수
            threshold: 최소 유사도 임계값
        """
        self.model_name = model_name
        self.data_path = data_path
        self.top_k = top_k
        self.threshold = threshold
        self.vector_store = None
        
        try:
            # VectorStore 초기화
            logger.info(f"VectorStore 초기화 중: model={model_name}, data_path={data_path}")
            self.vector_store = VectorStore(model_name=model_name, data_path=data_path)
            success = self.vector_store.initialize_store()
            
            if success:
                logger.info("Retriever 초기화 완료")
            else:
                logger.error("VectorStore 초기화 실패")
        except Exception as e:
            logger.error(f"Retriever 초기화 오류: {str(e)}")
            raise
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[Any, float]]:
        """쿼리에 가장 관련성 높은 문서 검색
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 문서 수
            
        Returns:
            List[Tuple[Document, score]]: 검색된 문서와 유사도 점수
        """
        # 벡터 스토어를 통해 유사 문서 검색
        results = self.vector_store.similarity_search(query, top_k=top_k)
        
        # 결과가 없으면 빈 리스트 반환
        if not results:
            return []
        
        # 결과 반환
        return results
    
    def retrieve_documents(self, query: str, top_k: Optional[int] = None, threshold: Optional[float] = None) -> List[Dict]:
        """
        사용자 쿼리와 관련된 문서 검색
        
        Args:
            query: 사용자 쿼리
            top_k: 검색 결과 수 (기본값: self.top_k)
            threshold: 유사도 임계값 (기본값: self.threshold)
            
        Returns:
            List[Dict]: 검색된 문서 목록 (question, answer, score 포함)
        """
        if not query or not query.strip():
            logger.warning("빈 쿼리로 문서 검색 시도")
            return []
            
        if self.vector_store is None:
            logger.error("VectorStore가 초기화되지 않음")
            return []
            
        # 파라미터 설정
        _top_k = top_k if top_k is not None else self.top_k
        _threshold = threshold if threshold is not None else self.threshold
        
        try:
            logger.info(f"'{query}' 문서 검색 요청: top_k={_top_k}, threshold={_threshold}")
            documents = self.vector_store.similarity_search(query, top_k=_top_k, threshold=_threshold)
            return documents
        except Exception as e:
            logger.error(f"문서 검색 오류: {str(e)}")
            return []

    def create_multi_query_retriever(self, base_retriever: Any):
        """다중 쿼리 검색기를 생성합니다."""
        return MultiQueryRetriever.from_llm(
            retriever=base_retriever,
            llm=self.llm
        )
    
    def create_compression_retriever(self, base_compressor: Any, base_retriever: Any):
        """컨텍스트 압축 검색기를 생성합니다."""
        return ContextualCompressionRetriever(
            base_compressor=base_compressor,
            base_retriever=base_retriever
        ) 