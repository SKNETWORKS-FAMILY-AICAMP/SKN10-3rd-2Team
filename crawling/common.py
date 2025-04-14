# crawling/common.py

import re
import requests
from fake_useragent import UserAgent
from urllib.parse import urlparse
import warnings
from bs4 import XMLParsedAsHTMLWarning
import pytesseract
from PIL import Image
import io

# 경고 제거
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# 세션 설정
ua = UserAgent()
session = requests.Session()
session.headers.update({
    "User-Agent": ua.chrome,
    "Referer": "https://www.google.com"
})

def get_session():
    return session

def is_valid_post_url(url):
    return (
        'logNo=' in url or '/entry/' in url or re.search(r'/\d+$', url)
    ) and not any(x in url for x in [
        'PostList.naver', 'CommentList.naver', 'BuddyList.naver',
        'OfficialBlog.naver', 'Login.naver', 'GuestbookList.naver',
        'BlogStat.naver', 'PostSearchList.naver', 'blogpeople'
    ])

def extract_text_from_image(image_url):
    try:
        response = session.get(image_url, timeout=5)
        image = Image.open(io.BytesIO(response.content))
        text = pytesseract.image_to_string(image, lang='kor+eng')
        return text.strip()
    except Exception as e:
        print(f"[이미지 텍스트 추출 실패] {image_url} / {e}")
        return ""

def is_single_post_url(url):
    return (
        "logNo=" in url or re.search(r'tistory\\.com/\\d+$', url) is not None
    )
