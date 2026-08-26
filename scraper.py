name: 야쿱 뉴스 크롤러

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run scraper
      run: python scraper.py
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: articles
        path: data/articles.json
