# crawling/tistory.py

from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
import os
import time
import re
from crawling.common import get_session

session = get_session()

def extract_post_links_tistory(blog_url):
    post_links = set()
    try:
        # ❌ 모바일 주소 변환 제거
        # blog_url = blog_url.replace('tistory.com', 'tistory.com/m')

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = session.get(blog_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/entry/' in href or '/post/' in href or re.search(r'tistory\.com/\d+$', href):
                full_url = urljoin(blog_url, href)
                post_links.add(full_url)

        if not post_links:
            print(f"[Tistory] 링크를 찾을 수 없습니다: {blog_url}")
        return list(post_links)

    except Exception as e:
        print(f"[Tistory 링크 추출 실패] {blog_url}: {e}")
        return []

def search_tistory_direct(query, max_posts=100):
    try:
        search_url = f"https://search.tistory.com/search?q={quote(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html",
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
