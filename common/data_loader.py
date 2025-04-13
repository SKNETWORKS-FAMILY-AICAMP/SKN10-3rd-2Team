import pandas as pd
from typing import List
from langchain.schema import Document

class DataLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def load_csv(self) -> List[Document]:
        """CSV 파일을 로드하고 Document 객체로 변환합니다."""
        df = pd.read_csv(self.file_path)
        documents = []
        
        # Q와 A를 하나의 문서로 결합
        for _, row in df.iterrows():
            content = f"Q: {row['Q']}\nA: {row['A']}"
            documents.append(Document(page_content=content))
        
        return documents 