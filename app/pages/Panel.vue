<template>
  <aside class="editor-right">
    <nav class="right-tabs">
      <button 
        v-for="tab in tabList" 
        :key="tab.id"
        :class="['tab-pill', { active: currentTab === tab.id }]" 
        @click="handleTabChange(tab.id)" 
      >
        {{ tab.label }}
      </button>
    </nav>

    <div class="right-content-scroll">
      <keep-alive>
        <component 
          :is="tabComponents[currentTab]" 
          :active-question="activeQuestion"
          :materials="materials"
          :selected-materials="selectedMaterials"
          @update:selected-materials="$emit('update:selectedMaterials', $event)"
          @open-modal="$emit('open-modal')"
        />
      </keep-alive>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import StepDraft from '../components/Panel/StepDraft.vue'
import StepFeedback from '../components/Panel/StepFeedback.vue'
import StepSubhead from '../components/Panel/StepSubhead.vue'

const props = defineProps(['activeQuestion', 'materials', 'selectedMaterials', 'currentTab'])
const emit = defineEmits(['open-modal', 'update:selectedMaterials', 'analyze', 'update:currentTab'])

const tabList = [
  { id: 'draft', label: '초안 생성' },
  { id: 'feedback', label: '피드백 받기' },
  { id: 'subhead', label: '소제목 추천' }
]

const tabComponents = {
  draft: StepDraft,
  feedback: StepFeedback,
  subhead: StepSubhead
}

// 탭 변경 핸들러
const handleTabChange = (tabId) => {
  emit('update:currentTab', tabId)
  
  if (tabId === 'feedback' && props.activeQuestion) {
    if (!props.activeQuestion.content.trim()) return alert('초안을 먼저 작성해주세요!');
    emit('analyze', props.activeQuestion)
  }
  
  if (tabId === 'subhead' && props.activeQuestion) {
    if (!props.activeQuestion.content.trim()) return alert('초안을 먼저 작성해주세요!');
    emit('analyzeSubhead', props.activeQuestion) // 새로운 이벤트 발생
  }
}
</script>

<style scoped>
/* Panel 전체 레이아웃만 남김 */
.editor-right { flex: 0 0 40%; background-color: #f8fafc; display: flex; flex-direction: column; padding: 40px 30px; box-sizing: border-box; }
.right-tabs { display: flex; gap: 15px; border-bottom: 1px solid #e2e8f0; margin-bottom: 20px; }
.tab-pill { background: none; border: none; padding: 10px 0; color: #94a3b8; cursor: pointer; font-size: 14px; }
.tab-pill.active { color: #1d4ed8; font-weight: 700; border-bottom: 2px solid #1d4ed8; }
.right-content-scroll { flex: 1; overflow-y: auto; }
.empty-state { padding: 40px; text-align: center; color: #94a3b8; }
</style>