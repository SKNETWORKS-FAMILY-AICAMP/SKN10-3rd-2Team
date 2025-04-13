import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import CrossEncoder
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from typing import List, Dict, Any
from langchain.schema import Document



class Reranker:
    def __init__(self, model_name: str = "Dongjin-kr/ko-reranker", device: str = "cpu"):
        self.cross_encoder = CrossEncoder(model_name, max_length=512, device=device)
        self.hf_cross_encoder = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
        self.compressor = CrossEncoderReranker(model=self.hf_cross_encoder, top_n=3)
    
    def rank(self, query: str, documents: List[Document], top_k: int = 3) -> List[Dict[str, Any]]:
        """문서를 재순위화합니다."""
        return self.cross_encoder.rank(
            query,
            [doc.page_content for doc in documents],
            top_k=top_k,
            return_documents=True
        )
    
    def get_compressor(self):
        """문서 압축기를 반환합니다."""
        return self.compressor



