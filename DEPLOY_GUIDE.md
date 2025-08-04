# 🚀 Render 배포 가이드

## GitHub 레포지토리
✅ 생성 완료: https://github.com/manwonyori/raw-material-calculator

## Render 배포 단계

### 1. Render 로그인
https://render.com 접속 후 로그인

### 2. 새 웹 서비스 생성
1. Dashboard에서 **"New +"** 클릭
2. **"Web Service"** 선택

### 3. GitHub 연결
1. **"Connect a repository"** 선택
2. GitHub 계정 연결 (처음인 경우)
3. `manwonyori/raw-material-calculator` 레포지토리 선택
4. **"Connect"** 클릭

### 4. 서비스 설정
자동으로 설정되는 내용:
- **Name**: raw-material-calculator
- **Region**: Singapore (자동 선택됨)
- **Branch**: master
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### 5. 배포 시작
**"Create Web Service"** 클릭

### 6. 배포 완료 대기
- 약 2-5분 소요
- 로그에서 진행 상황 확인
- "Your service is live 🎉" 메시지 확인

### 7. 접속 URL
배포 완료 후 제공되는 URL:
`https://raw-material-calculator.onrender.com`

## 📱 사용 방법
1. 웹사이트 접속
2. 토마토소스 데이터 자동 로드됨
3. 계산하기 클릭
4. 결과 확인 및 엑셀 다운로드

## 🔧 문제 해결
- 배포 실패 시: Logs 탭에서 에러 확인
- 느린 로딩: 무료 플랜은 15분 비활성 후 슬립 (첫 접속 시 30초 대기)