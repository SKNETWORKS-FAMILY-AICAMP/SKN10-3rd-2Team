import pandas as pd
import re
from tqdm import tqdm

def clean_text(text):
    if pd.isna(text):
        return ""
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    # 특수문자 제거 (한글, 영어, 숫자, 기본 문장부호만 남김)
    text = re.sub(r'[^\w\s.,!?()가-힣]', '', text)
    
    return text.strip()

def preprocess_data(input_file, output_file):
    # CSV 파일 읽기
    df = pd.read_csv(input_file)
    
    # 1. 본문이 없는 게시물 제거
    df = df[df['게시글내용'] != '본문 없음']
    
    # 2. 중복된 내용 제거 (동일한 내용을 가진 게시물 중 첫 번째만 남김)
    df = df.drop_duplicates(subset=['게시글내용'], keep='first')
    
    # 3. 텍스트 정리
    print("텍스트 정리 중...")
    df['게시글내용'] = df['게시글내용'].apply(clean_text)
    
    # 4. 내용이 너무 짧은 게시물 제거 (100자 미만)
    df = df[df['게시글내용'].str.len() >= 100]
    
    # 5. 불필요한 컬럼 제거
    df = df[['블로그주소', '게시글제목', '게시글내용']]
    
    # 결과 저장
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ 데이터 정리 완료: {output_file}")
    print(f"총 {len(df)}개의 유효한 게시물이 남았습니다.")

if __name__ == "__main__":
    input_file = r"D:\부트캠프\MiniProject\SKN10-3rd-2Team\크롤링_결과.csv"
    output_file = r"D:\부트캠프\MiniProject\SKN10-3rd-2Team\data\cleaned_blog_posts.csv"
    preprocess_data(input_file, output_file) 