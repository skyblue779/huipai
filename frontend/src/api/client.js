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

const listProjectTypes = ({ skip = 0, limit = 300 } = {}) => {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit)
  });
  return request('GET', `/api/project-type/list?${params.toString()}`);
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

const createStage = (data) => request('POST', '/api/stage/create', data);
const updateStage = (dataId, data) => request('PUT', `/api/stage/update/${dataId}`, data);
const deleteStage = (dataId) => request('DELETE', `/api/stage/delete/${dataId}`);

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

const createProjectProgress = (data) => request('POST', '/api/progress/create', data);
const updateProjectProgress = (dataId, data) => request('PUT', `/api/progress/update/${dataId}`, data);
const deleteProjectProgress = (dataId) => request('DELETE', `/api/progress/delete/${dataId}`);
const uploadProjectProgressFiles = (files) => request('POST', '/api/progress/upload', files);

const listUsers = () => request('GET', '/api/user/list');
const getUserInfo = (userId) => request('GET', `/api/user/info/${userId}`);

export default {
  listProjectTypes,
  listStages,
  createStage,
  updateStage,
  deleteStage,
  listProjectProgress,
  createProjectProgress,
  updateProjectProgress,
  deleteProjectProgress,
  uploadProjectProgressFiles,
  listUsers,
  getUserInfo
};
