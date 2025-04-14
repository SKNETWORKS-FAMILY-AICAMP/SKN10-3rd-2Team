import pandas as pd
import re

# 1. CSV 파일 불러오기
file_path = "20250410 유튜브 자막.csv"  # 경로 수정 필요
df = pd.read_csv(file_path)

# 2. 결측값 처리
df['caption'] = df['caption'].fillna("")

# 3. 필터링 키워드 정의
blacklist_keywords = [
    r'씨발|ㅅㅂ|ㅂㅅ|병신|지랄|ㅈㄹ|좆|개새|염병|좃|fuck|shit|bitch|asshole',  # 욕설/비방
    r'섹스|sex|야해|자위|노출|변태|69|porn|av|야동|딸딸|보지|자지',              # 성적 표현
    r'\[음악\]|\[music\]|\[bgm\]|\[노래\]|배경음악|음악 나와',              # 음악 표시
    r'으어+|오오+|어어+|하하하+|ㅎㅎ+|ㅋㅋ+|ㅠㅠ+|ㅜㅜ+|…+|~~+|!!+|ㅎㅎㅎ+', # 감탄사/의성어
    r'^\s*[가-힣]{1,2}\s*$'  # 의미 없는 한글 1~2글자 단독 문장
]

# 4. 정규식 패턴 결합
pattern = re.compile("|".join(blacklist_keywords), flags=re.IGNORECASE)

# 5. 필터링 적용
filtered_df = df[~df['caption'].str.contains(pattern)]

# 6. 필터링된 결과 저장
filtered_df.to_csv("filtered_유튜브_자막.csv", index=False)
