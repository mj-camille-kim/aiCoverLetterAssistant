<template>
  <div class="panel-section">
    <div v-if="!activeQuestion.isStarted" class="start-guide-box">
      <div class="empty-state-icon">🎯</div>
      <p class="guide-text" v-if="!isLoading">문항을 분석하고 경험을 골라<br>나만의 맞춤 초안을 만들어보세요!</p>
      <p class="guide-text loading-text" v-else>문항 맞춤 경험을 찾는 중입니다...</p>
      <button class="start-analysis-btn" :disabled="isLoading" @click="handleStart">
        <span v-if="!isLoading">문항 분석 및 경험 선택하기</span>
        <span v-else class="loader"></span>
      </button>
    </div>

    <div v-else class="draft-active-content">
      <div class="modern-guide-card" v-if="analysisGuide">
        <div class="card-glass-effect"></div>
        <div class="guide-header">
          <div class="ai-icon-wrapper">✨</div>
          <div class="header-text">
            <h3 class="guide-title">문항 분석 가이드라인</h3>
            <p class="guide-subtitle">문항의 의도를 파악한 전략적 가이드입니다</p>
          </div>
        </div>

        <div class="guide-content">
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">문항유형</span>
              <span class="info-value highlight-text">{{ analysisGuide.analysis.q_type }}</span>
            </div>
            <div class="info-divider"></div>
            <div class="info-item">
              <span class="info-label">문항의도</span>
              <div class="intent-tags">
                <span v-for="intent in analysisGuide.analysis.q_intention" :key="intent" class="intent-tag">
                  {{ intent }}
                </span>
              </div>
            </div>
          </div>

          <div class="guideline-section">
            <div class="section-title">
              <span class="dot"></span>
              <h4>작성 가이드라인</h4>
            </div>
            <div class="guideline-box">
              <p class="guideline-text">{{ analysisGuide.guideline }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="material-section">
        <div class="material-header">
          <h4 class="material-title">문항 맞춤 추천 경험 <span>{{ recommendedMaterials.length }}</span></h4>
          <button class="material-add-btn" @click="$emit('open-modal')">경험 직접 추가</button>
        </div>

        <div class="material-grid">
          <div v-for="(material, index) in recommendedMaterials" 
               :key="index" 
               class="modern-recommend-card"
               :class="{ 'selected-card': isSelected(material.title) }">
            
            <div class="card-top">
              <span class="recom-badge" :class="{ 'top-recom': index === 0 }">
                {{ index === 0 ? '✨ 강력 추천' : '적합 소재' }}
              </span>
              <div class="select-checkbox" 
                   :class="{ 'is-active': isSelected(material.title) }"
                   @click="toggleMaterial(material.title)">
                <span class="check-icon">✓</span>
              </div>
            </div>

            <div class="card-body">
              <h5 class="mat-title">{{ material.title }}</h5>
              <p class="mat-keywords">{{ material.keywords }}</p>
            </div>

            <div class="card-footer">
              <button class="detail-link-btn">상세보기</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="selectedMaterials.length > 0" class="action-footer">
        <button class="generate-btn" @click="startGeneration">
          <span>{{ selectedMaterials.length }}개의 소재로 초안 생성하기</span>
          <span class="arrow">→</span>
        </button>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref } from 'vue';
import axios from 'axios';
import bus from '../../util/bus';

const props = defineProps(['activeQuestion', 'userEmail', 'companyPerson', 'jdAnalysis', 'selectedMaterials']);
const emit = defineEmits(['open-modal', 'update:selectedMaterials']);

// 1. 데이터를 담을 변수
const userInfo = JSON.parse(localStorage.getItem("userInfo"));
const email = userInfo?.email || "";
const analysisGuide = ref(null);
const recommendedMaterials = ref([]);
const isLoading = ref(false);


// 2. 분석 시작 및 API 호출 핸들러
const handleStart = async () => {
  isLoading.value = true;

  // 가데이터
  const mockPayload = {
    userEmail: email,
    question: props.activeQuestion?.title || "지원동기를 기술해주십시오.",
    company_person: props.companyPerson || "창의적이고 도전적인 인재상",
    jd_analysis: props.jdAnalysis || "프론트엔드 개발 및 UI/UX 최적화 담당"
  };

  try {
    const response = await axios.post('http://localhost:8000/analyze/guide-and-recommend', mockPayload);

  // try {
  //   const response = await axios.post('http://localhost:8000/analyze/guide-and-recommend', {
  //     userEmail: props.userEmail,
  //     question: props.activeQuestion.title,
  //     company_person: props.companyPerson,
  //     jd_analysis: props.jdAnalysis
  //   });

    // 백엔드 리턴값 저장 (가이드 + 추천 3개)
    analysisGuide.value = response.data.guide;
    recommendedMaterials.value = response.data.recommendations;

    // UI 상태 변경
    if (props.activeQuestion) {
      props.activeQuestion.isStarted = true;
    }
  } catch (error) {
    console.error("분석 실패:", error);
    alert("데이터를 불러오지 못했습니다.");
  } finally {
    isLoading.value = false;
  }
}

// 소재 선택 여부 확인 (title이나 고유 ID를 기준으로 체크)
const isSelected = (title) => props.selectedMaterials.includes(title)

// 소재 선택 토글 (최대 2개)
const toggleMaterial = (title) => {
  let updated = [...props.selectedMaterials]
  if (isSelected(title)) {
    updated = updated.filter(t => t !== title)
  } else if (updated.length < 2) {
    updated.push(title)
  }
  emit('update:selectedMaterials', updated)
}

// 자소서 초안 생성 버튼
const startGeneration = () => {
  const dummyDraft = "지원동기 초안입니다. 본인이 왜 이 포지션에 적합한지 구체적 사례를 통해 강조하겠습니다...";
  // 에디터로 데이터 전송
  bus.emit('generateDraft', dummyDraft);
};

</script>

<style scoped>
/* 폰트 및 기본 설정 */
.panel-section { 
  display: flex; 
  flex-direction: column; 
  font-family: 'Pretendard', -apple-system, sans-serif;
  letter-spacing: -0.01em;
}

/* --- 시작 가이드 및 로딩 상태 --- */
.start-guide-box { 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  justify-content: center; 
  padding: 80px 20px; 
  text-align: center; 
  background: #f8fafc; 
  border-radius: 20px; 
  border: 2px dashed #e2e8f0; 
  margin-top: 20px; 
}

.empty-state-icon { font-size: 48px; margin-bottom: 20px; }

.guide-text { 
  font-size: 15px; 
  color: #475569; 
  line-height: 1.6; 
  margin-bottom: 28px; 
  font-weight: 500;
}

/* 로딩 텍스트 애니메이션 */
.loading-text {
  color: #3b82f6;
  font-weight: 600;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.start-analysis-btn { 
  background-color: #3b82f6; 
  color: white; 
  border: none; 
  width: 220px;
  height: 52px;
  border-radius: 12px; 
  font-weight: 700; 
  font-size: 15px;
  cursor: pointer; 
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.start-analysis-btn:hover:not(:disabled) {
  background-color: #2563eb;
  transform: translateY(-1px);
}

.start-analysis-btn:disabled {
  background-color: #cbd5e1;
  cursor: not-allowed;
  box-shadow: none;
}

/* 버튼 내 스피너 */
.loader {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 0.8s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* --- AI 분석 카드 섹션 --- */
.modern-guide-card {
  position: relative;
  background: #ffffff;
  border-radius: 24px;
  border: 1px solid #eef2f6;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  margin-bottom: 32px;
}

.card-glass-effect {
  position: absolute;
  top: 0; left: 0; right: 0; height: 5px;
  background: linear-gradient(90deg, #3b82f6 0%, #2dd4bf 100%);
}

.guide-header {
  display: flex;
  align-items: center;
  padding: 28px 24px 20px;
  gap: 16px;
}

.ai-icon-wrapper {
  width: 44px; height: 44px;
  background: #eff6ff;
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center; font-size: 20px;
}

.guide-title { font-size: 1.1rem; font-weight: 800; color: #0f172a; margin: 0; }
.guide-subtitle { font-size: 0.85rem; color: #64748b; margin-top: 3px; }

.info-row {
  display: flex; background: #f8fafc; margin: 0 24px; padding: 18px;
  border-radius: 16px; gap: 24px;
}

.info-item { display: flex; flex-direction: column; gap: 6px; flex: 1; }
.info-label { font-size: 0.7rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; }
.info-value { font-size: 0.95rem; font-weight: 700; color: #1e293b; }
.highlight-text { color: #3b82f6; }

.intent-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.intent-tag {
  background: #fff; border: 1px solid #e2e8f0; padding: 3px 10px;
  border-radius: 8px; font-size: 0.8rem; color: #475569; font-weight: 600;
}

.info-divider { width: 1px; background: #e2e8f0; }

.guideline-section { padding: 24px; }
.section-title { display: flex; align-items: center; gap: 8px; margin-bottom: 14px; }
.section-title h4 { font-size: 0.95rem; font-weight: 700; color: #1e293b; margin: 0; }
.section-title .dot { width: 6px; height: 6px; background: #3b82f6; border-radius: 50%; }

.guideline-box {
  background: #fafafa; padding: 20px; border-radius: 16px;
  border-left: 4px solid #3b82f6;
}

.guideline-text {
  font-size: 0.95rem; line-height: 1.7; color: #334155; margin: 0;
  white-space: pre-wrap; word-break: keep-all;
}

/* --- 추천 경험 섹션 --- */
.material-header { 
  display: flex; justify-content: space-between; align-items: center; 
  padding: 0 4px; margin-bottom: 16px; 
}
.material-title { font-size: 16px; font-weight: 800; color: #0f172a; }
.material-title span { color: #3b82f6; margin-left: 4px; }
.material-add-btn { 
  background: #fff; border: 1px solid #e2e8f0; color: #475569; 
  padding: 6px 12px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; 
}

.modern-recommend-card {
  background: #fff; border: 1.5px solid #e2e8f0; border-radius: 20px;
  padding: 24px; margin-bottom: 16px; transition: all 0.25s ease;
}

.modern-recommend-card:hover { 
  border-color: #3b82f6; 
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.06);
}

.selected-card { 
  border-color: #3b82f6; 
  background: #f5f9ff; 
}

.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.recom-badge { 
  font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 8px; 
  background: #f1f5f9; color: #64748b; 
}
.top-recom { background: #eff6ff; color: #3b82f6; }

.select-checkbox {
  width: 26px; height: 26px; border: 2.5px solid #cbd5e1; border-radius: 50%;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  background: #fff; transition: all 0.2s;
}

.select-checkbox.is-active {
  background: #3b82f6; border-color: #3b82f6; color: #fff;
}

.mat-title { font-size: 17px; font-weight: 800; color: #1e293b; margin: 0 0 8px 0; }
.mat-keywords { font-size: 13.5px; color: #64748b; font-weight: 500; }

.card-footer { margin-top: 18px; padding-top: 14px; border-top: 1px solid #f1f5f9; }
.detail-link-btn { background: none; border: none; color: #94a3b8; font-size: 12px; font-weight: 600; cursor: pointer; }
.detail-link-btn:hover { color: #3b82f6; }

/* --- 하단 생성 버튼 --- */
.action-footer {
  position: sticky; bottom: 0; background: #fff;
  padding: 20px 0; border-top: 1px solid #f1f5f9;
}

.generate-btn {
  width: 100%; padding: 18px; background: #0f172a; color: #fff;
  border: none; border-radius: 16px; font-weight: 700; font-size: 16px;
  cursor: pointer; display: flex; justify-content: center; align-items: center; gap: 10px;
  transition: all 0.2s;
}

.generate-btn:hover { background: #1e293b; transform: translateY(-1px); }
.generate-btn .arrow { font-size: 18px; transition: transform 0.2s; }
.generate-btn:hover .arrow { transform: translateX(4px); }
</style>