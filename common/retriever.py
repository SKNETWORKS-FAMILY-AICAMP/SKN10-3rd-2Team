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
import re

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
    
    def _preprocess_query(self, query: str) -> str:
        """
        쿼리 전처리
        
        Args:
            query: 원본 쿼리
            
        Returns:
            str: 전처리된 쿼리
        """
        if not query:
            return ""
        
        # 기본 전처리
        query = query.strip()
        
        # 불필요한 특수문자 제거
        query = re.sub(r'[^\w\s가-힣]', ' ', query)
        
        # 연속된 공백 제거
        query = re.sub(r'\s+', ' ', query)
        
        # 키워드 강조 (중요 단어는 반복)
        keywords = {
            # 출결 관련 (가중치: 3)
            "병가": 3, "휴가": 3, "결석": 3, "출석": 3, "지각": 3, "조퇴": 3, "외출": 3, "공가": 3,
            # 교육 관련 (가중치: 2)
            "교육": 2, "프로젝트": 2, "캠프": 2, "학습": 2, "과제": 2, "실습": 2, "복습": 2,
            # 일정 관련 (가중치: 2)
            "일정": 2, "시간": 2, "기간": 2, "날짜": 2, "스케줄": 2, "OT": 2, "프리코스": 2,
            # 시설 관련 (가중치: 1)
            "시설": 1, "장소": 1, "위치": 1, "건물": 1, "강의실": 1, "라운지": 1, "흡연": 1,
            # 규정 관련 (가중치: 2)
            "규정": 2, "규칙": 2, "정책": 2, "절차": 2, "방법": 2, "처리": 2, "신청": 2,
            # 지원금 관련 (가중치: 3)
            "훈련장려금": 3, "국민취업지원제도": 3, "비용": 3, "지급": 3, "신청": 3,
            # 시험/자격증 관련 (가중치: 2)
            "시험": 2, "자격증": 2, "기능사": 2, "기사": 2, "기술사": 2,
            # 기타 (가중치: 1)
            "노트북": 1, "재해보험": 1, "스터디": 1, "블로그": 1, "인프런": 1, "와이파이": 1
        }
        
        # 키워드 가중치 적용
        processed_query = query
        for keyword, weight in keywords.items():
            if keyword in query:
                processed_query = processed_query.replace(keyword, f"{keyword} " * weight)
        
        return processed_query.strip()

    def _calculate_similarity(self, query: str, document: str) -> float:
        """
        쿼리와 문서 간의 유사도 계산
        
        Args:
            query: 검색 쿼리
            document: 비교할 문서
            
        Returns:
            float: 유사도 점수 (0.0 ~ 1.0)
        """
        # 쿼리 전처리
        processed_query = self._preprocess_query(query)
        
        # 문서 전처리
        processed_doc = document.lower().strip()
        
        # 유사도 계산
        query_tokens = set(processed_query.split())
        doc_tokens = set(processed_doc.split())
        
        # Jaccard 유사도 계산
        intersection = len(query_tokens.intersection(doc_tokens))
        union = len(query_tokens.union(doc_tokens))
        
        if union == 0:
            return 0.0
        
        # 기본 유사도 점수
        similarity = intersection / union
        
        # 키워드 매칭 가중치 적용
        keyword_matches = sum(1 for token in query_tokens if token in doc_tokens)
        keyword_weight = 1.0 + (keyword_matches * 0.1)  # 매칭된 키워드당 10% 가중치
        
        # 최종 유사도 점수 계산
        final_similarity = min(1.0, similarity * keyword_weight)
        
        return final_similarity

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
        
        # 쿼리 전처리
        processed_query = self._preprocess_query(query)
        
        # 파라미터 설정
        _top_k = top_k if top_k is not None else self.top_k
        _threshold = threshold if threshold is not None else 0.7  # 임계값 상향 조정
        
        try:
            logger.info(f"'{processed_query}' 문서 검색 요청: top_k={_top_k}, threshold={_threshold}")
            
            # BM25 검색 결과
            bm25_scores = self.vector_store.bm25.get_scores(self._tokenize(processed_query))
            
            # 벡터 검색 결과
            vector_results = self.vector_store.similarity_search(processed_query, top_k=_top_k * 3)
            
            # 결과 결합 및 재정렬
            combined_results = []
            for idx, (doc, vector_score) in enumerate(vector_results):
                bm25_score = bm25_scores[idx] if idx < len(bm25_scores) else 0
                combined_score = 0.9 * vector_score + 0.1 * bm25_score  # 벡터 검색 가중치 증가
                
                # 임계값보다 높은 점수만 포함
                if combined_score >= _threshold:
                    # 문서 내용이 쿼리와 관련이 있는지 추가 확인
                    if self._is_relevant(doc, processed_query, combined_score):
                        # 문서에 점수 정보 추가
                        doc['score'] = combined_score
                        combined_results.append((doc, combined_score))
            
            # 점수순 정렬 및 상위 K개 반환
            return sorted(combined_results, key=lambda x: x[1], reverse=True)[:_top_k]
            
        except Exception as e:
            logger.error(f"문서 검색 오류: {str(e)}")
            return []

    def _is_relevant(self, doc: Dict, query: str, score: float) -> bool:
        """
        문서가 쿼리와 관련이 있는지 확인
        
        Args:
            doc: 검색된 문서
            query: 사용자 쿼리
            score: 유사도 점수
            
        Returns:
            bool: 관련성 여부
        """
        # 기본 점수 임계값
        if score < 0.6:  # 임계값 상향 조정
            return False
        
        # 문서 내용이 비어있는 경우 제외
        if not doc.get('content', '').strip():
            return False
        
        # 쿼리와 문서의 키워드 매칭 확인
        query_keywords = set(self._tokenize(query))
        doc_keywords = set(self._tokenize(doc.get('content', '')))
        
        # 최소 3개 이상의 키워드가 매칭되어야 함
        if len(query_keywords.intersection(doc_keywords)) < 3:
            return False
        
        # 문서 내용이 쿼리와 관련이 있는지 추가 확인
        content = doc.get('content', '').lower()
        query = query.lower()
        
        # 핵심 키워드가 문서에 포함되어 있는지 확인
        core_keywords = ["병가", "휴가", "결석", "출석", "교육", "프로젝트", "캠프", "학습"]
        if any(keyword in query for keyword in core_keywords):
            if not any(keyword in content for keyword in core_keywords):
                return False
            
        # 문서 내용이 쿼리와 관련이 있는지 추가 확인
        if not self._check_semantic_relevance(content, query):
            return False
        
        # 문서의 신뢰도 확인
        if not self._check_document_confidence(doc, query):
            return False
            
        return True

    def _check_document_confidence(self, doc: Dict, query: str) -> bool:
        """
        문서의 신뢰도를 확인
        
        Args:
            doc: 검색된 문서
            query: 사용자 쿼리
            
        Returns:
            bool: 신뢰도 여부
        """
        content = doc.get('content', '')
        
        # 불확실한 표현이 포함된 경우 제외
        uncertain_phrases = [
            "아마도", "추정", "예상", "가능성", "보통", "대부분",
            "일반적으로", "보통은", "보통의 경우", "보통의 상황",
            "대체로", "주로", "주로는", "주로의 경우"
        ]
        
        if any(phrase in content for phrase in uncertain_phrases):
            return False
        
        # 질문에 대한 직접적인 답변이 포함되어 있는지 확인
        if "?" in query:
            answer_indicators = ["입니다", "합니다", "입니다.", "합니다.", "입니다!", "합니다!"]
            if not any(indicator in content for indicator in answer_indicators):
                return False
            
        return True

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