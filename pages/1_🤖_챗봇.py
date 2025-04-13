import streamlit as st
import sys
import os
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.vector_store import VectorStore

# 환경 변수 로드
load_dotenv()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

def init_vector_store():
    try:
        if st.session_state.vector_store is None:
            st.session_state.vector_store = VectorStore()
            if not st.session_state.vector_store.load_existing_store():
                csv_path = os.path.join("data", "___RAG_QA_____.csv")
                st.session_state.vector_store.load_data(csv_path)
        return st.session_state.vector_store
    except Exception as e:
        st.error(f"벡터 저장소 초기화 중 오류 발생: {str(e)}")
        return None

def format_response(docs):
    """검색된 문서를 자연스러운 응답 형식으로 변환"""
    if not docs:
        return "죄송합니다. 관련된 정보를 찾을 수 없습니다."
    
    # Gemma가 생성한 응답을 그대로 사용
    return docs[0]

def main():
    # 스타일 추가
    st.markdown("""
    <style>
    .chat-container {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        padding: 10px;
        background-color: #fafafa;
        height: 70vh;
        overflow-y: auto;
    }
    .chat-header {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: #1976D2;
        margin-bottom: 1rem !important;
    }
    .chat-subheader {
        color: #616161;
        margin-bottom: 1.5rem !important;
    }
    .user-bubble {
        background-color: #e3f2fd;
        border-radius: 15px 15px 0 15px;
        padding: 10px 15px;
        margin: 5px 0;
        max-width: 80%;
        align-self: flex-end;
    }
    .assistant-bubble {
        background-color: #f5f5f5;
        border-radius: 15px 15px 15px 0;
        padding: 10px 15px;
        margin: 5px 0;
        max-width: 80%;
        align-self: flex-start;
    }
    .sidebar-header {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        color: #1E88E5;
        margin-bottom: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 헤더 섹션
    st.markdown('<div class="chat-header">🤖 부트캠프 도우미 AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="chat-subheader">부트캠프 생활에 대한 모든 궁금증을 AI 챗봇에게 물어보세요.</div>', 
        unsafe_allow_html=True
    )
    
    # 사이드바 설정
    with st.sidebar:
        st.markdown('<div class="sidebar-header">⚙️ 챗봇 설정</div>', unsafe_allow_html=True)
        
        # 설명 추가
        st.info("""
        **처음 사용하시나요?**
        
        아래 '벡터 저장소 초기화' 버튼을 클릭하여 AI 챗봇을 준비해주세요.
        이 과정은 최초 1회만 필요합니다.
        """)
        
        # 초기화 버튼
        init_button = st.button(
            "🔄 벡터 저장소 초기화", 
            help="벡터 저장소를 초기화하고 데이터를 다시 로드합니다.", 
            type="primary",
            use_container_width=True
        )
        
        if init_button:
            with st.spinner("벡터 저장소를 초기화하는 중..."):
                vector_store = init_vector_store()
                if vector_store:
                    st.success("✅ 벡터 저장소가 초기화되었습니다.")
                else:
                    st.error("❌ 벡터 저장소 초기화에 실패했습니다.")
        
        # 추가 도움말
        st.markdown("---")
        st.markdown("### 💬 질문 예시")
        st.markdown("""
        - 부트캠프 일정은 어떻게 되나요?
        - 과제는 어떻게 제출하나요?
        - 팀 프로젝트는 어떻게 진행되나요?
        - 학습 자료는 어디서 찾을 수 있나요?
        """)
    
    # 메인 채팅 영역
    chat_container = st.container()
    with chat_container:
        # 채팅 기록 표시
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("질문을 입력하세요..."):
        # 사용자 메시지 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 벡터 저장소 초기화 확인
        if st.session_state.vector_store is None:
            with st.spinner("벡터 저장소를 초기화하는 중..."):
                vector_store = init_vector_store()
                if not vector_store:
                    st.error("""
                    ❌ 벡터 저장소 초기화에 실패했습니다.
                    사이드바의 '벡터 저장소 초기화' 버튼을 클릭해주세요.
                    """)
                    return
        
        # 유사한 문서 검색
        with st.spinner("생각하는 중..."):
            try:
                relevant_docs = st.session_state.vector_store.similarity_search(prompt, k=1)
                response = format_response(relevant_docs)
                
                # AI 응답 표시
                with st.chat_message("assistant"):
                    st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"""
                ❌ 오류가 발생했습니다: {str(e)}
                
                다음을 확인해주세요:
                1. 벡터 저장소가 제대로 초기화되었는지
                2. 데이터 파일이 올바른 위치에 있는지
                3. 인터넷 연결이 정상적인지
                """)

if __name__ == "__main__":
    main() 