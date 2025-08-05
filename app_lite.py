from flask import Flask, render_template, request, jsonify, send_file, Response
from datetime import datetime
import json
import csv
import io
import os
from data_manager import GitHubDataManager

app = Flask(__name__)
data_manager = GitHubDataManager()

class RawMaterialCalculator:
    def __init__(self):
        self.materials = []
        
    def calculate_cost(self, recipe_data, loss_rate=0.22):
        """원재료 계산 핵심 로직"""
        total_input_weight = recipe_data.get('total_weight', 244)  # kg
        total_material_cost = 0
        
        materials_detail = []
        
        for material in recipe_data.get('materials', []):
            # 재료별 사용량 계산
            usage_kg = total_input_weight * (material['percentage'] / 100)
            usage_g = usage_kg * 1000
            
            # 재료별 비용 계산
            material_cost = usage_kg * material['price_per_kg']
            total_material_cost += material_cost
            
            materials_detail.append({
                'name': material['name'],
                'percentage': material['percentage'],
                'price_per_kg': material['price_per_kg'],
                'price_per_g': material['price_per_kg'] / 1000,
                'usage_kg': round(usage_kg, 2),
                'usage_g': round(usage_g, 2),
                'cost': round(material_cost, 0)
            })
        
        # 로스율 적용
        actual_production_kg = total_input_weight * (1 - loss_rate)
        actual_production_g = actual_production_kg * 1000
        
        # g당 원가 계산
        cost_per_g = total_material_cost / actual_production_g
        cost_per_100g = cost_per_g * 100
        
        # 팩 단위별 원가
        pack_costs = {
            '350g': round(cost_per_g * 350),
            '500g': round(cost_per_g * 500),
            '1kg': round(cost_per_g * 1000),
            '2kg': round(cost_per_g * 2000)
        }
        
        return {
            'recipe_name': recipe_data.get('recipe_name', '토마토만능소스'),
            'total_input_kg': total_input_weight,
            'loss_rate': loss_rate * 100,
            'actual_production_kg': round(actual_production_kg, 2),
            'total_material_cost': round(total_material_cost),
            'cost_per_g': round(cost_per_g, 2),
            'cost_per_100g': round(cost_per_100g),
            'materials_detail': materials_detail,
            'pack_costs': pack_costs,
            'calculation_date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    calculator = RawMaterialCalculator()
    result = calculator.calculate_cost(data)
    return jsonify(result)

@app.route('/save_recipe', methods=['POST'])
def save_recipe():
    """레시피 저장"""
    try:
        data = request.json
        calculator = RawMaterialCalculator()
        result = calculator.calculate_cost(data)
        
        # 레시피 데이터 준비
        recipe_data = {
            'recipe_name': data.get('recipe_name', ''),
            'brand': data.get('brand', ''),
            'category': data.get('category', '기타'),
            'total_weight': data.get('total_weight', 244),
            'loss_rate': data.get('loss_rate', 0.22),
            'materials': data.get('materials', []),
            'cost_per_100g': result.get('cost_per_100g'),
            'total_material_cost': result.get('total_material_cost'),
            'calculation_result': result
        }
        
        # 저장
        filepath = data_manager.save_recipe(recipe_data)
        
        # 원가 이력도 저장
        data_manager.save_cost_history(
            recipe_data['recipe_name'], 
            recipe_data['category'], 
            result
        )
        
        return jsonify({
            'success': True, 
            'message': '레시피가 저장되었습니다',
            'filepath': filepath
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/load_recipes')
def load_recipes():
    """모든 레시피 목록 조회"""
    try:
        recipes = data_manager.get_all_recipes()
        return jsonify({'success': True, 'recipes': recipes})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/load_recipe/<category>/<filename>')
def load_recipe(category, filename):
    """특정 레시피 불러오기"""
    try:
        recipe = data_manager.load_recipe(filename, category)
        return jsonify({'success': True, 'recipe': recipe})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/cost_trend/<category>/<recipe_name>')
def cost_trend(category, recipe_name):
    """원가 변동 추이 조회"""
    try:
        trends = data_manager.get_cost_trend(recipe_name, category)
        return jsonify({'success': True, 'trends': trends})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download_excel', methods=['POST'])
def download_csv():
    """CSV 파일로 다운로드 (Excel 대체)"""
    data = request.json
    calculator = RawMaterialCalculator()
    result = calculator.calculate_cost(data)
    
    # CSV 생성
    output = io.StringIO()
    
    # 요약 정보
    output.write("원재료 계산 결과\n")
    output.write(f"레시피명,{result['recipe_name']}\n")
    output.write(f"총 투입량(kg),{result['total_input_kg']}\n")
    output.write(f"로스율(%),{result['loss_rate']}\n")
    output.write(f"실제 생산량(kg),{result['actual_production_kg']}\n")
    output.write(f"총 재료비,{result['total_material_cost']}\n")
    output.write(f"100g당 원가,{result['cost_per_100g']}\n")
    output.write(f"계산일시,{result['calculation_date']}\n")
    output.write("\n")
    
    # 재료 상세
    output.write("재료명,비율(%),사용량(kg),kg당 단가,재료비\n")
    for material in result['materials_detail']:
        output.write(f"{material['name']},{material['percentage']},{material['usage_kg']},{material['price_per_kg']},{material['cost']}\n")
    output.write("\n")
    
    # 팩 단위 원가
    output.write("팩 규격,원가\n")
    for size, cost in result['pack_costs'].items():
        output.write(f"{size},{cost}\n")
    
    # CSV 응답
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv; charset=utf-8-sig',
        headers={
            'Content-Disposition': f'attachment; filename=원재료계산_{result["recipe_name"]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        }
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)