let currentData = null;
let savedRecipes = {};

// 페이지 로드 시 실행
window.onload = function() {
    loadSavedRecipes();
    addMaterial(); // 첫 번째 재료 입력칸 추가
};

// 저장된 레시피 불러오기
function loadSavedRecipes() {
    fetch('/load_recipes')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            savedRecipes = data.recipes;
            displayRecipeList('all');
        }
    })
    .catch(error => console.error('레시피 로드 실패:', error));
}

// 레시피 목록 표시
function displayRecipeList(category) {
    const listContainer = document.getElementById('recipeList');
    listContainer.innerHTML = '';
    
    let recipesToShow = [];
    
    if (category === 'all') {
        // 모든 카테고리의 레시피
        Object.keys(savedRecipes).forEach(cat => {
            savedRecipes[cat].forEach(recipe => {
                recipesToShow.push({...recipe, category: cat});
            });
        });
    } else {
        // 특정 카테고리의 레시피
        recipesToShow = savedRecipes[category] || [];
        recipesToShow = recipesToShow.map(recipe => ({...recipe, category}));
    }
    
    if (recipesToShow.length === 0) {
        listContainer.innerHTML = '<p class="no-recipes">저장된 레시피가 없습니다.</p>';
        return;
    }
    
    // 레시피 카드 생성
    recipesToShow.forEach(recipe => {
        const card = document.createElement('div');
        card.className = 'recipe-card';
        card.innerHTML = `
            <div class="recipe-header">
                <h4>${recipe.recipe_name}</h4>
                <span class="recipe-category">${recipe.category}</span>
            </div>
            <div class="recipe-info">
                <span class="recipe-cost">${recipe.cost_per_100g}원/100g</span>
                <span class="recipe-version">v${recipe.version}</span>
                <span class="recipe-date">${new Date(recipe.created_date).toLocaleDateString()}</span>
            </div>
            <div class="recipe-actions">
                <button onclick="loadRecipe('${recipe.category}', '${recipe.filename}')" class="btn-load">불러오기</button>
                <button onclick="showCostTrend('${recipe.category}', '${recipe.recipe_name}')" class="btn-trend">변동추이</button>
            </div>
        `;
        listContainer.appendChild(card);
    });
}

// 카테고리 탭 전환
function showCategory(category) {
    // 탭 버튼 활성화 상태 변경
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    displayRecipeList(category);
}

// 특정 레시피 불러오기
function loadRecipe(category, filename) {
    fetch(`/load_recipe/${category}/${filename}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const recipe = data.recipe;
            
            // 폼에 데이터 입력
            document.getElementById('recipeName').value = recipe.recipe_name || '';
            document.getElementById('brand').value = recipe.brand || '';
            document.getElementById('category').value = recipe.category || '기타';
            document.getElementById('totalWeight').value = recipe.total_weight || 244;
            document.getElementById('lossRate').value = (recipe.loss_rate * 100) || 22;
            
            // 재료 입력칸 초기화 후 데이터 입력
            document.getElementById('materialsContainer').innerHTML = '';
            recipe.materials.forEach(material => {
                addMaterial(material);
            });
            
            alert('레시피를 불러왔습니다!');
        } else {
            alert('레시피 불러오기 실패: ' + data.error);
        }
    })
    .catch(error => {
        alert('레시피 불러오기 중 오류: ' + error);
    });
}

// 원가 변동 추이 보기
function showCostTrend(category, recipeName) {
    fetch(`/cost_trend/${category}/${recipeName}`)
    .then(response => response.json())
    .then(data => {
        if (data.success && data.trends.length > 0) {
            displayCostTrend(data.trends);
            document.getElementById('costTrend').style.display = 'block';
        } else {
            alert('원가 변동 이력이 없습니다.');
        }
    })
    .catch(error => {
        alert('원가 변동 추이 조회 실패: ' + error);
    });
}

// 원가 변동 추이 표시
function displayCostTrend(trends) {
    const chartContainer = document.getElementById('trendChart');
    
    let html = '<table class="trend-table"><thead><tr><th>날짜</th><th>100g당 원가</th><th>총 재료비</th><th>로스율</th><th>변동률</th></tr></thead><tbody>';
    
    trends.forEach((trend, index) => {
        const date = new Date(trend.date).toLocaleDateString();
        const changeRate = index > 0 ? 
            ((trend.cost_per_100g - trends[index-1].cost_per_100g) / trends[index-1].cost_per_100g * 100).toFixed(1) : 
            0;
        
        const changeClass = changeRate > 0 ? 'increase' : changeRate < 0 ? 'decrease' : '';
        
        html += `
            <tr>
                <td>${date}</td>
                <td>${trend.cost_per_100g}원</td>
                <td>${trend.total_cost.toLocaleString()}원</td>
                <td>${trend.loss_rate}%</td>
                <td class="${changeClass}">${changeRate}%</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    chartContainer.innerHTML = html;
}

// 로스율 입력 방식 전환
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

// 재료 추가 (kg/g 단위만)
function addMaterial(materialData = null) {
    const container = document.getElementById('materialsContainer');
    const materialRow = document.createElement('div');
    materialRow.className = 'material-row';
    
    const data = materialData || { name: '', percentage: 0, price_per_kg: 0 };
    
    materialRow.innerHTML = `
        <input type="text" placeholder="재료명" value="${data.name}" class="material-name">
        <input type="number" placeholder="비율(%)" value="${data.percentage}" step="0.01" class="material-percentage">
        <select class="material-unit">
            <option value="kg">kg</option>
            <option value="g">g</option>
        </select>
        <input type="number" placeholder="단위당 가격" value="${data.price_per_kg || 0}" class="material-price">
        <button onclick="removeMaterial(this)" class="btn-remove">삭제</button>
    `;
    
    container.appendChild(materialRow);
}

// 재료 제거
function removeMaterial(button) {
    button.parentElement.remove();
}

// 재료 데이터 수집
function collectMaterialData() {
    const materials = [];
    const rows = document.querySelectorAll('.material-row');
    
    rows.forEach(row => {
        const name = row.querySelector('.material-name').value;
        const percentage = parseFloat(row.querySelector('.material-percentage').value);
        const unit = row.querySelector('.material-unit').value;
        const price = parseFloat(row.querySelector('.material-price').value);
        
        // kg당 가격으로 변환
        let pricePerKg = price;
        if (unit === 'g') {
            pricePerKg = price * 1000; // g당 가격을 kg당으로 변환
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

// 계산하기
function calculate() {
    const recipeName = document.getElementById('recipeName').value;
    const brand = document.getElementById('brand').value;
    const category = document.getElementById('category').value;
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
    
    if (materials.length === 0) {
        alert('재료를 입력해주세요.');
        return;
    }
    
    currentData = {
        recipe_name: recipeName,
        brand: brand,
        category: category,
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
        document.getElementById('saveBtn').disabled = false;
        document.getElementById('downloadBtn').disabled = false;
    })
    .catch(error => {
        alert('계산 중 오류가 발생했습니다: ' + error);
    });
}

// 결과 표시
function displayResults(data) {
    const resultsSection = document.getElementById('results');
    const resultContent = document.getElementById('resultContent');
    
    let html = `
        <div class="result-summary">
            <h3>📌 요약</h3>
            <p>레시피명: <strong>${data.recipe_name}</strong></p>
            <p>브랜드: <strong>${currentData.brand || '없음'}</strong></p>
            <p>카테고리: <strong>${currentData.category}</strong></p>
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

// 레시피 저장
function saveRecipe() {
    if (!currentData) {
        alert('먼저 계산을 실행해주세요.');
        return;
    }
    
    if (!currentData.recipe_name) {
        alert('제품명을 입력해주세요.');
        return;
    }
    
    fetch('/save_recipe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(currentData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('레시피가 저장되었습니다!');
            loadSavedRecipes(); // 목록 새로고침
        } else {
            alert('저장 실패: ' + data.error);
        }
    })
    .catch(error => {
        alert('저장 중 오류: ' + error);
    });
}

// CSV 다운로드
function downloadCSV() {
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
        a.download = `원재료계산_${currentData.recipe_name}_${new Date().toISOString().slice(0,10)}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        alert('다운로드 중 오류가 발생했습니다: ' + error);
    });
}