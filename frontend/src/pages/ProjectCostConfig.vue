<template>
  <el-config-provider :locale="zhCn">
    <div class="main-content">
    <!-- <div class="header">
      <div class="header-title">项目阶段配置管理</div>
      <div class="header-actions"></div>
    </div> -->

    <div class="top-row">
      <el-select
        v-model="selectedProjectType"
        placeholder="选择项目类型"
        @change="handleProjectTypeChange"
      >
        <el-option
          v-for="type in projectTypeOptions"
          :key="type._id"
          :label="type.name"
          :value="type.name"
        />
      </el-select>
      <span class="type-info">
        已加载类型：<strong>{{ projectTypeOptions.length }}</strong>
      </span>
    </div>

    <div class="page-container">
      <div class="config-layout">
        <div class="left-panel">
          <div class="panel-header">
            <span>阶段节点结构</span>
            <el-button type="primary" link :disabled="!selectedProjectType" @click="handleAddStage">
              新增阶段
            </el-button>
          </div>
          <div class="tree-container">
            <div v-if="loading" class="loading-state">
              <el-progress type="circle" :percentage="50" />
            </div>
            <div v-else-if="treeData.length === 0" class="empty-state">
              <p>暂无阶段数据</p>
            </div>
            <el-tree
              v-else
              ref="treeRef"
              :data="treeData"
              node-key="_id"
              :draggable="!savingOrder"
              :allow-drag="allowNodeDrag"
              :allow-drop="allowNodeDrop"
              default-expand-all
              :expand-on-click-node="false"
              @node-click="handleNodeClick"
              @node-drop="handleNodeDrop"
              highlight-current
              :props="treeProps"
            >
              <template #default="{ data }">
                <span class="custom-tree-node">
                  <span class="node-label" @click="handleNodeClick(data)">
                    <el-icon v-if="!data.parent_id" class="node-icon node-icon-root">
                      <Folder />
                    </el-icon>
                    <el-icon v-else class="node-icon node-icon-child">
                      <Document />
                    </el-icon>
                    <span class="node-name">{{ data.name }}</span>
                  </span>
                  <span class="node-actions">
                    <el-button
                      v-if="!isChildNode(data)"
                      type="primary"
                      link
                      size="small"
                      class="icon-action-btn"
                      title="添加子阶段"
                      @click.stop="handleAddNode(data)"
                    >
                      <el-icon><Plus /></el-icon>
                    </el-button>
                    <el-button
                      v-if="!hasChildren(data)"
                      type="danger"
                      link
                      size="small"
                      class="icon-action-btn danger"
                      title="删除"
                      @click.stop="handleDelete(data)"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </span>
                </span>
              </template>
            </el-tree>
          </div>
        </div>

        <div class="right-panel">
          <div v-if="currentNode" class="edit-form">
            <div class="panel-header panel-header-form">
              <span>{{ currentNode.parent_id ? '子阶段编辑' : '阶段信息编辑' }}</span>
              <div class="panel-header-actions">
                <el-button type="danger" plain @click="handleDelete(currentNode)">删除</el-button>
                <el-button type="primary" @click="handleSave">保存修改</el-button>
              </div>
            </div>
            <el-form :model="formData" label-width="100px">
              <el-form-item label="名称 *">
                <el-input v-model="formData.name" />
              </el-form-item>
              <el-form-item label="阶段ID">
                <el-input v-model="formData.id" disabled />
              </el-form-item>
              <el-form-item label="责任人">
                <el-select
                  v-model="formData.responsiblePersonId"
                  filterable
                  clearable
                  placeholder="请选择责任人"
                  style="width: 100%"
                  :loading="memberLoading"
                >
                  <el-option
                    v-for="item in memberOptions"
                    :key="item.id"
                    :label="item.label"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="预算标准">
                <el-input v-model.number="formData.budget_standard" type="number">
                  <template #append>元</template>
                </el-input>
              </el-form-item>
              <el-form-item label="说明">
                <el-input
                  v-model="formData.description"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入阶段说明（可选）"
                />
              </el-form-item>
            </el-form>

            <div class="log-section">
              <div class="panel-header panel-header-form panel-header-muted">
                <span>阶段基本信息</span>
              </div>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="创建时间">
                  {{ currentNode.createTime || '未知' }}
                </el-descriptions-item>
                <el-descriptions-item label="创建人">
                  {{ currentNode.creator?.name || '未知' }}
                </el-descriptions-item>
                <el-descriptions-item label="最后更新">
                  {{ currentNode.updateTime || '未知' }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
          <div v-else class="empty-state">
            <el-icon class="empty-icon"><Edit /></el-icon>
            <p>请在左侧选择阶段进行编辑</p>
          </div>
        </div>
      </div>
    </div>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue';
import { ElMessage, ElMessageBox, ElConfigProvider } from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { Folder, Document, Plus, Delete, Edit } from '@element-plus/icons-vue';
import api from '../api/client';

const loading = ref(false);
const savingOrder = ref(false);
const stages = ref([]);
const treeData = ref([]);
const treeRef = ref(null);
const currentNode = ref(null);
const projectTypeOptions = ref([]);
const selectedProjectType = ref('');
const members = ref([]);
const memberLoading = ref(false);

const formData = reactive({
  _id: '',
  name: '',
  id: '',
  description: '',
  budget_standard: 0,
  responsiblePersonId: ''
});

const treeProps = {
  children: 'children',
  label: 'name'
};

const isRootNode = (nodeData) =>
  !nodeData?.parent_id || nodeData.parent_id === null || nodeData.parent_id === '';

const isChildNode = (nodeData) => Boolean(nodeData) && !isRootNode(nodeData);

const compareBySortOrder = (a, b) =>
  (Number(a?.sort_order) || 0) - (Number(b?.sort_order) || 0);

const getMemberId = (value) => {
  if (!value) return '';
  if (Array.isArray(value)) return getMemberId(value[0]);
  if (typeof value === 'object') {
    return String(value.user_id || value._id || value.id || '').trim();
  }
  return String(value).trim();
};

const getMemberLabel = (value) => {
  if (!value) return '';
  if (Array.isArray(value)) return getMemberLabel(value[0]);
  if (typeof value === 'object') {
    return String(value.name || value.realname || value.account || value.user_id || value._id || value.id || '').trim();
  }
  return String(value).trim();
};

const memberOptions = computed(() =>
  members.value
    .map((item) => {
      const id = getMemberId(item);
      const label = getMemberLabel(item);
      if (!id) return null;
      return {
        id,
        label: label || id
      };
    })
    .filter(Boolean)
);

// 将节点编号转换为可比对的 key
const toKey = (value) => {
  if (value === null || value === undefined || value === '') return null;
  const numeric = Number(value);
  if (!Number.isNaN(numeric)) return numeric;
  const trimmed = String(value).trim();
  if (!trimmed) return null;
  const parsed = Number.parseInt(trimmed, 10);
  return Number.isNaN(parsed) ? trimmed : parsed;
};

// 判断节点是否有子节点
const hasChildren = (nodeData) => {
  const key = toKey(nodeData?.id);
  if (key === null) return false;
  return stages.value.some((stage) => toKey(stage.parent_id) === key);
};

// 生成树形结构数据（按排序字段排序）
const buildTreeData = (stageList = stages.value) => {
  if (!Array.isArray(stageList) || stageList.length === 0) return [];

  const buildTree = (nodes) =>
    [...nodes]
      .sort(compareBySortOrder)
      .map((node) => {
        const nodeKey = toKey(node.id);
        const children = stageList.filter((stage) => toKey(stage.parent_id) === nodeKey);
        const nodeData = { ...node };
        if (children.length > 0) {
          nodeData.children = buildTree(children);
        }
        return nodeData;
      });

  const roots = stageList.filter((stage) => isRootNode(stage));
  return buildTree(roots);
};

const syncTreeData = (stageList = stages.value) => {
  treeData.value = buildTreeData(stageList);
};

const getSiblingNodesFromTree = (parentKey) => {
  if (parentKey === null) return [];
  const parentNode = treeData.value.find((node) => toKey(node.id) === parentKey);
  return Array.isArray(parentNode?.children) ? parentNode.children : [];
};

const getSiblingOrderSnapshot = (parentKey) =>
  stages.value
    .filter((stage) => toKey(stage.parent_id) === parentKey)
    .sort(compareBySortOrder)
    .map((stage) => stage._id)
    .filter(Boolean);

const restoreCurrentSelection = async (nodeId) => {
  if (!nodeId) return;
  await nextTick();
  if (treeRef.value) {
    treeRef.value.setCurrentKey(nodeId);
  }
  const freshNode = stages.value.find((stage) => stage._id === nodeId);
  if (freshNode) {
    handleNodeClick(freshNode);
  }
};

const allowNodeDrag = (node) => isChildNode(node?.data);

const allowNodeDrop = (draggingNode, dropNode, type) => {
  if (type === 'inner') return false;

  const draggingData = draggingNode?.data;
  const dropData = dropNode?.data;
  if (!isChildNode(draggingData) || !isChildNode(dropData)) {
    return false;
  }

  return toKey(draggingData.parent_id) === toKey(dropData.parent_id);
};

const handleNodeDrop = async (draggingNode, dropNode) => {
  const draggingData = draggingNode?.data;
  const dropData = dropNode?.data;
  const parentKey = toKey(dropData?.parent_id);

  if (!isChildNode(draggingData) || !isChildNode(dropData) || parentKey === null) {
    syncTreeData();
    return;
  }

  if (savingOrder.value) {
    syncTreeData();
    return;
  }

  const siblings = getSiblingNodesFromTree(parentKey).filter((node) => node?._id);
  if (siblings.length === 0) {
    syncTreeData();
    return;
  }

  const previousOrder = getSiblingOrderSnapshot(parentKey);
  const nextOrder = siblings.map((node) => node._id);
  const hasOrderChanged =
    previousOrder.length !== nextOrder.length ||
    previousOrder.some((nodeId, index) => nodeId !== nextOrder[index]);

  if (!hasOrderChanged) {
    return;
  }

  const activeNodeId = draggingData?._id || currentNode.value?._id;
  savingOrder.value = true;
  try {
    await Promise.all(
      siblings.map((node, index) =>
        api.updateCostStage(node._id, {
          sort_order: index + 1
        })
      )
    );

    ElMessage.success('子阶段顺序已更新');
    await loadStages();
    await restoreCurrentSelection(activeNodeId);
  } catch (error) {
    console.error('更新子阶段顺序失败：', error);
    try {
      await loadStages();
      await restoreCurrentSelection(activeNodeId);
    } catch (reloadError) {
      console.error('恢复阶段数据失败：', reloadError);
      syncTreeData();
    }
    ElMessage.error(error?.message || '更新子阶段顺序失败');
  } finally {
    savingOrder.value = false;
  }
};

// 清空当前选中与表单数据
const resetSelection = () => {
  currentNode.value = null;
  formData._id = '';
  formData.name = '';
  formData.id = '';
  formData.description = '';
  formData.budget_standard = 0;
  formData.responsiblePersonId = '';
};

const ensureCurrentResponsibleOption = (value) => {
  const id = getMemberId(value);
  if (!id || members.value.some((item) => getMemberId(item) === id)) return;
  members.value = [
    ...members.value,
    {
      user_id: id,
      name: getMemberLabel(value) || id
    }
  ];
};

const loadMembers = async () => {
  if (memberLoading.value) return;
  memberLoading.value = true;
  try {
    const result = await api.listUsers();
    if (result?.code === 200 && Array.isArray(result.data)) {
      members.value = result.data;
    } else {
      members.value = [];
      ElMessage.error(result?.msg || '加载成员失败');
    }
  } catch (error) {
    console.error('加载成员失败：', error);
    members.value = [];
    ElMessage.error('加载成员失败');
  } finally {
    memberLoading.value = false;
  }
};

// 加载项目类型下拉数据
const loadProjectTypes = async () => {
  try {
    const result = await api.listCostTypes({ skip: 0, limit: 300 });
    if (result?.code === 200 && Array.isArray(result.data)) {
      projectTypeOptions.value = result.data;
      if (projectTypeOptions.value.length > 0) {
        selectedProjectType.value = projectTypeOptions.value[0].name;
        await handleProjectTypeChange();
      } else {
        selectedProjectType.value = '';
        await loadStages();
      }
    } else {
    ElMessage.error(result?.msg || '加载项目类型失败');
  }
  } catch (error) {
    console.error('加载项目类型失败：', error);
    ElMessage.error('加载项目类型失败');
  }
};

// 加载成本阶段配置数据
const loadStages = async () => {
  loading.value = true;
  try {
    const result = await api.listCostStages({
      skip: 0,
      limit: 300,
      projectType: selectedProjectType.value
    });
    if (result?.code === 200 && Array.isArray(result.data)) {
      stages.value = result.data;
      syncTreeData(result.data);
    } else {
      ElMessage.error(result?.msg || '加载阶段失败');
    }
  } catch (error) {
    console.error('加载阶段失败：', error);
    ElMessage.error('加载阶段失败');
  } finally {
    loading.value = false;
  }
};

// 切换项目类型时刷新阶段
const handleProjectTypeChange = async () => {
  resetSelection();
  await loadStages();
};

// 点击节点时填充编辑表单
const handleNodeClick = (data) => {
  if (!data) return;
  currentNode.value = { ...data };
  formData._id = data._id || '';
  formData.name = data.name || '';
  formData.id = data.id || '';
  formData.description = data.description || '';
  formData.budget_standard = data.budget_standard ?? 0;
  formData.responsiblePersonId = getMemberId(data.responsible_person);
  ensureCurrentResponsibleOption(data.responsible_person);
};

// 新增主阶段
const handleAddStage = async () => {
  if (!selectedProjectType.value) {
    ElMessage.warning('请先选择项目类型');
    return;
  }

  try {
    const { value } = await ElMessageBox.prompt('请输入新阶段名称。', '新增阶段', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /\S+/,
      inputErrorMessage: '请输入有效名称'
    });

    const maxSort = Math.max(
      0,
      ...stages.value
        .filter((stage) => !stage.parent_id)
        .map((stage) => stage.sort_order || 0)
    );

    const newStage = {
      name: value,
      sort_order: maxSort + 1,
      project_type: selectedProjectType.value,
      budget_standard: 0
    };

    const result = await api.createCostStage(newStage);
    if (result?.code === 200) {
      ElMessage.success('阶段创建成功');
      await loadStages();
      await nextTick();
      if (treeRef.value && result.data?._id) {
        treeRef.value.setCurrentKey(result.data._id);
        const freshNode = stages.value.find((stage) => stage._id === result.data._id) || result.data;
        handleNodeClick(freshNode);
      }
    } else {
      ElMessage.error(result?.msg || '创建阶段失败');
    }
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      console.error('创建阶段失败：', error);
      ElMessage.error('创建阶段失败');
    }
  }
};

// 新增子阶段
const handleAddNode = async (parentData) => {
  if (!parentData?.id) {
    ElMessage.warning('父节点无效');
    return;
  }

  if (isChildNode(parentData)) {
    ElMessage.warning('子节点不能继续新增子子节点');
    return;
  }

  if (!selectedProjectType.value) {
    ElMessage.warning('请先选择项目类型');
    return;
  }

  try {
    const { value } = await ElMessageBox.prompt('请输入子阶段名称。', '新增子阶段', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /\S+/,
      inputErrorMessage: '请输入有效名称'
    });

    const parentKey = toKey(parentData.id);
    const siblings = stages.value.filter((stage) => toKey(stage.parent_id) === parentKey);
    const maxSort = Math.max(0, ...siblings.map((stage) => stage.sort_order || 0));

    const newStage = {
      name: value,
      parent_id: parentKey,
      sort_order: maxSort + 1,
      project_type: selectedProjectType.value,
      budget_standard: 0
    };

    const result = await api.createCostStage(newStage);
    if (result?.code === 200) {
      ElMessage.success('子阶段创建成功');
      await loadStages();
      await nextTick();
      if (treeRef.value && result.data?._id) {
        try {
          const parentNode = treeRef.value.getNode(parentData._id);
          if (parentNode) {
            parentNode.expanded = true;
          }
        } catch (error) {
          console.warn('展开父节点失败：', error);
        }

        setTimeout(() => {
          if (treeRef.value) {
            treeRef.value.setCurrentKey(result.data._id);
            handleNodeClick(result.data);
          }
        }, 100);
      }
    } else {
      ElMessage.error(result?.msg || '创建子阶段失败');
    }
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      console.error('创建子阶段失败：', error);
      ElMessage.error('创建子阶段失败');
    }
  }
};

// 保存阶段编辑
const handleSave = async () => {
  if (!formData.name.trim()) {
    ElMessage.warning('名称不能为空');
    return;
  }

  try {
    const dataToSave = {
      name: formData.name,
      description: formData.description,
      project_type: selectedProjectType.value,
      budget_standard: Number(formData.budget_standard || 0),
      responsible_person: formData.responsiblePersonId || ''
    };

    const result = await api.updateCostStage(formData._id, dataToSave);
    if (result?.code === 200) {
      ElMessage.success('保存成功');
      await loadStages();
      resetSelection();
    } else {
      ElMessage.error(result?.msg || '保存失败');
    }
  } catch (error) {
    console.error('保存失败：', error);
    ElMessage.error('保存失败');
  }
};

// 删除阶段节点
const handleDelete = async (data) => {
  if (!data?._id) {
    ElMessage.warning('未选择可删除的阶段');
    return;
  }

  const dataKey = toKey(data?.id);
  const childCount = stages.value.filter((stage) => toKey(stage.parent_id) === dataKey).length;
  if (childCount > 0) {
    ElMessage.warning(`该阶段有 ${childCount} 个子节点，无法删除。`);
    return;
  }

  try {
    await ElMessageBox.confirm(
      '确定删除该阶段吗？该操作不可恢复。',
      '警告',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );

    const result = await api.deleteCostStage(data._id);
    if (result?.code === 200) {
      ElMessage.success('删除成功');
      await loadStages();
      resetSelection();
    } else {
      ElMessage.error(result?.msg || '删除失败');
    }
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      console.error('删除失败：', error);
      ElMessage.error('删除失败');
    }
  }
};

// 页面初始化时加载项目类型
onMounted(async () => {
  await loadMembers();
  await loadProjectTypes();
});
</script>
