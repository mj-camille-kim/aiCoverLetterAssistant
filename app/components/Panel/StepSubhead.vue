<template>
  <div class="subhead-section">
    <div class="subhead-list">
      <div v-if="activeQuestion.isSubheadStarted && !activeQuestion.subheads" class="loading-container">
        <div class="spinner"></div>
        <p class="loading-text">본문을 분석하여 최적의 소제목을 뽑아내고 있습니다...</p>
      </div>

      <template v-else-if="activeQuestion.subheads">
        <div v-for="(item, index) in activeQuestion.subheads" :key="item.id" class="subhead-card">
          <div class="card-tag">추천 {{ index + 1 }}</div>
          <p class="subhead-text">"{{ item.text }}"</p>
          <button class="copy-btn" @click="copyToClipboard(item.text)">복사하기</button>
        </div>
      </template>

      <div v-else class="empty-state">
        <p>본문 작성이 완료되었다면<br>소제목 추천을 받아보세요!</p>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps(['activeQuestion'])

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text);
  alert('소제목이 클립보드에 복사되었습니다!');
}
</script>

<style scoped>
.subhead-list { display: flex; flex-direction: column; gap: 16px; padding: 10px 0; }
.subhead-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
  padding: 20px; position: relative; transition: transform 0.2s;
}
.subhead-card:hover { transform: translateY(-2px); border-color: #6366f1; }
.card-tag { font-size: 11px; color: #6366f1; font-weight: 700; margin-bottom: 8px; }
.subhead-text { font-size: 16px; font-weight: 700; color: #1e293b; line-height: 1.5; margin-bottom: 15px; }
.copy-btn { 
  width: 100%; padding: 8px; background: #f8fafc; border: 1px solid #e2e8f0;
  border-radius: 6px; font-size: 13px; cursor: pointer; color: #64748b;
}
.copy-btn:hover { background: #6366f1; color: white; }

/* 로딩/비어있음 스타일은 피드백과 동일하게 구성 */
.loading-container { text-align: center; padding: 100px 0; }
.spinner { width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #6366f1; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-text, .empty-state { color: #94a3b8; font-size: 14px; text-align: center; line-height: 1.6; }
</style>