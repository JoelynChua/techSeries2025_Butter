import { createRouter, createWebHistory } from 'vue-router'
import closeFriendsRoutes from '../modules/close-friends/routes.js'
import QuizPage from '../modules/quiz/pages/QuizPage.vue'

// Lazy-load to avoid bundling issues
const HomePage = () => import('../modules/homepage.vue')
const CloseFriendPage = () => import('../modules/close-friends/pages/CloseFriendsPage.vue')

const routes = [
  ...closeFriendsRoutes,
  {
    path: '/quiz', name: 'Quiz',component: QuizPage},
  { path: '/', name: 'Home', component: HomePage },
  { path: '/homepage', redirect: { name: 'Home' } },

  // ✅ Direct route to close-friend page
  { path: '/close-friends', name: 'CloseFriends', component: CloseFriendPage },

  // ✅ Include any child routes defined in closeFriendsRoutes
  ...closeFriendsRoutes,

  // Catch-all → redirect home
  { path: '/:pathMatch(.*)*', redirect: { name: 'Home' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
