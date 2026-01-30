<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <header class="modal-header">
        <div class="header-left" @click="$emit('close')">
          <span class="back-icon">〈</span>
          <h2>직접 정리하기</h2>
        </div>
        <span class="close-icon" @click="$emit('close')">✕</span>
      </header>

      <div class="modal-body">
        <p class="description">STARI 방법으로 직접 입력하여 경험을 저장할 수 있어요.</p>
        
        <div v-for="(exp, index) in experiences" :key="index" class="experience-section">
          <div class="exp-header">
            <h3 class="exp-title">경험 {{ index + 1 }}</h3>
            <span 
              v-if="experiences.length > 1" 
              class="delete-btn" 
              @click="removeExperience(index)"
            >삭제</span>
          </div>

          <div class="star-grid">
            <div v-for="(label, key) in starLabels" :key="key" class="star-col">
              <label>{{ label.title }}<br>({{ label.eng }})</label>
              <textarea 
                v-model="exp[key]" 
                :placeholder="label.title + '를 적어주세요'"
              ></textarea>
            </div>
          </div>
        </div>
        
        <div class="action-row">
          <span class="add-text-btn" @click="addExperience">+ 추가하기</span>
        </div>
      </div>

      <footer class="modal-footer">
        <div class="footer-right">
          <p class="footer-notice">각 항목을 10자 이상 입력해주세요</p>
          <button 
            class="submit-btn" 
            :disabled="!isAllReady"
            @click="$emit('submit', experiences)"
          >
            경험 저장하기
          </button>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const emit = defineEmits(['close', 'submit']);

const starLabels = {
  situation: { title: '배경/상황', eng: 'Situation'},
  task: { title: '역할/과제', eng: 'Task'},
  action: { title: '행동', eng: 'Action'},
  result: { title: '결과', eng: 'Result'},
  insight: { title: '배운 점', eng: 'Insight'}
};

const submitExperience = () => {
  if (!isAllReady.value) return;

  // 변환 없이 원본 데이터 배열(situation, task 등 포함)을 그대로 보냅니다.
  emit('submit', experiences.value); 
};

const experiences = ref([
  { situation: '', task: '', action: '', result: '', insight: '' }
]);

const addExperience = () => {
  experiences.value.push({
    situation: '', task: '', action: '', result: '', insight: ''
  });
};

const removeExperience = (index) => {
  experiences.value.splice(index, 1);
};

const isAllReady = computed(() => {
  return experiences.value.every(exp => 
    Object.values(exp).every(val => val.length >= 10)
  );
});
</script>

<style scoped>
/* 기존 스타일 유지 및 추가 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.modal-content {
  background: white;
  width: 95%;
  max-width: 1200px;
  border-radius: 20px;
  padding: 30px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.close-icon { cursor: pointer; font-size: 20px; color: #868e96; }

/* 경험 섹션 상단 (제목 + 삭제버튼) */
.exp-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 10px;
  margin-top: 25px;
}

.exp-title { margin: 0; font-size: 1.1rem; font-weight: bold; }

.delete-btn {
  font-size: 0.85rem;
  color: #adb5bd;
  text-decoration: underline;
  cursor: pointer;
}

.delete-btn:hover { color: #fa5252; }

.star-grid {
  display: flex;
  border: 1px solid #dee2e6;
  border-radius: 12px;
  overflow: hidden;
}

.star-col { flex: 1; border-right: 1px solid #dee2e6; }
.star-col:last-child { border-right: none; }

.star-col label {
  display: block; padding: 12px;
  background: #f1f3f5; font-size: 0.8rem;
  font-weight: bold; text-align: center;
  border-bottom: 1px solid #dee2e6;
}

.star-col textarea {
  width: 100%; height: 250px; padding: 15px;
  border: none; resize: none; outline: none;
  font-size: 0.9rem; line-height: 1.6;
}

/* 추가하기 버튼 & 푸터 오른쪽 정렬 */
.action-row { display: flex; justify-content: flex-end; margin: 15px 0 30px; }

.add-text-btn {
  color: #868e96; font-size: 0.95rem; cursor: pointer;
  padding: 8px 15px; border: 1px solid #dee2e6; border-radius: 6px;
}

.modal-footer { display: flex; justify-content: flex-end; border-top: 1px solid #f1f3f5; padding-top: 20px; }
.footer-right { text-align: right; }
.footer-notice { font-size: 0.85rem; color: #868e96; margin-bottom: 10px; }

.submit-btn {
  background: #A5B4FC; color: white; border: none;
  padding: 12px 40px; border-radius: 8px;
  font-weight: bold; cursor: pointer;
}

.submit-btn:disabled { background: #e9ecef; color: #adb5bd; cursor: not-allowed; }
</style>