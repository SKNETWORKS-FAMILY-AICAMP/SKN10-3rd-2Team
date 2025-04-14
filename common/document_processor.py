from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
from langchain.schema import Document
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DocumentProcessor')

class DocumentProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """문서를 청크로 분할합니다."""
        return self.text_splitter.split_documents(documents)
    
    def process_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """문서를 처리합니다.
        
        Args:
            documents: 원본 문서 리스트 (데이터프레임에서 변환된)
            
        Returns:
            List[Dict[str, Any]]: 처리된 문서 리스트
        """
        logger.info(f"{len(documents)}개의 문서 처리 중")
        
        processed_documents = []
        for doc in documents:
            if isinstance(doc, Dict):
                processed_documents.append(doc)
            else:
                # 데이터프레임 행을 딕셔너리로 변환
                processed_documents.append({
                    "question": getattr(doc, "question", ""),
                    "answer": getattr(doc, "answer", "")
                })
        
        logger.info(f"{len(processed_documents)}개의 문서 처리 완료")
        return processed_documents
    
    @staticmethod
    def pretty_print_docs(docs: List[Document]) -> None:
        """문서를 보기 좋게 출력합니다."""
        print(
            f"\n{'-' * 100}\n".join(
                [f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]
            )
        ) 