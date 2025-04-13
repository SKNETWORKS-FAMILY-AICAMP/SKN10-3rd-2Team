# blog_crawler.py

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from urllib.parse import urlparse, parse_qs, urljoin
import pandas as pd
from fake_useragent import UserAgent
from tqdm import tqdm
import time, random, warnings, re

# 경고 제거
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# 세션 설정
ua = UserAgent()
session = requests.Session()
session.headers.update({
    "User-Agent": ua.chrome,
    "Referer": "https://www.google.com"
})

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

def is_single_post_url(url):
    return (
        "logNo=" in url or
        re.search(r'tistory\.com/\d+$', url) is not None
    )

def fetch_post_content(url):
    try:
        url = convert_to_mobile_naver(url)
        res = session.get(url, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.title.text.strip() if soup.title else "제목 없음"

        content = (
            soup.find("div", class_="se-main-container") or
            soup.find("div", id="postViewArea") or
            soup.find("div", class_="post_ct") or
            soup.find("div", class_="view")
        )
        content_text = content.get_text(separator='\n').strip() if content else "본문 없음"
        return title, content_text
    except Exception as e:
        print(f"[본문 추출 실패] {url} / {e}")
        return None, None

def extract_post_links(blog_url):
    post_links = set()
    try:
        res = session.get(blog_url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all('a', href=True):
            href = a['href']
            if not href or href.startswith("#"):
                continue
            full_url = urljoin(blog_url, href)
            if any(x in full_url for x in ['entry', 'post', 'logNo', 'tistory.com']):
                post_links.add(convert_to_mobile_naver(full_url))
    except Exception as e:
        print(f"[링크 추출 실패] {blog_url} / {e}")
    return list(post_links)

def crawl_all_blogs(blog_list):
    rows = []
    for blog_url in tqdm(blog_list):
        print(f"\n📌 크롤링 시작: {blog_url}")
        post_links = []

        if is_single_post_url(blog_url):
            post_links = [blog_url]
        else:
            post_links = extract_post_links(blog_url)

        print(f"  ↳ 게시글 수 추출됨: {len(post_links)}")

        for link in post_links:
            title, content = fetch_post_content(link)
            if title and content:
                rows.append({
                    "블로그주소": blog_url,
                    "게시글제목": title,
                    "게시글내용": content
                })
            time.sleep(random.uniform(1.0, 2.2))
    return pd.DataFrame(rows)



if __name__ == "__main__":
    import argparse

    # 기본 CSV 파일 경로 설정
    default_input = r"D:\부트캠프\MiniProject\SKN10-3rd-2Team\data\블로그 정리 취합본.csv"
    
    parser = argparse.ArgumentParser(description="블로그 주소 CSV에서 회고 크롤링")
    parser.add_argument("--input", type=str, default=default_input, help="블로그 주소 CSV 경로 (컬럼: 블로그주소)")
    parser.add_argument("--output", type=str, default="크롤링_결과.csv", help="결과 저장 파일명")
    args = parser.parse_args()

    df_links = pd.read_csv(args.input)
    blog_list = df_links['블로그주소'].dropna().unique().tolist()

    df_result = crawl_all_blogs(blog_list)
    post_counts = df_result.groupby("블로그주소").size().reset_index(name="게시글수")
    df_final = pd.merge(df_result, post_counts, on="블로그주소")

    df_final.to_csv(args.output, index=False)
    print(f"\n✅ 크롤링 완료: {args.output}")
