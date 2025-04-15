import streamlit as st
import os
import re
from typing import Any, Optional, List, Dict
from common.ollama_manager import OllamaManager

# 페이지 설정 - 반드시 가장 먼저 실행
st.set_page_config(
    page_title="SK네트웍스 Family AI 캠프 도우미",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"  # 처음에는 사이드바 닫아두기
)

# CSS 스타일 정의
def apply_styles():
    st.markdown("""
    <style>
    /* 전체 페이지 스타일링 */
    .main {
        padding: 2rem 1rem;
    }
    
    /* 헤더 스타일링 */
    .main-header {
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        margin-bottom: 1rem !important;
        color: #FF8A00;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem !important;
        font-weight: 400 !important;
        color: #424242;
        margin-bottom: 2rem !important;
    }
    
    /* 카드 스타일링 */
    .feature-card {
        background-color: #f8f9fa;
        padding: 1.8rem;
        border-radius: 0.8rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
        height: 100%;
        transition: transform 0.3s, box-shadow 0.3s;
        border-left: 4px solid #FF8A00;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .feature-header {
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        color: #FF8A00;
        margin-bottom: 1rem !important;
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        color: #FF8A00;
    }
    
    /* 버튼 스타일링 */
    .custom-button {
        display: inline-block;
        padding: 0.8rem 1.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        text-align: center;
        text-decoration: none;
        border-radius: 8px;
        margin: 0.5rem 0;
        transition: all 0.3s;
        width: 100%;
        cursor: pointer;
        border: none;
    }
    .primary-button {
        background-color: #FF8A00;
        color: white;
    }
    .primary-button:hover {
        background-color: #E67E00;
        box-shadow: 0 4px 8px rgba(255, 138, 0, 0.3);
        transform: translateY(-2px);
    }
    .secondary-button {
        background-color: #f8f9fa;
        color: #FF8A00;
        border: 2px solid #FF8A00;
    }
    .secondary-button:hover {
        background-color: #FFF4E6;
        box-shadow: 0 4px 8px rgba(255, 138, 0, 0.2);
        transform: translateY(-2px);
    }
    
    /* 섹션 스타일링 */
    .section-title {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #FF8A00;
        margin: 2rem 0 1.5rem 0 !important;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e0e0e0;
    }
    
    /* 단계별 가이드 스타일링 */
    .step-container {
        background-color: #f5f7fa;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 4px solid #FF8A00;
    }
    .step-number {
        display: inline-block;
        width: 30px;
        height: 30px;
        background-color: #FF8A00;
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 30px;
        margin-right: 10px;
        font-weight: bold;
    }
    .step-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #FF8A00;
        margin-bottom: 10px;
    }
    .step-content {
        margin-left: 40px;
        color: #424242;
    }
    
    /* 카테고리 선택 버튼 */
    .category-button {
        background-color: #f1f3f5;
        border: none;
        border-radius: 20px;
        padding: 10px 15px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.2s;
        font-weight: 500;
    }
    .category-button:hover, .category-button.active {
        background-color: #FF8A00;
        color: white;
    }
    
    /* 푸터 스타일링 */
    .footer {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-top: 30px;
        text-align: center;
        border-top: 1px solid #e0e0e0;
    }
    
    /* 모바일 대응 */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem !important;
        }
        .sub-header {
            font-size: 1.3rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def _preprocess_text(self, text: str) -> str:
    if not text:
        return ""
    
    # 기본 전처리
    text = text.strip()
    
    # 불필요한 특수문자 제거
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    # 키워드 강조 (중요 단어는 반복)
    keywords = ["교육", "프로젝트", "캠프", "학습"]
    for keyword in keywords:
        if keyword in text:
            text = text.replace(keyword, f"{keyword} {keyword}")
    
    return text

def create_compression_retriever(self, base_compressor: Any, base_retriever: Any):
    # 컨텍스트 압축 적용
    return ContextualCompressionRetriever(
        base_compressor=base_compressor,
        base_retriever=base_retriever,
        search_kwargs={"k": 10}  # 더 많은 후보 검색
    )

def _adjust_threshold(self, query_length: int) -> float:
    # 쿼리 길이에 따라 임계값 동적 조정
    if query_length < 5:
        return 0.15  # 짧은 쿼리는 더 엄격한 임계값
    elif query_length > 20:
        return 0.25  # 긴 쿼리는 더 관대한 임계값
    else:
        return 0.2  # 기본 임계값

def generate_response(self, prompt: str) -> str:
    try:
        response = self.llm(prompt)
        return response
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            return "죄송합니다. AI 모델 서버에 연결할 수 없습니다. 다음 사항을 확인해주세요:\n1. Ollama 서버가 실행 중인지 확인\n2. 'ollama pull gemma:2b' 명령어로 모델 설치\n3. 서버 재시작 후 다시 시도"
        else:
            return f"오류가 발생했습니다: {error_msg}"

def retrieve_documents(self, query: str, top_k: Optional[int] = None, threshold: Optional[float] = None) -> List[Dict]:
    try:
        # BM25 검색 결과
        bm25_scores = self.vector_store.bm25.get_scores(self._tokenize(query))
        
        # 벡터 검색 결과
        vector_results = self.vector_store.similarity_search(query, top_k=_top_k * 2)  # 더 많은 후보 검색
        
        # 결과 결합 및 재정렬
        combined_results = []
        for idx, (doc, vector_score) in enumerate(vector_results):
            bm25_score = bm25_scores[idx] if idx < len(bm25_scores) else 0
            combined_score = 0.7 * vector_score + 0.3 * bm25_score  # 가중치 조정
            
            if combined_score >= _threshold:
                combined_results.append((doc, combined_score))
        
        # 점수순 정렬 및 상위 K개 반환
        return sorted(combined_results, key=lambda x: x[1], reverse=True)[:_top_k]
        
    except Exception as e:
        logger.error(f"문서 검색 오류: {str(e)}")
        return []

def main():
    # Ollama 서버 확인 및 시작
    OllamaManager.start_ollama_server()
    
    # CSS 스타일 적용
    apply_styles()

    # 히어로 섹션
    st.markdown("<div style='animation: fadeIn 1s ease-out;'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="main-header">SK네트웍스 Family AI 캠프 도우미</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">AI 캠프 생활에 필요한 모든 정보를 AI 챗봇으로 쉽고 빠르게 알아보세요!</div>', unsafe_allow_html=True)
        
        # 강조 텍스트 추가
        st.markdown("""
        <div style="background-color: #FFF4E6; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        📢 <b>Gemma</b> 모델 기반 AI 챗봇으로 SK네트웍스 Family AI 캠프 10기 생활에 대한 모든 질문을 해결하세요.  
        실시간으로 관련 정보를 검색하고 맞춤형 답변을 제공합니다.
        </div>
        """, unsafe_allow_html=True)
        
        # 바로가기 버튼
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.markdown("""
            <a href="pages/1_🤖_챗봇.py" class="custom-button primary-button">
                🤖 챗봇 시작하기
            </a>
            """, unsafe_allow_html=True)
        with col_btn2:
            st.markdown("""
            <a href="https://playdatacademy.notion.site/G-FAQ-b1ea666d01eb42ab8d5f6f941a64eea0" class="custom-button secondary-button">
                📚 정보 둘러보기
            </a>
            """, unsafe_allow_html=True)
        
        # 퀵 액세스: 자주 묻는 질문
        st.markdown("""
        <div style="margin-top: 25px;">
            <h4 style="color: #616161;">자주 묻는 질문 바로가기:</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # 자주 묻는 질문 버튼들
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            st.markdown("""
            <a href="https://calendar.google.com/calendar/u/0/r?cid=NWQ5ZTU5YTU2NjgwMzQ4NzhiNDVkOGQxNWQ3OGNhZGRkZjAwYjQ1MzdmOTk2Y2E5OTNmNDdlMmQxMWVhODhmZTdAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ&pli=1" class="custom-button secondary-button">
                🗓️ 교육 일정
            </a>
            """, unsafe_allow_html=True)
            st.markdown("""
            <a href="pages/1_🤖_챗봇.py" class="custom-button secondary-button">
                📝 블로그 회고 작성
            </a>
            """, unsafe_allow_html=True)
        with col_q2:
            st.markdown("""
            <a href="https://github.com/SKNETWORKS-FAMILY-AICAMP" class="custom-button secondary-button">
                👥 단위 프로젝트
            </a>
            """, unsafe_allow_html=True)
            st.markdown("""
            <a href="https://www.work24.go.kr/cm/main.do" class="custom-button secondary-button">
                💰 훈련장려금
            </a>
            """, unsafe_allow_html=True)
    
    with col2:
        # SKN 로고 또는 이미지
        st.image("SKN_logo.png", width=280)
    
    st.markdown("</div>", unsafe_allow_html=True)  # 모션 효과 div 닫기
    
    st.divider()
    
    # 교육 과정 정보 섹션 추가
    st.markdown('<div class="section-title">📋 SK네트웍스 Family AI 캠프 10기 안내</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #FF8A00;">
            <h3 style="color: #FF8A00; margin-bottom: 15px;">🏫 교육 과정 정보</h3>
            <ul>
                <li><b>교육 기간:</b> 2025.01.07 ~ 2025.07.07 (6개월)</li>
                <li><b>교육 시간:</b> 9:00 ~ 18:00 (점심시간: 13:00 ~ 14:00)</li>
                <li><b>교육 장소:</b> 플레이데이터 G밸리캠퍼스 (서울시 금천구)</li>
                <li><b>캠퍼스 운영:</b> 8:30 ~ 21:50 (일부 날짜 변경될 수 있음)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #FF8A00;">
            <h3 style="color: #FF8A00; margin-bottom: 15px;">📚 교과목 구성</h3>
            <ul>
                <li><b>프로그래밍과 데이터 기초</b></li>
                <li><b>데이터 분석과 머신러닝, 딥러닝</b></li>
                <li><b>LLM(초거대언어모델)</b></li>
                <li><b>AI 활용 애플리케이션 개발</b></li>
                <li><b>단위 프로젝트 및 최종 프로젝트</b></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # 주요 기능 설명 - 애니메이션 효과 추가
    st.markdown('<div class="section-title">📌 주요 기능</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center;" class="feature-icon">🤖</div>
            <div class="feature-header">AI 챗봇 상담</div>
            <ul>
                <li><b>교육 일정 안내</b> - 수업, 프로젝트, 시험 일정 확인</li>
                <li><b>훈련장려금 정보</b> - 지급 일정 및 필요 서류 안내</li>
                <li><b>블로그 회고 작성</b> - 회고 작성 가이드 및 우수 사례</li>
                <li><b>24/7 이용</b> - 언제든지 필요한 정보 얻기</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 챗봇 시작하기 버튼
        st.page_link("pages/1_🤖_챗봇.py", label="🤖 챗봇 시작하기", icon="🤖")
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center;" class="feature-icon">📚</div>
            <div class="feature-header">학습 자료 센터</div>
            <ul>
                <li><b>온라인 프리코스</b> - Python, Git/GitHub 강의 제공</li>
                <li><b>인프런 강의</b> - 성취도 평가에 따른 맞춤형 강의</li>
                <li><b>교육 교재</b> - 교과목별 교재 정보 및 배부 안내</li>
                <li><b>추가 학습 자료</b> - AWS, LLM 실습 등 특강 정보</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 정보 센터 가기 버튼
        st.link_button("📚 정보 센터 가기", "https://playdatacademy.notion.site/G-FAQ-b1ea666d01eb42ab8d5f6f941a64eea0", use_container_width=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center;" class="feature-icon">💡</div>
            <div class="feature-header">AI 캠프 가이드</div>
            <ul>
                <li><b>단위 프로젝트</b> - 프로젝트 팀 구성 및 일정 안내</li>
                <li><b>출석 관리</b> - HRD 앱 사용법 및 출결 규정</li>
                <li><b>캠퍼스 시설</b> - 라운지, 도서대여, 피트니스 제휴 정보</li>
                <li><b>스터디 그룹</b> - 자격증, 코딩테스트 스터디 운영 정보</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 챗봇으로 적응 가이드 물어보기 버튼
        st.page_link("pages/1_🤖_챗봇.py", label="💡 적응 가이드 물어보기", icon="💡")
    
    st.divider()
    
    # 사용 방법 - 단계별 가이드 개선
    st.markdown('<div class="section-title">🔍 이용 가이드</div>', unsafe_allow_html=True)
    
    # 간단한 소개 추가
    st.markdown("""
    <p style="margin-bottom: 20px; color: #616161;">
    SK네트웍스 Family AI 캠프 도우미는 직관적이고 사용하기 쉽게 설계되었습니다. 다음 단계를 따라 빠르게 시작해보세요:
    </p>
    """, unsafe_allow_html=True)
    
    # 탭으로 구분하여 보기 좋게 구성
    tab1, tab2 = st.tabs(["🤖 챗봇 사용하기", "📚 정보 센터 활용하기"])
    
    with tab1:
        st.markdown("""
        <div class="step-container">
            <div class="step-title"><span class="step-number">1</span> 챗봇 페이지 접속하기</div>
            <div class="step-content">
                상단의 <b>"🤖 챗봇 시작하기"</b> 버튼을 클릭하거나, 왼쪽 사이드바에서 <b>"🤖 챗봇과 대화하기"</b> 메뉴를 선택합니다.
            </div>
        </div>
        
        <div class="step-container">
            <div class="step-title"><span class="step-number">2</span> 첫 사용 시 초기화하기</div>
            <div class="step-content">
                처음 사용할 때는 오른쪽 사이드바에서 <b>"🔄 벡터 저장소 초기화"</b> 버튼을 클릭합니다. 이 과정은 최초 1회만 필요하며, 몇 분 정도 소요될 수 있습니다.
            </div>
        </div>
        
        <div class="step-container">
            <div class="step-title"><span class="step-number">3</span> 질문하기</div>
            <div class="step-content">
                하단의 입력 필드에 궁금한 내용을 자연어로 입력하고 Enter 키를 누릅니다. 예시: "훈련장려금은 언제 지급되나요?", "블로그 회고는 어떻게 작성하나요?"
            </div>
        </div>
        
        <div class="step-container">
            <div class="step-title"><span class="step-number">4</span> 설정 조정하기 (선택사항)</div>
            <div class="step-content">
                사이드바에서 <b>유사도 임계값</b>을 조정하여 챗봇의 응답 정확도를 변경할 수 있습니다. 낮은 값은 더 많은 문서를 관련 있는 것으로 간주합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 사용 팁 추가
        st.info("""
        **💡 챗봇 활용 팁**
        
        - 질문은 구체적으로 작성할수록 더 정확한 답변을 얻을 수 있습니다
        - 대화 중간에 "🗑️ 대화 기록 초기화" 버튼을 클릭하면 새로운 대화를 시작할 수 있습니다
        - 챗봇은 이전 대화 내용을 기억하므로 문맥을 유지하며 대화할 수 있습니다
        """)
    
    with tab2:
        st.markdown("""
        <div class="step-container">
            <div class="step-title"><span class="step-number">1</span> 정보 센터 접속하기</div>
            <div class="step-content">
                상단의 <b>"📚 정보 둘러보기"</b> 버튼을 클릭하면 Notion 페이지에서 SK네트웍스 Family AI 캠프 관련 종합 정보를 확인할 수 있습니다.
            </div>
        </div>
        
        <div class="step-container">
            <div class="step-title"><span class="step-number">2</span> 카테고리 필터링</div>
            <div class="step-content">
                Notion 페이지에서 목차를 통해 특정 주제(수업, 훈련장려금, 프로젝트, 학습자료 등)에 관한 정보만 볼 수 있습니다.
            </div>
        </div>
        
        <div class="step-container">
            <div class="step-title"><span class="step-number">3</span> 키워드 검색</div>
            <div class="step-content">
                Notion 페이지 상단의 검색 기능을 이용하여 원하는 정보를 빠르게 찾을 수 있습니다.
            </div>
        </div>
        
        <div class="step-container">
            <div class="step-title"><span class="step-number">4</span> 정보 열람</div>
            <div class="step-content">
                원하는 정보를 클릭하면 상세 내용을 확인할 수 있습니다. 모든 정보는 체계적으로 정리되어 있습니다.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 정보 센터 팁 추가
        st.info("""
        **💡 Notion 페이지 활용 팁**
        
        - 브라우저 즐겨찾기에 추가하면 빠르게 접근할 수 있습니다
        - 목차와 검색 기능을 함께 활용하면 더 정확한 결과를 얻을 수 있습니다
        - Notion 페이지에 없는 내용은 챗봇에게 물어보세요
        """)
    
    # 사용자 피드백 섹션 (간단한 평가)
    st.divider()
    
    st.markdown('<div class="section-title">💬 의견을 들려주세요</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <p style="color: #616161;">SK네트웍스 Family AI 캠프 도우미를 개선하는데 도움이 됩니다. 경험을 평가해주세요:</p>
        """, unsafe_allow_html=True)
        
        # 간단한 별점 평가 UI
        rating = st.slider("AI 도우미 평가", 1, 5, 5, help="서비스 만족도를 1-5점으로 평가해주세요")
        
        if rating < 3:
            feedback = st.text_area("개선점이나 문제점을 알려주세요", height=100)
            if st.button("피드백 제출"):
                st.success("소중한 의견 감사합니다! 더 나은 서비스로 개선하겠습니다.")
        else:
            st.success("좋은 평가 감사합니다! 더 나은 서비스로 보답하겠습니다.")
    
    with col2:
        # 고급 설정 옵션 (실제 기능은 없지만 UI만 표시)
        st.markdown("### ⚙️ 앱 설정")
        theme = st.selectbox("테마", ["라이트 모드", "다크 모드 (개발 중)"])
        language = st.selectbox("언어", ["한국어", "영어 (개발 중)"])
    
    # 푸터
    st.markdown("""
    <div class="footer">
        <p><b>SK네트웍스 Family AI 캠프 도우미</b> - 당신의 성공적인 AI 캠프 학습을 응원합니다 👍</p>
        <p>기술 스택: <b>Gemma</b> | <b>scikit-learn</b> | <b>BM25</b> | <b>Streamlit</b></p>
        <p>© 2025 SK네트웍스 Family AI 캠프 도우미 | Made with ❤️ for AI Camp Students</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main() 