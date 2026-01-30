<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <header class="modal-header">
        <div class="header-left">
          <textarea 
            :readonly="!isEditing"
            v-model="editedExp.title" 
            :class="['title-area', { 'editing-active': isEditing }]"
            rows="2"
          ></textarea>
          
          <div class="tag-group">
            <span v-for="tag in editedExp.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>
        
        <div class="header-right">
          <button v-if="!isEditing" class="action-btn delete-style">삭제하기</button>
          <button v-if="!isEditing" class="edit-btn" @click="isEditing = true">수정하기</button>
          <div v-else class="edit-actions">
            <button class="save-btn" @click="handleSave">저장</button>
            <button class="cancel-btn" @click="cancelEdit">취소</button>
          </div>
          <button class="close-btn" @click="$emit('close')">&times;</button>
        </div>
      </header>

      <div class="modal-body">
        <table class="star-table">
          <thead>
            <tr>
              <th v-for="(label, key) in starLabels" :key="key">
                {{ label.title }}<br>({{ label.eng.toUpperCase() }})
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td v-for="(label, key) in starLabels" :key="key">
                <textarea 
                  :readonly="!isEditing"
                  v-model="editedExp.details[key]" 
                  :class="['content-area', { 'editing-active': isEditing }]"
                ></textarea>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const props = defineProps(['experience'])
const emit = defineEmits(['close', 'update'])

const isEditing = ref(false)
const editedExp = reactive(JSON.parse(JSON.stringify(props.experience)))

const starLabels = {
  situation: { title: '배경/상황', eng: 'Situation' },
  task: { title: '역할/과제', eng: 'Task' },
  action: { title: '행동', eng: 'Action' },
  result: { title: '결과', eng: 'Result' },
  insight: { title: '배운 점', eng: 'Insight' }
}

const handleSave = () => {
  emit('update', JSON.parse(JSON.stringify(editedExp)))
  isEditing.value = false
}

const cancelEdit = () => {
  Object.assign(editedExp, JSON.parse(JSON.stringify(props.experience)))
  isEditing.value = false
}
</script>

<style scoped>
/* 기본 설정: 모든 요소에 box-sizing 적용하여 튀어나감 방지 */
* { box-sizing: border-box; }

.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.modal-content {
  background: white; width: 95%; max-width: 1300px; border-radius: 16px;
  padding: 40px; position: relative; max-height: 90vh; overflow-y: auto;
}

.modal-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 25px; gap: 40px; }
.header-left { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.title-area {
  width: 100%; font-size: 24px; font-weight: 800; color: #1e293b; 
  line-height: 1.4; border: none; background: transparent;
  outline: none; resize: none; margin-bottom: 12px; font-family: inherit;
  padding: 4px 0; transition: all 0.2s;
  overflow: hidden; /* 제목창 스크롤바 숨김 */
}

.title-area.editing-active {
  color: #6366f1; background: #f8fafc; border-bottom: 2px solid #6366f1; padding: 4px 8px;
}

.tag-group { display: flex; gap: 8px; }
.tag { background: #f1f5f9; color: #475569; padding: 4px 12px; border-radius: 6px; font-size: 13px; font-weight: 600; }

.header-right { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
.edit-btn { background: #fff; color: #6366f1; border: 1px solid #6366f1; padding: 8px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; }
.save-btn { background: #6366f1; color: white; border: none; padding: 8px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; }
.cancel-btn { background: #f1f5f9; color: #64748b; border: none; padding: 8px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; }
.close-btn { font-size: 28px; border: none; background: none; cursor: pointer; color: #cbd5e1; }
.delete-style { background: #fff; color: #6366f1; border: 1px solid #6366f1; padding: 8px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; }


/* 표 디자인: table-layout: fixed는 유지하고 border-spacing 해결 */
.star-table { width: 100%; border-collapse: collapse; border: 1px solid #e2e8f0; table-layout: fixed; }
.star-table th { background: #f8fafc; padding: 15px; font-size: 13px; font-weight: 700; color: #1e293b; border: 1px solid #e2e8f0; }
.star-table td { border: 1px solid #e2e8f0; height: 400px; padding: 0; vertical-align: top; overflow: hidden; }

/* 내용 텍스트 영역: box-sizing과 overflow 설정으로 튀어나감 방지 */
.content-area {
  width: 100%; height: 100%; padding: 20px; border: none; resize: none; outline: none;
  font-size: 15px; line-height: 1.7; color: #475569; background: transparent; font-family: inherit;
  display: block; /* 여백 방지 */
  word-break: break-all; /* 단어 길면 자동 줄바꿈 */
}

.content-area.editing-active {
  background: #fcfdff; color: #1e293b;
}
.content-area.editing-active:focus {
  background: #f5f7ff;
}
</style>