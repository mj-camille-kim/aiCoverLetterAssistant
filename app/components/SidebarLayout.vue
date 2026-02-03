<template>
  <div class="container">
    <aside :class="['sidebar', { 'is-closed': !isSidebarOpen }]">
      <div class="sidebar-header">
        <div class="logo-circle"></div>
        <span v-if="isSidebarOpen" class="service-name">서비스이름</span>
      </div>

      <nav class="menu-list">
        <template v-for="item in menuItems" :key="item.label">
          <router-link
            v-if="item.to"
            :to="item.to"
            class="menu-item"
            active-class="active"
          >
            <span class="menu-icon">{{ item.icon }}</span>
            <span v-if="isSidebarOpen">{{ item.label }}</span>
          </router-link>
          <div v-else class="menu-item">
            <span class="menu-icon">{{ item.icon }}</span>
            <span v-if="isSidebarOpen">{{ item.label }}</span>
          </div>
        </template>
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

    <button
      @click="isSidebarOpen = !isSidebarOpen"
      class="toggle-btn"
      :style="{ left: isSidebarOpen ? '240px' : '10px' }"
    >
      {{ isSidebarOpen ? '◀' : '▶' }}
    </button>

    <main :class="['main-content', { 'expanded': !isSidebarOpen }]">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { deleteCookie } from '../util/cookieUtils'

const isSidebarOpen = ref(true)
const router = useRouter()
const userStore = useUserStore()

const menuItems = [
  { icon: '📝', label: '자기소개서 작성', to: '/resume' },
  { icon: '📄', label: '자소서 에디터', to: '/resume/editor' },
  { icon: '🏠', label: '메인', to: '/' },
  { icon: '📂', label: '경험 저장소', to: '/storage' }
]

const handleLogout = () => {
  userStore.clearUser()
  deleteCookie('accessToken')
  router.push('/login')
}
</script>

<style scoped>
.container {
  display: flex;
  height: 100vh;
  width: 100vw;
  font-family: 'Pretendard', sans-serif;
  background-color: #ffffff;
}

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
  text-decoration: none;
}

.menu-item:hover,
.menu-item.active {
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

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  transition: margin 0.3s ease;
}
</style>
