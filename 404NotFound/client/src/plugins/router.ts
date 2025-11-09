import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/pages/Dashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: () => import('@/pages/Analytics.vue'),
  },
  {
    path: '/returns',
    name: 'Returns',
    component: () => import('@/pages/Returns.vue'),
  },
  {
    path: '/shopify/:platformId/products',
    name: 'ShopifyProducts',
    component: () => import('@/pages/ShopifyProducts.vue'),
    props: true,
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
