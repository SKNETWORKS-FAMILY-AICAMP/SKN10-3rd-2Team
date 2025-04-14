import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from urllib.parse import urlparse, parse_qs, urljoin, quote, urlencode
import pandas as pd
from fake_useragent import UserAgent
from tqdm import tqdm
import time, random, warnings, re
import pytesseract
from PIL import Image
import io
import os
import json
from datetime import datetime, timedelta

# 경고 제거
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# API 키 설정
NAVER_CLIENT_ID = "gp7QrsmuqPDOrDZFNPpY"
NAVER_CLIENT_SECRET = "gyq30kWXZg"

# 세션 설정
ua = UserAgent()
session = requests.Session()
session.headers.update({
    "User-Agent": ua.chrome,
    "Referer": "https://www.google.com"
})

def extract_text_from_image(image_url):
    try:
        response = session.get(image_url, timeout=5)
        image = Image.open(io.BytesIO(response.content))
        text = pytesseract.image_to_string(image, lang='kor+eng')
        return text.strip()
    except Exception as e:
        print(f"[이미지 텍스트 추출 실패] {image_url} / {e}")
        return ""

def convert_to_mobile_naver(url):
    try:
        parsed = urlparse(url)
        if "blog.naver.com" in parsed.netloc:
            if parsed.netloc == "m.blog.naver.com":
                return url
            if "PostView.naver" in parsed.path:
                q = parse_qs(parsed.query)
                blog_id = q.get("blogId", [""])[0]
                log_no = q.get("logNo", [""])[0]
                if blog_id and log_no:
                    return f"https://m.blog.naver.com/{blog_id}/{log_no}"
            if "PostList.naver" in parsed.path:
                q = parse_qs(parsed.query)
                blog_id = q.get("blogId", [""])[0]
                category_no = q.get("categoryNo", [""])[0]
                if blog_id and category_no:
                    return f"https://m.blog.naver.com/{blog_id}?categoryNo={category_no}"
    except Exception as e:
        print(f"[URL 변환 실패] {url} - {str(e)}")
    return url

def is_single_post_url(url):
    return (
        "logNo=" in url or
        re.search(r'tistory\\.com/\\d+$', url) is not None
    )

def fetch_post_content(url, platform):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = None
        if platform == 'naver':
            title_elem = soup.select_one('h3.se_textarea, div.se-title-text')
            if not title_elem:
                title_elem = soup.select_one('div.pcol1')
            if title_elem:
                title = title_elem.get_text(strip=True)
        elif platform == 'tistory':
            title_elem = soup.select_one('h1.title, div.article-title')
            if title_elem:
                title = title_elem.get_text(strip=True)

        content = None
        if platform == 'naver':
            content_selectors = [
                'div.se-main-container',
                'div#postViewArea',
                'div#contentArea',
                'div#content-area',
                'div.post_ct',
                'div#post-area',
                'article'
            ]
            for sel in content_selectors:
                content = soup.select_one(sel)
                if content:
                    break
            if not content:
                print(f"[본문 없음] {url}")
                return None, None
        elif platform == 'tistory':
            content = soup.select_one('div.article-content, div.contents_style')
            if not content:
                print(f"[본문 없음 - 티스토리] {url}")
                return None, None

        return title, content.get_text(strip=True)

    except Exception as e:
        print(f"[오류 발생] {url}: {str(e)}")
        return None, None


def extract_post_links(blog_url):
    post_links = set()
    try:
        debug_dir = "debug"
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)

        if 'tistory.com' in blog_url:
            blog_url = blog_url.replace('tistory.com', 'tistory.com/m')
        elif 'naver.com' in blog_url:
            blog_url = convert_to_mobile_naver(blog_url)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://m.search.naver.com/',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0'
        }

        response = session.get(blog_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        if 'naver.com' in blog_url:
            for link in soup.find_all('a', href=True):
                href = link['href']
                naver_patterns = ['logNo=', 'PostView.naver', 'PostView.nhn', 'blogId=', 'categoryNo=', 'blog.naver.com']
                if any(pattern in href for pattern in naver_patterns):
                    full_url = urljoin(blog_url, href)
                    post_links.add(full_url)

            selectors = ['div.post a', 'div.article a', 'div.thumb a', 'div.list_post a',
                         'div.blog2_series a', 'div.paging a', 'div.post_cover a', 'div.post-item a',
                         'div.total_wrap a', 'div.total_area a', 'div.blog_post a', 'div.total_group a']

            for selector in selectors:
                for link in soup.select(selector):
                    href = link.get('href', '')
                    if href and any(pattern in href for pattern in naver_patterns):
                        full_url = urljoin(blog_url, href)
                        post_links.add(full_url)

        elif 'tistory.com' in blog_url:
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/entry/' in href or '/post/' in href:
                    full_url = urljoin(blog_url, href)
                    post_links.add(full_url)

        if not post_links:
            print(f"[DEBUG] 포스트 링크를 찾을 수 없습니다. URL: {blog_url}")
            print(f"[DEBUG] 페이지 제목: {soup.title.text if soup.title else '없음'}")
            print(f"[DEBUG] 링크 수: {len(soup.find_all('a'))}")
            with open(os.path.join(debug_dir, f"debug_{blog_url.split('/')[-1]}.html"), "w", encoding="utf-8") as f:
                f.write(response.text)

    except Exception as e:
        print(f"[ERROR] 포스트 링크 추출 중 오류 발생: {str(e)}")
        print(f"[DEBUG] 오류 발생 URL: {blog_url}")

    return list(post_links)

def is_valid_post_url(url):
    return (
        'logNo=' in url or '/entry/' in url or re.search(r'/\d+$', url)
    ) and not any(x in url for x in [
        'PostList.naver', 'CommentList.naver', 'BuddyList.naver',
        'OfficialBlog.naver', 'Login.naver', 'GuestbookList.naver',
        'BlogStat.naver', 'PostSearchList.naver', 'blogpeople'
    ])

def crawl_all_blogs(blog_list):
    results = []
    error_count = 0
    success_count = 0
    failed_urls = []

    for blog_url in tqdm(blog_list, desc="블로그 크롤링 중"):
        try:
            if not blog_url.startswith(('http://', 'https://')):
                blog_url = 'https://' + blog_url

            parsed = urlparse(blog_url)
            if not parsed.netloc:
                print(f"[ERROR] 잘못된 URL: {blog_url}")
                error_count += 1
                failed_urls.append(blog_url)
                continue

            if not is_valid_post_url(blog_url):
                print(f"[SKIP] 유효하지 않은 포스트 URL: {blog_url}")
                continue

            if is_single_post_url(blog_url) and 'naver.com' in blog_url:
                blog_url = convert_to_mobile_naver(blog_url)

            platform = 'tistory' if 'tistory.com' in blog_url else 'naver'
            print(f"[INFO] 플랫폼 감지: {platform} - {blog_url}")

            try:
                response = session.head(blog_url, timeout=10)
                if response.status_code == 404:
                    print(f"[ERROR] 페이지가 존재하지 않습니다: {blog_url}")
                    error_count += 1
                    failed_urls.append(blog_url)
                    continue
            except Exception as e:
                print(f"[ERROR] 연결할 수 없습니다: {blog_url} - {str(e)}")
                error_count += 1
                failed_urls.append(blog_url)
                continue

            if is_single_post_url(blog_url):
                post_links = [blog_url]
                print(f"[INFO] 단일 포스트 URL 감지: {blog_url}")
            else:
                post_links = extract_post_links(blog_url)
                post_links = [u for u in post_links if is_valid_post_url(u)]
                if not post_links:
                    print(f"[INFO] 페이지에서 포스트 링크를 찾을 수 없습니다: {blog_url}")
                    error_count += 1
                    failed_urls.append(blog_url)
                    continue
                print(f"[INFO] {len(post_links)}개의 포스트 링크를 찾았습니다.")

            for post_url in post_links:
                try:
                    title, content = fetch_post_content(post_url, platform)
                    if title and content:
                        results.append({
                            "platform": platform,
                            "keyword": "회고",
                            "title": title,
                            "link": post_url,
                            "body": content,
                            "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        success_count += 1
                        print(f"[SUCCESS] 포스트 크롤링 성공: {title[:30]}...")
                        time.sleep(random.uniform(2, 4))
                    else:
                        print(f"[ERROR] 포스트 내용 추출 실패: {post_url}")
                        error_count += 1
                        failed_urls.append(post_url)
                except Exception as e:
                    print(f"[ERROR] 포스트 크롤링 중 오류 발생 {post_url}: {str(e)}")
                    error_count += 1
                    failed_urls.append(post_url)
                    continue

        except Exception as e:
            print(f"[ERROR] 처리 중 오류 발생 {blog_url}: {str(e)}")
            error_count += 1
            failed_urls.append(blog_url)
            continue

    print(f"\n크롤링 완료:")
    print(f"성공: {success_count}개")
    print(f"실패: {error_count}개")
    print(f"총 처리: {success_count + error_count}개")

    if failed_urls:
        pd.DataFrame(failed_urls, columns=["failed_link"]).to_csv("crawl_failed_links.csv", index=False)
        print(f"[INFO] 실패한 링크 {len(failed_urls)}개 저장 완료 → crawl_failed_links.csv")

    return pd.DataFrame(results)

def search_naver_blog(query, display=300, sort="date"):
    results = []
    seen_links = set()
    start = 1
    max_pages = display // 10

    debug_dir = "debug"
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)

    base_url = "https://search.naver.com/search.naver"

    for page in range(1, max_pages + 1):
        try:
            params = {
                "where": "view",
                "sm": "tab_viw.blog",
                "query": query,
                "start": start,
                "date_option": "0",
                "date_from": "",
                "date_to": "",
                "nso": "so:dd",
            }
            url = f"{base_url}?{urlencode(params)}"
            print(f"[DEBUG] 검색 URL: {url}")

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Cache-Control": "max-age=0",
                "Referer": "https://search.naver.com"
            }

            response = session.get(url, headers=headers)
            print(f"[DEBUG] 검색 페이지 응답: {response.status_code}")

            if response.status_code != 200:
                print(f"[ERROR] 검색 실패: {response.status_code}")
                print(f"[DEBUG] 응답 헤더: {dict(response.headers)}")
                break

            with open(os.path.join(debug_dir, f"search_page_{page}.html"), "w", encoding="utf-8") as f:
                f.write(response.text)

            soup = BeautifulSoup(response.text, "html.parser")
            posts = soup.select("li.sh_blog_top")
            if not posts:
                posts = soup.select("div.view_wrap")

            if not posts:
                print(f"[DEBUG] 페이지 {page}에서 포스트를 찾을 수 없음")
                print(soup.prettify()[:1000])
                break

            print(f"[DEBUG] {len(posts)}개의 포스트를 찾았습니다.")
            found_new = False

            for post in posts:
                try:
                    title_elem = post.select_one("a.sh_blog_title")
                    if not title_elem:
                        title_elem = post.select_one("a.title_link")
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    link = title_elem.get("href")
                    if not link or link in seen_links:
                        continue

                    seen_links.add(link)
                    found_new = True

                    desc_elem = post.select_one("div.sh_blog_passage, dd.sh_blog_passage")
                    if not desc_elem:
                        desc_elem = post.select_one("div.detail_box")
                    description = desc_elem.get_text(strip=True) if desc_elem else ""

                    date_elem = post.select_one("dd.txt_inline")
                    if not date_elem:
                        date_elem = post.select_one("span.sub_time, span.date")
                    post_date = date_elem.get_text(strip=True) if date_elem else ""

                    blog_name_elem = post.select_one("a.sh_blog_title")
                    if not blog_name_elem:
                        blog_name_elem = post.select_one("a.sub_txt, a.writer")
                    blog_name = blog_name_elem.get_text(strip=True) if blog_name_elem else ""

                    result = {
                        "title": title,
                        "link": link,
                        "description": description,
                        "date": post_date,
                        "blog_name": blog_name
                    }
                    results.append(result)
                    print(f"[DEBUG] 결과 추가됨: {title}")

                except Exception as e:
                    print(f"[포스트 파싱 에러] {str(e)}")
                    continue

            if len(results) >= display or not found_new:
                break

            start += 10
            time.sleep(random.uniform(2, 4))

        except Exception as e:
            print(f"[검색 에러] {str(e)}")
            break

    print(f"[SUCCESS] 총 검색 결과: {len(results)}개 찾음")
    return results

def search_tistory_direct(query, max_posts=100):
    try:
        search_url = f"https://search.tistory.com/search?q={quote(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        response = session.get(search_url, headers=headers)
        response.raise_for_status()

        with open("tistory_search.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        soup = BeautifulSoup(response.text, 'html.parser')
        results = []

        for item in soup.select('.list_search_post .item'):
            if len(results) >= max_posts:
                break

            title_elem = item.select_one('.txt_tit')
            if not title_elem:
                continue

            title = title_elem.text.strip()
            link = title_elem.get('href')
            desc_elem = item.select_one('.txt_g')
            description = desc_elem.text.strip() if desc_elem else ""
            date_elem = item.select_one('.date')
            postdate = date_elem.text.strip() if date_elem else ""
            blog_name_elem = item.select_one('.info a')
            blog_name = blog_name_elem.text.strip() if blog_name_elem else ""

            if link and 'tistory.com' in link:
                result = {
                    "title": title,
                    "link": link,
                    "description": description,
                    "postdate": postdate,
                    "blog_name": blog_name
                }
                results.append(result)
                print(f"[DEBUG] Tistory 결과 추가됨: {result}")

        return results

    except Exception as e:
        print(f"[Tistory 검색 실패] {str(e)}")
        if 'response' in locals():
            print(f"[DEBUG] Response status: {response.status_code}")
            print(f"[DEBUG] Response text: {response.text[:500]}")
        return []

def search_blogs(keywords, platforms=["naver", "tistory"], max_posts=100):
    results = []
    for keyword in keywords:
        print(f"\n🔍 검색 키워드: {keyword}")

        if "naver" in platforms:
            print("Naver 블로그 검색 중...")
            naver_results = search_naver_blog(keyword, display=min(100, max_posts))
            for item in naver_results:
                results.append({
                    "platform": "naver",
                    "keyword": keyword,
                    "title": item["title"],
                    "link": item["link"],
                    "description": item["description"],
                    "postdate": item["date"]
                })

        if "tistory" in platforms:
            print("Tistory 블로그 검색 중...")
            tistory_results = search_tistory_direct(keyword, max_posts)
            for item in tistory_results:
                results.append({
                    "platform": "tistory",
                    "keyword": keyword,
                    "title": item["title"],
                    "link": item["link"],
                    "description": item.get("description", ""),
                    "postdate": item.get("postdate", "")
                })

        time.sleep(1)

    return pd.DataFrame(results)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="블로그 크롤링 및 검색")
    parser.add_argument("--mode", type=str, choices=["crawl", "search"], default="crawl",
                        help="크롤링 모드 선택 (crawl: 링크 기반, search: 검색 기반)")
    parser.add_argument("--input", type=str, default=os.path.join("data", "블로그 정리 취합본.csv"),
                        help="블로그 주소 CSV 경로 (컬럼: link)")
    parser.add_argument("--output", type=str, default="crawled_all_blogs.csv",
                        help="결과 저장 파일명")
    parser.add_argument("--keywords", type=str, nargs="+", default=["부트캠프 회고", "코딩 교육 후기"],
                        help="검색할 키워드 목록")
    parser.add_argument("--platforms", type=str, nargs="+", choices=["naver", "tistory"], default=["naver", "tistory"],
                        help="검색할 플랫폼 목록")
    parser.add_argument("--max-posts", type=int, default=100,
                        help="플랫폼당 최대 검색 결과 수")

    args = parser.parse_args()

    if args.mode == "crawl":
        df_links = pd.read_csv(args.input)
        blog_list = df_links['link'].dropna().unique().tolist() if 'link' in df_links.columns else df_links['블로그주소'].dropna().unique().tolist()
        df_result = crawl_all_blogs(blog_list)
    else:
        df_result = search_blogs(args.keywords, args.platforms, args.max_posts)

    df_result.to_csv(args.output, index=False)
    print(f"\n✅ 작업 완료: {args.output}")
