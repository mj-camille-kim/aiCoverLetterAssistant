<template>
    <div class="login-container">
      <div class="login-box">
        <h1>AI 자소서 로그인</h1>
        <p class="subtitle">서비스 이용을 위해 로그인해 주세요.</p>
        
        <form @submit.prevent="handleLogin">
          <div class="input-group">
            <label>이메일</label>
            <input type="email" v-model="email" placeholder="example@email.com" required />
          </div>
          
          <div class="input-group">
            <label>비밀번호</label>
            <input type="password" v-model="password" placeholder="••••••••" required />
          </div>
          
          <button type="submit" :disabled="isLoading">
            {{ isLoading ? '로그인 중...' : '로그인' }}
          </button>
        </form>
        
        <div class="footer-links">
          <span>계정이 없으신가요?</span>
          <router-link to="/join">회원가입</router-link>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useUserStore } from '../stores/user'
  
  const email = ref('')
  const password = ref('')
  const isLoading = ref(false)
  const router = useRouter()
  const userStore = useUserStore()
  
  // 로그인 페이지 버튼 클릭 시 동작하는 함수
  const handleLogin = async () => {
    isLoading.value = true
    
    try {
      // 로그인 인증 서버에 요청 전송
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: email.value,
          password: password.value
        })
      });
      // 서버 측 응답 추출
      const data = await res.json();
      if (data.success && data.user) {
        // 사용자 정보를 store에 저장
        userStore.setUser(data.user);
        router.push('/');
      }
    } catch (err) {
      console.error(err);
    } finally {
      isLoading.value = false
    }
  }
  </script>
  
  <style scoped>
  .login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f5f7fa;
  }
  
  .login-box {
    background: white;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
    text-align: center;
  }
  
  h1 {
    margin-bottom: 10px;
    color: #2c3e50;
  }
  
  .subtitle {
    color: #7f8c8d;
    margin-bottom: 30px;
  }
  
  .input-group {
    text-align: left;
    margin-bottom: 20px;
  }
  
  .input-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: bold;
  }
  
  input {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    box-sizing: border-box;
  }
  
  button {
    width: 100%;
    padding: 14px;
    background-color: #42b883;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    cursor: pointer;
    transition: background 0.3s;
  }
  
  button:hover {
    background-color: #3aa876;
  }
  
  .footer-links {
    margin-top: 20px;
    font-size: 14px;
  }
  
  a {
    color: #42b883;
    text-decoration: none;
    margin-left: 8px;
  }
  </style>