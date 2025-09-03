import { createRouter, createWebHistory } from 'vue-router'
import closeFriendsRoutes from '../modules/close-friends/routes.js'
import QuizPage from '../modules/quiz/pages/QuizPage.vue'

// Lazy-load to avoid bundling issues; adjust the path to where your file is.
const HomePage = () => import('../modules/homepage.vue') // e.g. '../pages/homepage.vue' if you moved it

const routes = [
  ...closeFriendsRoutes,
  {
    path: '/quiz', name: 'Quiz',component: QuizPage},
  { path: '/', name: 'Home', component: HomePage },
  // Optional: allow /homepage URL too
  { path: '/homepage', redirect: { name: 'Home' } },

  ...closeFriendsRoutes,

  // Optional: catch-all → go home (or show a 404 component)
  { path: '/:pathMatch(.*)*', redirect: { name: 'Home' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
