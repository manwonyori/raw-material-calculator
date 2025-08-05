#!/usr/bin/env python3
"""다운로드 기능 테스트 스크립트"""

import requests
import json
from datetime import datetime

# 테스트 데이터 (토마토소스)
test_data = {
    "recipe_name": "최씨네토마토만능소스",
    "brand": "만원요리",
    "category": "소스류",
    "total_weight": 244,
    "loss_rate": 0.22,
    "materials": [
        {"name": "농축토마토", "percentage": 53.18, "price_per_kg": 3654},
        {"name": "간양파", "percentage": 18.41, "price_per_kg": 1500},
        {"name": "베이컨류", "percentage": 8.18, "price_per_kg": 9950},
        {"name": "다진마늘", "percentage": 0.82, "price_per_kg": 2000},
        {"name": "식용유", "percentage": 1.23, "price_per_kg": 2500},
        {"name": "다진돼지고기", "percentage": 10.23, "price_per_kg": 5500},
        {"name": "설탕", "percentage": 2.29, "price_per_kg": 1653},
        {"name": "다진소고기", "percentage": 1.02, "price_per_kg": 10000},
        {"name": "오레가노럽드", "percentage": 0.21, "price_per_kg": 15000},
        {"name": "바질럽드", "percentage": 0.15, "price_per_kg": 9000},
        {"name": "치킨스톡분말", "percentage": 0.18, "price_per_kg": 6029},
        {"name": "원계수잎분말", "percentage": 0.01, "price_per_kg": 16500}
    ]
}

def test_download_local():
    """로컬 서버에서 다운로드 테스트"""
    try:
        print("=== 로컬 서버 다운로드 테스트 ===")
        
        # 로컬 서버 URL
        url = "http://localhost:5000/download_excel"
        
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            # CSV 파일 저장
            filename = f"test_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"✅ 다운로드 성공: {filename}")
            print(f"✅ 파일 크기: {len(response.text)} 문자")
            
            # CSV 내용 미리보기
            print("\n=== CSV 내용 미리보기 ===")
            lines = response.text.split('\n')[:20]  # 첫 20줄만
            for i, line in enumerate(lines, 1):
                print(f"{i:2d}: {line}")
            
            if len(lines) >= 20:
                print("... (더 많은 내용)")
            
            return True
            
        else:
            print(f"❌ 다운로드 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False

def test_download_production():
    """프로덕션 서버에서 다운로드 테스트"""
    try:
        print("\n=== 프로덕션 서버 다운로드 테스트 ===")
        
        # 프로덕션 서버 URL
        url = "https://raw-material-calculator.onrender.com/download_excel"
        
        response = requests.post(url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            filename = f"production_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"✅ 프로덕션 다운로드 성공: {filename}")
            print(f"✅ 파일 크기: {len(response.text)} 문자")
            return True
            
        else:
            print(f"❌ 프로덕션 다운로드 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 프로덕션 테스트 실패: {e}")
        return False

def analyze_csv_structure():
    """CSV 구조 분석"""
    print("\n=== 예상 CSV 구조 ===")
    sections = [
        "1. 요약 정보 (레시피명, 브랜드, 총 재료비 등)",
        "2. 재료별 상세 (재료명, 비율, 사용량, 단가, 재료비)",
        "3. 팩 단위별 원가 (350g, 500g, 1kg, 2kg)",
        "4. 원가 분석 (주요 재료 TOP 5, 비중 분석)"
    ]
    
    for section in sections:
        print(f"   {section}")
    
    print("\n=== Excel에서 확인할 점 ===")
    checks = [
        "✅ 한글이 깨지지 않는지",
        "✅ 숫자에 천단위 콤마가 적용되는지",
        "✅ 각 섹션이 명확히 구분되는지",
        "✅ 판매가 계산이 정확한지 (원가율 30% 기준)"
    ]
    
    for check in checks:
        print(f"   {check}")

if __name__ == "__main__":
    analyze_csv_structure()
    
    # 로컬 테스트 (선택적)
    # test_download_local()
    
    # 프로덕션 테스트
    test_download_production()