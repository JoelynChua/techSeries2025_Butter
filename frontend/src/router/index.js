import { createRouter, createWebHistory } from 'vue-router'
import closeFriendsRoutes from '../modules/close-friends/routes.js'
import QuizPage from '../modules/QuizPage.vue'
import Profile from '../modules/profile.vue'

// Lazy-load to avoid bundling issues
const HomePage = () => import('../modules/homepage.vue')
const CloseFriendPage = () => import('../modules/close-friends/pages/CloseFriendsPage.vue')
const LoginPage = () => import('../modules/Login.vue')
const SignUpPage = () => import('../modules/Signup.vue')

const routes = [
  ...closeFriendsRoutes,

  { path: '/quiz', name: 'Quiz', component: QuizPage },

  // 🔑 Default root now goes to Login
  { path: '/', redirect: { name: 'Login' } },

  // Optional secondary home path
  { path: '/homepage', name: 'Home', component: HomePage },

  { path: '/close-friends', name: 'CloseFriends', component: CloseFriendPage },

  { path: '/login', name: 'Login', component: LoginPage },
  { path: '/signup', name: 'SignUp', component: SignUpPage },

  ...closeFriendsRoutes,

  { path: '/profile', name: 'profile', component: Profile },

  // Catch-all → redirect to Login (instead of Home)
  { path: '/:pathMatch(.*)*', redirect: { name: 'Login' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
