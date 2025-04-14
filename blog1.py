import pandas as pd
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urlparse, parse_qs
import re
import time
import random
import pytesseract
from PIL import Image
import io
import os

# ====== 설정 ======
INPUT_CSV = 'data/블로그1.csv'
OUTPUT_CSV = 'rag_dataset.csv'

# ====== 초기화 ======
ua = UserAgent()
session = requests.Session()
session.headers.update({
    "User-Agent": ua.chrome,
    "Referer": "https://www.google.com"
})

# ====== 이미지에서 텍스트 추출 ======
def extract_text_from_image(image_url):
    try:
        # 이미지 다운로드
        response = session.get(image_url, timeout=5)
        image = Image.open(io.BytesIO(response.content))
        
        # OCR 수행
        text = pytesseract.image_to_string(image, lang='kor+eng')
        return text.strip()
    except Exception as e:
        print(f"[이미지 텍스트 추출 실패] {image_url} / {e}")
        return ""

# ====== 네이버 주소 모바일로 변환 ======
def convert_to_mobile_naver(url):
    try:
        parsed = urlparse(url)
        if "blog.naver.com" in parsed.netloc and "PostView.naver" in parsed.path:
            q = parse_qs(parsed.query)
            blog_id = q.get("blogId", [""])[0]
            log_no = q.get("logNo", [""])[0]
            if blog_id and log_no:
                return f"https://m.blog.naver.com/{blog_id}/{log_no}"
    except:
        pass
    return url

# ====== 주차 정보 추출 ======
def extract_week(title):
    match = re.search(r'(\d)[ ]*주차', str(title))
    return int(match.group(1)) if match else None

# ====== 본문 크롤링 ======
def fetch_post(url):
    url = convert_to_mobile_naver(url)
    try:
        res = session.get(url, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.title.text.strip() if soup.title else "제목 없음"

        content = (
            soup.find("div", class_="se-main-container") or
            soup.find("div", id="postViewArea") or
            soup.find("div", class_="post_ct") or
            soup.find("div", class_="view")
        )
        
        # 텍스트 내용 추출
        content_text = content.get_text(separator='\n').strip() if content else "본문 없음"
        
        # 이미지에서 텍스트 추출
        image_texts = []
        for img in content.find_all('img'):
            img_url = img.get('src')
            if img_url:
                img_text = extract_text_from_image(img_url)
                if img_text:
                    image_texts.append(img_text)
        
        # 텍스트와 이미지 텍스트 결합
        full_content = content_text
        if image_texts:
            full_content += "\n\n[이미지에서 추출된 텍스트]\n" + "\n".join(image_texts)
            
        return title, full_content
    except Exception as e:
        print(f"[크롤링 실패] {url} / {e}")
        return None, None

# ====== 전체 실행 함수 ======
def main():
    df = pd.read_csv(INPUT_CSV)
    url_list = df.iloc[:, 0].dropna().unique().tolist()
    results = []

    for url in url_list:
        print(f"📌 크롤링 중: {url}")
        title, content = fetch_post(url)
        if not content or content == "본문 없음":
            continue
        week = extract_week(title)
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        for i, para in enumerate(paragraphs, 1):
            results.append({
                '블로그주소': url,
                '게시글제목': title,
                '주차': week,
                '문단': para,
                '문단순번': i
            })
        time.sleep(random.uniform(1.0, 2.0))

    df_out = pd.DataFrame(results)
    df_out.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ 크롤링 완료: {OUTPUT_CSV}")

# ====== 실행 ======
if __name__ == "__main__":
    main()
