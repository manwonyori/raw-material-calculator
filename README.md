# 🧮 원재료 계산기 - 만원요리 최씨남매

원재료 비용을 정확하게 계산하고 엑셀로 다운로드할 수 있는 웹 애플리케이션입니다.

## 🌟 주요 기능

### 1. 유연한 단위 입력
- kg, g, 통, 박스, 봉 등 다양한 구매 단위 지원
- 자동으로 kg당 단가로 변환

### 2. 로스율 계산
- 로스율(%) 직접 입력
- 실제 생산량 입력 후 로스율 자동 계산

### 3. 팩 단위별 원가
- 350g, 500g, 1kg, 2kg 등 팩 규격별 원가 자동 계산

### 4. 엑셀 다운로드
- 요약, 재료상세, 팩단위원가 시트로 구성
- 언제든 재사용 가능한 형식

## 🚀 배포 방법

### GitHub에 업로드
```bash
git init
git add .
git commit -m "원재료 계산기 초기 커밋"
git remote add origin [your-github-repo-url]
git push -u origin main
```

### Render 배포
1. [Render](https://render.com) 로그인
2. New → Web Service
3. GitHub 레포지토리 연결
4. 자동 배포 설정 완료

## 💻 로컬 실행
```bash
pip install -r requirements.txt
python app.py
```
브라우저에서 http://localhost:5000 접속

## 📊 사용 예시
1. 레시피명과 총 생산량 입력
2. 재료별 비율과 단가 입력
3. 로스율 설정 (22% 등)
4. 계산하기 클릭
5. 결과 확인 및 엑셀 다운로드

## 🎨 브랜드 컬러
- Primary: #FF6B35 (만원요리 주황)
- Secondary: #2D3436 (검정)
- Accent: #74B9FF (하늘)