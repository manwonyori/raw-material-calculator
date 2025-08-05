import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import subprocess

class GitHubDataManager:
    def __init__(self, base_path="data"):
        self.base_path = base_path
        self.ensure_directories()
    
    def ensure_directories(self):
        """필요한 디렉토리 생성"""
        dirs = [
            f"{self.base_path}/recipes/소스류",
            f"{self.base_path}/recipes/반찬류", 
            f"{self.base_path}/recipes/국찌개류",
            f"{self.base_path}/materials",
            f"{self.base_path}/history"
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def save_recipe(self, recipe_data: Dict) -> str:
        """레시피 저장"""
        try:
            # 파일명 생성
            recipe_name = recipe_data.get('recipe_name', 'unnamed')
            category = recipe_data.get('category', '기타')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 버전 관리
            existing_files = self.get_recipe_versions(recipe_name, category)
            version = len(existing_files) + 1
            
            filename = f"{recipe_name}_v{version}_{timestamp}.json"
            filepath = f"{self.base_path}/recipes/{category}/{filename}"
            
            # 메타데이터 추가
            recipe_data.update({
                'version': version,
                'created_date': datetime.now().isoformat(),
                'filename': filename
            })
            
            # 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(recipe_data, f, ensure_ascii=False, indent=2)
            
            # Git commit
            self.git_commit_and_push(f"Add recipe: {recipe_name} v{version}")
            
            return filepath
            
        except Exception as e:
            raise Exception(f"레시피 저장 실패: {str(e)}")
    
    def get_recipe_versions(self, recipe_name: str, category: str) -> List[str]:
        """레시피의 모든 버전 조회"""
        category_path = f"{self.base_path}/recipes/{category}"
        if not os.path.exists(category_path):
            return []
        
        files = []
        for file in os.listdir(category_path):
            if file.startswith(recipe_name) and file.endswith('.json'):
                files.append(file)
        
        return sorted(files)
    
    def load_recipe(self, filename: str, category: str) -> Dict:
        """특정 레시피 불러오기"""
        filepath = f"{self.base_path}/recipes/{category}/{filename}"
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"레시피 파일을 찾을 수 없습니다: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_all_recipes(self) -> Dict[str, List[Dict]]:
        """모든 레시피 목록 조회"""
        recipes = {}
        recipes_path = f"{self.base_path}/recipes"
        
        if not os.path.exists(recipes_path):
            return recipes
        
        for category in os.listdir(recipes_path):
            category_path = f"{recipes_path}/{category}"
            if os.path.isdir(category_path):
                recipes[category] = []
                
                for file in os.listdir(category_path):
                    if file.endswith('.json'):
                        try:
                            recipe = self.load_recipe(file, category)
                            recipes[category].append({
                                'filename': file,
                                'recipe_name': recipe.get('recipe_name'),
                                'version': recipe.get('version'),
                                'created_date': recipe.get('created_date'),
                                'cost_per_100g': recipe.get('cost_per_100g', 0)
                            })
                        except Exception as e:
                            print(f"레시피 로드 실패 {file}: {e}")
                
                # 버전 순으로 정렬
                recipes[category].sort(key=lambda x: x.get('version', 0), reverse=True)
        
        return recipes
    
    def save_cost_history(self, recipe_name: str, category: str, cost_data: Dict):
        """원가 이력 저장"""
        try:
            month = datetime.now().strftime('%Y-%m')
            history_dir = f"{self.base_path}/history/{month}"
            os.makedirs(history_dir, exist_ok=True)
            
            history_file = f"{history_dir}/{recipe_name}_{category}.json"
            
            # 기존 이력 로드
            history = []
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # 새 이력 추가
            history.append({
                'date': datetime.now().isoformat(),
                'cost_per_100g': cost_data.get('cost_per_100g'),
                'total_cost': cost_data.get('total_material_cost'),
                'loss_rate': cost_data.get('loss_rate')
            })
            
            # 저장
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            # Git commit
            self.git_commit_and_push(f"Update cost history: {recipe_name}")
            
        except Exception as e:
            print(f"원가 이력 저장 실패: {e}")
    
    def git_commit_and_push(self, message: str):
        """Git commit and push"""
        try:
            subprocess.run(['git', 'add', 'data/'], check=True, cwd='.')
            subprocess.run(['git', 'commit', '-m', message], check=True, cwd='.')
            subprocess.run(['git', 'push'], check=True, cwd='.')
            print(f"Git commit 성공: {message}")
        except subprocess.CalledProcessError as e:
            print(f"Git commit 실패: {e}")
        except Exception as e:
            print(f"Git 작업 중 오류: {e}")
    
    def get_cost_trend(self, recipe_name: str, category: str) -> List[Dict]:
        """원가 변동 추이 조회"""
        trends = []
        history_path = f"{self.base_path}/history"
        
        if not os.path.exists(history_path):
            return trends
        
        # 모든 월별 디렉토리 검색
        for month_dir in os.listdir(history_path):
            history_file = f"{history_path}/{month_dir}/{recipe_name}_{category}.json"
            
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    monthly_history = json.load(f)
                    trends.extend(monthly_history)
        
        # 날짜 순 정렬
        trends.sort(key=lambda x: x['date'])
        return trends