import { createRouter, createWebHistory } from 'vue-router';
import StageConfig from '../pages/StageConfig.vue';
import ProjectProgressManagement from '../pages/ProjectProgressManagement.vue';

const routes = [
  {
    path: '/',
    redirect: '/stage-config'
  },
  {
    path: '/stage-config',
    name: 'StageConfig',
    component: StageConfig
  },
  {
    path: '/project-progress',
    name: 'ProjectProgress',
    component: ProjectProgressManagement
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
