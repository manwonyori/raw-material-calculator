from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from datetime import datetime
import io
import json
import os

app = Flask(__name__)

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

@app.route('/download_excel', methods=['POST'])
def download_excel():
    data = request.json
    calculator = RawMaterialCalculator()
    result = calculator.calculate_cost(data)
    
    # 엑셀 파일 생성
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # 요약 시트
        summary_df = pd.DataFrame([{
            '레시피명': result['recipe_name'],
            '총 투입량(kg)': result['total_input_kg'],
            '로스율(%)': result['loss_rate'],
            '실제 생산량(kg)': result['actual_production_kg'],
            '총 재료비': f"{result['total_material_cost']:,}원",
            'g당 원가': f"{result['cost_per_g']}원",
            '100g당 원가': f"{result['cost_per_100g']}원",
            '계산일시': result['calculation_date']
        }])
        summary_df.to_excel(writer, sheet_name='요약', index=False)
        
        # 재료 상세 시트
        materials_df = pd.DataFrame(result['materials_detail'])
        materials_df.to_excel(writer, sheet_name='재료상세', index=False)
        
        # 팩 단위 원가 시트
        pack_df = pd.DataFrame([result['pack_costs']])
        pack_df.to_excel(writer, sheet_name='팩단위원가', index=False)
        
        # 컬럼 너비 조정
        workbook = writer.book
        for sheet_name in ['요약', '재료상세', '팩단위원가']:
            worksheet = writer.sheets[sheet_name]
            worksheet.set_column('A:H', 15)
    
    output.seek(0)
    
    filename = f"원재료계산_{result['recipe_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)