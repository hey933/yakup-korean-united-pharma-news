name: 야쿱 뉴스 크롤러

on:
  schedule:
    - cron: '0 0 * * *'
  
  workflow_dispatch:

permissions:
  contents: write

jobs:
  scrape:
    runs-on: ubuntu-latest
    
    steps:
    - name: 저장소 체크아웃
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Python 3.11 설정
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: 의존성 설치
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: 크롤러 실행
      run: python scraper.py
    
    - name: 변경사항 커밋 및 푸시
      run: |
        git config --local user.email "41898282+github-actions[bot]@users.noreply.github.com"
        git config --local user.name "github-actions[bot]"
        git add -A
        if git diff --cached --quiet; then
          echo "변경사항 없음"
        else
          git commit -m "🤖 자동 업데이트: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
          git push
        fi
