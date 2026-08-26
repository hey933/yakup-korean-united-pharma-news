#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from urllib.parse import urljoin

BASE_URL = "https://www.yakup.com/"
SEARCH_URL = "https://www.yakup.com/news/index.html"
KEYWORDS = ['한국유나이티드제약', '한국유나이티드', 'KUP']
OUTPUT_FILE = "data/articles.json"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def ensure_data_dir():
    os.makedirs('data', exist_ok=True)

def fetch_articles():
    articles = []
    try:
        print(f"[{datetime.now()}] 크롤링 시작...")
        response = requests.get(SEARCH_URL, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for link in soup.find_all('a'):
            title = link.get_text(strip=True)
            url = link.get('href', '')
            
            if url.startswith('/'):
                url = urljoin(BASE_URL, url)
            elif not url.startswith('http'):
                url = urljoin(BASE_URL, url)
            
            if any(kw.lower() in title.lower() for kw in KEYWORDS) and url:
                articles.append({
                    'title': title,
                    'url': url,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'source': 'yakup.com'
                })
        
        print(f"[{datetime.now()}] 완료: {len(articles)}개")
    except Exception as e:
        print(f"오류: {e}")
    
    return articles

def load_existing_articles():
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f).get('articles', [])
        except:
            return []
    return []

def save_articles(articles):
    ensure_data_dir()
    existing = load_existing_articles()
    existing_urls = {a['url'] for a in existing}
    
    merged = [a for a in articles if a['url'] not in existing_urls] + existing
    merged = merged[:1000]
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'articles': merged,
            'last_updated': datetime.now().isoformat(),
            'total_count': len(merged)
        }, f, ensure_ascii=False, indent=2)
    
    print(f"저장 완료: {OUTPUT_FILE} ({len(merged)}개)")

def main():
    print("="*50)
    print("야쿱 크롤러 시작")
    print("="*50)
    articles = fetch_articles()
    save_articles(articles)
    print("="*50)
    print("완료")
    print("="*50)

if __name__ == '__main__':
    main()
