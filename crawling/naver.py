# crawling/naver.py

from urllib.parse import urlparse, parse_qs, urljoin, urlencode
from bs4 import BeautifulSoup
import os
import time
import random
from crawling.common import get_session

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

session = get_session()

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

def extract_post_links_naver(blog_url):
    post_links = set()
    try:
        blog_url = convert_to_mobile_naver(blog_url)

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--lang=ko_KR')
        options.add_argument('user-agent=Mozilla/5.0 (Linux; Android 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(blog_url)
        time.sleep(2.5)

        # ✅ iframe 전환
        try:
            driver.switch_to.frame("mainFrame")
        except Exception as e:
            print(f"[iframe 전환 실패] {blog_url}: {e}")

        html = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html, 'html.parser')

        for link in soup.find_all('a', href=True):
            href = link['href']
            naver_patterns = ['logNo=', 'PostView.naver', 'PostView.nhn', 'blogId=', 'categoryNo=', 'blog.naver.com']
            if any(pattern in href for pattern in naver_patterns):
                full_url = urljoin(blog_url, href)
                post_links.add(full_url)

        return list(post_links)
    except Exception as e:
        print(f"[Naver 링크 추출 실패] {blog_url}: {e}")
        return []

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
