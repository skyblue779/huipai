import { createRouter, createWebHistory } from 'vue-router';
import StageConfig from '../pages/StageConfig.vue';
import ProjectCostConfig from '../pages/ProjectCostConfig.vue';
import ProjectBudgetManagement from '../pages/ProjectBudgetManagement.vue';
import ProjectProgressManagement from '../pages/ProjectProgressManagement.vue';
import ProjectExecution from '../pages/ProjectExecution.vue';
import OverallBudgetDashboard from '../pages/OverallBudgetDashboard.vue';
import ProjectControlDashboard from '../pages/ProjectControlDashboard.vue';
import DeliveryManagement from '../pages/DeliveryManagement.vue';

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
    path: '/overall-budget-dashboard',
    name: 'OverallBudgetDashboard',
    component: OverallBudgetDashboard
  },
  {
    path: '/project-control-dashboard',
    name: 'ProjectControlDashboard',
    component: ProjectControlDashboard
  },
  {
    path: '/project-cost-config',
    name: 'ProjectCostConfig',
    component: ProjectCostConfig
  },
  {
    path: '/project-budget-management',
    name: 'ProjectBudgetManagement',
    component: ProjectBudgetManagement
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
  },
  {
    path: '/delivery-management',
    name: 'DeliveryManagement',
    component: DeliveryManagement
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
