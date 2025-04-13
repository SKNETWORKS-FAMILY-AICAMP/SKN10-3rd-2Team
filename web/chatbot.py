import streamlit as st
import sys
import os
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    
    # 가장 관련성 높은 첫 번째 문서만 사용
    doc = docs[0]
    content = doc.page_content
    
    if "Q:" in content and "A:" in content:
        q, a = content.split("A:", 1)
        q = q.replace("Q:", "").strip()
        a = a.strip()
        
        # 자연스러운 응답 형식으로 변환
        response = a
        
        # RAG 데이터의 말투를 분석하여 적절한 접두어 추가
        if "죄송합니다" in a or "알려드리겠습니다" in a:
            response = a
        elif "다음과 같습니다" in a or "아래와 같습니다" in a:
            response = a
        else:
            # 기본 응답 형식
            response = f"알려드리자면, {a}"
            
    else:
        response = f"알려드리자면, {content}"
    
    return response

def main():
    st.set_page_config(
        page_title="RAG 기반 챗봇",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 RAG 기반 챗봇")
    st.markdown("""
    이 챗봇은 RAG(Retrieval-Augmented Generation) 기술을 사용하여 질문에 대한 답변을 제공합니다.
    질문을 입력하면 관련된 정보를 찾아 답변해드립니다.
    """)
    
    # 사이드바 설정
    with st.sidebar:
        st.header("설정")
        if st.button("벡터 저장소 초기화", help="벡터 저장소를 초기화하고 데이터를 다시 로드합니다."):
            with st.spinner("벡터 저장소를 초기화하는 중..."):
                vector_store = init_vector_store()
                if vector_store:
                    st.success("벡터 저장소가 초기화되었습니다.")
                else:
                    st.error("벡터 저장소 초기화에 실패했습니다.")
        
        st.markdown("---")
        st.markdown("### 정보")
        st.markdown("""
        - 데이터 소스: RAG_QA 데이터셋
        - 검색 방식: 유사도 기반 검색
        - 응답 방식: 가장 관련성 높은 답변 1개 제공
        """)
    
    # 채팅 기록 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("질문을 입력하세요"):
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
                    벡터 저장소 초기화에 실패했습니다.
                    사이드바의 '벡터 저장소 초기화' 버튼을 클릭해주세요.
                    """)
                    return
        
        # 유사한 문서 검색
        with st.spinner("관련 정보를 검색하는 중..."):
            try:
                relevant_docs = st.session_state.vector_store.similarity_search(prompt, k=1)  # k=1로 설정하여 1개만 검색
                response = format_response(relevant_docs)
                
                # AI 응답 표시
                with st.chat_message("assistant"):
                    st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"""
                오류가 발생했습니다: {str(e)}
                
                다음을 확인해주세요:
                1. 벡터 저장소가 제대로 초기화되었는지
                2. 데이터 파일이 올바른 위치에 있는지
                3. 인터넷 연결이 정상적인지
                """)

if __name__ == "__main__":
    main() 