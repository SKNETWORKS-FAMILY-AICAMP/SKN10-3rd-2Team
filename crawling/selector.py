from bs4 import BeautifulSoup
from crawling.common import get_session
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, parse_qs
from webdriver_manager.chrome import ChromeDriverManager
import time

session = get_session()

def convert_sympathy_url_to_mobile(real_url):
    if "SympathyHistoryList.naver" in real_url:
        q = parse_qs(urlparse(real_url).query)
        blog_id = q.get("blogId", [""])[0]
        log_no = q.get("logNo", [""])[0]
        return f"https://m.blog.naver.com/{blog_id}/{log_no}"
    return real_url

def fetch_post_content(url, platform, use_selenium=False):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://search.naver.com" if platform == 'naver' else "https://search.daum.net",
            "Connection": "keep-alive"
        }

        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title, content = extract_title_and_body(soup, url, platform)
        if title and content:
            return title, content

        # fallback to selenium
        if use_selenium:
            return fetch_with_selenium(url, platform)
        return None, None

    except Exception as e:
        print(f"[오류 발생] {url}: {str(e)}")
        return None, None

def fetch_with_selenium(url, platform):
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--lang=ko_KR')
        options.add_argument('user-agent=Mozilla/5.0 (Linux; Android 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # 티스토리 모바일 강제 진입
        if platform == 'tistory':
            parsed = urlparse(url)
            if not parsed.netloc.startswith('m.'):
                url = url.replace('https://', 'https://m.')

        driver.get(url)
        time.sleep(2.5)

        if platform == 'naver':
            if "SympathyHistoryList.naver" in url:
                new_url = convert_sympathy_url_to_mobile(url)
                print(f"[Selenium] 본문용 모바일 URL 재접속: {new_url}")
                driver.get(new_url)
                time.sleep(2)
            else:
                iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                if iframes:
                    src = iframes[0].get_attribute('src')
                    print(f"[Selenium] iframe src 재접속: {src}")
                    driver.get(src)
                    time.sleep(2)
                else:
                    print("[Selenium] iframe 없음 → 현재 페이지 그대로 사용")

        html = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html, 'html.parser')
        return extract_title_and_body(soup, url, platform)
    except Exception as e:
        print(f"[오류 발생 - Selenium] {url}: {str(e)}")
        return None, None

def extract_title_and_body(soup, url, platform):
    title = None
    if platform == 'naver':
        title_elem = soup.select_one('h3.se_textarea, div.se-title-text')
        if not title_elem:
            title_elem = soup.select_one('div.pcol1')
        if title_elem:
            title = title_elem.get_text(strip=True)
    elif platform == 'tistory':
        title_elem = soup.select_one('h1.title, div.article-title')
        if not title_elem:
            title_elem = soup.select_one('meta[property="og:title"]')
            if title_elem:
                title = title_elem.get("content", "").strip()
        elif title_elem:
            title = title_elem.get_text(strip=True)

    content = None
    content_selectors = []
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
    elif platform == 'tistory':
        content_selectors = [
            'div.tt_article_useless_p_margin.contents_style',
            'div.tt_article_useless_p_margin',
            'div.contents_style',
            'div.article-content',
            'div.entry-content',
            'div#content',
            'div.content',
            'article',
            'section.article'
        ]

    for sel in content_selectors:
        content = soup.select_one(sel)
        if content:
            break

    if not content:
        print(f"[본문 없음] {url}")
        return None, None

    return title, content.get_text(strip=True)
