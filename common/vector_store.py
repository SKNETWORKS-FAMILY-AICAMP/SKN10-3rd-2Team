from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List
from langchain.schema import Document

class VectorStore:
    def __init__(self, model_name: str = "sentence-transformers/msmarco-distilbert-dot-v5"):
        self.embeddings_model = HuggingFaceEmbeddings(model_name=model_name)
        self.vector_db = None
    
    def create_from_documents(self, documents: List[Document]) -> None:
        """문서로부터 벡터 저장소를 생성합니다."""
        self.vector_db = FAISS.from_documents(documents, self.embeddings_model)
    
    def get_retriever(self, k: int = 10):
        """검색기를 반환합니다."""
        if self.vector_db is None:
            raise ValueError("Vector store has not been initialized. Call create_from_documents first.")
        return self.vector_db.as_retriever(search_kwargs={"k": k}) 