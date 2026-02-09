const DEFAULT_BASE_URL = 'http://172.16.0.66:9989';

const normalizeBaseUrl = (url) => url.replace(/\/+$/, '');

const resolveBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl && String(envUrl).trim()) {
    return normalizeBaseUrl(String(envUrl).trim());
  }
  return normalizeBaseUrl(DEFAULT_BASE_URL);
};

const baseUrl = resolveBaseUrl();

const buildUrl = (endpoint) => {
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${baseUrl}${normalizedEndpoint}`;
};

const parseResponse = async (response) => {
  let payload = null;
  try {
    payload = await response.json();
  } catch (error) {
    payload = null;
  }

  if (!response.ok) {
    const message = payload?.msg || `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return payload;
};

const request = async (method, endpoint, data) => {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json'
    }
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(buildUrl(endpoint), options);
  return parseResponse(response);
};

const requestForm = async (method, endpoint, formData) => {
  const options = {
    method,
    body: formData
  };
  const response = await fetch(buildUrl(endpoint), options);
  return parseResponse(response);
};

const listProjectTypes = ({ skip = 0, limit = 300 } = {}) => {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit)
  });
  return request('GET', `/api/project-type/list?${params.toString()}`);
};

const listCostTypes = ({ skip = 0, limit = 300 } = {}) => {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit)
  });
  return request('GET', `/api/cost-type/list?${params.toString()}`);
};

const listStages = ({ skip = 0, limit = 300, projectType = '' } = {}) => {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit)
  });
  if (projectType) {
    params.set('project_type', projectType);
  }
  return request('GET', `/api/stage/list?${params.toString()}`);
};

const listCostStages = ({ skip = 0, limit = 300, projectType = '' } = {}) => {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit)
  });
  if (projectType) {
    params.set('project_type', projectType);
  }
  return request('GET', `/api/cost-stage/list?${params.toString()}`);
};

const createStage = (data) => request('POST', '/api/stage/create', data);
const updateStage = (dataId, data) => request('PUT', `/api/stage/update/${dataId}`, data);
const deleteStage = (dataId) => request('DELETE', `/api/stage/delete/${dataId}`);

const createCostStage = (data) => request('POST', '/api/cost-stage/create', data);
const updateCostStage = (dataId, data) => request('PUT', `/api/cost-stage/update/${dataId}`, data);
const deleteCostStage = (dataId) => request('DELETE', `/api/cost-stage/delete/${dataId}`);

const listProjectProgress = ({ skip = 0, limit = 300, search = '', projectCode = '', projectName = '' } = {}) => {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit)
  });
  if (search) {
    params.set('search', search);
  }
  if (projectCode) {
    params.set('project_code', projectCode);
  }
  if (projectName) {
    params.set('project_name', projectName);
  }
  return request('GET', `/api/progress/list?${params.toString()}`);
};

const listProjectSummary = ({ skip = 0, limit = 300, search = '', projectCode = '', projectName = '' } = {}) => {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit)
  });
  if (search) {
    params.set('search', search);
  }
  if (projectCode) {
    params.set('project_code', projectCode);
  }
  if (projectName) {
    params.set('project_name', projectName);
  }
  return request('GET', `/api/project/list-summary?${params.toString()}`);
};

const createProjectProgress = (data) => request('POST', '/api/progress/create', data);
const updateProjectProgress = (dataId, data) => request('PUT', `/api/progress/update/${dataId}`, data);
const deleteProjectProgress = (dataId) => request('DELETE', `/api/progress/delete/${dataId}`);
const uploadProjectProgressFiles = (files) => {
  if (files instanceof FormData) {
    return requestForm('POST', '/api/progress/upload', files);
  }
  return request('POST', '/api/progress/upload', files);
};

const listProjectBudgets = ({
  skip = 0,
  limit = 300,
  search = '',
  projectCode = '',
  projectName = '',
  projectType = '',
  costCenter = '',
  costItem = '',
  status = '',
  mainStageOrder = '',
  projectStageOrder = ''
} = {}) => {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit)
  });
  if (search) params.set('search', search);
  if (projectCode) params.set('project_code', projectCode);
  if (projectName) params.set('project_name', projectName);
  if (projectType) params.set('project_type', projectType);
  if (costCenter) params.set('cost_center', costCenter);
  if (costItem) params.set('cost_item', costItem);
  if (status) params.set('status', status);
  if (mainStageOrder) params.set('main_stage_order', mainStageOrder);
  if (projectStageOrder) params.set('project_stage_order', projectStageOrder);
  return request('GET', `/api/project-budget/list?${params.toString()}`);
};

const listDeliveries = ({
  skip = 0,
  limit = 300,
  search = '',
  deliveryNo = '',
  projectName = '',
  orderNo = '',
  status = ''
} = {}) => {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit)
  });
  if (search) params.set('search', search);
  if (deliveryNo) params.set('delivery_no', deliveryNo);
  if (projectName) params.set('project_name', projectName);
  if (orderNo) params.set('order_no', orderNo);
  if (status) params.set('status', status);
  return request('GET', `/api/delivery/list?${params.toString()}`);
};

const listInspections = ({ skip = 0, limit = 300, search = '', inspectionProject = '' } = {}) => {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit)
  });
  if (search) params.set('search', search);
  if (inspectionProject) params.set('inspection_project', inspectionProject);
  return request('GET', `/api/inspection/list?${params.toString()}`);
};

const createDelivery = (data) => request('POST', '/api/delivery/create', data);
const updateDelivery = (dataId, data) => request('PUT', `/api/delivery/update/${dataId}`, data);
const deleteDelivery = (dataId) => request('DELETE', `/api/delivery/delete/${dataId}`);
const uploadDeliveryFiles = (files) => {
  if (files instanceof FormData) {
    return requestForm('POST', '/api/delivery/upload', files);
  }
  return request('POST', '/api/delivery/upload', files);
};

const createProjectBudget = (data) => request('POST', '/api/project-budget/create', data);
const updateProjectBudget = (dataId, data) => request('PUT', `/api/project-budget/update/${dataId}`, data);
const deleteProjectBudget = (dataId) => request('DELETE', `/api/project-budget/delete/${dataId}`);
const uploadProjectBudgetFiles = (files) => {
  if (files instanceof FormData) {
    return requestForm('POST', '/api/project-budget/upload', files);
  }
  return request('POST', '/api/project-budget/upload', files);
};

const listUsers = () => request('GET', '/api/user/list');
const getUserInfo = (userId) => request('GET', `/api/user/info/${userId}`);

export default {
  listProjectTypes,
  listCostTypes,
  listStages,
  listCostStages,
  createStage,
  updateStage,
  deleteStage,
  createCostStage,
  updateCostStage,
  deleteCostStage,
  listProjectProgress,
  listProjectSummary,
  createProjectProgress,
  updateProjectProgress,
  deleteProjectProgress,
  uploadProjectProgressFiles,
  listProjectBudgets,
  createProjectBudget,
  updateProjectBudget,
  deleteProjectBudget,
  uploadProjectBudgetFiles,
  listDeliveries,
  listInspections,
  createDelivery,
  updateDelivery,
  deleteDelivery,
  uploadDeliveryFiles,
  listUsers,
  getUserInfo
};
