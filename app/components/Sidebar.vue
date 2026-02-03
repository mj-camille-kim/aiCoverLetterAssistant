<template>
  <aside :class="['sidebar', { 'is-mini': !isSidebarOpen }]">
    <div class="sidebar-header" @click="isSidebarOpen = !isSidebarOpen" style="cursor: pointer;">
      <div class="logo-circle"></div>
      <span v-if="isSidebarOpen" class="service-name">서비스이름</span>
    </div>

    <nav class="menu-list">
      <div
        v-for="item in menuItems"
        :key="item.path"
        class="menu-item"
        :class="{ 'is-active': $route.path === item.path }"
        @click="$router.push(item.path)"
      >
        <span class="menu-icon">{{ item.icon }}</span>
        <span v-if="isSidebarOpen">{{ item.label }}</span>
      </div>
    </nav>

    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar"></div>
        <div v-if="isSidebarOpen" class="user-text">
          <p class="user-name">{{ userStore.userNickName || '사용자' }}</p>
          <p class="logout-btn" @click="handleLogout">로그아웃</p>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/user';
import { deleteCookie } from '../util/cookieUtils';

const isSidebarOpen = ref(true);
const router = useRouter();
const userStore = useUserStore();

const menuItems = [
  { icon: '📝', label: '자기소개서 작성', path: '/' },
  { icon: '📂', label: '경험 저장소', path: '/storage' },
  { icon: '🏠', label: '마이페이지', path: '/mypage' },
];

const handleLogout = () => {
  userStore.clearUser();
  deleteCookie('accessToken');

  router.push('/login');
};
</script>

<style scoped>
/* 사이드바 스타일 (약간 회색) */
.sidebar {
  width: 260px;
  background-color: #f8f9fa;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  position: relative;
  height: 100vh;
}

.sidebar.is-mini {
  width: 80px;
}

.sidebar.is-mini .menu-item {
  justify-content: center;
  padding: 12px 0;
}

.sidebar.is-mini .menu-icon {
  margin-right: 0;
}

.sidebar.is-mini .sidebar-header,
.sidebar.is-mini .user-info {
  justify-content: center;
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
  transition: color 0.2s;
}

.logout-btn:hover {
  color: #495057;
}
</style>
