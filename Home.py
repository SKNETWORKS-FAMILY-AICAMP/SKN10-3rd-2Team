import streamlit as st

def main():
    st.set_page_config(
        page_title="부트캠프 도우미 AI",
        page_icon="🤖",
        layout="wide"
    )
    
    # CSS 스타일 추가
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        color: #1E88E5;
    }
    .sub-header {
        font-size: 1.5rem !important;
        font-weight: 400 !important;
        color: #424242;
        margin-bottom: 2rem !important;
    }
    .feature-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        height: 100%;
    }
    .feature-header {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        color: #1976D2;
        margin-bottom: 1rem !important;
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 히어로 섹션
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="main-header">부트캠프 도우미 AI 🤖</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">부트캠프 생활에 필요한 모든 정보를 AI 챗봇으로 쉽고 빠르게 알아보세요!</div>', unsafe_allow_html=True)
        
        st.markdown("""
        Gemma 2B 모델 기반 AI 챗봇으로 부트캠프 생활에 대한 모든 질문을 해결하세요.  
        실시간으로 관련 정보를 검색하고 맞춤형 답변을 제공합니다.
        """)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
        with col_btn1:
            if st.button("🤖 챗봇 시작하기", type="primary", use_container_width=True):
                st.switch_page("pages/1_🤖_챗봇.py")
        with col_btn2:
            if st.button("📚 정보 둘러보기", type="secondary", use_container_width=True):
                st.switch_page("pages/2_📚_정보_확인.py")
    
    with col2:
        # 로컬 이미지가 있으면 그것을 사용하고, 없으면 온라인 이미지 사용
        try:
            st.image("web/assets/robot.png", width=250)
        except:
            st.image("https://cdn-icons-png.flaticon.com/512/4616/4616734.png", width=250)
    
    st.divider()
    
    # 주요 기능 설명
    st.markdown("## 📌 주요 기능", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-header">🤖 AI 챗봇 대화</div>
            <ul>
                <li>자연어로 질문하고 즉시 답변 받기</li>
                <li>부트캠프 관련 정보 지능적 검색</li>
                <li>24/7 언제든지 질문 가능</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-header">📚 종합 정보 제공</div>
            <ul>
                <li>필요한 모든 정보를 한눈에 확인</li>
                <li>키워드 검색으로 빠르게 찾기</li>
                <li>Q&A 형식의 쉬운 정보 제공</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-header">💡 핵심 가이드</div>
            <ul>
                <li>교육 과정 및 수업 진행 방식</li>
                <li>과제 및 프로젝트 관련 도움말</li>
                <li>학습 자료 활용 및 효과적인 공부법</li>
                <li>부트캠프 생활 적응 노하우</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # 사용 방법
    st.markdown("## 🔍 이용 방법", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 첫 사용자를 위한 안내
        
        1. 왼쪽 사이드바에서 "🤖 챗봇과 대화하기" 메뉴 선택
        2. 처음 사용 시 "벡터 저장소 초기화" 버튼 클릭 (최초 1회)
        3. 질문 입력 필드에 궁금한 내용 작성 후 Enter
        4. AI의 답변 확인하기
        """)
    
    with col2:
        st.markdown("""
        ### 정보 찾아보기
        
        1. 왼쪽 사이드바에서 "📚 정보 확인" 메뉴 선택
        2. 검색창에 키워드 입력하여 필요한 정보 검색
        3. 원하는 질문 클릭하여 답변 확인
        4. 모든 정보는 Q&A 형식으로 쉽게 확인 가능
        """)
    
    # 푸터
    st.divider()
    st.markdown("### 🛠️ 기술 정보")
    st.markdown("이 챗봇은 **Gemma 2B** 모델을 기반으로 작동합니다. **Ollama**와 **Streamlit**을 활용하여 구현되었습니다.")
    st.markdown("© 2024 부트캠프 도우미 AI | Made with ❤️ for Bootcamp Students")

if __name__ == "__main__":
    main() 