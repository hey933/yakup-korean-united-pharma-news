#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def ensure_data_dir():
    os.makedirs('data', exist_ok=True)

def fetch_from_search(keyword, max_pages=30):
    """야쿱 검색 결과에서 기사 수집"""
    articles = []
    
    for page in range(1, max_pages + 1):
        try:
            search_url = f"https://www.yakup.com/search/index.html?search_word={quote(keyword)}&page={page}"
            print(f"[페이지 {page}] {keyword}")
            
            response = requests.get(search_url, headers=HEADERS, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 검색 결과 컨테이너 찾기
            search_result = soup.find('div', class_='search_result_new_view')
            if not search_result:
                print(f"  검색 결과 없음")
                break
            
            # 각 기사 찾기
            list_items = search_result.find_all('div', class_='left_con')
            print(f"  발견: {len(list_items)}개")
            
            if len(list_items) == 0:
                break
            
            for item in list_items:
                try:
                    # 제목 및 링크 찾기
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
                    if not date_elem:
                        date_elem = item.find('span')
                    
                    date_str = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d')
                    
                    # 기본 포맷 (YYYY-MM-DD) 확인
                    if len(date_str) > 10:
                        date_str = date_str[:10]
                    
                    article = {
                        'title': title,
                        'url': url,
                        'date': date_str,
                        'source': 'yakup.com'
                    }
                    
                    articles.append(article)
                    print(f"  ✓ [{date_str}] {title[:50]}")
                
                except Exception as e:
                    continue
            
            if len(list_items) == 0:
                break
            
            time.sleep(1)
            
        except Exception as e:
            print(f"  오류: {e}")
            break
    
    return articles

def remove_duplicates(articles):
    """중복 제거"""
    seen_urls = set()
    unique = []
    
    for article in articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique.append(article)
    
    return unique

def load_existing():
    """기존 데이터 로드"""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('articles', [])
        except:
            return []
    return []

def save_articles(articles):
    """데이터 저장"""
    ensure_data_dir()
    
    existing = load_existing()
    existing_urls = {a['url'] for a in existing}
    
    new_articles = [a for a in articles if a['url'] not in existing_urls]
    merged = new_articles + existing
    merged = remove_duplicates(merged)
    merged = merged[:3000]
    merged.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    data = {
        'articles': merged,
        'last_updated': datetime.now().isoformat(),
        'total_count': len(merged)
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n저장 완료: {len(merged)}개 (신규: {len(new_articles)}개)")

def main():
    print("="*60)
    print("🤖 야쿱 크롤러 시작")
    print("="*60)
    
    all_articles = []
    
    for keyword in KEYWORDS:
        print(f"\n🔍 '{keyword}' 검색\n")
        articles = fetch_from_search(keyword, max_pages=30)
        all_articles.extend(articles)
        time.sleep(2)
    
    print("\n" + "="*60)
    save_articles(all_articles)
    print("="*60)

if __name__ == '__main__':
    main()
