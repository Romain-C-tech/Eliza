import { createRouter, createWebHistory } from 'vue-router'
import DocsLayout from '../views/DocsLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: () => import('../views/HomeView.vue') },
    {
      path: '/docs',
      name: 'documentations',
      component: DocsLayout,
      children: [
        { path: '', name: 'docs-home', component: () => import('../views/DocsHome.vue') },
        { path: 'installation', name: 'docs-install', component: () => import('../views/DocsSection/InstallSection.vue') },
        { 
          path: 'commandes',
          name: 'docs-commands',
          children: [
            { path: '', name: 'docs-commands-home', component: () => import('../views/DocsSection/CommandsSection.vue') },
            { path: 'setup', name: 'docs-command-setup', component: () => import('../views/Commands/SetupCommandDetail.vue') },
            { path: 'cancel', name: 'docs-command-cancel', component: () => import('../views/Commands/CancelCommandDetail.vue') },
          ] 
        },
        { path: 'feature', name: 'docs-features', component: () => import('../views/DocsSection/FeatureSection.vue') },
      ],
    },
    { path: '/premium', name: 'premium', component: () => import('../views/PremiumView.vue') },
  ],
})

export default router