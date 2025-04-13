from typing import List, Dict, Any
import os
from llama_cpp import Llama

class LLMModel:
    def __init__(self, model_path: str = "model.Q8_0.gguf"):
        """양자화된 LLM 모델을 로드합니다."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.model = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4
        )
    
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """프롬프트를 기반으로 텍스트를 생성합니다."""
        output = self.model(
            prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
            repeat_penalty=1.1,
            stop=["</s>", "Human:", "Assistant:"]
        )
        return output['choices'][0]['text'].strip()
    
    def generate_with_context(self, context: str, question: str) -> str:
        """컨텍스트와 질문을 기반으로 응답을 생성합니다."""
        prompt = f"""다음은 컨텍스트 정보입니다:
{context}

위 정보를 바탕으로 다음 질문에 답변해주세요:
{question}

답변:"""
        return self.generate(prompt) 