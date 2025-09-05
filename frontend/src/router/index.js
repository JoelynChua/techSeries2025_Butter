import { createRouter, createWebHistory } from 'vue-router'
import closeFriendsRoutes from '../modules/close-friends/routes.js'
import QuizPage from '../modules/QuizPage.vue'
import Profile from '../modules/profile.vue'

// Lazy-load to avoid bundling issues
const HomePage = () => import('../modules/homepage.vue')
const CloseFriendPage = () => import('../modules/close-friends/pages/CloseFriendsPage.vue')
const LoginPage = () => import('../modules/Login.vue') // Import Login.vue
const SignUpPage = () => import('../modules/SignUp.vue') // Import SignUp.vue

const routes = [
  ...closeFriendsRoutes,

  { path: '/quiz', name: 'Quiz', component: QuizPage },

  { path: '/', name: 'Home', component: HomePage },
  { path: '/homepage', redirect: { name: 'Home' } },

  // ✅ Direct route to close-friend page
  { path: '/close-friends', name: 'CloseFriends', component: CloseFriendPage },

  // ✅ Add Login route
  { path: '/login', name: 'Login', component: LoginPage },

  // ✅ Add SignUp route
  { path: '/signup', name: 'SignUp', component: SignUpPage },

  // ✅ Include any child routes defined in closeFriendsRoutes
  ...closeFriendsRoutes,

  { path: '/profile', name: 'profile', component: Profile },

  // Catch-all → redirect home
  { path: '/:pathMatch(.*)*', redirect: { name: 'Home' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router