<template>
  <div class="panel-section">
    <div v-if="!activeQuestion.isStarted" class="start-guide-box">
      <p class="guide-text">문항을 분석하고 소재를 골라<br>나만의 맞춤 초안을 만들어보세요!</p>
      <button class="start-analysis-btn" @click="handleStart">문항 분석 및 경험 선택하기</button>
    </div>

    <div v-else class="draft-active-content">
      
      <div class="analysis-guide-card">
        <div class="guide-header">
          <span class="ai-stars">✨</span>
          <h3 class="guide-title">AI 문항 분석 가이드라인</h3>
        </div>
        <div class="guide-body">
          <p class="main-strategy">
            이 문항은 <strong>"실무 역량과 문제 해결 능력"</strong>을 강조하는 것이 핵심입니다.
          </p>
          <ul class="strategy-tips">
            <li>과거의 구체적인 수치와 성과를 바탕으로 작성하세요.</li>
            <li>본인이 맡았던 구체적인 역할(Role)을 명확히 드러내세요.</li>
            <li>문제 상황보다는 해결을 위해 노력한 **'과정'**에 집중하세요.</li>
          </ul>
        </div>
      </div>

      <div class="material-section">
        <div class="material-header">
          <p class="material-title">문항에 최적화된 추천 경험 (최대 2개)</p>
          <button class="material-add-btn" @click="$emit('open-modal')">+ 경험 추가</button>
        </div>

        <div class="material-list">
          <div v-for="material in materials" :key="material.id" class="recommend-card">
            <div class="card-top">
              <div class="badge-group">
                <span class="badge recommended">강력 추천</span>
                <span class="badge score">적합도 {{ material.score || 90 }}%</span>
              </div>
              <div 
                class="select-circle" 
                :class="{ active: isSelected(material.id) }"
                @click="toggleMaterial(material.id)"
              ></div>
            </div>

            <h4 class="material-name">{{ material.title }}</h4>
            <p class="material-desc">{{ material.description }}</p>
            
            <div class="card-footer">
              <button class="view-detail-btn">경험 상세 보기 ↗</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="selectedMaterials.length > 0" class="action-footer">
        <button class="generate-btn">이 소재로 초안 생성하기</button>
      </div>

    </div>
  </div>
</template>

<script setup>
const props = defineProps(['activeQuestion', 'materials', 'selectedMaterials'])
const emit = defineEmits(['open-modal', 'update:selectedMaterials'])

// 분석 시작 버튼 핸들러
const handleStart = () => {
  if (props.activeQuestion) {
    props.activeQuestion.isStarted = true;
  }
}

// 소재 선택 여부 확인
const isSelected = (id) => props.selectedMaterials.includes(id)

// 소재 선택 토글
const toggleMaterial = (id) => {
  let updated = [...props.selectedMaterials]
  if (isSelected(id)) {
    updated = updated.filter(i => i !== id)
  } else if (updated.length < 2) {
    updated.push(id)
  }
  emit('update:selectedMaterials', updated)
}
</script>

<style scoped>
.panel-section { display: flex; flex-direction: column; }

/* 시작 가이드 */
.start-guide-box { 
  display: flex; flex-direction: column; align-items: center; justify-content: center; 
  padding: 60px 20px; text-align: center; background: #fff; border-radius: 16px; 
  border: 1px dashed #cbd5e1; margin-top: 20px; 
}
.guide-text { font-size: 14px; color: #64748b; line-height: 1.6; margin-bottom: 20px; }
.start-analysis-btn { background-color: #3b82f6; color: white; border: none; padding: 14px 24px; border-radius: 8px; font-weight: 700; cursor: pointer; }

/* AI 가이드라인 카드 */
.analysis-guide-card {
  background: linear-gradient(135deg, #f8faff 0%, #eff6ff 100%);
  border: 1px solid #dbeafe; border-radius: 16px; padding: 24px; margin-bottom: 24px;
}
.guide-header { display: flex; align-items: center; gap: 8px; margin-bottom: 14px; }
.guide-title { font-size: 16px; font-weight: 800; color: #1e40af; margin: 0; }
.main-strategy { font-size: 14px; color: #1e3a8a; margin-bottom: 12px; line-height: 1.6; }
.strategy-tips { padding-left: 20px; margin: 0; font-size: 13px; color: #3b82f6; }
.strategy-tips li { margin-bottom: 6px; }

/* 경험 추천 영역 */
.material-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.material-title { font-size: 15px; font-weight: 700; color: #1e293b; }
.material-add-btn { background: none; border: none; color: #3b82f6; font-size: 13px; font-weight: 600; cursor: pointer; }

.recommend-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 16px;
  padding: 20px; margin-bottom: 16px; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.recommend-card:hover { border-color: #3b82f6; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08); }

.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.badge-group { display: flex; gap: 6px; }
.badge { padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
.badge.recommended { background: #eff6ff; color: #3b82f6; }
.badge.score { background: #f0fdf4; color: #16a34a; }

/* 원형 체크박스 */
.select-circle {
  width: 24px; height: 24px; border: 2px solid #cbd5e1; border-radius: 50%;
  cursor: pointer; position: relative; transition: all 0.2s;
}
.select-circle.active { background: #3b82f6; border-color: #3b82f6; }
.select-circle.active::after {
  content: '✓'; color: #fff; font-size: 14px; font-weight: 900;
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
}

.material-name { font-size: 16px; font-weight: 700; color: #1e293b; margin: 0 0 8px 0; }
.material-desc { font-size: 13px; color: #64748b; margin-bottom: 14px; line-height: 1.5; }
.card-footer { border-top: 1px solid #f1f5f9; padding-top: 12px; text-align: right; }
.view-detail-btn { background: none; border: none; color: #94a3b8; font-size: 12px; cursor: pointer; }

/* 하단 생성 버튼 */
.action-footer {
  margin-top: 10px; padding: 20px 0; border-top: 1px solid #e2e8f0;
}
.generate-btn {
  width: 100%; padding: 16px; background-color: #1e293b; color: #fff;
  border: none; border-radius: 12px; font-weight: 700; font-size: 15px;
  cursor: pointer; transition: background 0.2s;
}
.generate-btn:hover { background-color: #0f172a; }
</style>