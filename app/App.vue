<template>
  <div class="app-layout">
    <div class="page-container">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useUserStore } from './stores/user';

const userStore = useUserStore();

onMounted(() => {
  if (!userStore.user) {
    const savedUser = localStorage.getItem('userInfo');
    if (savedUser) {
      try {
        userStore.setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error(error);
      }
    }
  }
});
</script>

<style>
/* 모든 페이지에 공통으로 적용될 스타일 */
body {
  margin: 0;
  padding: 0;
}

.app-layout {
  display: flex; /* 사이드바와 페이지가 가로로 나란히 서게 함 */
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.page-container {
  flex: 1;
  position: relative;
  overflow-y: auto;
  display: flex;
  flex-direction: column;;
}
</style>