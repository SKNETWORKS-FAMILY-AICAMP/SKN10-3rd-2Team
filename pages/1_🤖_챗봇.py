import streamlit as st
import pandas as pd
import logging
import os
import sys
from pathlib import Path
import requests
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 현재 파일의 위치를 기준으로 프로젝트 루트 경로 설정
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent

# 각 데이터셋에 대한 벡터 저장소 파일 경로 정의
CAMPUS_VECTOR_STORE_PATH = project_root / "vector_store" / "campus_vector_store.pkl"
CODING_VECTOR_STORE_PATH = project_root / "vector_store" / "coding_vector_store.pkl"

# common 모듈 import
from common.data_loader import DataLoader
from common.document_processor import DocumentProcessor

# 유사도 임계값 설정
SIMILARITY_THRESHOLD = 0.3

# Gemma API 호출 함수
def ask_gemma(prompt, model_name="gemma:2b-instruct"):
    try:
        url = "http://localhost:11434/api/generate"
        data = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        
        logger.info(f"Gemma API 요청: 프롬프트={prompt[:50]}...")
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "")
            logger.info(f"Gemma 응답 성공: {answer[:50]}...")
            return answer
        else:
            logger.error(f"API 오류: {response.status_code}")
            return f"API 오류: {response.status_code}"
    except Exception as e:
        logger.error(f"요청 오류: {str(e)}")
        return f"오류 발생: {str(e)}"

# 벡터 검색 함수
def search_vector_store(query, vector_store_path, top_k=2):
    try:
        # 임포트를 함수 내부로 이동
        from common.embedding_model import EmbeddingModel
        from common.vector_store import VectorStore
        
        # 임베딩 모델 및 벡터 저장소 초기화
        embedding_model = EmbeddingModel()
        vector_store = VectorStore(embedding_model)
        vector_store.vector_store_file = vector_store_path
        
        if not vector_store.load():
            return None, "벡터 저장소가 초기화되지 않았습니다."
        
        # 쿼리 전처리
        processed_query = query.lower().strip()
        
        # 유사 문서 검색
        results = vector_store.similarity_search(processed_query, top_k=top_k)
        
        if not results or len(results) == 0:
            return None, "관련 정보를 찾을 수 없습니다."
        
        return results, None
    except Exception as e:
        logger.error(f"벡터 검색 오류: {str(e)}")
        return None, f"검색 오류: {str(e)}"

# 세션 상태 초기화
if "campus_messages" not in st.session_state:
    st.session_state.campus_messages = []
if "coding_messages" not in st.session_state:
    st.session_state.coding_messages = []
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "campus"
if "use_gemma" not in st.session_state:
    st.session_state.use_gemma = True

# 타이틀 설정
st.title("SK 네트웍스 부트캠프 FAQ 챗봇")

# 사이드바 설정
with st.sidebar:
    st.header("벡터 저장소 관리")
    
    # 벡터 저장소 초기화 버튼
    if st.button("벡터 저장소 초기화"):
        try:
            with st.spinner("벡터 저장소 초기화 중..."):
                # 임베딩 모델 초기화
                from common.embedding_model import EmbeddingModel
                from common.vector_store import VectorStore
                
                embedding_model = EmbeddingModel()
                data_loader = DataLoader()
                doc_processor = DocumentProcessor()
                
                # 캠퍼스 FAQ 처리
                campus_csv_path = project_root / "data" / "campusfaq.csv"
                campus_documents = data_loader.load_qa_data(str(campus_csv_path))
                
                if campus_documents:
                    processed_docs = doc_processor.process_documents(campus_documents)
                    
                    vector_store = VectorStore(embedding_model)
                    vector_store.vector_store_file = CAMPUS_VECTOR_STORE_PATH
                    if vector_store.create_index(processed_docs) and vector_store.save():
                        st.success(f"캠퍼스 FAQ 벡터 저장소 초기화 완료: {len(processed_docs)}개 문서")
                else:
                    st.error(f"캠퍼스 FAQ 데이터를 로드할 수 없습니다.")
                
                # 코딩 학습 처리
                coding_csv_path = project_root / "data" / "codingstudy.csv"
                coding_documents = data_loader.load_qa_data(str(coding_csv_path))
                
                if coding_documents:
                    processed_docs = doc_processor.process_documents(coding_documents)
                    
                    vector_store = VectorStore(embedding_model)
                    vector_store.vector_store_file = CODING_VECTOR_STORE_PATH
                    if vector_store.create_index(processed_docs) and vector_store.save():
                        st.success(f"코딩 학습 벡터 저장소 초기화 완료: {len(processed_docs)}개 문서")
                else:
                    st.error(f"코딩 학습 데이터를 로드할 수 없습니다.")
        
        except Exception as e:
            st.error(f"벡터 저장소 초기화 중 오류 발생: {str(e)}")
    
    st.header("Gemma 설정")
    
    # Gemma 사용 여부
    st.session_state.use_gemma = st.checkbox("Gemma 모델 사용", value=True)
    
    # RAG 기능 사용 여부
    st.session_state.use_rag = st.checkbox("RAG 기능 사용", value=False)
    
    # Gemma가 활성화된 경우 모델 선택 옵션 표시
    if st.session_state.use_gemma:
        st.session_state.gemma_model = st.selectbox(
            "Gemma 모델 선택",
            options=["gemma:2b-instruct", "gemma:7b-instruct"],
            index=0
        )
        
        # Gemma 테스트 버튼
        if st.button("Gemma 테스트"):
            with st.spinner("Gemma 테스트 중..."):
                response = ask_gemma("안녕하세요?", st.session_state.gemma_model)
                st.success("Gemma 테스트 성공!")
                st.write(f"Gemma 응답: {response}")

# 탭 선택 함수
def on_tab_change():
    tab_id = st.session_state.tabs
    st.session_state.active_tab = tab_id

# 탭 선택기 (라디오 버튼으로 대체)
tab_options = ["campus", "coding"]
tab_names = ["캠퍼스 생활 도우미", "코딩 학습 도우미"]

# 세션 상태에 탭 선택기 초기화
if "tabs" not in st.session_state:
    st.session_state.tabs = "campus"

# 탭 선택
st.radio(
    "도우미 선택",
    options=tab_options,
    format_func=lambda x: "캠퍼스 생활 도우미" if x == "campus" else "코딩 학습 도우미",
    key="tabs",
    on_change=on_tab_change,
    horizontal=True
)

# 현재 선택된 탭에 따라 내용 표시
if st.session_state.active_tab == "campus":
    # 캠퍼스 관련 콘텐츠
    st.subheader("캠퍼스 생활 도우미")
    
    # 예시 질문 버튼
    campus_examples = [
        "부트캠프 일정은 어떻게 되나요?",
        "훈련장려금은 언제, 어떻게 신청하나요?",
        "국민 취업 지원 제도의 조건과 신청하는 방법은 어떻게 되나요?",
        "병가 사용 시 필요한 증빙자료는 어떤 서류가 필요한가요?",
        "지각이나 조퇴, 결석은 어떻게 처리되나요?",
        "팀 프로젝트는 어떻게 진행되나요?"
    ]
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("부트캠프 일정", key="campus_ex_0"):
            st.session_state.campus_input = campus_examples[0]
        if st.button("훈련장려금", key="campus_ex_1"):
            st.session_state.campus_input = campus_examples[1]
        if st.button("병가 증빙", key="campus_ex_3"):
            st.session_state.campus_input = campus_examples[3]
    
    with col2:
        if st.button("국민취업지원", key="campus_ex_2"):
            st.session_state.campus_input = campus_examples[2]
        if st.button("출결 처리", key="campus_ex_4"):
            st.session_state.campus_input = campus_examples[4]
        if st.button("팀 프로젝트", key="campus_ex_5"):
            st.session_state.campus_input = campus_examples[5]
    
    # 현재 메시지 표시
    for message in st.session_state.campus_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # 채팅 입력 (캠퍼스)
    if "campus_input" not in st.session_state:
        st.session_state.campus_input = ""
        
    campus_prompt = st.chat_input("캠퍼스 생활에 대해 물어보세요!", key="campus_chat_input")
    
    if campus_prompt or st.session_state.campus_input:
        # 실제 사용할 프롬프트 설정
        prompt_to_use = campus_prompt if campus_prompt else st.session_state.campus_input
        st.session_state.campus_input = ""  # 입력값 초기화
        
        # 유저 메시지 추가 및 표시
        st.session_state.campus_messages.append({"role": "user", "content": prompt_to_use})
        
        with st.chat_message("user"):
            st.markdown(prompt_to_use)
            
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # Gemma로 응답 생성
            if st.session_state.use_gemma:
                with st.spinner("응답 생성 중..."):
                    if st.session_state.use_rag:
                        try:
                            # 필요한 모듈 임포트
                            from common.embedding_model import EmbeddingModel
                            from common.vector_store import VectorStore
                            
                            # 벡터 검색 수행
                            embedding_model = EmbeddingModel()
                            vector_store = VectorStore(embedding_model)
                            vector_store.vector_store_file = CAMPUS_VECTOR_STORE_PATH
                            
                            if not vector_store.load():
                                rag_response = "벡터 저장소가 초기화되지 않았습니다. '벡터 저장소 초기화' 버튼을 클릭해주세요."
                            else:
                                # 쿼리 전처리 및 검색
                                results = vector_store.similarity_search(prompt_to_use, top_k=1)
                                
                                if not results or len(results) == 0:
                                    rag_response = "죄송합니다. 질문에 대한 관련 정보를 찾을 수 없습니다. 다른 질문을 해보세요."
                                else:
                                    # 최상위 문서 사용
                                    best_doc = results[0]
                                    question = best_doc.get('question', '')
                                    answer = best_doc.get('answer', '')
                                    
                                    # 간단한 프롬프트 구성
                                    rag_prompt = f"""질문: {prompt_to_use}

참고 정보: {answer}

위 정보를 바탕으로 답변해주세요."""
                                    
                                    # Gemma 응답 생성
                                    rag_response = ask_gemma(rag_prompt, st.session_state.gemma_model)
                            
                            response = rag_response
                        except Exception as e:
                            logger.error(f"RAG 처리 중 오류: {str(e)}")
                            response = f"RAG 처리 중 오류가 발생했습니다: {str(e)}"
                    else:
                        # RAG 없이 직접 Gemma 응답 생성
                        response = ask_gemma(prompt_to_use, st.session_state.gemma_model)
                    
                    # 응답 저장 및 표시
                    st.session_state.campus_messages.append({"role": "assistant", "content": response})
                    message_placeholder.markdown(response)
            else:
                # Gemma 사용하지 않는 경우 기본 응답
                response = "Gemma를 사용하지 않도록 설정되어 있습니다. 사이드바에서 활성화해주세요."
                st.session_state.campus_messages.append({"role": "assistant", "content": response})
                message_placeholder.markdown(response)

else:  # coding 탭
    # 코딩 관련 콘텐츠
    st.subheader("코딩 학습 도우미")
    
    # 예시 질문 버튼
    coding_examples = [
        "주석을 왜 꾸준히 추가해야 할까?",
        "복습을 잘 못 하겠어요. 어떻게 해야 하나요?",
        "구글링으로 혼자 해결하는 게 어렵습니다.",
        "실습이 너무 어려워요. 어떻게 적응해야 하나요?"
    ]
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("주석 작성", key="coding_ex_0"):
            st.session_state.coding_input = coding_examples[0]
        if st.button("구글링 방법", key="coding_ex_2"):
            st.session_state.coding_input = coding_examples[2]
    
    with col2:
        if st.button("복습 방법", key="coding_ex_1"):
            st.session_state.coding_input = coding_examples[1]
        if st.button("실습 적응", key="coding_ex_3"):
            st.session_state.coding_input = coding_examples[3]
    
    # 현재 메시지 표시
    for message in st.session_state.coding_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # 채팅 입력 (코딩)
    if "coding_input" not in st.session_state:
        st.session_state.coding_input = ""
        
    coding_prompt = st.chat_input("코딩 학습에 대해 물어보세요!", key="coding_chat_input")
    
    if coding_prompt or st.session_state.coding_input:
        # 실제 사용할 프롬프트 설정
        prompt_to_use = coding_prompt if coding_prompt else st.session_state.coding_input
        st.session_state.coding_input = ""  # 입력값 초기화
        
        # 유저 메시지 추가 및 표시
        st.session_state.coding_messages.append({"role": "user", "content": prompt_to_use})
        
        with st.chat_message("user"):
            st.markdown(prompt_to_use)
            
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # Gemma로 응답 생성
            if st.session_state.use_gemma:
                with st.spinner("응답 생성 중..."):
                    if st.session_state.use_rag:
                        try:
                            # 필요한 모듈 임포트
                            from common.embedding_model import EmbeddingModel
                            from common.vector_store import VectorStore
                            
                            # 벡터 검색 수행
                            embedding_model = EmbeddingModel()
                            vector_store = VectorStore(embedding_model)
                            vector_store.vector_store_file = CODING_VECTOR_STORE_PATH
                            
                            if not vector_store.load():
                                rag_response = "벡터 저장소가 초기화되지 않았습니다. '벡터 저장소 초기화' 버튼을 클릭해주세요."
                            else:
                                # 쿼리 전처리 및 검색
                                results = vector_store.similarity_search(prompt_to_use, top_k=1)
                                
                                if not results or len(results) == 0:
                                    rag_response = "죄송합니다. 질문에 대한 관련 정보를 찾을 수 없습니다. 다른 질문을 해보세요."
                                else:
                                    # 최상위 문서 사용
                                    best_doc = results[0]
                                    question = best_doc.get('question', '')
                                    answer = best_doc.get('answer', '')
                                    
                                    # 간단한 프롬프트 구성
                                    rag_prompt = f"""질문: {prompt_to_use}

참고 정보: {answer}

위 정보를 바탕으로 답변해주세요."""
                                    
                                    # Gemma 응답 생성
                                    rag_response = ask_gemma(rag_prompt, st.session_state.gemma_model)
                            
                            response = rag_response
                        except Exception as e:
                            logger.error(f"RAG 처리 중 오류: {str(e)}")
                            response = f"RAG 처리 중 오류가 발생했습니다: {str(e)}"
                    else:
                        # RAG 없이 직접 Gemma 응답 생성
                        response = ask_gemma(prompt_to_use, st.session_state.gemma_model)
                    
                    # 응답 저장 및 표시
                    st.session_state.coding_messages.append({"role": "assistant", "content": response})
                    message_placeholder.markdown(response)
            else:
                # Gemma 사용하지 않는 경우 기본 응답
                response = "Gemma를 사용하지 않도록 설정되어 있습니다. 사이드바에서 활성화해주세요."
                st.session_state.coding_messages.append({"role": "assistant", "content": response})
                message_placeholder.markdown(response) 