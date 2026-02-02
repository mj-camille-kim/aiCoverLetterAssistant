import { createRouter, createWebHistory } from 'vue-router'
import Login from './pages/Login.vue'
import Join from './pages/Join.vue'
import Main from './pages/Main.vue'
import ExpUpload from './pages/ExpUpload.vue'
import Editor from './pages/Editor.vue'
import ExpStore from './pages/ExpStore.vue'
import MyPage from './pages/MyPage.vue'

const routes = [
  { path: '/', component: Main },
  { path: '/login', component: Login },
  { path: '/join', component: Join },
  { path: '/upload', component: ExpUpload },
  { path: '/editor', component: Editor },
  { path: '/storage', component: ExpStore },
  { path: '/mypage', component: MyPage}
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router