# crawling/fetcher.py

from datetime import datetime
import time, random
import pandas as pd
from tqdm import tqdm
from urllib.parse import urlparse

from crawling.common import get_session, is_valid_post_url, is_single_post_url
from crawling.naver import convert_to_mobile_naver, extract_post_links_naver
from crawling.tistory import extract_post_links_tistory
from crawling.selector import fetch_post_content  # 추후 분리될 통합 fetcher

session = get_session()

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
                if platform == 'naver':
                    post_links = extract_post_links_naver(blog_url)
                else:
                    post_links = extract_post_links_tistory(blog_url)
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
                    if not title or not content:
                        print("➡️ fallback to Selenium")
                        title, content = fetch_post_content(post_url, platform, use_selenium=True)
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
