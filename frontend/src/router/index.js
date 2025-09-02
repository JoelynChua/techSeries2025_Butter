import { createRouter, createWebHistory } from 'vue-router'
import closeFriendsRoutes from '../modules/close-friends/routes.js'
import QuizPage from '../modules/quiz/pages/QuizPage.vue'

const routes = [
  ...closeFriendsRoutes,
  {
    path: '/quiz',
    name: 'Quiz',
    component: QuizPage
  }
]

const router = createRouter({ history: createWebHistory(), routes })
export default router
