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

  fileName.value = file.name;
  isLoading.value = true;
  analysisResults.value = null;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post('http://localhost:8000/analyze/pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    analysisResults.value = response.data;
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
    const response = await axios.post('http://localhost:8000/analyze/json', experienceList);
    analysisResults.value = response.data;
  } catch (error) {
    console.error("복수 데이터 전송 실패:", error);
    alert("데이터 분석 중 오류가 발생했습니다.");
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.upload-page-wrapper {
  display: flex;
  min-height: 100vh;
  background-color: #fcfcfc;
}

.main-content {
  flex: 1;
  padding: 60px 80px;
  max-width: 1200px;
}

/* 헤더 스타일 */
.page-header {
  margin-bottom: 50px;
}
.page-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: #111;
  margin-bottom: 10px;
}
.page-subtitle {
  color: #666;
  font-size: 1.1rem;
}

/* 업로드 아이템 스타일 (카드 형태 탈피) */
.upload-section {
  margin-bottom: 60px;
}
.action-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}
.upload-item {
  display: flex;
  align-items: center;
  padding: 30px;
  background: white;
  border: 1px solid #eee;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}
.upload-item:hover {
  border-color: #0000FF;
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.05);
}
.icon-box {
  width: 60px;
  height: 60px;
  background: #f0f3ff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
}
.icon { width: 30px; height: 30px; color: #0000FF; }
.item-text { flex: 1; text-align: left; }
.item-text h3 { font-size: 1.2rem; margin-bottom: 5px; }
.item-text p { font-size: 0.95rem; color: #888; }
.file-status { display: block; margin-top: 8px; color: #0000FF; font-weight: bold; font-size: 0.85rem; }

/* 버튼 스타일 */
.btn-primary { background: #0000FF; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.btn-secondary { background: white; color: #333; border: 1px solid #ddd; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }

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
  color: #74f074; /* 터미널 느낌의 연두색 */
  padding: 30px;
  border-radius: 16px;
  font-family: 'Fira Code', monospace;
  font-size: 0.9rem;
  overflow-x: auto;
  line-height: 1.6;
}
.btn-close { background: none; border: 1px solid #ff4d4f; color: #ff4d4f; padding: 5px 15px; border-radius: 6px; cursor: pointer; }

/* 로딩 애니메이션 */
.loading-state { text-align: center; padding: 50px; }
.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #0000FF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>