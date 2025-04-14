# main.py

import argparse
import pandas as pd
from crawling.fetcher import crawl_all_blogs
from crawling.searcher import search_blogs
import os


def main():
    parser = argparse.ArgumentParser(description="블로그 크롤링 및 검색")
    parser.add_argument("--mode", type=str, choices=["crawl", "search"], default="crawl",
                        help="크롤링 모드 선택 (crawl: 링크 기반, search: 검색 기반)")
    parser.add_argument("--input", type=str, default=os.path.join("data", "블로그 정리 취합본.csv"),
                        help="블로그 주소 CSV 경로 (컬럼: link 또는 블로그주소)")
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

if __name__ == "__main__":
    main()
