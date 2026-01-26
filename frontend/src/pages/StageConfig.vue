<template>
  <div class="main-content">
    <div class="header">
      <div class="header-title">Project Stage Configuration</div>
      <div class="header-actions"></div>
    </div>

    <div class="top-row">
      <el-select
        v-model="selectedProjectType"
        placeholder="Select project type"
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
        Loaded types: <strong>{{ projectTypeOptions.length }}</strong>
      </span>
    </div>

    <div class="page-container">
      <div class="config-layout">
        <div class="left-panel">
          <div class="panel-header">
            <span>Stage Node Structure</span>
            <el-button type="primary" link :disabled="!selectedProjectType" @click="handleAddStage">
              New Stage
            </el-button>
          </div>
          <div class="tree-container">
            <div v-if="loading" class="loading-state">
              <el-progress type="circle" :percentage="50" />
            </div>
            <div v-else-if="treeData.length === 0" class="empty-state">
              <p>No stage data available.</p>
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
                      title="Add child stage"
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
                      title="Delete"
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
              <span>{{ currentNode.parent_id ? 'Child Stage Editing' : 'Stage Details' }}</span>
              <el-button type="primary" @click="handleSave">Save Changes</el-button>
            </div>
            <el-form :model="formData" label-width="100px">
              <el-form-item label="Name *">
                <el-input v-model="formData.name" />
              </el-form-item>
              <el-form-item label="Stage ID">
                <el-input v-model="formData.id" disabled />
              </el-form-item>
              <el-form-item label="Description">
                <el-input
                  v-model="formData.description"
                  type="textarea"
                  :rows="4"
                  placeholder="Optional stage description"
                />
              </el-form-item>
            </el-form>

            <div class="log-section">
              <div class="panel-header panel-header-form panel-header-muted">
                <span>Stage Metadata</span>
              </div>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="Created At">
                  {{ currentNode.createTime || 'Unknown' }}
                </el-descriptions-item>
                <el-descriptions-item label="Creator">
                  {{ currentNode.creator?.name || 'Unknown' }}
                </el-descriptions-item>
                <el-descriptions-item label="Last Updated">
                  {{ currentNode.updateTime || 'Unknown' }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
          <div v-else class="empty-state">
            <el-icon class="empty-icon"><Edit /></el-icon>
            <p>Select a stage on the left to edit.</p>
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
    const result = await api.listProjectTypes({ skip: 0, limit: 300 });
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
      ElMessage.error(result?.msg || 'Failed to load project types.');
    }
  } catch (error) {
    console.error('Failed to load project types:', error);
    ElMessage.error('Failed to load project types.');
  }
};

const loadStages = async () => {
  loading.value = true;
  try {
    const result = await api.listStages({
      skip: 0,
      limit: 300,
      projectType: selectedProjectType.value
    });
    if (result?.code === 200 && Array.isArray(result.data)) {
      stages.value = result.data;
    } else {
      ElMessage.error(result?.msg || 'Failed to load stages.');
    }
  } catch (error) {
    console.error('Failed to load stages:', error);
    ElMessage.error('Failed to load stages.');
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
    ElMessage.warning('Select a project type first.');
    return;
  }

  try {
    const { value } = await ElMessageBox.prompt('Enter the new stage name.', 'New Stage', {
      confirmButtonText: 'Create',
      cancelButtonText: 'Cancel',
      inputPattern: /\S+/,
      inputErrorMessage: 'Please enter a valid name.'
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

    const result = await api.createStage(newStage);
    if (result?.code === 200) {
      ElMessage.success('Stage created successfully.');
      await loadStages();
      await nextTick();
      if (treeRef.value && result.data?._id) {
        treeRef.value.setCurrentKey(result.data._id);
      }
    } else {
      ElMessage.error(result?.msg || 'Failed to create stage.');
    }
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      console.error('Failed to create stage:', error);
      ElMessage.error('Failed to create stage.');
    }
  }
};

const handleAddNode = async (parentData) => {
  if (!parentData?.id) {
    ElMessage.warning('Invalid parent stage.');
    return;
  }

  if (!selectedProjectType.value) {
    ElMessage.warning('Select a project type first.');
    return;
  }

  try {
    const { value } = await ElMessageBox.prompt('Enter the child stage name.', 'New Child Stage', {
      confirmButtonText: 'Create',
      cancelButtonText: 'Cancel',
      inputPattern: /\S+/,
      inputErrorMessage: 'Please enter a valid name.'
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

    const result = await api.createStage(newStage);
    if (result?.code === 200) {
      ElMessage.success('Child stage created successfully.');
      await loadStages();
      await nextTick();
      if (treeRef.value && result.data?._id) {
        try {
          const parentNode = treeRef.value.getNode(parentData._id);
          if (parentNode) {
            parentNode.expanded = true;
          }
        } catch (error) {
          console.warn('Failed to expand parent node:', error);
        }

        setTimeout(() => {
          if (treeRef.value) {
            treeRef.value.setCurrentKey(result.data._id);
            handleNodeClick(result.data);
          }
        }, 100);
      }
    } else {
      ElMessage.error(result?.msg || 'Failed to create child stage.');
    }
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      console.error('Failed to create child stage:', error);
      ElMessage.error('Failed to create child stage.');
    }
  }
};

const handleSave = async () => {
  if (!formData.name.trim()) {
    ElMessage.warning('Name is required.');
    return;
  }

  try {
    const dataToSave = {
      name: formData.name,
      description: formData.description,
      project_type: selectedProjectType.value
    };

    const result = await api.updateStage(formData._id, dataToSave);
    if (result?.code === 200) {
      ElMessage.success('Changes saved successfully.');
      await loadStages();
      resetSelection();
    } else {
      ElMessage.error(result?.msg || 'Failed to save changes.');
    }
  } catch (error) {
    console.error('Failed to save changes:', error);
    ElMessage.error('Failed to save changes.');
  }
};

const handleDelete = async (data) => {
  const dataKey = toKey(data?.id);
  const childCount = stages.value.filter((stage) => toKey(stage.parent_id) === dataKey).length;
  if (childCount > 0) {
    ElMessage.warning(`This stage has ${childCount} child nodes and cannot be deleted.`);
    return;
  }

  try {
    await ElMessageBox.confirm(
      'Are you sure you want to delete this stage? This action cannot be undone.',
      'Warning',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    );

    const result = await api.deleteStage(data._id);
    if (result?.code === 200) {
      ElMessage.success('Stage deleted successfully.');
      await loadStages();
      resetSelection();
    } else {
      ElMessage.error(result?.msg || 'Failed to delete stage.');
    }
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      console.error('Failed to delete stage:', error);
      ElMessage.error('Failed to delete stage.');
    }
  }
};

onMounted(async () => {
  await loadProjectTypes();
});
</script>
