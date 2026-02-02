<template>
  <div class="main-wrapper">
    <Sidebar />

    <div class="editor-layout">
      <section class="editor-left">
        <div class="header-container">
          <h1 class="page-title">자기소개서 작성</h1>
          <div class="report-button-wrapper">
            <button class="report-button" @click="openReport">📊 기업 분석 리포트</button>
            <div class="tooltip">
              JD 분석과 기업 기본 정보를 확인하고<br>
              단계별로 자소서를 써보세요!
            </div>
          </div>
        </div>
        
        <div class="question-tabs">
          <button
            v-for="(question, index) in questions"
            :key="question.id"
            class="tab-item"
            :class="{ 'is-active': index === activeIndex }"
            @click="setActive(index)"
          >
            {{ question.label }}
          </button>
          <button class="tab-item add-tab" @click="addQuestion">+ 추가</button>
        </div>

        <div class="question-header">
          <span class="question-title">
            <template v-if="isEditingTitle">
              <input v-model="draftTitle" class="title-input" type="text" maxlength="30" @keyup.enter="toggleEditTitle" />
            </template>
            <template v-else>
              {{ activeQuestion.title }}
            </template>
          </span>
          <div class="question-actions">
            <button class="action-btn" @click="toggleEditTitle">
              {{ isEditingTitle ? '완료' : '문항 수정' }}
            </button>
            <span class="action-divider">|</span>
            <button class="action-btn" @click="removeQuestion">삭제</button>
          </div>
        </div>

        <div class="question-body">
          <textarea
            v-model="activeQuestion.content"
            class="question-textarea"
            placeholder="내용을 입력하거나 우측에서 초안을 생성해보세요."
          ></textarea>
        </div>
      </section>

      <Panel 
        v-model:currentTab="currentPanelTab"  :active-question="activeQuestion" 
        :materials="materials"
        v-model:selectedMaterials="selectedMaterials"
        @open-modal="isModalOpen = true"
        @analyze="handleAnalyze"
        @analyzeSubhead="handleAnalyzeSubhead"
      />

      <ExpModal 
        v-if="isModalOpen" 
        @close="isModalOpen = false" 
        @save="handleSaveExperience"
      />

      <ReportModal v-if="isReportOpen" @close="isReportOpen = false" />

    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onMounted, onUnmounted } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import Panel from './Panel.vue'
import ExpModal from '../components/ExpModal.vue'
import ReportModal from '../components/ReportModal.vue'
import bus from '../util/bus';

// 데이터 상태 관리
const questions = ref([
  { id: 1, label: '문항1', title: '지원동기', content: '', draft: '', isStarted: false, feedback: null, subheads: null },
  { id: 2, label: '문항2', title: '성격의 장단점', content: '', draft: '', isStarted: false, feedback: null, subheads: null },
  { id: 3, label: '문항3', title: '강점', content: '', draft: '', isStarted: false, feedback: null, subheads: null },
  { id: 4, label: '문항4', title: '입사 후 포부 및 계획', content: '', draft: '', isStarted: false, feedback: null, subheads: null }
])

const activeIndex = ref(0)
const currentPanelTab = ref('draft') // 패널의 현재 탭 상태를 부모가 관리
const isEditingTitle = ref(false)
const draftTitle = ref(questions.value[0].title)
const selectedMaterials = ref([])
const isModalOpen = ref(false)
const isReportOpen = ref(true)
const activeQuestion = computed(() => questions.value[activeIndex.value])

let typingInterval = null;

const typeWriter = (text) => {
  // 1. 기존에 타이핑 중이었다면 중지
  if (typingInterval) clearInterval(typingInterval);
  
  // 2. 현재 선택된 문항의 내용을 비우고 시작 (원치 않으면 이 줄만 삭제)
  activeQuestion.value.content = '';
  
  let index = 0;
  typingInterval = setInterval(() => {
    if (index < text.length) {
      // 3. 현재 활성화된 문항(activeQuestion)의 content에 한 글자씩 추가
      activeQuestion.value.content += text.charAt(index);
      index++;
    } else {
      clearInterval(typingInterval);
    }
  }, 30); // 30ms 속도로 한 글자씩 출력
};

onMounted(() => {
  // 4. 버스 신호 수신: 'generateDraft'라는 신호가 오면 typeWriter 함수 실행
  bus.on('generateDraft', (draftText) => {
    typeWriter(draftText);
  });
});

onUnmounted(() => {
  // 5. 컴포넌트 종료 시 무전기 끄기 및 인터벌 제거
  bus.off('generateDraft');
  if (typingInterval) clearInterval(typingInterval);
});


const materials = ref([
  { id: 1, title: '생성형 AI 프로젝트', description: 'AI 모델 선정 및 자동 배포 시스템 구축' },
  { id: 2, title: '데이터 분석 교육', description: 'Python 기반 시각화 및 모델링 수행' }
])

// 피드백 분석 함수 (나중에 실제 API 호출로 대체)
const handleAnalyze = async (question) => {
  // 이미 분석 데이터가 있으면 다시 실행하지 않음
  if (question.feedback) return;

  question.isStarted = true;
  
  // 시뮬레이션: 1.2초 후 데이터 주입
  await new Promise(resolve => setTimeout(resolve, 1200));

  question.feedback = {
    hr: [
      { category: '전달력', rating: 4, tags: [], text: '문장이 간결하고 의도가 명확합니다.' },
      { category: '문항 의도 파악', rating: 5, tags: [], text: '질문의 핵심을 정확히 파악했습니다.' },
      { category: '조직 적합성', rating: 4, tags: ['도전정신'], text: '적극적인 태도가 돋보입니다.' }
    ],
    pro: [
      { category: '직무 적합성', rating: 4, tags: ['꼼꼼함'], text: '실무 역량이 잘 드러나 있습니다.' },
      { category: '기술 전문성', rating: 3, tags: ['Python'], text: '기술적 디테일을 조금 더 보강하세요.' },
      { category: '문제 해결력', rating: 5, tags: ['논리력'], text: '해결 과정이 매우 논리적입니다.' }
    ]
  };
};

// 소제목 분석 함수 (나중에 실제 API 호출로 대체)
const handleAnalyzeSubhead = async (question) => {
  if (question.subheads || !question.content.trim()) return;

  question.isSubheadStarted = true; // 소제목 전용 로딩 상태
  await new Promise(resolve => setTimeout(resolve, 1500)); // 시뮬레이션

  // LLM이 본문을 파악해 추천해준 컨셉의 소제목 3개
  question.subheads = [
    { id: 1, text: "데이터로 증명하는 분석 전문가, OO 기업의 성장을 이끌다" },
    { id: 2, text: "협업의 가치를 아는 개발자: 15% 효율 개선을 이뤄낸 소통의 힘" },
    { id: 3, text: "도전을 멈추지 않는 열정, 기술적 한계를 넘어선 프로젝트 경험" }
  ];
};

// 함수 로직
const setActive = (i) => { 
  activeIndex.value = i; 
  isEditingTitle.value = false; 
  draftTitle.value = questions.value[i].title; 
  
  // 문항을 누를 때마다 오른쪽 패널을 '초안 생성'으로 초기화
  currentPanelTab.value = 'draft'; 
}
const toggleEditTitle = () => { 
  if (isEditingTitle.value) activeQuestion.value.title = draftTitle.value; 
  isEditingTitle.value = !isEditingTitle.value; 
}
const addQuestion = () => { 
  questions.value.push({ 
    id: Date.now(), 
    label: `문항${questions.value.length+1}`, 
    title: '새 문항', 
    content: '', 
    draft: '',
    isStarted: false // 새 문항도 초기값은 분석 전 상태
  }); 
  setActive(questions.value.length - 1); 
}
const removeQuestion = () => { 
  if (questions.value.length > 1) { 
    questions.value.splice(activeIndex.value, 1); 
    setActive(0); 
  } 
}

const openReport = () => { 
  isReportOpen.value = true 
}
</script>

<style scoped>
/* 1. 레이아웃 고정 */
.main-wrapper {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background-color: #fff; overflow: hidden; display: flex;
}

.editor-layout { display: flex; flex: 1; height: 100%; }

/* 2. 왼쪽 에디터 영역 (60%) */
.editor-left {
  flex: 0 0 60%;
  display: flex; flex-direction: column;
  padding: 40px 60px; border-right: 1px solid #f0f0f0;
  box-sizing: border-box;
}

/* 3. 헤더 (제목 & 툴팁 버튼) */
.header-container {
  display: flex; justify-content: space-between; align-items: center;
  width: 100%; margin-bottom: 8px;
}

.page-title { font-size: 24px; font-weight: 800; margin: 0; }

.report-button-wrapper { position: relative; display: inline-block; }

.report-button {
  display: flex; align-items: center; gap: 8px;
  background-color: #3b82f6; color: white; border: none;
  padding: 10px 18px; border-radius: 8px; font-weight: 600;
  font-size: 14px; cursor: pointer; transition: background 0.2s;
}
.report-button:hover { background-color: #2563eb; }

.tooltip {
  visibility: hidden; opacity: 0; position: absolute;
  top: 110%; right: 0; width: 220px;
  background-color: #334155; color: #fff; text-align: center;
  padding: 10px; border-radius: 6px; font-size: 12px;
  line-height: 1.5; z-index: 1000; transition: opacity 0.3s;
  white-space: pre-line; pointer-events: none;
}
.report-button-wrapper:hover .tooltip { visibility: visible; opacity: 1; }

/* 4. 문항 탭 스타일 */
.question-tabs { display: flex; gap: 20px; margin-bottom: 20px; border-bottom: 1px solid #f0f0f0; }
.tab-item { border: none; background: none; padding-bottom: 10px; cursor: pointer; color: #999; font-size: 15px; }
.tab-item.is-active { color: #1d4ed8; font-weight: 700; border-bottom: 2px solid #1d4ed8; }
.add-tab { color: #3b82f6; font-weight: 600; }

/* 5. 에디터 상단 (제목 수정/삭제) */
.question-header { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.question-title { font-size: 18px; font-weight: 700; color: #111; }
.title-input { border: 1px solid #3b82f6; outline: none; padding: 4px 8px; border-radius: 4px; font-size: 16px; }
.question-actions { color: #ccc; font-size: 13px; display: flex; gap: 8px; align-items: center; }
.action-btn { background: none; border: none; color: #999; cursor: pointer; font-size: 13px; }
.action-btn:hover { color: #666; }

/* 6. 텍스트 입력창 */
.question-body { flex: 1; border-top: 2px solid #111; margin-top: 15px; }
.question-textarea {
  width: 100%; height: 100%; border: none; outline: none; resize: none;
  font-size: 16px; padding: 20px 0; line-height: 1.8; color: #333;
}
</style>