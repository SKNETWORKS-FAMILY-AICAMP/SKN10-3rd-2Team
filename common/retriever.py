from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain_openai import ChatOpenAI
from typing import Any

class Retriever:
    def __init__(self, temperature: float = 0, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(temperature=temperature, model=model)
    
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