import streamlit as st 

from common.screen.history import add_history
from common.screen.display import print_message
from common.screen.input import get_prompt
from common.llm.call_provider import get_response_from_llm, PROVIDER_TYPE
from common.llm.ollama import OLLAMA_LLMs
from common.screen.constant import ROLE_TYPE, HISTORY_INFO
from common.screen.utils import init_page
from common.rag.retriever import get_rag_result


def app():
  st.title("RAG 쳇봇")

  # 화면 초기화  
  choiced_provider = PROVIDER_TYPE.ollama.name
  choiced_llm = OLLAMA_LLMs.gemma3_q8.name
  # 사용자 입력
  prompt = get_prompt()

  if prompt is not None:
    # 사용자 메시지를 세션 상태에 추가
    add_history(ROLE_TYPE.user, prompt)
    # 사용자 메시지 표시
    print_message(ROLE_TYPE.user.name, prompt)
    
    # AI 응답 요청
    messages = list(st.session_state.messages)
    messages[-1][HISTORY_INFO.content.name] = get_rag_result(prompt)
    print("="*50)    
    print(messages[-1][HISTORY_INFO.content.name])      

    generator = get_response_from_llm(
        choiced_provider=PROVIDER_TYPE[choiced_provider].value[1]() # Provider 인스턴스화
        , messages=messages
        , llm_name=choiced_llm)
    # AI 응답 표시
    assistant_message = print_message(
      ROLE_TYPE.assistant.name
      , generator)
    
    add_history(ROLE_TYPE.assistant, assistant_message)

if __name__=="__main__":
  init_page()
  app() 
