<template>
  <div class="container">
    <Sidebar />
    <main class="main-content">
      <header class="top-header">
        <button class="help-btn">?</button>
      </header>

      <div class="content-body">
        <h1 class="main-title">서비스이름</h1>

        <div class="input-container">
          <input
            v-model="jobLink"
            type="text"
            placeholder="채용 공고 링크를 입력해주세요."
            class="url-input"
            :disabled="isLoading"
          />
          <button
            class="search-submit"
            :disabled="isLoading"
            @click="openJobModal"
          >
            {{ isLoading ? '…' : '↑' }}
          </button>
        </div>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <p v-else class="notice">링크를 입력하면 경험 유무를 확인한 뒤 보고서를 만들거나 업로드 페이지로 이동합니다.</p>
      </div>
    </main>

    <!-- 직무/경력 입력 모달 -->
    <div v-if="isJobModalOpen" class="modal-overlay" @click.self="isJobModalOpen = false">
      <div class="modal-box">
        <header class="modal-header">
          <h2>직무 · 경력 입력</h2>
          <button type="button" class="modal-close" @click="isJobModalOpen = false">&times;</button>
        </header>
        <div class="modal-body">
          <div class="modal-field">
            <label>직무</label>
            <input
              v-model="selectedJob"
              type="text"
              placeholder="예: 백엔드 개발자"
              class="modal-input"
            />
          </div>
          <div class="modal-field">
            <label>경력</label>
            <input
              v-model="experienceLevel"
              type="text"
              placeholder="예: 신입, 1-3년"
              class="modal-input"
            />
          </div>
        </div>
        <footer class="modal-footer">
          <button type="button" class="btn-cancel" @click="isJobModalOpen = false">취소</button>
          <button type="button" class="btn-confirm" @click="confirmAndRequest">보고서 요청</button>
        </footer>
      </div>
    </div>

    <!-- 보고서 생성 로딩 화면 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-box">
        <div class="loading-spinner"></div>
        <p class="loading-title">보고서 생성 중입니다</p>
        <p class="loading-desc">최대 5분 정도 소요될 수 있습니다.</p>
      </div>
    </div>

    <ReportModal
      v-if="reportHtml"
      :report-html="reportHtml"
      @close="reportHtml = ''"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Sidebar from '../components/Sidebar.vue';
import ReportModal from '../components/ReportModal.vue';
import { getCookie } from '../util/cookieUtils';
import { useUserStore } from '../stores/user';
import { fetchAnalysisReport } from '../api/analyze';

const router = useRouter();
const jobLink = ref('');
const selectedJob = ref('');
const experienceLevel = ref('신입');
const userStore = useUserStore();
const isLoading = ref(false);
const errorMessage = ref('');
const reportHtml = ref('');
const isJobModalOpen = ref(false);

onMounted(() => {
  const token = getCookie('accessToken');
  if (!token) {
    router.push('/login');
  }
});

const openJobModal = () => {
  const link = jobLink.value?.trim();
  if (!link) {
    alert('채용 공고 링크를 입력해주세요!');
    return;
  }
  const userEmail = userStore.userEmail || JSON.parse(localStorage.getItem('userInfo') || '{}')?.email;
  if (!userEmail) {
    alert('로그인 정보가 없습니다. 다시 로그인해 주세요.');
    return;
  }
  isJobModalOpen.value = true;
};

const confirmAndRequest = async () => {
  isJobModalOpen.value = false;
  const link = jobLink.value?.trim();
  if (!link) return;

  const userEmail = userStore.userEmail || JSON.parse(localStorage.getItem('userInfo') || '{}')?.email;
  if (!userEmail) return;

  isLoading.value = true;
  errorMessage.value = '';

  try {
    const { data } = await axios.post('/api/getUserExp', { userEmail });
    const experiences = data?.data ?? [];

    if (!Array.isArray(experiences) || experiences.length === 0) {
      router.push('/upload');
      return;
    }

    const html = await fetchAnalysisReport(
      {
        targetUrl: link,
        selectedJob: selectedJob.value?.trim() || '',
        experienceLevel: experienceLevel.value?.trim() || '신입'
      },
      { maxPollTimeMs: 5 * 60 * 1000, pollIntervalMs: 60 * 1000 }
    );
    reportHtml.value = html;
    localStorage.setItem('analyzedReportHtml', html);
    router.push('/editor');
  } catch (err) {
    errorMessage.value = err.response?.data?.message || err.message || '처리 중 오류가 발생했습니다.';
    console.error(err);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
/* 전체 레이아웃 */
.container {
  display: flex;
  height: 100vh;
  width: 100vw;
  font-family: 'Pretendard', sans-serif;
  background-color: #ffffff;
}

/* 메인 컨텐츠 영역 (가운데 정렬) */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  transition: margin 0.3s ease;
}

.top-header {
  height: 80px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding-right: 40px;
}

.help-btn {
  width: 40px;
  height: 40px;
  background-color: #212529;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
}

.content-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center; /* 가운데 정렬 */
  padding-bottom: 10vh; /* 하단 쏠림 방지 및 위치 조절 */
}

.main-title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 60px;
  letter-spacing: -2px;
}

/* 입력창 스타일 */
.input-container {
  width: 100%;
  max-width: 700px;
  position: relative;
  display: flex;
  align-items: center;
}

/* 직무/경력 모달 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9998;
}

.modal-box {
  background: #fff;
  border-radius: 16px;
  min-width: 360px;
  max-width: 90vw;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

.modal-close {
  background: none;
  border: none;
  font-size: 28px;
  color: #94a3b8;
  cursor: pointer;
  line-height: 1;
  padding: 0 4px;
}

.modal-close:hover {
  color: #64748b;
}

.modal-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.modal-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.modal-field label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #475569;
}

.modal-input {
  padding: 12px 16px;
  font-size: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  outline: none;
  transition: border-color 0.2s;
}

.modal-input:focus {
  border-color: #339af0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #eee;
}

.btn-cancel {
  padding: 10px 20px;
  border: 1px solid #e2e8f0;
  background: #fff;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  color: #64748b;
}

.btn-cancel:hover {
  background: #f8fafc;
}

.btn-confirm {
  padding: 10px 20px;
  border: none;
  background: #339af0;
  color: #fff;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.btn-confirm:hover {
  background: #228be6;
}

/* 보고서 생성 로딩 화면 */
.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-box {
  text-align: center;
  padding: 48px;
}

.loading-spinner {
  width: 56px;
  height: 56px;
  border: 4px solid #e2e8f0;
  border-top-color: #339af0;
  border-radius: 50%;
  animation: loading-spin 0.9s linear infinite;
  margin: 0 auto 24px;
}

@keyframes loading-spin {
  to { transform: rotate(360deg); }
}

.loading-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px;
}

.loading-desc {
  font-size: 0.95rem;
  color: #64748b;
  margin: 0;
}

.url-input {
  width: 100%;
  padding: 20px 30px;
  font-size: 1.1rem;
  border: 2px solid #f1f3f5;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  outline: none;
  transition: border-color 0.2s;
}

.url-input:focus {
  border-color: #339af0;
}

.url-input:disabled {
  opacity: 0.7;
}

.search-submit {
  position: absolute;
  right: 15px;
  width: 45px;
  height: 45px;
  background-color: #339af0;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.5rem;
  cursor: pointer;
  transition: background 0.2s;
}

.search-submit:hover:not(:disabled) {
  background-color: #228be6;
}

.search-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.notice {
  margin-top: 20px;
  color: #adb5bd;
  font-size: 0.9rem;
}

.error-message {
  margin-top: 20px;
  color: #dc2626;
  font-size: 0.9rem;
}
</style>