<template>
  <div class="container">
    <Sidebar />

    <main class="main-content">
      <div class="content-body">
        <header class="repo-header">
          <div class="header-left">
            <h1 class="page-title">경험 관리</h1>
            <p class="page-desc">경험을 정리해서 자기소개서 소재로 활용해요</p>
          </div>
          <button class="add-btn" @click="isModalOpen = true">
            경험 추가
          </button>
        </header>

        <div class="filter-bar">
        </div>

        <div class="experience-grid">
          <div 
            v-for="item in mockMaterials" 
            :key="item.id" 
            class="card material-card"
            @click="selectedExp = item" 
          >
            <span class="file-source">{{ item.fileName }}</span>
            <h3 class="material-title">{{ item.title }}</h3>
            <div class="tag-group">
              <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>

      <ExperienceModal
        v-if="isModalOpen" 
        @close="isModalOpen = false" 
        @submit="handleExperienceSubmit"
        />

      <ExpDetailModal 
        v-if="selectedExp" 
        :experience="selectedExp" 
        @close="selectedExp = null" 
        @update="handleUpdateExperience" 
        />

    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import ExperienceModal from '../components/ExpModal.vue'
import ExpDetailModal from '../components/ExpDetailModal.vue'

const isModalOpen = ref(false)
const selectedExp = ref(null)
const isAddModalOpen = ref(false)

// 이미지 기반 가데이터 3개
const mockMaterials = ref([
  {
    id: 1,
    fileName: '김민지_이력서_자기소개서.pdf',
    title: '경기도 공공자전거 서비스 종료 원인 분석 프로젝트를 통한 EDA 및 데이터 구조화 역량 강화',
    tags: ['데이터 분석', '문제 분석', '논리적 사고', '적응력'],
    details: {
      situation: '경기도 내 공공자전거 이용률이 전년 대비 30% 감소하며 서비스 종료 위기에 처한 상황이었습니다.',
      task: '종료 여부 결정을 위해 이용 패턴을 분석하고 정확한 하락 원인을 파악해야 했습니다.',
      action: '3개년 이용 데이터 50만 건을 수집하여 파이썬으로 EDA를 실시하고, 연령대별/지역별 이용 지도를 시각화했습니다.',
      result: '핵심 원인이 인프라 노후화와 특정 구간 연계성 부족임을 데이터로 증명하여 전략 보고서를 제출했습니다.',
      insight: '방대한 데이터를 비즈니스 관점에서 구조화하고 논리적 근거를 도출하는 분석 역량을 키웠습니다.'
    }
  },
  {
    id: 2,
    fileName: '김민지_이력서_자기소개서.pdf',
    title: 'RAG 시스템 기반 HS코드 탐색기 고도화 프로젝트를 통한 임베딩 및 벡터 검색 이해 심화',
    tags: ['데이터 분석', '프로젝트 관리', '논리적 사고', '문제 분석'],
    details: {
      situation: '기존 관세 코드 탐색 시스템의 정확도가 낮아 실무자의 업무 효율이 떨어지는 상태였습니다.',
      task: 'RAG(검색 증강 생성) 기술을 적용해 유사 코드 추천의 정확도를 90% 이상으로 높이는 것이 목표였습니다.',
      action: '다양한 임베딩 모델을 테스트하고 벡터 데이터베이스를 최적화하여 검색 성능을 고도화했습니다.',
      result: '테스트 결과 기존 대비 검색 정확도가 25% 향상되었으며 실무 도입 확정을 이끌어냈습니다.',
      insight: '최신 AI 기술을 실제 산업 도메인에 적용하는 과정에서의 트러블슈팅 경험을 쌓았습니다.'
    }
  },
  {
    id: 3,
    fileName: '김민지_이력서_자기소개서.pdf',
    title: '교환학생 중 발생한 비상 상황 대처 경험을 통한 회복탄력성 및 문제 해결 능력 함양',
    tags: ['적응력', '추진력', '문제 분석'],
    details: {
      situation: '해외 교환학생 기간 중 숙소 결제 오류로 인해 당일 거처가 불분명해진 비상 상황이었습니다.',
      task: '낯선 환경에서 침착하게 24시간 이내에 새로운 숙소를 확보하고 학업 스케줄을 유지해야 했습니다.',
      action: '현지 커뮤니티와 학교 사무실에 즉시 연락을 취하고 가능한 모든 플랫폼을 동원해 대안을 찾았습니다.',
      result: '당일 내에 안전한 숙소로 재배치되었으며, 이후 비슷한 상황의 동료들을 돕는 매뉴얼을 작성했습니다.',
      insight: '예기치 못한 위기 앞에서도 당황하지 않고 해결책을 찾아가는 회복탄력성의 중요성을 배웠습니다.'
    }
  }
])

const handleExperienceSubmit = (data) => {
  console.log('새 경험 등록 데이터:', data)
  isModalOpen.value = false
}

const handleUpdateExperience = (updatedData) => {
  // 배열에서 해당 ID를 찾아 데이터 교체 (DB 업데이트 효과)
  const index = mockMaterials.value.findIndex(item => item.id === updatedData.id);
  if (index !== -1) {
    mockMaterials.value[index] = { ...updatedData };
    console.log('DB 업데이트 완료:', updatedData);
  }
  selectedExp.value = null; // 모달 닫기 (또는 유지하고 싶으면 그대로 둠)
};

</script>

<style scoped>
/* 1. 공통 레이아웃 스타일 (ExpUpload.vue와 동일) */
.container {
  display: flex;
  width: 100vw;
  height: 100vh;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background-color: #fff;
}

.content-body {
  padding: 40px 60px;
}

/* 2. 경험 관리 페이지 전용 스타일 */
.repo-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 30px; }
.page-title { font-size: 28px; font-weight: 800; margin-bottom: 8px; color: #0f172a; }
.page-desc { color: #64748b; font-size: 15px; }

.add-btn {
  background: #fff; border: 1px solid #e2e8f0; padding: 10px 20px;
  border-radius: 8px; font-weight: 700; cursor: pointer; transition: 0.2s;
}
.add-btn:hover { background: #f8fafc; border-color: #94a3b8; }

.filter-bar { display: flex; gap: 12px; margin-bottom: 30px; }
.filter-select { border: 1px solid #e2e8f0; padding: 8px 16px; border-radius: 8px; color: #64748b; min-width: 150px; }

/* 그리드 레이아웃 */
.experience-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.card {
  background: #fff; border: 1px solid #f1f5f9; border-radius: 16px;
  padding: 24px; min-height: 220px; cursor: pointer; transition: all 0.2s;
  display: flex; flex-direction: column;
}
.card:hover { transform: translateY(-4px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); }

/* 새 소재 만들기 카드 전용 */
.add-card {
  border: 2px dashed #e2e8f0; background: #f8fafc;
  align-items: center; justify-content: center;
}
.plus-circle {
  width: 48px; height: 48px; background: #334155; color: white;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 24px; margin-bottom: 12px;
}
.add-text { font-weight: 700; color: #334155; }

/* 경험 정보 카드 */
.file-source { font-size: 12px; color: #94a3b8; margin-bottom: 12px; display: block; }
.material-title { font-size: 18px; font-weight: 800; line-height: 1.5; color: #1e293b; margin-bottom: 20px; word-break: keep-all; }

.tag-group { display: flex; flex-wrap: wrap; gap: 6px; margin-top: auto; }
.tag { background: #f1f5f9; color: #475569; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; }
</style>