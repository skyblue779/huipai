import { createRouter, createWebHistory } from 'vue-router';
import StageConfig from '../pages/StageConfig.vue';
import ProjectCostConfig from '../pages/ProjectCostConfig.vue';
import ProjectBudgetManagement from '../pages/ProjectBudgetManagement.vue';
import MyBudgetResponsibilities from '../pages/MyBudgetResponsibilities.vue';
import ProjectProgressManagement from '../pages/ProjectProgressManagement.vue';
import ProjectExecution from '../pages/ProjectExecution.vue';
import OverallBudgetDashboard from '../pages/OverallBudgetDashboard.vue';
import ProjectControlDashboard from '../pages/ProjectControlDashboard.vue';
import DeliveryManagement from '../pages/DeliveryManagement.vue';
import InspectionDeliveryManagement from '../pages/InspectionDeliveryManagement.vue';
import InspectionDeliveryMobile from '../pages/InspectionDeliveryMobile.vue';
import Workbench from '../pages/Workbench.vue';
import { readStoredWebpageUserId, resolveWebpageUserId, storeWebpageUserId } from '../utils/webpageUser';

const routes = [
  {
    path: '/',
    redirect: '/workbench'
  },
  {
    path: '/workbench',
    name: 'Workbench',
    component: Workbench
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
    path: '/my-budget-responsibilities',
    name: 'MyBudgetResponsibilities',
    component: MyBudgetResponsibilities
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
  },
  {
    path: '/inspection-delivery-management',
    name: 'InspectionDeliveryManagement',
    component: InspectionDeliveryManagement
  },
  {
    path: '/inspection-delivery-mobile',
    name: 'InspectionDeliveryMobile',
    component: InspectionDeliveryMobile
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const currentUserId = resolveWebpageUserId(to) || resolveWebpageUserId(from) || readStoredWebpageUserId();
  if (!currentUserId) {
    next();
    return;
  }

  storeWebpageUserId(currentUserId);
  const targetUserId = String(to.query?.webpage_user_id || '').trim();
  if (targetUserId === currentUserId) {
    next();
    return;
  }

  next({
    name: to.name || undefined,
    path: to.name ? undefined : to.path,
    params: to.params,
    hash: to.hash,
    replace: true,
    query: {
      ...to.query,
      webpage_user_id: currentUserId
    }
  });
});

export default router;
