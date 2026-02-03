import { defineStore } from 'pinia';

const USER_STORAGE_KEY = 'userInfo';

export const useUserStore = defineStore('user', {
  state: () => {
    let user = null;
    try {
      const savedUser = localStorage.getItem(USER_STORAGE_KEY);
      if (savedUser) user = JSON.parse(savedUser);
    } catch (e) {
      console.warn('userInfo 파싱 실패:', e);
      localStorage.removeItem(USER_STORAGE_KEY);
    }
    return { user };
  },

  getters: {
    isAuthenticated: (state) => !!state.user,
    userEmail: (state) => state.user?.email || null,
    userNickName: (state) => state.user?.nickName || null,
  },

  actions: {
    // 사용자 정보를 설정
    setUser(userData) {
      this.user = userData;
      if (userData) {
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userData));
      } else {
        localStorage.removeItem(USER_STORAGE_KEY);
      }
    },

    // 사용자 정보를 초기화
    clearUser() {
      this.user = null;
      localStorage.removeItem(USER_STORAGE_KEY);
    },
  },
});
