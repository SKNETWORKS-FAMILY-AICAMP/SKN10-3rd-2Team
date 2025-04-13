import enum
import time

from common.llm.provider import Provider
from common.llm.openai import OPENAI_LLMs, Provider_OPENAI
from common.llm.llama import GROQ_LLMs, Provider_GROQ
from common.llm.ollama import OLLAMA_LLMs, Provider_OLLAMA

class PROVIDER_TYPE(enum.Enum):
  # 제공자명 = (인덱스, 호출함수, 사용가능한 모델 리스트)
  groq = (enum.auto(), Provider_GROQ, GROQ_LLMs)
  openai = (enum.auto(), Provider_OPENAI, OPENAI_LLMs)
  ollama = (enum.auto(), Provider_OLLAMA, OLLAMA_LLMs)

def get_response_from_llm(choiced_provider:Provider, messages, llm_name:str):
  if not isinstance(choiced_provider, Provider):
    raise Exception("허락한 제공자가 아닙니다.") 
  elif llm_name not in choiced_provider.provider_LLMs.__members__:
    raise Exception("허락한 모델명이 아닙니다.") 

  generator = choiced_provider(
    model_name=llm_name, messages=messages
  )
  for token in generator:
    yield token
    time.sleep(0.05)








