import pandas as pd
import os
import logging
from pathlib import Path
from typing import List
from langchain.schema import Document

# 로깅 설정
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, file_path=None):
        """데이터 로더 초기화"""
        # 현재 파일 경로 기준으로 프로젝트 루트 찾기
        current_dir = Path(__file__).resolve().parent
        project_root = current_dir.parent
        self.data_dir = project_root / "data"
        
        # 기본 데이터 파일 경로 설정 (campusfaq.csv로 변경)
        self.qa_file_path = file_path if file_path else self.data_dir / "campusfaq.csv"
        
        # 데이터 캐시
        self.qa_data = None
    
    def load_qa_data(self, file_path=None):
        """질문-답변 데이터 로드"""
        try:
            # 파일 경로가 지정된 경우 해당 경로 사용
            if file_path:
                self.qa_file_path = Path(file_path)
                self.qa_data = None  # 캐시 초기화
                
            if self.qa_data is not None:
                logger.info("캐시된 QA 데이터 반환")
                return self.qa_data
            
            logger.info(f"QA 데이터 수동 로드 중: {self.qa_file_path}")
            
            # 수동으로 CSV 파일 처리 (pandas 대신 직접 처리)
            documents = []
            with open(self.qa_file_path, 'r', encoding='utf-8') as f:
                # 헤더 건너뛰기
                header = f.readline().strip()
                
                # 헤더에 question과 answer가 있는지 확인
                columns = [col.strip() for col in header.split(',')]
                question_idx = 0  # 기본값
                answer_idx = 1    # 기본값
                
                if 'question' in columns:
                    question_idx = columns.index('question')
                elif 'Q' in columns:
                    question_idx = columns.index('Q')
                    
                if 'answer' in columns:
                    answer_idx = columns.index('answer')
                elif 'A' in columns:
                    answer_idx = columns.index('A')
                
                # 각 줄 처리
                for i, line in enumerate(f, start=2):  # 헤더를 건너뛰었으므로 2부터 시작
                    try:
                        # CSV 라인 파싱 (인용 부호 처리)
                        parts = self._parse_csv_line(line)
                        
                        if len(parts) > max(question_idx, answer_idx):
                            # 질문과 답변 분리
                            question = parts[question_idx].strip('"').strip()
                            answer = parts[answer_idx].strip('"').strip()
                            
                            # 문서 추가
                            documents.append({
                                'question': question,
                                'answer': answer
                            })
                    except Exception as e:
                        logger.warning(f"CSV 파일 {i}번째 줄 처리 중 오류: {str(e)}")
                        continue
            
            # 데이터프레임 생성하지 않고 직접 딕셔너리 리스트 반환
            self.qa_data = documents
            
            logger.info(f"QA 데이터 로드 완료: {len(documents)} 개 문서")
            return self.qa_data
            
        except Exception as e:
            logger.error(f"QA 데이터 로드 중 오류 발생: {str(e)}")
            # 오류 발생 시 빈 리스트 반환
            return []
    
    def _parse_csv_line(self, line):
        """CSV 라인을 안전하게 파싱 (인용부호 처리)"""
        parts = []
        current = ""
        in_quotes = False
        
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                parts.append(current)
                current = ""
            else:
                current += char
        
        # 마지막 부분 추가
        if current:
            parts.append(current)
            
        return parts
            
    def get_qa_pairs(self):
        """질문-답변 쌍을 리스트로 반환"""
        documents = self.load_qa_data()
        if not documents:
            return []
            
        # 리스트 형태로 데이터가 저장됨
        return [(doc['question'], doc['answer']) for doc in documents]

    def load_csv(self, file_path=None) -> List[Document]:
        """CSV 파일을 로드하고 Document 객체로 변환합니다."""
        try:
            documents = self.load_qa_data(file_path)
            if not documents:
                return []
                
            doc_objects = []
            # 질문과 답변을 하나의 문서로 결합
            for doc in documents:
                content = f"Q: {doc['question']}\nA: {doc['answer']}"
                doc_objects.append(Document(page_content=content))
            
            logger.info(f"{len(doc_objects)}개의 Document 객체 생성 완료")
            return doc_objects
        except Exception as e:
            logger.error(f"CSV 파일을 Document로 변환 중 오류 발생: {str(e)}")
            return [] 