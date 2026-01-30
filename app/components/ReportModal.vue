<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content report-size">
      <header class="modal-header">
        <div class="header-left">
          <span class="report-icon">📊</span>
          <h2>기업 상세 분석 리포트</h2>
        </div>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </header>

      <div class="modal-body report-body">
        <div v-if="reportHtml" v-html="reportHtml"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps(['reportHtml'])
defineEmits(['close'])
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.6); display: flex; align-items: center; justify-content: center; z-index: 9999;
}
.modal-content.report-size {
  /* 너비와 높이를 화면의 80%로 설정 */
  width: 80vw; 
  height: 80vh; 
  
  background: #fff; 
  border-radius: 20px; 
  display: flex; 
  flex-direction: column; 
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2); /* 좀 더 입체감 있는 그림자 추가 */
}

.modal-header { padding: 20px 30px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; gap: 10px; }
.report-icon { font-size: 24px; }
.close-btn { background: none; border: none; font-size: 30px; cursor: pointer; color: #999; }

/* 스크롤바 커스터마이징 */
.modal-body::-webkit-scrollbar {
  width: 8px;
}

.report-section { margin-bottom: 30px; }
.report-section h3 { color: #1d4ed8; font-size: 18px; margin-bottom: 10px; border-left: 4px solid #1d4ed8; padding-left: 10px; }
.keyword-group { display: flex; gap: 10px; margin-top: 10px; }
.keyword { background: #eff6ff; color: #1d4ed8; padding: 5px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }

.modal-footer { padding: 20px 30px; border-top: 1px solid #eee; text-align: right; }
.confirm-btn { background: #3b82f6; color: #fff; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 700; cursor: pointer; }
</style>