<template>
  <div class="container">
    <Sidebar />
    <main :class="['main-content', { 'expanded': !isSidebarOpen }]">
      
      <header class="top-header">
        <div class="header-left">
          <h2 class="page-title">내 대시보드</h2>
          <p class="sub-title">활동 통계와 역량 키워드를 확인하세요.</p>
        </div>
        <button class="help-btn">?</button>
      </header>

      <div class="content-body">
        <section class="stats-grid">
          <div v-for="item in stats" :key="item.label" class="stat-card">
            <div class="stat-icon">{{ item.icon }}</div>
            <div class="stat-info">
              <span class="label">{{ item.label }}</span>
              <strong class="count">{{ item.value }}</strong>
            </div>
          </div>
        </section>

        <section class="analysis-card">
          <div class="card-header">
            <h3>나의 강점 분석</h3>
          </div>
          
          <div class="tag-cloud">
            <span 
              v-for="(tag, index) in strengthTags" 
              :key="tag" 
              :class="['tag', { 'top-tag': index === 0 }]"
            >
              {{ tag }}
            </span>
          </div>
          
          <div class="insight-box">
            <span class="lightbulb">💡</span>
            <p class="insight-text">
              현재까지 기록된 경험을 토대로 볼 때, <b>{{ strengthTags[0] }}</b> 역량이 가장 돋보이네요! <br>
              이 역량을 강조할 수 있는 자기소개서 문항을 추천해 드릴까요?
            </p>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script>
import Sidebar from '../components/Sidebar.vue';

export default {
  components: { Sidebar },
  data() {
    return {
      isSidebarOpen: true,
      stats: [
        { label: '경험 기록', value: 24, icon: '📝' },
        { label: '자기소개서', value: 5, icon: '📁' },
        { label: '기업 리포트', value: 12, icon: '🔖' }
      ],
      strengthTags: ['#문제해결', '#소통', '#분석력', '#열정', '#협업']
    }
  }
}
</script>

<style scoped>
/* 전체 배경 설정 */
.container {
  display: flex;
  background-color: #f9fafb; /* 연한 회색 배경 */
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: 40px;
}

/* 헤더 개선 */
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40px;
}
.page-title { font-size: 26px; font-weight: 800; color: #111827; margin: 0; }
.sub-title { font-size: 14px; color: #6b7280; margin-top: 4px; }

/* 활동 요약 카드 디자인 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}
.stat-card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
  border: 1px solid #f3f4f6;
}
.stat-card:hover { transform: translateY(-5px); }
.stat-icon { font-size: 32px; }
.label { font-size: 13px; color: #6b7280; display: block; }
.count { font-size: 24px; font-weight: 800; color: #111827; }

/* 강점 분석 카드 디자인 */
.analysis-card {
  background: white;
  padding: 32px;
  border-radius: 20px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  border: 1px solid #f3f4f6;
}
.card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
.card-header h3 { font-size: 18px; font-weight: 700; margin: 0; }
.badge { font-size: 11px; background: #EEF2FF; color: #4F46E5; padding: 4px 8px; border-radius: 6px; font-weight: 600; }

.tag-cloud { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 24px; }
.tag {
  padding: 8px 18px;
  background: #f3f4f6;
  border-radius: 50px;
  font-size: 14px;
  color: #4b5563;
  transition: 0.3s;
}
.top-tag {
  background: #4F46E5; /* 메인 컬러 */
  color: white;
  font-weight: 600;
  box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3);
}

/* 인사이트 박스 디자인 */
.insight-box {
  background: #f8faff;
  border: 1px dashed #c7d2fe;
  padding: 20px;
  border-radius: 12px;
  display: flex;
  gap: 12px;
}
.lightbulb { font-size: 20px; }
.insight-text { font-size: 14px; color: #374151; line-height: 1.6; margin: 0; }
.insight-text b { color: #4F46E5; }

.help-btn {
  width: 35px; height: 35px; border-radius: 50%; border: 1px solid #ddd; background: white; cursor: pointer;
}
</style>