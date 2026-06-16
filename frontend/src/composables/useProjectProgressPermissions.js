import { computed, ref } from 'vue';
import { ElMessage } from 'element-plus';
import api from '../api/client';
import { getProjectStageLabel, normalizeLabel } from '../utils/projectProgress';
import { resolveWebpageUserId } from '../utils/webpageUser';

const USER_TOKEN_KEYS = [
  'user_id',
  'userid',
  'userId',
  '_id',
  'id',
  'account',
  'name',
  'username',
  'user_name',
  'userName',
  'nickname',
  'realname',
  'uniqueid',
  'mobile',
  'email'
];

const normalizeToken = (value) => normalizeLabel(value).toLowerCase();

const isSameUserToken = (left, right) => {
  const leftToken = normalizeToken(left);
  const rightToken = normalizeToken(right);
  return Boolean(leftToken && rightToken && leftToken === rightToken);
};

const collectUserTokens = (value) => {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value.flatMap((item) => collectUserTokens(item));
  }
  if (typeof value === 'object') {
    return USER_TOKEN_KEYS.flatMap((key) => collectUserTokens(value?.[key]));
  }
  const token = normalizeToken(value);
  return token ? [token] : [];
};

export const useProjectProgressPermissions = (route) => {
  const userParam = ref('');
  const userProfile = ref({
    user_id: '',
    name: '',
    account: ''
  });
  const projectManagerMembers = ref([]);
  const projectManagerLoading = ref(false);

  const currentUserTokens = computed(
    () =>
      new Set(
        collectUserTokens([
          userParam.value,
          userProfile.value
        ])
      )
  );

  const userValueMatchesCurrentUser = (value) => {
    const tokens = currentUserTokens.value;
    if (!tokens.size) return false;
    return collectUserTokens(value).some((token) => tokens.has(token));
  };

  const isProjectManager = computed(() =>
    projectManagerMembers.value.some((member) => userValueMatchesCurrentUser(member))
  );

  const loadProjectManagers = async () => {
    if (projectManagerLoading.value) return;
    projectManagerLoading.value = true;
    try {
      const result = await api.listProjectManagers();
      if (result?.code === 200 && Array.isArray(result.data)) {
        projectManagerMembers.value = result.data;
      } else {
        projectManagerMembers.value = [];
        ElMessage.warning(result?.msg || '项目管理员权限加载失败，当前按只读模式处理');
      }
    } catch (error) {
      console.error('加载项目管理员成员失败：', error);
      projectManagerMembers.value = [];
      ElMessage.warning('项目管理员权限加载失败，当前按只读模式处理');
    } finally {
      projectManagerLoading.value = false;
    }
  };

  const resolveUserProfile = async () => {
    if (!userParam.value) return;
    try {
      const result = await api.getUserInfo(userParam.value);
      if (result?.code === 200 && result.data) {
        userProfile.value = {
          ...result.data,
          user_id: result.data.user_id || result.data._id || result.data.id || userParam.value,
          name: result.data.name || '',
          account: result.data.account || ''
        };
        return;
      }
    } catch (error) {
      console.warn('用户信息查询失败，尝试使用项目管理员列表匹配。', error);
    }

    const matchedMember = projectManagerMembers.value.find(
      (item) =>
        isSameUserToken(item?.user_id, userParam.value) ||
        isSameUserToken(item?.account, userParam.value) ||
        isSameUserToken(item?.name, userParam.value) ||
        isSameUserToken(item?.uniqueid, userParam.value)
    );

    if (matchedMember) {
      userProfile.value = {
        ...matchedMember,
        user_id: matchedMember.user_id || userParam.value,
        name: matchedMember.name || '',
        account: matchedMember.account || ''
      };
      return;
    }

    try {
      const result = await api.listUsers();
      if (result?.code === 200 && Array.isArray(result.data)) {
        const match = result.data.find(
          (item) =>
            isSameUserToken(item?.user_id, userParam.value) ||
            isSameUserToken(item?.account, userParam.value) ||
            isSameUserToken(item?.name, userParam.value) ||
            isSameUserToken(item?.uniqueid, userParam.value)
        );
        if (match) {
          userProfile.value = {
            ...match,
            user_id: match.user_id || userParam.value,
            name: match.name || '',
            account: match.account || ''
          };
        }
      }
    } catch (error) {
      console.warn('成员列表匹配失败。', error);
    }
  };

  const syncCurrentUser = async () => {
    const nextUserId = resolveWebpageUserId(route);
    if (nextUserId === userParam.value) {
      return;
    }

    userParam.value = nextUserId;
    userProfile.value = {
      user_id: '',
      name: '',
      account: ''
    };

    if (!userParam.value) {
      ElMessage.warning('未获取到用户ID，当前按只读模式处理');
      return;
    }

    await resolveUserProfile();
  };

  const ensureProjectManagerAction = (message = '仅项目管理员可操作') => {
    if (isProjectManager.value) return true;
    ElMessage.warning(message);
    return false;
  };

  const canManageNode = (row) =>
    Boolean(isProjectManager.value && row && !row.isGroup && row.recordId && getProjectStageLabel(row));

  return {
    userParam,
    userProfile,
    projectManagerMembers,
    projectManagerLoading,
    isProjectManager,
    loadProjectManagers,
    resolveUserProfile,
    syncCurrentUser,
    ensureProjectManagerAction,
    canManageNode,
    userValueMatchesCurrentUser
  };
};
