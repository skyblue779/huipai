import { createRouter, createWebHistory } from 'vue-router';
import StageConfig from '../pages/StageConfig.vue';
import ProjectCostConfig from '../pages/ProjectCostConfig.vue';
import ProjectProgressManagement from '../pages/ProjectProgressManagement.vue';
import ProjectExecution from '../pages/ProjectExecution.vue';

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
    path: '/project-cost-config',
    name: 'ProjectCostConfig',
    component: ProjectCostConfig
  },
  {
    path: '/project-progress',
    name: 'ProjectProgress',
    component: ProjectProgressManagement
  },
  {
    path: '/project-execution',
    name: 'ProjectExecution',
    component: ProjectExecution
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
