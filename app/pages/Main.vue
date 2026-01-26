<template>
  <div class="container">
    <aside :class="['sidebar', { 'is-closed': !isSidebarOpen }]">
      <div class="sidebar-header">
        <div class="logo-circle"></div>
        <span v-if="isSidebarOpen" class="service-name">서비스이름</span>
      </div>

      <nav class="menu-list">
        <div v-for="item in menuItems" :key="item.label" class="menu-item">
          <span class="menu-icon">{{ item.icon }}</span>
          <span v-if="isSidebarOpen">{{ item.label }}</span>
        </div>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar"></div>
          <div v-if="isSidebarOpen" class="user-text">
            <p class="user-name">홍길동</p>
            <p class="logout-btn">로그아웃</p>
          </div>
        </div>
      </div>
    </aside>

    <button @click="isSidebarOpen = !isSidebarOpen" class="toggle-btn" :style="{ left: isSidebarOpen ? '240px' : '10px' }">
      {{ isSidebarOpen ? '◀' : '▶' }}
    </button>

    <main :class="['main-content', { 'expanded': !isSidebarOpen }]">
      <header class="top-header">
        <button class="help-btn">?</button>
      </header>

      <div class="content-body">
        <h1 class="main-title">서비스이름</h1>
        
        <div class="input-container">
          <input 
            type="text" 
            placeholder="채용 공고 링크를 입력해주세요." 
            class="url-input"
          />
          <button class="search-submit">↑</button>
        </div>
        <p class="notice">링크를 입력하면 분석이 시작됩니다.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const isSidebarOpen = ref(true);

const menuItems = [
  { icon: '📝', label: '자기소개서 작성' },
  { icon: '📊', label: '기업 분석 리포트' },
  { icon: '👥', label: '면접 준비' },
  { icon: '📅', label: '채용 달력' },
];
</script>

<style scoped>
/* 전체 레이아웃 */
.container {
  display: flex;
  height: 100vh;
  width: 100vw;
  font-family: 'Pretendard', sans-serif;
  background-color: #ffffff;
}

/* 사이드바 스타일 (약간 회색) */
.sidebar {
  max-height: 98%;
  width: 260px;
  background-color: #f8f9fa;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  z-index: 10;
}

.sidebar.is-closed {
  width: 0;
  overflow: hidden;
  border: none;
}

.sidebar-header {
  padding: 30px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-circle {
  width: 32px;
  height: 32px;
  background-color: #dee2e6;
  border-radius: 50%;
}

.service-name {
  font-weight: bold;
  font-size: 1.2rem;
}

.menu-list {
  flex: 1;
  padding: 0 15px;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 8px;
  border-radius: 10px;
  cursor: pointer;
  color: #495057;
  transition: background 0.2s;
}

.menu-item:hover {
  background-color: #e9ecef;
}

.menu-icon {
  margin-right: 12px;
  font-size: 1.2rem;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid #e9ecef;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 35px;
  height: 35px;
  background-color: #ced4da;
  border-radius: 50%;
}

.user-name {
  font-weight: 600;
  font-size: 0.9rem;
  margin: 0;
}

.logout-btn {
  font-size: 0.8rem;
  color: #adb5bd;
  margin: 0;
  cursor: pointer;
}

/* 토글 버튼 */
.toggle-btn {
  position: absolute;
  top: 20px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 5px;
  cursor: pointer;
  padding: 5px 8px;
  z-index: 20;
  transition: left 0.3s ease;
}

/* 메인 컨텐츠 영역 (가운데 정렬) */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  transition: margin 0.3s ease;
}

.top-header {
  height: 80px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding-right: 40px;
}

.help-btn {
  width: 40px;
  height: 40px;
  background-color: #212529;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
}

.content-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center; /* 가운데 정렬 */
  padding-bottom: 10vh; /* 하단 쏠림 방지 및 위치 조절 */
}

.main-title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 60px;
  letter-spacing: -2px;
}

/* 입력창 스타일 */
.input-container {
  width: 100%;
  max-width: 700px;
  position: relative;
  display: flex;
  align-items: center;
}

.url-input {
  width: 100%;
  padding: 20px 30px;
  font-size: 1.1rem;
  border: 2px solid #f1f3f5;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  outline: none;
  transition: border-color 0.2s;
}

.url-input:focus {
  border-color: #339af0;
}

.search-submit {
  position: absolute;
  right: 15px;
  width: 45px;
  height: 45px;
  background-color: #339af0; /* 파란색 계열 */
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.5rem;
  cursor: pointer;
  transition: background 0.2s;
}

.search-submit:hover {
  background-color: #228be6;
}

.notice {
  margin-top: 20px;
  color: #adb5bd;
  font-size: 0.9rem;
}
</style>