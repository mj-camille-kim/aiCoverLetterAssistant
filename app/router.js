import { createRouter, createWebHistory } from 'vue-router'
import Login from './pages/Login.vue'
import Join from './pages/Join.vue'
import Main from './pages/Main.vue'

const routes = [
  { path: '/', component: Main },
  { path: '/login', component: Login },
  { path: '/join', component: Join },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router