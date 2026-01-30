<template>
  <div class="feedback-section">
    <div class="feedback-tabs">
      <button :class="['tab-btn', { active: activeTab === 'hr' }]" @click="activeTab = 'hr'">인사담당자</button>
      <button :class="['tab-btn', { active: activeTab === 'pro' }]" @click="activeTab = 'pro'">실무담당자</button>
    </div>

    <div class="feedback-list">
      <div v-if="activeQuestion.isStarted && !activeQuestion.feedback" class="loading-container">
        <div class="spinner"></div>
        <p class="loading-text">AI가 당신의 자소서를 분석하고 있습니다...</p>
      </div>

      <template v-else-if="activeQuestion.feedback">
        <div v-for="(item, index) in currentFeedback" :key="index" class="feedback-card">
          <div class="card-header">
            <div class="title-line">
              <h4 class="category-title">{{ item.category }}</h4>
              <div class="star-rating">
                <span v-for="i in 5" :key="i" :class="['star', { filled: i <= item.rating }]">★</span>
              </div>
            </div>
            <div class="tag-group" v-if="item.tags && item.tags.length">
              <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>

          <div class="card-body">
            <p class="feedback-main-text">{{ item.text }}</p>
          </div>

          <div class="card-icon-deco">🌐</div>
        </div>
      </template>

      <div v-else class="empty-state">
        <p>상단 버튼을 눌러 피드백을 시작해 보세요.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps(['activeQuestion'])
const activeTab = ref('hr')

const currentFeedback = computed(() => {
  if (!props.activeQuestion || !props.activeQuestion.feedback) return []
  return props.activeQuestion.feedback[activeTab.value] || []
})
</script>

<style scoped>
/* 기존 스타일 유지 */
.feedback-tabs { display: flex; gap: 15px; margin-bottom: 15px; border-bottom: 1px solid #f0f0f0; }
.tab-btn { background: none; border: none; padding: 10px 0; cursor: pointer; color: #999; font-weight: bold; }
.tab-btn.active { color: #6366f1; border-bottom: 2px solid #6366f1; }

/* --- 로딩 애니메이션 스타일 추가 --- */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #6366f1; /* 탭 포인트 컬러와 맞춤 */
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
}
/* ---------------------------------- */

.feedback-card {
  background: #fff; border: 1px solid #e5e7eb; border-radius: 12px;
  padding: 24px; margin-bottom: 16px; position: relative;
}
.title-line { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.category-title { font-size: 18px; font-weight: 800; margin: 0; }
.star-rating { color: #d1d5db; font-size: 12px; }
.star.filled { color: #818cf8; }

.tag-group { display: flex; gap: 8px; margin-top: 5px; }
.tag { font-size: 12px; font-weight: 600; color: #2dd4bf; }

.feedback-main-text { font-size: 22px; font-weight: 700; color: #334155; margin: 30px 0; text-align: center; }
.card-icon-deco { position: absolute; top: 10px; right: 15px; opacity: 0.3; font-size: 20px; }

.empty-state { text-align: center; padding: 60px 0; color: #94a3b8; }
</style>