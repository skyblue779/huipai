<template>
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
              default-expand-all
              :expand-on-click-node="false"
              @node-click="handleNodeClick"
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
              <el-button type="primary" @click="handleSave">保存修改</el-button>
            </div>
            <el-form :model="formData" label-width="100px">
              <el-form-item label="名称 *">
                <el-input v-model="formData.name" />
              </el-form-item>
              <el-form-item label="阶段ID">
                <el-input v-model="formData.id" disabled />
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
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Folder, Document, Plus, Delete, Edit } from '@element-plus/icons-vue';
import api from '../api/client';

const loading = ref(false);
const stages = ref([]);
const treeRef = ref(null);
const currentNode = ref(null);
const projectTypeOptions = ref([]);
const selectedProjectType = ref('');

const formData = reactive({
  _id: '',
  name: '',
  id: '',
  description: ''
});

const treeProps = {
  children: 'children',
  label: 'name'
};

const toKey = (value) => {
  if (value === null || value === undefined || value === '') return null;
  const numeric = Number(value);
  if (!Number.isNaN(numeric)) return numeric;
  const trimmed = String(value).trim();
  if (!trimmed) return null;
  const parsed = Number.parseInt(trimmed, 10);
  return Number.isNaN(parsed) ? trimmed : parsed;
};

const hasChildren = (nodeData) => {
  const key = toKey(nodeData?.id);
  if (key === null) return false;
  return stages.value.some((stage) => toKey(stage.parent_id) === key);
};

const treeData = computed(() => {
  if (!stages.value.length) return [];

  const roots = stages.value.filter(
    (stage) => !stage.parent_id || stage.parent_id === null || stage.parent_id === ''
  );

  const buildTree = (nodes) =>
    nodes
      .map((node) => {
        const nodeKey = toKey(node.id);
        const children = stages.value.filter((stage) => toKey(stage.parent_id) === nodeKey);
        const nodeData = { ...node };
        if (children.length > 0) {
          nodeData.children = buildTree(children);
        }
        return nodeData;
      })
      .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0));

  return buildTree(roots);
});

const resetSelection = () => {
  currentNode.value = null;
  formData._id = '';
  formData.name = '';
  formData.id = '';
  formData.description = '';
};

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

const handleProjectTypeChange = async () => {
  resetSelection();
  await loadStages();
};

const handleNodeClick = (data) => {
  if (!data) return;
  currentNode.value = { ...data };
  formData._id = data._id || '';
  formData.name = data.name || '';
  formData.id = data.id || '';
  formData.description = data.description || '';
};

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
      project_type: selectedProjectType.value
    };

    const result = await api.createCostStage(newStage);
    if (result?.code === 200) {
      ElMessage.success('阶段创建成功');
      await loadStages();
      await nextTick();
      if (treeRef.value && result.data?._id) {
        treeRef.value.setCurrentKey(result.data._id);
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

const handleAddNode = async (parentData) => {
  if (!parentData?.id) {
    ElMessage.warning('父节点无效');
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
      project_type: selectedProjectType.value
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

const handleSave = async () => {
  if (!formData.name.trim()) {
    ElMessage.warning('名称不能为空');
    return;
  }

  try {
    const dataToSave = {
      name: formData.name,
      description: formData.description,
      project_type: selectedProjectType.value
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

const handleDelete = async (data) => {
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

onMounted(async () => {
  await loadProjectTypes();
});
</script>
