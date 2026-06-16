import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/models' },
    {
      path: '/models',
      name: 'models',
      component: () => import('../views/ModelsView.vue'),
    },
    {
      path: '/models/:id',
      name: 'model-detail',
      component: () => import('../views/ModelDetailView.vue'),
    },
    {
      path: '/training',
      name: 'training',
      component: () => import('../views/TrainingView.vue'),
    },
    {
      path: '/training/:id',
      name: 'training-detail',
      component: () => import('../views/TrainingDetailView.vue'),
    },
    {
      path: '/evaluation',
      name: 'evaluation',
      component: () => import('../views/EvaluationView.vue'),
    },
    {
      path: '/evaluation/:id',
      name: 'evaluation-detail',
      component: () => import('../views/EvaluationDetailView.vue'),
    },
    {
      path: '/publishing',
      name: 'publishing',
      component: () => import('../views/PublishView.vue'),
    },
  ],
})

export default router
