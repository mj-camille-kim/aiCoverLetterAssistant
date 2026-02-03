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

      <div
        v-if="reportHtml"
        class="modal-body report-body"
        ref="bodyRef"
        @click="onBodyClick"
      >
        <div class="report-html-wrap" v-html="reportHtml"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps(['reportHtml'])
defineEmits(['close'])

const bodyRef = ref(null)

function onBodyClick(e) {
  const a = e.target.closest('a[href]')
  if (!a) return

  const href = (a.getAttribute('href') || '').trim()
  if (href.startsWith('#tab')) {
    e.preventDefault()
    switchTabInModal(href.slice(1))
    return
  }
  e.preventDefault()
  window.open(a.href, '_blank', 'noopener,noreferrer')
}

function switchTabInModal(tabId) {
  const wrap = bodyRef.value?.querySelector('.report-html-wrap')
  if (!wrap) return
  const contents = wrap.querySelectorAll('.tab-content')
  const tabs = wrap.querySelectorAll('a.tab')
  contents.forEach((el) => {
    el.style.display = el.id === tabId ? 'block' : 'none'
    el.classList.toggle('active', el.id === tabId)
  })
  tabs.forEach((el) => {
    const isActive = (el.getAttribute('href') || '') === '#' + tabId
    el.classList.toggle('active', isActive)
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.6); display: flex; align-items: center; justify-content: center; z-index: 9999;
}
.modal-content.report-size {
  width: 80vw;
  height: 80vh;
  max-height: 90vh;
  background: #fff;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.modal-header {
  flex-shrink: 0;
  padding: 20px 30px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-left { display: flex; align-items: center; gap: 10px; }
.report-icon { font-size: 24px; }
.close-btn { background: none; border: none; font-size: 30px; cursor: pointer; color: #999; }

/* 본문: 남은 높이 채우고 스크롤 가능 — 잘림/클릭 안 됨 방지 */
.modal-body.report-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: auto;
  padding: 24px;
}
.report-html-wrap {
  min-height: min-content;
  pointer-events: auto;
}
.report-html-wrap a[href] {
  color: #1d4ed8;
  text-decoration: underline;
  cursor: pointer;
}

.modal-body::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
.modal-body::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.report-section { margin-bottom: 30px; }
.report-section h3 { color: #1d4ed8; font-size: 18px; margin-bottom: 10px; border-left: 4px solid #1d4ed8; padding-left: 10px; }
.keyword-group { display: flex; gap: 10px; margin-top: 10px; }
.keyword { background: #eff6ff; color: #1d4ed8; padding: 5px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }

.modal-footer { padding: 20px 30px; border-top: 1px solid #eee; text-align: right; }
.confirm-btn { background: #3b82f6; color: #fff; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 700; cursor: pointer; }
</style>