import streamlit as st
from pathlib import Path
import sys
import os

# 현재 스크립트의 디렉토리를 가져와서 프로젝트 루트 경로 설정
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.append(str(project_root))

# 벡터 스토어 가져오기
from common.vector_store import VectorStore

def initialize_session_state():
    """세션 상태 초기화"""
    # 벡터 스토어 초기화
    if 'vector_store' not in st.session_state:
        try:
            st.session_state.vector_store = VectorStore()
            is_initialized = st.session_state.vector_store.initialize_store()
            if not is_initialized:
                st.error("벡터 스토어 초기화에 실패했습니다. 데이터가 올바르게 로드되었는지 확인해주세요.")
        except Exception as e:
            st.error(f"벡터 스토어 초기화 중 오류가 발생했습니다: {str(e)}")
            st.session_state.vector_store = None
    
    # 채팅 기록 초기화
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # 설정 초기화
    if 'similarity_threshold' not in st.session_state:
        st.session_state.similarity_threshold = 0.5
    
    if 'max_documents' not in st.session_state:
        st.session_state.max_documents = 3

def display_chat_history():
    """채팅 기록 표시"""
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            with st.chat_message('user'):
                st.write(message['content'])
        else:
            with st.chat_message('assistant'):
                st.write(message['content'])

def process_query(query):
    """사용자 쿼리 처리"""
    if not query:
        return

    # 사용자 메시지 저장
    st.session_state.chat_history.append({
        'role': 'user',
        'content': query
    })

    # 벡터 스토어 확인
    if 'vector_store' not in st.session_state or st.session_state.vector_store is None:
        error_message = "벡터 스토어가 초기화되지 않았습니다. 페이지를 새로고침 해주세요."
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': error_message
        })
        return

    with st.spinner('답변 생성 중...'):
        try:
            # 응답 생성
            response = st.session_state.vector_store.get_response(
                query,
                top_k=st.session_state.max_documents,
                threshold=st.session_state.similarity_threshold
            )
            
            # 응답 저장
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
        except Exception as e:
            error_message = f"응답 생성 중 오류가 발생했습니다: {str(e)}"
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': error_message
            })

def chatbot_interface():
    """챗봇 인터페이스"""
    st.header("SK네트웍스 Family AI 캠프 챗봇", divider="red")
    
    # 세션 상태 초기화
    initialize_session_state()
    
    # 사이드바 추가
    add_sidebar()
    
    # 채팅 기록 표시
    display_chat_history()
    
    # 사용자 입력
    query = st.chat_input("무엇을 도와드릴까요?")
    if query:
        process_query(query)

def add_sidebar():
    """사이드바 추가"""
    with st.sidebar:
        st.title("챗봇 설정")
        
        # 고급 설정
        st.header("고급 설정")
        
        # 유사도 임계값 설정
        similarity_threshold = st.slider(
            "유사도 임계값", 
            min_value=0.1, 
            max_value=0.9, 
            value=st.session_state.similarity_threshold,
            step=0.1,
            help="낮을수록 더 다양한 답변을 제공하지만 정확도가 떨어질 수 있습니다."
        )
        st.session_state.similarity_threshold = similarity_threshold
        
        # 최대 문서 수 설정
        max_documents = st.slider(
            "최대 문서 수", 
            min_value=1, 
            max_value=5, 
            value=st.session_state.max_documents,
            step=1,
            help="검색할 문서의 최대 개수입니다."
        )
        st.session_state.max_documents = max_documents
        
        # 자주 묻는 질문
        st.header("자주 묻는 질문")
        if st.button("수업 따라가기 힘들 때는 어떻게 해야 하나요?"):
            process_query("수업 따라가기 힘들 때는 어떻게 해야 하나요?")
        
        if st.button("기술 용어가 어려워요"):
            process_query("기술 용어가 어려워요")
        
        if st.button("부트캠프 중 스트레스 관리는 어떻게 하나요?"):
            process_query("부트캠프 중 스트레스 관리는 어떻게 하나요?")
            
        if st.button("모르는 내용을 질문하기가 부끄러워요"):
            process_query("모르는 내용을 질문하기가 부끄러워요")

def main():
    """메인 함수"""
    st.set_page_config(
        page_title="SK네트웍스 Family AI 캠프 챗봇",
        page_icon="🤖",
        layout="wide"
    )
    
    chatbot_interface()

if __name__ == "__main__":
    main() 