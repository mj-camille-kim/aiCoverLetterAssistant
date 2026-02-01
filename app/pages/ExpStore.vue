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
          <div v-if="isLoading" class="loading-text">데이터를 불러오는 중입니다...</div>
          
          <div 
            v-else
            v-for="item in experiences" 
            :key="item.id" 
            class="card material-card"
            @click="selectedExp = item" 
          >
            <h3 class="material-title">{{ item.title }}</h3>
            <div class="tag-group">
              <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>

          <div v-if="!isLoading && experiences.length === 0" class="empty-state">
            등록된 경험이 없습니다. 새로운 경험을 추가해보세요!
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
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Sidebar from '../components/Sidebar.vue'
import ExperienceModal from '../components/ExpModal.vue'
import ExpDetailModal from '../components/ExpDetailModal.vue'

const isModalOpen = ref(false)
const selectedExp = ref(null)
const isAddModalOpen = ref(false)

// 1. 가데이터를 비우고 빈 배열로 초기화
const experiences = ref([])
const isLoading = ref(true)

const fetchExperiences = async () => {
  try {
    isLoading.value = true;
    const userEmail = JSON.parse(localStorage.getItem("userInfo")).email;
    
    // POST로 변경하셨으니 axios.post를 사용해야 합니다.
    const response = await axios.post("/api/getUserExp", {
      userEmail: userEmail
    });

    // 💡 수정 포인트: response.data가 아니라 response.data.data를 가져와야 합니다.
    // 서버 응답: { success: true, data: [...] } 이기 때문입니다.
    const rawData = response.data.data; 

    if (Array.isArray(rawData)) {
      experiences.value = rawData.map(item => ({
        id: item.id,
        title: item.title,
        tags: item.keywords, 
        details: {
          situation: item.classifySTARI?.situation || '',
          task: item.classifySTARI?.task || '',
          action: item.classifySTARI?.action || '',
          result: item.classifySTARI?.result || '',
          insight: item.classifySTARI?.insight || ''
        }
      }));
    } else {
      console.error('서버에서 온 데이터가 배열 형식이 아닙니다:', rawData);
    }
  } catch (error) {
    console.error('경험 데이터를 가져오는데 실패했습니다:', error);
  } finally {
    isLoading.value = false;
  }
}


onMounted(() => {
  fetchExperiences()
})

const handleExperienceSubmit = async (data) => {
  // 등록 후 목록 새로고침
  await fetchExperiences()
  isModalOpen.value = false
}

const handleUpdateExperience = async (updatedData) => {
  // 성공적으로 업데이트되었다면 목록 다시 불러오기
  await fetchExperiences()
  selectedExp.value = null
}

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