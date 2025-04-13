import streamlit as st
import pandas as pd
import os
import re

def categorize_question(question, answer):
    """질문과 답변 내용을 분석하여 적절한 카테고리 할당"""
    # 카테고리와 관련 키워드 정의
    categories = {
        "수업": ["수업", "강의", "교육", "커리큘럼", "진도", "프로그램", "진행", "출석"],
        "과제": ["과제", "제출", "마감", "숙제", "평가", "점수", "채점", "합격", "불합격"],
        "프로젝트": ["프로젝트", "팀", "협업", "미팅", "발표", "데모", "시연", "기획", "개발", "배포"],
        "일정": ["일정", "시간", "날짜", "요일", "기간", "주차", "달력", "휴일", "휴가", "종료"],
        "학습자료": ["자료", "교재", "책", "강의록", "문서", "참고", "링크", "사이트", "다운", "업로드"],
        "시설": ["교실", "강의실", "컴퓨터", "장비", "시설", "자리", "좌석", "위치", "주소"],
        "생활정보": ["식사", "점심", "저녁", "카페", "휴게", "기숙사", "교통", "주차"]
    }
    
    # 질문과 답변을 소문자로 변환
    question_lower = question.lower()
    answer_lower = answer.lower()
    
    # 각 카테고리 키워드와 일치하는지 확인하고 점수 계산
    category_scores = {}
    for category, keywords in categories.items():
        score = 0
        for keyword in keywords:
            # 질문에서 키워드 찾기 (가중치 2)
            if keyword in question_lower:
                score += 2
            # 답변에서 키워드 찾기 (가중치 1)
            if keyword in answer_lower:
                score += 1
        category_scores[category] = score
    
    # 가장 높은 점수의 카테고리 선택
    best_category = max(category_scores.items(), key=lambda x: x[1])
    
    # 모든 점수가 0이면 '기타' 카테고리로 분류
    if best_category[1] == 0:
        return "기타"
    
    return best_category[0]

def main():
    # 스타일 추가
    st.markdown("""
    <style>
    .info-header {
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: #1E88E5;
        margin-bottom: 1rem !important;
    }
    .info-subheader {
        color: #616161;
        margin-bottom: 1.5rem !important;
    }
    .search-container {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    .qa-container {
        margin-top: 20px;
    }
    .qa-question {
        font-weight: 600;
        color: #1976D2;
    }
    .qa-answer {
        margin-top: 10px;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 5px;
        border-left: 3px solid #1976D2;
    }
    .expander-header {
        font-weight: 600 !important;
        color: #424242 !important;
    }
    .stat-container {
        background-color: #e3f2fd;
        padding: 10px 15px;
        border-radius: 5px;
        margin-top: 15px;
        text-align: center;
    }
    .category-pill {
        display: inline-block;
        padding: 2px 8px;
        background-color: #E3F2FD;
        color: #1976D2;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-right: 8px;
        margin-bottom: 5px;
    }
    .category-count {
        display: inline-block;
        padding: 1px 6px;
        background-color: #1976D2;
        color: white;
        border-radius: 10px;
        font-size: 0.7rem;
        margin-left: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 헤더 섹션
    st.markdown('<div class="info-header">📚 부트캠프 정보 센터</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="info-subheader">부트캠프 적응에 필요한 모든 정보를 카테고리별로 확인하세요.</div>', 
        unsafe_allow_html=True
    )
    
    # 검색 컨테이너
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.subheader("🔍 정보 검색")
    st.markdown("키워드 검색 또는 카테고리 필터를 사용하여 필요한 정보를 빠르게 찾아보세요.")
    
    # CSV 파일 로드
    try:
        csv_path = os.path.join("data", "___RAG_QA_____.csv")
        df = pd.read_csv(csv_path)
        
        # 카테고리 자동 할당
        if 'category' not in df.columns:
            # 세션 상태로 카테고리 저장 (처음 실행 시만 계산)
            if 'categorized_df' not in st.session_state:
                # 진행 표시기 추가
                with st.spinner("질문을 카테고리별로 분류하는 중..."):
                    df['category'] = df.apply(lambda row: categorize_question(row['Q'], row['A']), axis=1)
                st.session_state.categorized_df = df
            else:
                df = st.session_state.categorized_df
                
        # 카테고리 통계 계산
        category_counts = df['category'].value_counts().to_dict()
        all_categories = ['전체'] + sorted(df['category'].unique().tolist())
        
        # 상단에 카테고리 필터 추가 (카운트와 함께 표시)
        category_cols = st.columns(len(all_categories))
        selected_category = st.session_state.get('selected_category', '전체')
        
        for i, category in enumerate(all_categories):
            count = category_counts.get(category, len(df)) if category != '전체' else len(df)
            category_label = f"{category} ({count})"
            
            # 선택된 카테고리에 대한 스타일 조정
            if category == selected_category:
                category_cols[i].markdown(
                    f"<div style='text-align:center;'><div style='background-color:#1976D2;color:white;padding:8px 12px;border-radius:20px;font-weight:bold;'>{category_label}</div></div>",
                    unsafe_allow_html=True
                )
            else:
                if category_cols[i].button(category_label, key=f"cat_{category}", use_container_width=True):
                    st.session_state.selected_category = category
                    st.rerun()
        
        # 검색 기능
        search_query = st.text_input("", placeholder="검색어를 입력하세요 (예: 과제, 수업, 프로젝트 등)")
        
        # 필터링 로직
        if search_query:
            # 대소문자 구분 없이 검색
            mask = df['Q'].str.contains(search_query, case=False) | df['A'].str.contains(search_query, case=False)
            filtered_df = df[mask]
            st.markdown(f"🔎 '{search_query}'에 대한 검색 결과: **{len(filtered_df)}개**의 정보를 찾았습니다.")
        else:
            filtered_df = df.copy()
        
        # 카테고리 필터링
        if selected_category != '전체':
            filtered_df = filtered_df[filtered_df['category'] == selected_category]
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 정보 표시
        if not filtered_df.empty:
            # Q&A 컨테이너
            st.markdown('<div class="qa-container">', unsafe_allow_html=True)
            
            # 현재 표시 중인 카테고리에 대한 설명 추가
            if selected_category != '전체':
                category_descriptions = {
                    "수업": "수업 진행 방식, 커리큘럼, 출석 등에 관한 정보입니다.",
                    "과제": "과제 제출 방법, 평가 기준, 마감일 등에 관한 정보입니다.",
                    "프로젝트": "팀 프로젝트 진행, 협업 방식, 발표 등에 관한 정보입니다.",
                    "일정": "부트캠프 일정, 중요 날짜, 주차별 계획 등에 관한 정보입니다.",
                    "학습자료": "교재, 강의자료, 참고 사이트 등에 관한 정보입니다.",
                    "시설": "강의실, 장비, 시설 이용 등에 관한 정보입니다.",
                    "생활정보": "식사, 휴게, 교통 등 일상생활 관련 정보입니다.",
                    "기타": "기타 부트캠프 생활에 필요한 정보입니다."
                }
                if selected_category in category_descriptions:
                    st.info(f"**{selected_category}** 카테고리: {category_descriptions[selected_category]}")
            
            # 정렬 옵션
            sort_options = st.radio(
                "정렬 방식:",
                ["기본", "질문 길이 (짧은순)", "질문 길이 (긴순)"],
                horizontal=True
            )
            
            if sort_options == "질문 길이 (짧은순)":
                filtered_df = filtered_df.assign(q_len=filtered_df['Q'].str.len()).sort_values('q_len')
            elif sort_options == "질문 길이 (긴순)":
                filtered_df = filtered_df.assign(q_len=filtered_df['Q'].str.len()).sort_values('q_len', ascending=False)
            
            # Q&A 목록 표시 - 수정된 부분
            for idx, row in filtered_df.iterrows():
                # 카테고리 태그 추가
                question_text = f"Q: {row['Q']}"
                category_text = row['category']
                
                # 카테고리 정보를 별도로 표시
                with st.expander(question_text):
                    st.markdown(f"**카테고리:** {category_text}")
                    st.markdown("---")
                    st.markdown("**답변:**")
                    # 답변 표시 - HTML 태그 사용하지 않고 기본 마크다운 사용
                    st.markdown(row['A'])
                    
                    # 디버깅용 정보 (필요시 주석 해제)
                    # st.write("DEBUG - 답변 내용 길이:", len(row['A']))
            
            # 통계 정보
            st.markdown(
                f"<div class='stat-container'>총 {len(filtered_df)}개의 정보가 있습니다.</div>", 
                unsafe_allow_html=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("검색 결과가 없습니다. 다른 키워드로 검색하거나 다른 카테고리를 선택해보세요.")
            
    except Exception as e:
        st.error(f"""
        ❌ 데이터를 로드하는 중 오류가 발생했습니다: {str(e)}
        
        다음을 확인해주세요:
        1. 데이터 파일(___RAG_QA_____.csv)이 'data' 폴더에 있는지
        2. 파일 형식이 올바른지 (Q와 A 열이 포함된 CSV)
        """)

if __name__ == "__main__":
    main() 