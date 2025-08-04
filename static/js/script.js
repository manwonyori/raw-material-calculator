// 초기 토마토소스 재료 데이터
const initialMaterials = [
    { name: '농축토마토', percentage: 53.18, price_per_kg: 3654, unit: '통', unit_weight: 850, unit_price: 3200 },
    { name: '간양파', percentage: 18.41, price_per_kg: 1500, unit: 'kg', unit_weight: 1000, unit_price: 1500 },
    { name: '베이컨류', percentage: 8.18, price_per_kg: 9950, unit: '박스', unit_weight: 5000, unit_price: 49750 },
    { name: '다진마늘', percentage: 0.82, price_per_kg: 2000, unit: 'kg', unit_weight: 1000, unit_price: 2000 },
    { name: '식용유', percentage: 1.23, price_per_kg: 2500, unit: 'kg', unit_weight: 1000, unit_price: 2500 },
    { name: '다진돼지고기', percentage: 10.23, price_per_kg: 5500, unit: 'kg', unit_weight: 1000, unit_price: 5500 },
    { name: '설탕', percentage: 2.29, price_per_kg: 1653, unit: 'kg', unit_weight: 1000, unit_price: 1653 },
    { name: '다진소고기', percentage: 1.02, price_per_kg: 10000, unit: 'kg', unit_weight: 1000, unit_price: 10000 },
    { name: '오레가노럽드', percentage: 0.21, price_per_kg: 15000, unit: 'g', unit_weight: 100, unit_price: 1500 },
    { name: '바질럽드', percentage: 0.15, price_per_kg: 9000, unit: 'g', unit_weight: 100, unit_price: 900 },
    { name: '치킨스톡분말', percentage: 0.18, price_per_kg: 6029, unit: 'kg', unit_weight: 1000, unit_price: 6029 },
    { name: '원계수잎분말', percentage: 0.01, price_per_kg: 16500, unit: 'g', unit_weight: 100, unit_price: 1650 }
];

let currentData = null;

// 페이지 로드 시 초기 재료 추가
window.onload = function() {
    initialMaterials.forEach(material => {
        addMaterial(material);
    });
};

function toggleLossInput() {
    const type = document.getElementById('lossRateType').value;
    const percentageInput = document.getElementById('lossPercentageInput');
    const productionInput = document.getElementById('actualProductionInput');
    
    if (type === 'percentage') {
        percentageInput.style.display = 'block';
        productionInput.style.display = 'none';
    } else {
        percentageInput.style.display = 'none';
        productionInput.style.display = 'block';
    }
}

function addMaterial(materialData = null) {
    const container = document.getElementById('materialsContainer');
    const materialRow = document.createElement('div');
    materialRow.className = 'material-row';
    
    const data = materialData || { name: '', percentage: 0, price_per_kg: 0, unit: 'kg', unit_weight: 1000, unit_price: 0 };
    
    materialRow.innerHTML = `
        <input type="text" placeholder="재료명" value="${data.name}" class="material-name">
        <input type="number" placeholder="비율(%)" value="${data.percentage}" step="0.01" class="material-percentage">
        <select class="material-unit" onchange="updateUnitPrice(this)">
            <option value="kg" ${data.unit === 'kg' ? 'selected' : ''}>kg</option>
            <option value="g" ${data.unit === 'g' ? 'selected' : ''}>g</option>
            <option value="통" ${data.unit === '통' ? 'selected' : ''}>통</option>
            <option value="박스" ${data.unit === '박스' ? 'selected' : ''}>박스</option>
            <option value="봉" ${data.unit === '봉' ? 'selected' : ''}>봉</option>
        </select>
        <input type="number" placeholder="단위당 가격" value="${data.unit_price}" class="material-unit-price">
        <button onclick="removeMaterial(this)" class="btn-remove">삭제</button>
    `;
    
    container.appendChild(materialRow);
}

function removeMaterial(button) {
    button.parentElement.remove();
}

function updateUnitPrice(select) {
    // 단위 변경 시 가격 재계산 로직 (필요시 구현)
}

function collectMaterialData() {
    const materials = [];
    const rows = document.querySelectorAll('.material-row');
    
    rows.forEach(row => {
        const name = row.querySelector('.material-name').value;
        const percentage = parseFloat(row.querySelector('.material-percentage').value);
        const unit = row.querySelector('.material-unit').value;
        const unitPrice = parseFloat(row.querySelector('.material-unit-price').value);
        
        // kg당 가격 계산 (단위 변환)
        let pricePerKg = unitPrice;
        if (unit === 'g') {
            pricePerKg = unitPrice * 10; // 100g 기준이므로
        } else if (unit === '통') {
            pricePerKg = (unitPrice / 0.85); // 850g 기준
        } else if (unit === '박스') {
            pricePerKg = (unitPrice / 5); // 5kg 기준
        }
        
        if (name && percentage > 0) {
            materials.push({
                name: name,
                percentage: percentage,
                price_per_kg: pricePerKg
            });
        }
    });
    
    return materials;
}

function calculate() {
    const recipeName = document.getElementById('recipeName').value;
    const totalWeight = parseFloat(document.getElementById('totalWeight').value);
    const lossRateType = document.getElementById('lossRateType').value;
    
    let lossRate;
    if (lossRateType === 'percentage') {
        lossRate = parseFloat(document.getElementById('lossRate').value) / 100;
    } else {
        const actualProduction = parseFloat(document.getElementById('actualProduction').value);
        lossRate = 1 - (actualProduction / totalWeight);
    }
    
    const materials = collectMaterialData();
    
    currentData = {
        recipe_name: recipeName,
        total_weight: totalWeight,
        loss_rate: lossRate,
        materials: materials
    };
    
    fetch('/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(currentData)
    })
    .then(response => response.json())
    .then(data => {
        displayResults(data);
        document.getElementById('downloadBtn').disabled = false;
    })
    .catch(error => {
        alert('계산 중 오류가 발생했습니다: ' + error);
    });
}

function displayResults(data) {
    const resultsSection = document.getElementById('results');
    const resultContent = document.getElementById('resultContent');
    
    let html = `
        <div class="result-summary">
            <h3>📌 요약</h3>
            <p>레시피명: <strong>${data.recipe_name}</strong></p>
            <p>총 투입량: ${data.total_input_kg}kg</p>
            <p>로스율: ${data.loss_rate}%</p>
            <p>실제 생산량: ${data.actual_production_kg}kg</p>
            <p>총 재료비: <span class="highlight">${data.total_material_cost.toLocaleString()}원</span></p>
            <p>100g당 원가: <span class="highlight">${data.cost_per_100g}원</span></p>
        </div>
        
        <h3>📦 재료별 상세</h3>
        <table>
            <thead>
                <tr>
                    <th>재료명</th>
                    <th>비율(%)</th>
                    <th>사용량(kg)</th>
                    <th>kg당 단가</th>
                    <th>재료비</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.materials_detail.forEach(material => {
        html += `
            <tr>
                <td>${material.name}</td>
                <td>${material.percentage}%</td>
                <td>${material.usage_kg}kg</td>
                <td>${material.price_per_kg.toLocaleString()}원</td>
                <td>${material.cost.toLocaleString()}원</td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
        
        <h3>🏷️ 팩 단위별 원가</h3>
        <div class="pack-costs">
    `;
    
    for (const [size, cost] of Object.entries(data.pack_costs)) {
        html += `
            <div class="pack-item">
                <div class="size">${size}</div>
                <div class="price">${cost.toLocaleString()}원</div>
            </div>
        `;
    }
    
    html += '</div>';
    
    resultContent.innerHTML = html;
    resultsSection.style.display = 'block';
}

function downloadExcel() {
    if (!currentData) {
        alert('먼저 계산을 실행해주세요.');
        return;
    }
    
    fetch('/download_excel', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(currentData)
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `원재료계산_${currentData.recipe_name}_${new Date().toISOString().slice(0,10)}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        alert('다운로드 중 오류가 발생했습니다: ' + error);
    });
}