#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
야쿱(yakup.com) 검색 결과 크롤러
한국유나이티드제약 관련 기사를 수집합니다.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from urllib.parse import urljoin, quote
import time

BASE_URL = "https://www.yakup.com/"
KEYWORDS = ['한국유나이티드제약', '한국유나이티드']
OUTPUT_FILE = "data/articles.json"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def ensure_data_dir():
    """data 디렉토리 생성"""
    os.makedirs('data', exist_ok=True)

def fetch_from_search(keyword, max_pages=20):
    """야쿱 검색 결과에서 기사 수집"""
    articles = []
    
    for page in range(1, max_pages + 1):
        try:
            # 야쿱 검색 URL
            search_url = f"https://www.yakup.com/search/index.html?search_word={quote(keyword)}&page={page}"
            print(f"[페이지 {page}] {keyword} 검색 중... {search_url}")
            
            response = requests.get(search_url, headers=HEADERS, timeout=10)
            response.encoding = 'utf-8'
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 개발자 도구에서 본 구조:
            # <div class="list_con">
            #   <div class="list_item">
            #     <a href="...">기사제목</a>
            #   </div>
            # </div>
            
            # 기사 목록 찾기
            list_con = soup.find('div', class_='list_con')
            if not list_con:
                print(f"  ⚠️ 기사 목록을 찾을 수 없음")
                break
            
            list_items = list_con.find_all('div', class_='list_item')
            print(f"  → 이 페이지에서 {len(list_items)}개 항목 발견")
            
            if len(list_items) == 0:
                print(f"  → 결과 없음, 검색 종료")
                break
            
            found_in_page = 0
            for item in list_items:
                try:
                    # 기사 링크 찾기
                    link = item.find('a')
                    if not link:
                        continue
                    
                    title = link.get_text(strip=True)
                    url = link.get('href', '')
                    
                    if not title or not url or len(title) < 3:
                        continue
                    
                    # URL 정규화
                    if url.startswith('/'):
                        url = urljoin(BASE_URL, url)
                    elif not url.startswith('http'):
                        url = urljoin(BASE_URL, url)
                    
                    # 날짜 찾기
                    date_elem = item.find('span', class_='date')
                    date_str = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d')
                    
                    # 기사 데이터 생성
                    article = {
                        'title': title,
                        'url': url,
                        'date': date_str,
                        'source': 'yakup.com',
                        'keyword': keyword
                    }
                    
                    articles.append(article)
                    found_in_page += 1
                    print(f"    ✓ [{date_str}] {title[:60]}")
                
                except Exception as e:
                    print(f"    ⚠️ 항목 처리 오류: {e}")
                    continue
            
            print(f"  → 수집: {found_in_page}개")
            
            if found_in_page == 0:
                break
            
            # 과도한 요청 방지
            time.sleep(1)
            
        except requests.RequestException as e:
            print(f"  ✗ 요청 오류: {e}")
            break
        except Exception as e:
            print(f"  ✗ 오류: {e}")
            break
    
    return articles

def remove_duplicates(articles):
    """중복 제거 (URL 기준)"""
    seen_urls = set()
    unique = []
    
    for article in articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique.append(article)
    
    return unique

def load_existing_articles():
    """기존 기사 데이터 로드"""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('articles', [])
        except Exception as e:
            print(f"⚠️ 기존 데이터 로드 오류: {e}")
            return []
    return []

def save_articles(articles):
    """기사 데이터를 JSON 파일로 저장"""
    ensure_data_dir()
    
    # 기존 기사 로드
    existing = load_existing_articles()
    existing_urls = {a['url'] for a in existing}
    
    # 새 기사만 필터링
    new_articles = [a for a in articles if a['url'] not in existing_urls]
    
    # 병합 (새 기사 + 기존 기사)
    merged = new_articles + existing
    
    # 중복 제거
    merged = remove_duplicates(merged)
    
    # 최근 2000개 유지
    merged = merged[:2000]
    
    # 날짜순 정렬 (최신순)
    merged.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    data = {
        'articles': merged,
        'last_updated': datetime.now().isoformat(),
        'total_count': len(merged)
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return data, len(new_articles)

def main():
    """메인 실행 함수"""
    print("="*70)
    print("🤖 야쿱 한국유나이티드제약 뉴스 크롤러")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    all_articles = []
    
    # 각 키워드별로 검색
    for keyword in KEYWORDS:
        print(f"\n🔍 키워드 검색: '{keyword}'")
        print("-" * 70)
        articles = fetch_from_search(keyword, max_pages=20)
        all_articles.extend(articles)
        time.sleep(2)  # 요청 간 대기
    
    # 저장
    print("\n" + "="*70)
    print("💾 데이터 저장 중...")
    print("="*70)
    data, new_count = save_articles(all_articles)
    
    print(f"\n✅ 크롤링 완료!")
    print(f"  - 새로 수집: {new_count}개")
    print(f"  - 총 저장: {data['total_count']}개")
    print(f"  - 파일: {OUTPUT_FILE}")
    print(f"  - 마지막 업데이트: {data['last_updated']}")
    print("="*70)

if __name__ == '__main__':
    main()
