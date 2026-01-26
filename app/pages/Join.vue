<template>
    <div class="join-container">
      <div class="join-box">
        <h1>회원가입</h1>
        <form @submit.prevent="handleJoin">
          <div class="input-group">
            <label>이메일</label>
            <input type="email" v-model="email" placeholder="example@email.com" required />
          </div>
          
          <div class="input-group">
            <label>비밀번호</label>
            <input type="password" v-model="password" placeholder="8자 이상 입력" required />
          </div>
  
          <div class="input-group">
            <label>비밀번호 확인</label>
            <input type="password" v-model="passwordConfirm" placeholder="비밀번호 재입력" required />
          </div>

          <div class="input-group">
            <label>사용자명</label>
            <input type="text" v-model="nickName" placeholder="홍길동" required />
          </div>
          
          <button type="submit" :disabled="isLoading">
            {{ isLoading ? '가입 처리 중...' : '회원가입' }}
          </button>
        </form>
        
        <div class="footer-links">
          <span>이미 계정이 있으신가요?</span>
          <router-link to="/login">로그인하기</router-link>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  
  const router = useRouter()
  const email = ref('')
  const password = ref('')
  const nickName = ref('')
  const passwordConfirm = ref('')
  const isLoading = ref(false)
  
  const handleJoin = async () => {
    if (password.value !== passwordConfirm.value) {
      alert('비밀번호가 일치하지 않습니다!')
      return
    }
  
    isLoading.value = true
    
    try {
      const response = await fetch('/api/auth/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: email.value,
          password: password.value,
          nickName: nickName.value
        })
      });
      const data = await response.json();
      if (response.ok) {
        alert(data.message);
        router.push('/login');
      } else {
        alert(data.message);
      }

    } catch (error) {
        console.error(error);
        alert('회원가입 실패');
    } finally {
        isLoading.value = false
    }
  }
  </script>
  
  <style scoped>
  .join-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f5f7fa;
  }
  
  .join-box {
    background: white;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
    text-align: center;
  }
  
  h1 { margin-bottom: 10px; color: #2c3e50; }
  .subtitle { color: #7f8c8d; margin-bottom: 30px; }
  .input-group { text-align: left; margin-bottom: 20px; }
  .input-group label { display: block; margin-bottom: 8px; font-weight: bold; }
  input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
  
  button {
    width: 100%; padding: 14px; background-color: #42b883; color: white;
    border: none; border-radius: 6px; font-size: 16px; cursor: pointer;
    transition: background 0.3s; margin-top: 10px;
  }
  
  button:hover { background-color: #3aa876; }
  .footer-links { margin-top: 20px; font-size: 14px; }
  a { color: #42b883; text-decoration: none; margin-left: 8px; }
  </style>