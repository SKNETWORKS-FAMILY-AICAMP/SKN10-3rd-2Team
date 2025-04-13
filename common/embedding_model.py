import ollama
from typing import List

class EmbeddingModel:
    def __init__(self, model_name: str = "nomic-embed-text"):
        """임베딩 모델을 초기화합니다."""
        self.model_name = model_name
    
    def get_embedding(self, text: str) -> List[float]:
        """텍스트의 임베딩을 생성합니다."""
        response = ollama.embed(model=self.model_name, input=text)
        return response["embeddings"][0]
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """여러 텍스트의 임베딩을 생성합니다."""
        return [self.get_embedding(text) for text in texts] 