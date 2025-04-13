import enum
import time
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from common.screen.constant import ROLE_TYPE, HISTORY_INFO
from .provider import Provider

class OLLAMA_LLMs(enum.Enum):
  gemma3 = (enum.auto(), "gemma3:1b")
  gemma3_q8 = (enum.auto(), "gemma3-q8") 
  gemma3_1b = (enum.auto(), "gemma3-1b")
  gemma3_diseases = (enum.auto(), "gemma3-diseases") 

class Provider_OLLAMA(Provider):
  def __init__(self, provider_LLMs=OLLAMA_LLMs) -> None:
    super().__init__(provider_LLMs)

  def __call__(self, 
      model_name, messages):
    # Ollama 모델을 불러옵니다.
    llm = ChatOllama(model=self.provider_LLMs[model_name].value[1])

    # 프롬프트
    prompts = []
    for msg in messages[:-1]: # 사용자의 메세지는 제외
      prompts.append(tuple(msg.values()))

    prompts += [(ROLE_TYPE.user.name, "{user_input}")] # 사용자의 메세지 입력 프론프트
    chat_prompt = ChatPromptTemplate.from_messages(prompts)

    # 체인 생성
    chain = chat_prompt | llm | StrOutputParser()
    # 모델 답변 
    
    for token in chain.stream({"user_input": messages[-1][HISTORY_INFO.content.name]}):
      yield token
      time.sleep(0.05) 
