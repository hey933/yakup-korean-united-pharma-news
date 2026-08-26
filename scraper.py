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
KEYWORDS = ['한국유나이티드제약', '한국유나이티드', 'KUP', 'KUPP']
OUTPUT_FILE = "data/articles.json"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def ensure_data_dir():
    os.makedirs('data', exist_ok=True)

def fetch_from_search(keyword, max_pages=5):
    """검색 결과 페이지에서 기사 수집"""
    articles = []
    
    for page in range(1, max_pages + 1):
        try:
            # 야쿱 검색 URL
            search_url = f"https://www.yakup.com/search.html?keyword={quote(keyword)}&page={page}"
            print(f"[검색] {keyword} - {page}페이지 크롤링 중...")
            
            response = requests.get(search_url, headers=HEADERS, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 검색 결과 링크 찾기
            article_links = soup.find_all('a', class_=['news-link', 'article-title', 'title'])
            if not article_links:
                article_links = soup.find_all('a')
            
            found_in_page = 0
            for link in article_links:
                try:
                    title = link.get_text(strip=True)
                    url = link.get('href', '')
                    
                    if not url or not title or len(title) < 5:
                        continue
                    
                    if url.startswith('/'):
                        url = urljoin(BASE_URL, url)
                    elif not url.startswith('http'):
                        url = urljoin(BASE_URL, url)
                    
                    # 키워드 확인
                    if keyword.lower() in title.lower():
                        article = {
                            'title': title,
                            'url': url,
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'source': 'yakup.com',
                            'keyword': keyword
                        }
                        articles.append(article)
                        found_in_page += 1
                        print(f"  ✓ {title[:60]}")
                except Exception as e:
                    continue
            
            print(f"  → 이 페이지에서 {found_in_page}개 발견")
            
            if found_in_page == 0:
                print(f"  → 더 이상 결과 없음, 다음 키워드로")
                break
            
            # 과도한 요청 방지
            time.sleep(2)
            
        except Exception as e:
            print(f"  오류: {e}")
            continue
    
    return articles

def fetch_from_news_category():
    """뉴스 카테고리 페이지에서 기사 수집"""
    articles = []
    
    try:
        print("[카테고리] 뉴스 페이지 크롤링 중...")
        news_url = "https://www.yakup.com/news/index.html"
        
        response = requests.get(news_url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 모든 링크에서 기사 찾기
        for link in soup.find_all('a'):
            try:
                title = link.get_text(strip=True)
                url = link.get('href', '')
                
                if not url or not title or len(title) < 5:
                    continue
                
                if url.startswith('/'):
                    url = urljoin(BASE_URL, url)
                elif not url.startswith('http'):
                    url = urljoin(BASE_URL, url)
                
                # 키워드 필터링
                is_relevant = any(kw.lower() in title.lower() for kw in KEYWORDS)
                
                if is_relevant:
                    article = {
                        'title': title,
                        'url': url,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'source': 'yakup.com'
                    }
                    articles.append(article)
                    print(f"  ✓ {title[:60]}")
            except:
                continue
        
        print(f"  → 총 {len(articles)}개 발견")
        
    except Exception as e:
        print(f"  오류: {e}")
    
    return articles

def fetch_all_articles():
    """모든 방법으로 기사 수집"""
    all_articles = []
    
    print("="*60)
    print("야쿱 뉴스 크롤러 시작")
    print(f"시작 시간: {datetime.now()}")
    print("="*60)
    
    # 1. 뉴스 카테고리에서 수집
    category_articles = fetch_from_news_category()
    all_articles.extend(category_articles)
    
    print()
    
    # 2. 검색을 통해 과거 기사 수집
    for keyword in KEYWORDS:
        search_articles = fetch_from_search(keyword, max_pages=10)
        all_articles.extend(search_articles)
        time.sleep(1)
    
    return all_articles

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
        except:
            return []
    return []

def save_articles(articles):
    """기사 데이터를 JSON 파일로 저장"""
    ensure_data_dir()
    
    # 기존 기사와 병합
    existing = load_existing_articles()
    existing_urls = {a['url'] for a in existing}
    
    # 새 기사만 추가
    new_articles = [a for a in articles if a['url'] not in existing_urls]
    
    # 병합 (새 기사 + 기존 기사)
    merged = new_articles + existing
    
    # 중복 제거
    merged = remove_duplicates(merged)
    
    # 최근 5000개 유지
    merged = merged[:5000]
    
    # 정렬 (최신순)
    merged.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    data = {
        'articles': merged,
        'last_updated': datetime.now().isoformat(),
        'total_count': len(merged)
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print()
    print("="*60)
    print(f"✓ 저장 완료: {OUTPUT_FILE}")
    print(f"  - 새로 수집: {len(new_articles)}개")
    print(f"  - 총 저장: {len(merged)}개")
    print(f"  - 마지막 업데이트: {data['last_updated']}")
    print("="*60)
    
    return data

def main():
    articles = fetch_all_articles()
    print()
    save_articles(articles)

if __name__ == '__main__':
    main()
