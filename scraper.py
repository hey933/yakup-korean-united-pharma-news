#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
야쿱(yakup.com) 뉴스 크롤러
한국유나이티드제약 관련 기사를 수집합니다.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from urllib.parse import urljoin

# 설정
BASE_URL = "https://www.yakup.com/"
SEARCH_URL = "https://www.yakup.com/news/index.html"
KEYWORDS = ['한국유나이티드제약', '한국유나이티드', 'KUP', 'KUPP']
OUTPUT_FILE = "data/articles.json"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def ensure_data_dir():
    """data 디렉토리 생성"""
    os.makedirs('data', exist_ok=True)


def fetch_articles():
    """야쿱 뉴스에서 기사 수집"""
    articles = []
    
    try:
        print(f"[{datetime.now()}] 야쿱 뉴스 크롤링 시작...")
        
        response = requests.get(SEARCH_URL, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        article_links = soup.find_all('a')
        
        processed = set()
        
        for link in article_links:
            try:
                title = link.get_text(strip=True)
                url = link.get('href', '')
                
                if url.startswith('/'):
                    url = urljoin(BASE_URL, url)
                elif not url.startswith('http'):
                    url = urljoin(BASE_URL, url)
                
                if url in processed:
                    continue
                
                is_relevant = any(keyword.lower() in title.lower() for keyword in KEYWORDS)
                
                if is_relevant and title and url and len(title) > 5:
                    processed.add(url)
                    
                    article = {
                        'title': title,
                        'url': url,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'source': 'yakup.com',
                        'keywords': [kw for kw in KEYWORDS if kw.lower() in title.lower()]
                    }
                    articles.append(article)
                    print(f"✓ 추가됨: {title[:50]}...")
            
            except Exception as e:
                print(f"⚠ 기사 처리 오류: {e}")
                continue
        
        print(f"[{datetime.now()}] 총 {len(articles)}개 기사 수집 완료")
        
    except requests.RequestException as e:
        print(f"✗ 네트워크 오류: {e}")
    except Exception as e:
        print(f"✗ 예상치 못한 오류: {e}")
    
    return articles


def load_existing_articles():
    """기존 기사 데이터 로드"""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('articles', [])
        except Exception as e:
            print(f"⚠ 기존 데이터 로드 오류: {e}")
    return []


def save_articles(articles):
    """기사 데이터를 JSON 파일로 저장"""
    ensure_data_dir()
    
    existing = load_existing_articles()
    existing_urls = {article['url'] for article in existing}
    
    merged = existing.copy()
    for article in articles:
        if article['url'] not in existing_urls:
            merged.insert(0, article)
    
    merged = merged[:1000]
    
    data = {
        'articles': merged,
        'last_updated': datetime.now().isoformat(),
        'total_count': len(merged)
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ {OUTPUT_FILE}에 저장 완료 (총 {len(merged)}개)")
    return data


def main():
    """메인 실행 함수"""
    print("="*50)
    print("야쿱 한국유나이티드제약 뉴스 크롤러")
    print(f"시작 시간: {datetime.now()}")
    print("="*50)
    
    articles = fetch_articles()
    data = save_articles(articles)
    
    print("="*50)
    print("✓ 크롤링 완료")
    print(f"마지막 업데이트: {data['last_updated']}")
    print("="*50)


if __name__ == '__main__':
    main()
