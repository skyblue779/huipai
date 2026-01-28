<template>
  <div class="main-content">
    <div class="page-container">
      <div class="progress-visual-card">
        <div class="visual-header">
          <div class="search-row">
            <el-select
              v-model="currentProjectKey"
              placeholder="选择项目"
              filterable
              style="width: 240px"
            >
              <el-option
                v-for="item in projectOptions"
                :key="item.key"
                :label="item.label"
                :value="item.key"
              />
            </el-select>
            <el-input
              v-model="searchQuery"
              placeholder="搜索项目名称/编号..."
              style="width: 240px"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" :loading="loading" @click="handleSearch">查询</el-button>
          </div>

          <div class="project-name-large">
            {{ currentProjectLabel }}
          </div>

          <div class="status-tags">
            <el-tag type="info" size="large" effect="plain">非线性节点看板</el-tag>
            <el-tag :type="overallProgressType" size="large" effect="dark">
              {{ overallProgress }}% 完成
            </el-tag>
          </div>
        </div>

        <div v-if="timelineNodes.length" class="segmented-timeline-wrapper">
          <div class="segmented-track">
            <div
              v-for="(node, index) in timelineNodes"
              :key="`${node.id || index}`"
              class="segment-block"
              :class="{
                'is-done': isDone(node.status),
                'is-overdue': node.status === '超期'
              }"
            ></div>
          </div>

          <div class="node-markers">
            <div
              v-for="(node, index) in timelineNodes"
              :key="`${node.id || 'marker'}-${index}`"
              class="marker-cell"
            >
              <div
                class="marker-dot"
                :class="{
                  'is-done': isDone(node.status),
                  'is-overdue': node.status === '超期',
                  'is-pending': node.status === '未完成'
                }"
              >
                <el-icon v-if="isDone(node.status)" size="14"><Check /></el-icon>
                <el-icon v-else-if="node.status === '超期'" size="14"><WarningFilled /></el-icon>
                <span v-else class="marker-pending-dot"></span>
                <el-icon v-if="isDone(node.status) && node.isMilestone" class="node-flag-icon">
                  <Flag />
                </el-icon>
              </div>
              <div class="marker-label">{{ node.name }}</div>
            </div>
          </div>
        </div>
        <div v-else class="empty-timeline">
          <el-empty description="暂无进度数据" />
        </div>
      </div>

      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="card-label">整体进度</div>
          <div class="card-value accent-blue">{{ overallProgress }}%</div>
        </div>
        <div class="dashboard-card">
          <div class="card-label">预警节点总数</div>
          <div class="card-value accent-danger">{{ totalWarningLevelCount }}</div>
        </div>
        <div class="dashboard-card">
          <div class="card-label">里程碑达成</div>
          <div class="card-value accent-warning">
            {{ milestoneReachedCount }}
            <span class="muted">/ {{ milestoneTotalCount }}</span>
          </div>
        </div>
        <div class="dashboard-card">
          <div class="card-label">预警数量</div>
          <div class="card-value accent-danger">
            {{ warningLevelCount }}
            <span class="muted">个</span>
          </div>
        </div>
      </div>

      <div class="progress-table-card">
        <div class="table-header">
          <div class="table-title">
            <h3>项目节点执行明细</h3>
          </div>
        </div>

        <el-table
          :data="tableRows"
          style="width: 100%"
          stripe
          border
          v-loading="loading"
          row-key="id"
          :tree-props="{ children: 'children' }"
          :default-expand-all="true"
          :row-class-name="getRowClass"
        >
          <el-table-column label="主阶段" min-width="180" fixed="left">
            <template #default="{ row }">
              <span v-if="row.isGroup" class="stage-group-title">{{ row.mainStageLabel || row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column label="节点名称" min-width="220">
            <template #default="{ row }">
              <span v-if="row.isGroup" class="stage-node-count">{{ row.nodeCount }} 个节点</span>
              <div v-else class="stage-node-item">
                <span class="stage-node-dot"></span>
                <span class="stage-node-text">{{ row.nodeLabel || row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="当前状态" width="120" align="center">
            <template #default="{ row }">
              <el-tag v-if="!row.isGroup" :type="getStatusTag(row.status)" effect="dark">
                {{ row.status || '未完成' }}
              </el-tag>
              <span v-else class="stage-placeholder">--</span>
            </template>
          </el-table-column>
          <el-table-column label="计划开始日期" width="140" align="center">
            <template #default="{ row }">
              <span v-if="!row.isGroup">{{ row.planStart }}</span>
              <span v-else class="stage-placeholder">--</span>
            </template>
          </el-table-column>
          <el-table-column label="计划结束日期" width="140" align="center">
            <template #default="{ row }">
              <span v-if="!row.isGroup">{{ row.planEnd }}</span>
              <span v-else class="stage-placeholder">--</span>
            </template>
          </el-table-column>
          <el-table-column label="预警等级" width="130" align="center">
            <template #default="{ row }">
              <el-tag v-if="!row.isGroup" :type="getWarningTag(row.warningLevel)" effect="plain">
                {{ row.warningLevel || '正常' }}
              </el-tag>
              <span v-else class="stage-placeholder">--</span>
            </template>
          </el-table-column>
          <el-table-column label="责任人" width="140" align="center">
            <template #default="{ row }">
              <span v-if="!row.isGroup">{{ row.executorName }}</span>
              <span v-else class="stage-placeholder">--</span>
            </template>
          </el-table-column>
          </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { Search, Check, WarningFilled, Flag } from '@element-plus/icons-vue';
import api from '../api/client';

const searchQuery = ref('');
const loading = ref(false);
const progressRecords = ref([]);
const currentProjectKey = ref('');

const ONE_DAY_MS = 24 * 60 * 60 * 1000;

const parseDateValue = (value) => {
  if (!value) return null;
  if (value instanceof Date) return value;
  if (typeof value === 'number') return new Date(value);
  if (typeof value === 'string') {
    const trimmed = value.trim();
    if (!trimmed) return null;
    const parsed = new Date(trimmed.replace(/-/g, '/'));
    if (!Number.isNaN(parsed.getTime())) return parsed;
  }
  return null;
};

const parseDateRange = (value) => {
  if (!value) return { start: null, end: null };
  if (Array.isArray(value)) {
    return {
      start: parseDateValue(value[0]),
      end: parseDateValue(value[1])
    };
  }
  if (typeof value === 'object') {
    const start = parseDateValue(value.start || value.begin || value.planStart);
    const end = parseDateValue(value.end || value.finish || value.planEnd);
    if (start || end) return { start, end };
  }
  if (typeof value === 'string') {
    const matches = value.match(
      /\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?/g
    );
    if (matches && matches.length >= 2) {
      return {
        start: parseDateValue(matches[0]),
        end: parseDateValue(matches[1])
      };
    }
  }
  const single = parseDateValue(value);
  return { start: single, end: null };
};

const formatDate = (value) => {
  if (!value) return '--';
  if (typeof value === 'string') {
    const match = value.match(/\d{4}[-/]\d{1,2}[-/]\d{1,2}/);
    return match ? match[0].replace(/\//g, '-') : value;
  }
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toISOString().slice(0, 10);
};

const formatUser = (value) => {
  if (!value) return '--';
  if (Array.isArray(value)) {
    const names = value.map((item) => item?.name || item?._id || item).filter(Boolean);
    return names.length ? names.join(' / ') : '--';
  }
  if (typeof value === 'object') {
    return value.name || value._id || '--';
  }
  return String(value);
};

const normalizeLabel = (value) => {
  if (value === null || value === undefined) return '';
  if (typeof value === 'string') return value.trim();
  return String(value);
};

const normalizeOrderValue = (value) => {
  if (value === null || value === undefined) return null;
  const trimmed = String(value).trim();
  if (!trimmed) return null;
  const numeric = Number(trimmed);
  if (Number.isFinite(numeric)) return numeric;
  return trimmed;
};

const compareOrderValue = (a, b) => {
  if (a === null || a === undefined) return b === null || b === undefined ? 0 : 1;
  if (b === null || b === undefined) return -1;
  const aIsNumber = typeof a === 'number' && Number.isFinite(a);
  const bIsNumber = typeof b === 'number' && Number.isFinite(b);
  if (aIsNumber && bIsNumber) return a - b;
  return String(a).localeCompare(String(b), 'zh');
};

const groupedProjects = computed(() => {
  const map = new Map();
  progressRecords.value.forEach((item) => {
    const projectCode = item.project_code || '';
    const projectName = item.project_name || '';
    const projectType = item.project_type || '';
    const key = `${projectCode}||${projectName}||${projectType}`;
    if (!map.has(key)) {
      map.set(key, {
        key,
        projectCode,
        projectName,
        projectType,
        records: []
      });
    }
    map.get(key).records.push(item);
  });
  return Array.from(map.values());
});

watch(
  groupedProjects,
  (groups) => {
    if (!groups.length) {
      currentProjectKey.value = '';
      return;
    }
    if (!groups.find((item) => item.key === currentProjectKey.value)) {
      currentProjectKey.value = groups[0].key;
    }
  },
  { immediate: true }
);

const currentProject = computed(() => {
  if (!groupedProjects.value.length) {
    return {
      projectName: '暂无项目',
      projectCode: '',
      projectType: '',
      records: []
    };
  }
  return (
    groupedProjects.value.find((item) => item.key === currentProjectKey.value) ||
    groupedProjects.value[0]
  );
});

const currentProjectLabel = computed(() => {
  const name = currentProject.value.projectName || '暂无项目';
  const code = currentProject.value.projectCode;
  return code ? `${name} (${code})` : name;
});

const projectOptions = computed(() =>
  groupedProjects.value.map((item) => {
    const name = item.projectName || '未命名项目';
    const code = item.projectCode ? ` (${item.projectCode})` : '';
    return {
      key: item.key,
      label: `${name}${code}`
    };
  })
);

const normalizeNode = (record, index) => {
  const planRange = parseDateRange(record.plan_time);
  const actualDate = parseDateValue(record.actual_finish);
  const planStartDate = planRange.start || actualDate;
  let planEndDate = planRange.end || actualDate || planStartDate;
  if (planStartDate && planEndDate && planEndDate <= planStartDate) {
    planEndDate = new Date(planStartDate.getTime() + ONE_DAY_MS);
  }
  if (planStartDate && !planEndDate) {
    planEndDate = new Date(planStartDate.getTime() + ONE_DAY_MS);
  }

  const mainStageLabel = normalizeLabel(record.main_stage || record.mainStage);
  const projectStageLabel = normalizeLabel(record.project_stage || record.projectStage || record.stage);
  const fallbackLabel = projectStageLabel || mainStageLabel || `节点${index + 1}`;
  const nodeLabel = projectStageLabel || (!mainStageLabel ? fallbackLabel : '');

  return {
    id: record._id || `${index}`,
    name: fallbackLabel,
    mainStageLabel,
    nodeLabel,
    mainStageOrder: normalizeOrderValue(record.main_stage_order),
    projectStageOrder: normalizeOrderValue(record.project_stage_order),
    status: record.status || '未完成',
    warningLevel: record.warning_level || '正常',
    executorName: formatUser(record.executor),
    planStart: formatDate(planStartDate || record.plan_time),
    planEnd: formatDate(planEndDate || record.actual_finish),
    planStartSort: planStartDate ? planStartDate.getTime() : null,
    originalIndex: index,
    isMilestone: isDone(record.status || '未完成')
  };
};

const timelineNodes = computed(() => {
  const nodes = currentProject.value.records.map((record, index) => normalizeNode(record, index));
  nodes.sort((a, b) => {
    const mainCompare = compareOrderValue(a.mainStageOrder, b.mainStageOrder);
    if (mainCompare !== 0) return mainCompare;
    const projectCompare = compareOrderValue(a.projectStageOrder, b.projectStageOrder);
    if (projectCompare !== 0) return projectCompare;
    const dateCompare = compareOrderValue(a.planStartSort, b.planStartSort);
    if (dateCompare !== 0) return dateCompare;
    return a.originalIndex - b.originalIndex;
  });
  return nodes;
});

const tableRows = computed(() => {
  const rows = [];
  const groupMap = new Map();
  timelineNodes.value.forEach((node, index) => {
    const mainLabel = node.mainStageLabel;
    if (!mainLabel) {
      rows.push({
        ...node,
        id: `node-${node.id ?? index}`,
        isGroup: false
      });
      return;
    }
    const key = `${mainLabel}||${node.mainStageOrder ?? ''}`;
    let group = groupMap.get(key);
    if (!group) {
      group = {
        id: `group-${groupMap.size}-${String(mainLabel)}`,
        isGroup: true,
        name: mainLabel,
        mainStageLabel: mainLabel,
        mainStageOrder: node.mainStageOrder,
        children: [],
        nodeCount: 0
      };
      groupMap.set(key, group);
      rows.push(group);
    }
    group.children.push({
      ...node,
      id: `node-${node.id ?? `${index}`}`,
      isGroup: false
    });
    group.nodeCount = group.children.length;
  });
  return rows;
});

const isDone = (status) => status === '完成' || status === '超期完成';

const overallProgress = computed(() => {
  const total = timelineNodes.value.length;
  const doneCount = timelineNodes.value.filter((node) => isDone(node.status)).length;
  return total === 0 ? 0 : Math.round((doneCount / total) * 100);
});

const totalWarningLevelCount = computed(
  () => timelineNodes.value.filter((node) => node.status === '超期').length
);
const warningLevelCount = computed(
  () => timelineNodes.value.filter((node) => node.warningLevel && node.warningLevel !== '正常').length
);

const milestoneReachedCount = computed(() => timelineNodes.value.filter((node) => isDone(node.status)).length);
const milestoneTotalCount = computed(() => timelineNodes.value.length);

const overallProgressType = computed(() => (warningLevelCount.value > 0 ? 'danger' : 'primary'));

const getStatusTag = (status) => {
  if (status === '完成' || status === '超期完成') return 'success';
  if (status === '超期') return 'danger';
  return 'info';
};

const getRowClass = ({ row }) => (row.isGroup ? 'table-group-row' : '');

const getWarningTag = (level) => {
  if (level === '三级预警') return 'danger';
  if (level === '二级预警') return 'warning';
  if (level === '一级预警') return 'info';
  return 'success';
};

const loadProgressRecords = async (search = '') => {
  loading.value = true;
  try {
    const result = await api.listProjectProgress({
      skip: 0,
      limit: 300,
      search
    });
    if (result?.code === 200 && Array.isArray(result.data)) {
      progressRecords.value = result.data;
    } else {
      progressRecords.value = [];
      ElMessage.error(result?.msg || '加载进度数据失败');
    }
  } catch (error) {
    console.error('加载进度数据失败：', error);
    progressRecords.value = [];
    ElMessage.error('加载进度数据失败');
  } finally {
    loading.value = false;
  }
};

const handleSearch = async () => {
  await loadProgressRecords(searchQuery.value.trim());
};

onMounted(async () => {
  await loadProgressRecords();
});
</script>

<style scoped>
.page-container {
  padding: 32px 40px;
  flex: 1;
  overflow-y: auto;
}

.progress-visual-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.visual-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 30px;
}

.search-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.project-name-large {
  font-size: 22px;
  font-weight: 600;
  text-align: center;
  flex: 1 1 auto;
  min-width: 200px;
}

.status-tags {
  display: flex;
  align-items: center;
  gap: 15px;
}

.segmented-timeline-wrapper {
  position: relative;
  padding: 40px 10px 60px 10px;
}

.segmented-track {
  display: flex;
  height: 14px;
  background: #f0f0f0;
  border-radius: 7px;
  gap: 6px;
  padding: 3px;
  margin-bottom: 15px;
  overflow: hidden;
}

.segment-block {
  flex: 1;
  height: 100%;
  border-radius: 4px;
  background-color: #e8e8e8;
  transition: all 0.4s ease;
}

.segment-block.is-done {
  background-color: #52c41a;
}

.segment-block.is-overdue {
  background-color: #ffccc7;
  border: 1px dashed #f5222d;
}

.node-markers {
  display: flex;
  justify-content: space-between;
  position: absolute;
  width: calc(100% - 20px);
  top: 25px;
}

.marker-cell {
  position: relative;
  flex: 1;
  display: flex;
  justify-content: center;
}

.marker-dot {
  width: 28px;
  height: 28px;
  background: #fff;
  border: 2px solid #d9d9d9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  position: relative;
}

.marker-dot.is-done {
  border-color: #52c41a;
  background: #52c41a;
  color: #fff;
}

.marker-dot.is-overdue {
  border-color: #f5222d;
  color: #f5222d;
  background: #fff1f0;
}

.marker-label {
  position: absolute;
  top: 40px;
  transform: translateX(-50%);
  left: 50%;
  white-space: nowrap;
  font-size: 13px;
  color: #666;
}

.marker-pending-dot {
  width: 6px;
  height: 6px;
  background: #d9d9d9;
  border-radius: 50%;
  display: inline-block;
}

.node-flag-icon {
  position: absolute;
  top: -18px;
  right: -10px;
  color: #f5222d;
  font-size: 16px;
  animation: wave 2s infinite ease-in-out;
}

@keyframes wave {
  0%,
  100% {
    transform: rotate(0deg);
  }
  50% {
    transform: rotate(15deg);
  }
}

.empty-timeline {
  padding: 20px 0;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.dashboard-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.card-label {
  color: #8c8c8c;
  font-size: 14px;
  margin-bottom: 12px;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
}

.accent-blue {
  color: #1890ff;
}

.accent-danger {
  color: #f5222d;
}

.accent-warning {
  color: #fa8c16;
}

.muted {
  font-size: 14px;
  font-weight: normal;
  color: #999;
}

.progress-table-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.table-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 20px;
}

.table-title h3 {
  margin: 0;
  font-size: 16px;
}

:deep(.table-group-row) td {
  background: #fafafa;
}

.stage-group-title {
  font-weight: 600;
  color: #303133;
}

.stage-node-count {
  font-size: 12px;
  color: #909399;
}

.stage-node-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #303133;
}

.stage-node-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #c0c4cc;
  flex-shrink: 0;
}

.stage-node-text {
  line-height: 1.2;
}

.stage-placeholder {
  color: #c0c4cc;
}

@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 20px;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .visual-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .project-name-large {
    text-align: left;
  }
}
</style>
