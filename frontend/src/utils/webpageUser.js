const STORAGE_KEY = 'webpage_user_id';

const normalizeWebpageUserId = (value) => {
  if (value === null || value === undefined) return '';
  return String(value).trim();
};

const readHashQueryUserId = () => {
  if (typeof window === 'undefined') return '';
  const hash = String(window.location.hash || '');
  const queryIndex = hash.indexOf('?');
  if (queryIndex === -1) return '';
  const params = new URLSearchParams(hash.slice(queryIndex + 1));
  return normalizeWebpageUserId(
    params.get('webpage_user_id') || params.get('user_id')
  );
};

const readSearchUserId = () => {
  if (typeof window === 'undefined') return '';
  const params = new URLSearchParams(window.location.search);
  return normalizeWebpageUserId(
    params.get('webpage_user_id') || params.get('user_id')
  );
};

export const readStoredWebpageUserId = () => {
  if (typeof window === 'undefined') return '';
  try {
    return normalizeWebpageUserId(window.sessionStorage.getItem(STORAGE_KEY));
  } catch (error) {
    console.warn('读取 webpage_user_id 缓存失败：', error);
    return '';
  }
};

export const storeWebpageUserId = (userId) => {
  if (typeof window === 'undefined') return;
  const normalized = normalizeWebpageUserId(userId);
  try {
    if (normalized) {
      window.sessionStorage.setItem(STORAGE_KEY, normalized);
    } else {
      window.sessionStorage.removeItem(STORAGE_KEY);
    }
  } catch (error) {
    console.warn('保存 webpage_user_id 缓存失败：', error);
  }
};

export const resolveWebpageUserId = (route = null) => {
  const queryValue = normalizeWebpageUserId(
    route?.query?.webpage_user_id || route?.query?.user_id
  );
  const resolved =
    queryValue ||
    readSearchUserId() ||
    readHashQueryUserId() ||
    readStoredWebpageUserId();

  if (resolved) {
    storeWebpageUserId(resolved);
  }
  return resolved;
};

export const mergeWebpageUserQuery = (target, route = null) => {
  const userId = resolveWebpageUserId(route);
  if (!userId) return target;

  if (typeof target === 'string') {
    return {
      path: target,
      query: {
        webpage_user_id: userId
      }
    };
  }

  const nextTarget = target && typeof target === 'object' ? { ...target } : {};
  nextTarget.query = {
    ...(nextTarget.query || {}),
    webpage_user_id: userId
  };
  return nextTarget;
};
