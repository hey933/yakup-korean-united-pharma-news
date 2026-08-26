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

def fetch_from_search(keyword, max_pages=20):
    articles = []
    
    for page in range(1, max_pages + 1):
        try:
            search_url = f"https://www.yakup.com/search/index.html?search_word={quote(keyword)}&page={page}"
            print(f"[{page}페이지] {keyword}")
            
            response = requests.get(search_url, headers=HEADERS, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            list_con = soup.find('div', class_='list_con')
            if not list_con:
                break
            
            list_items = list_con.find_all('div', class_='list_item')
            print(f"  발견: {len(list_items)}개")
            
            if len(list_items) == 0:
                break
            
            for item in list_items:
                try:
                    link = item.find('a')
                    if not link:
                        continue
                    
                    title = link.get_text(strip=True)
                    url = link.get('href', '')
                    
                    if not title or not url:
                        continue
                    
                    if url.startswith('/'):
                        url = urljoin(BASE_URL, url)
                    elif not url.startswith('http'):
                        url = urljoin(BASE_URL, url)
                    
                    date_elem = item.find('span', class_='date')
                    date_str = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d')
                    
                    article = {
                        'title': title,
                        'url': url,
                        'date': date_str,
                        'source': 'yakup.com'
                    }
                    articles.append(article)
                    print(f"  ✓ {title[:50]}")
                except:
                    continue
            
            time.sleep(1)
            
        except Exception as e:
            print(f"오류: {e}")
            break
    
    return articles

def load_existing():
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('articles', [])
        except:
            return []
    return []

def save_articles(articles):
    ensure_data_dir()
    
    existing = load_existing()
    existing_urls = {a['url'] for a in existing}
    
    new_articles = [a for a in articles if a['url'] not in existing_urls]
    merged = new_articles + existing
    
    seen = set()
    unique = []
    for a in merged:
        if a['url'] not in seen:
            seen.add(a['url'])
            unique.append(a)
    
    unique = unique[:2000]
    unique.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    data = {
        'articles': unique,
        'last_updated': datetime.now().isoformat(),
        'total_count': len(unique)
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n저장: {len(unique)}개")

def main():
    print("크롤러 시작")
    all_articles = []
    
    for keyword in KEYWORDS:
        print(f"\n검색: {keyword}")
        articles = fetch_from_search(keyword, max_pages=20)
        all_articles.extend(articles)
        time.sleep(1)
    
    save_articles(all_articles)
    print("완료")

if __name__ == '__main__':
    main()
