import { createRouter, createWebHistory } from 'vue-router'
import closeFriendsRoutes from '../modules/close-friends/routes.js'

const routes = [
  ...closeFriendsRoutes
]

const router = createRouter({ history: createWebHistory(), routes })
export default router
