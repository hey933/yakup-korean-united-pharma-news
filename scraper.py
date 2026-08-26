name: 야쿱 뉴스 크롤러

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

permissions:
  contents: write
  actions: write

jobs:
  scrape:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run scraper
      run: python scraper.py
    
    - name: Commit and push
      run: |
        git config --global user.name "GitHub Action"
        git config --global user.email "action@github.com"
        git add data/articles.json || true
        git commit -m "🤖 Update articles $(date -u '+%Y-%m-%d %H:%M:%S')" || true
        git push || true
