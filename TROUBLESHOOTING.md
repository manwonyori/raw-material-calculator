# 🔧 문제 해결 가이드

## 502 Bad Gateway 에러

### Render 대시보드에서 확인할 사항:

1. **Logs 탭 확인**
   - 에러 메시지 찾기
   - "killed" 메시지 = 메모리 부족
   - Import error = 패키지 문제

2. **일반적인 해결 방법**

### 옵션 1: 경량 버전 사용
```bash
# Procfile 수정
web: gunicorn simple_app:app
```

### 옵션 2: 패키지 제거
pandas 대신 CSV 사용:
```python
# CSV 다운로드로 변경
import csv
```

### 옵션 3: 유료 플랜
Render 무료 플랜 제한:
- RAM: 512MB
- CPU: 0.1
- 15분 후 슬립

### 로컬 테스트
```bash
pip install -r requirements.txt
python app.py
```
http://localhost:5000 접속

## 대안: Vercel 배포
더 간단한 배포를 원한다면 Vercel 사용 고려