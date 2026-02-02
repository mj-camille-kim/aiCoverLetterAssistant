<template>
  <div class="upload-page-wrapper">
    <Sidebar />
    
    <main class="main-content">
      <header class="page-header">
        <h1 class="page-title">경험 업로드</h1>
        <p class="page-subtitle">자기소개서 파일을 첨부하거나 경험을 직접 입력하여 AI 분석을 시작하세요.</p>
      </header>

      <section class="upload-section">
        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>경험 저장 중입니다...</p>
        </div>

        <div v-else class="action-group">
          <div class="upload-item" @click="triggerFileInput">
            <div class="icon-box">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="12" y1="18" x2="12" y2="12"></line>
                <polyline points="9 15 12 12 15 15"></polyline>
              </svg>
            </div>
            <div class="item-text">
              <h3>PDF 파일 첨부</h3>
              <p>작성해둔 자기소개서에서 경험을 추출합니다.</p>
              <span v-if="fileName" class="file-status">선택됨: {{ fileName }}</span>
            </div>
            <button class="btn-primary">파일 선택</button>
            <input type="file" ref="fileInput" @change="handleFileChange" accept=".pdf" style="display: none;" />
          </div>

          <div class="upload-item" @click="isModalOpen = true">
            <div class="icon-box">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
            </div>
            <div class="item-text">
              <h3>직접 입력하기</h3>
              <p>STARI 기법에 맞춰 경험을 새로 작성합니다.</p>
            </div>
            <button class="btn-secondary">입력창 열기</button>
          </div>

          <div class="upload-item" @click="router.push('/editor')">
          <div class="icon-box highlight">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 19l7-7 3 3-7 7-3-3z"></path>
              <path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"></path>
              <path d="M2 2l7.5 1.5"></path>
              <path d="M7.5 24l-3-3"></path>
            </svg>
          </div>
          <div class="item-text">
            <h3>바로 초안 작성</h3>
            <p>경험 정리 없이 AI와 함께 자소서를 씁니다.</p>
          </div>
          <button class="btn-outline">작성 시작</button>
        </div>
        </div>
      </section>

      <section v-if="analysisResults" class="result-section">
        <div class="section-header">
          <h2>분석 완료 데이터</h2>
          <button @click="analysisResults = null" class="btn-close">데이터 초기화</button>
        </div>
        <div class="result-display">
          <pre class="json-viewer">{{ JSON.stringify(analysisResults, null, 2) }}</pre>
        </div>
      </section>

      <ExperienceModal
        v-if="isModalOpen" 
        @close="isModalOpen = false" 
        @submit="handleExperienceSubmit"
      />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import ExperienceModal from '../components/ExpModal.vue'; 
import Sidebar from '../components/Sidebar.vue';

const router = useRouter();
const fileInput = ref(null);
const fileName = ref('');
const isModalOpen = ref(false);

// 상태 변수 정의 (변수명 일치 확인)
const isLoading = ref(false);
const analysisResults = ref(null);

const triggerFileInput = () => {
  fileInput.value.click();
};

// PDF 업로드 함수 업데이트
const handleFileChange = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const userInfo = JSON.parse(localStorage.getItem("userInfo"));
  const email = userInfo?.email || "";
  fileName.value = file.name;
  isLoading.value = true;
  analysisResults.value = null;

  const formData = new FormData();
  formData.append('file', file);
  formData.append('userEmail', email);

  try {
    const response = await axios.post('http://localhost:8000/analyze/pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    analysisResults.value = response.data;
    if (!!analysisResults.value) {
      await axios.post("/api/insertExp", {email: email, data: analysisResults.value});
    }
  } catch (error) {
    console.error("PDF 분석 실패:", error);
    alert("파일 분석 중 오류가 발생했습니다.");
  } finally {
    isLoading.value = false;
  }
};

// 직접 입력 함수 업데이트
const handleExperienceSubmit = async (experienceList) => {
  isModalOpen.value = false;
  isLoading.value = true;
  analysisResults.value = null;

  try {
    const userInfo = JSON.parse(localStorage.getItem("userInfo"));
    const email = userInfo?.email || "";
    const response = await axios.post('http://localhost:8000/analyze/json', {userEmail: email, data: experienceList});
    analysisResults.value = response.data;
    if (!!analysisResults.value) {
      await axios.post("/api/insertExp", {email: email, data: analysisResults.value});
    }
  } catch (error) {
    console.error("복수 데이터 전송 실패:", error);
    alert("데이터 분석 중 오류가 발생했습니다.");
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
/* 전체 레이아웃 세팅 */
.upload-page-wrapper {
  display: flex;
  min-height: 100vh;
  background-color: #f9f9fb; /* 아주 연한 배경색으로 카드 강조 */
}

.main-content {
  flex: 1;
  padding: 60px 50px;
  max-width: 1400px; /* 3개 카드가 충분히 펼쳐지도록 확장 */
  margin: 0 auto;
}

/* 헤더 스타일 */
.page-header {
  margin-bottom: 50px;
  text-align: left;
}
.page-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: #111;
  margin-bottom: 12px;
}
.page-subtitle {
  color: #666;
  font-size: 1.1rem;
}

/* 3열 카드 그리드 시스템 */
.upload-section {
  margin-bottom: 60px;
}
.action-group {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 정확히 3등분 */
  gap: 24px; /* 카드 사이 간격 */
}

/* 카드 아이템 스타일 개선 */
.upload-item {
  display: flex;
  flex-direction: column; /* 세로 방향으로 요소 나열 */
  align-items: center;
  justify-content: space-between; /* 위-중간-아래 간격 최적화 */
  padding: 50px 30px; /* 카드가 더 커 보이도록 패딩 증가 */
  background: white;
  border: 1px solid #eee;
  border-radius: 24px; /* 더 부드러운 라운딩 */
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  min-height: 400px; /* 카드의 세로 크기를 크게 고정 */
  text-align: center;
}

.upload-item:hover {
  border-color: #0000FF;
  transform: translateY(-10px); /* 더 역동적인 호버 효과 */
  box-shadow: 0 20px 40px rgba(0,0,255,0.08);
}

/* 아이콘 박스 크기 확대 */
.icon-box {
  width: 80px;
  height: 80px;
  background: #f0f3ff;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 25px;
}

.icon-box.highlight {
  background: #EBF5FF; /* 세 번째 카드용 포인트 컬러 */
}

.icon { width: 36px; height: 36px; color: #0000FF; }

/* 텍스트 영역 */
.item-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.item-text h3 {
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 12px;
  color: #111;
}

.item-text p {
  font-size: 1rem;
  color: #888;
  line-height: 1.6;
  word-break: keep-all; /* 한글 가독성 향상 */
}

.file-status {
  display: block;
  margin-top: 12px;
  color: #0000FF;
  font-weight: bold;
  font-size: 0.9rem;
}

/* 버튼 스타일: 카드 너비에 맞춰 확장 */
.btn-primary, .btn-secondary, .btn-outline {
  width: 100%;
  margin-top: 30px;
  padding: 14px 0;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  /* 작성 시작 버튼의 핵심 스타일 */
  background-color: white !important;
  color: #0000FF !important;
  border: 2px solid #0000FF !important;
}

/* 마우스를 올렸을 때 효과 (살짝 연한 파란색 배경) */
.btn-primary:hover, .btn-secondary:hover, .btn-outline:hover {
  background-color: #f0f3ff !important;
  box-shadow: 0 4px 12px rgba(0, 0, 255, 0.1);
}

/* 활성화(클릭) 시 효과 */
.btn-primary:active, .btn-secondary:active, .btn-outline:active {
  transform: scale(0.98);
}

/* 결과창 스타일 */
.result-section {
  margin-top: 40px;
  border-top: 2px solid #eee;
  padding-top: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.json-viewer {
  background: #1a1a1a;
  color: #74f074;
  padding: 30px;
  border-radius: 16px;
  font-family: 'Fira Code', monospace;
  font-size: 0.9rem;
  overflow-x: auto;
  line-height: 1.6;
}

.btn-close { 
  background: none; 
  border: 1px solid #ff4d4f; 
  color: #ff4d4f; 
  padding: 8px 20px; 
  border-radius: 8px; 
  cursor: pointer; 
}

/* 로딩 애니메이션 */
.loading-state { text-align: center; padding: 100px 0; }
.spinner {
  width: 60px;
  height: 60px;
  border: 6px solid #f3f3f3;
  border-top: 6px solid #0000FF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 25px;
}

@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* 반응형 처리 (화면이 작아지면 세로로 정렬) */
@media (max-width: 1024px) {
  .action-group {
    grid-template-columns: 1fr;
    max-width: 500px;
    margin: 0 auto;
  }
  .upload-item {
    min-height: auto;
  }
}
</style>