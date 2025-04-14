# crawling/searcher.py

import time
import pandas as pd
from crawling.naver import search_naver_blog
from crawling.tistory import search_tistory_direct

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
