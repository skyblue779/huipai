<template>
  <div class="page-root">
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
            <!-- <el-input
              v-model="searchQuery"
              placeholder="搜索项目名称/编号..."
              style="width: 240px"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input> -->
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

          <div class="segmented-progress">
            <div class="segmented-progress__fill" :style="{ width: `${overallProgress}%` }"></div>
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
          <div class="card-header">
            <div class="card-icon is-primary">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="card-label">整体进度</div>
          </div>
          <div class="card-value accent-blue">{{ overallProgress }}%</div>
        </div>
        <div class="dashboard-card">
          <div class="card-header">
            <div class="card-icon is-danger">
              <el-icon><WarningFilled /></el-icon>
            </div>
            <div class="card-label">预警节点总数(个)</div>
          </div>
          <div class="card-value accent-danger">{{ totalWarningLevelCount }}</div>
        </div>
        <div class="dashboard-card">
          <div class="card-header">
            <div class="card-icon is-warning">
              <el-icon><Flag /></el-icon>
            </div>
            <div class="card-label">里程碑达成</div>
          </div>
          <div class="card-value accent-warning">
            {{ milestoneReachedCount }}
            <span class="muted">/ {{ milestoneTotalCount }}</span>
          </div>
        </div>
        <div class="dashboard-card">
          <div class="card-header">
            <div class="card-icon is-danger">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="card-label">预警数量(个)</div>
          </div>
          <div class="card-value accent-danger">
            {{ warningLevelCount }}
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
                {{ displayStatus(row.status) }}
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
          <el-table-column label="操作" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button v-if="!row.isGroup" type="primary" link @click="openEditDialog(row)">编辑</el-button>
              <span v-else class="stage-placeholder">--</span>
            </template>
          </el-table-column>
          </el-table>
      </div>
    </div>
  </div>

    <el-dialog v-model="editDialogVisible" title="编辑节点" width="520px">
    <el-form label-width="110px">
      <el-form-item label="计划开始日期">
        <el-date-picker
          v-model="editForm.planStart"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="请选择日期"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="责任人">
        <el-select
          v-model="editForm.executorIds"
          multiple
          collapse-tags
          collapse-tags-tooltip
          filterable
          placeholder="请选择成员"
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
    </el-form>
    <template #footer>
      <el-button @click="editDialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="savingEdit" @click="handleSaveEdit">保存</el-button>
    </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { Search, Check, WarningFilled, Flag, TrendCharts, Bell } from '@element-plus/icons-vue';
import api from '../api/client';

const searchQuery = ref('');
const loading = ref(false);
const progressRecords = ref([]);
const currentProjectKey = ref('');
const editDialogVisible = ref(false);
const savingEdit = ref(false);
const editForm = ref({
  planStart: '',
  executorIds: []
});
const editRow = ref(null);
const originalExecutorIds = ref([]);
const members = ref([]);
const memberLoading = ref(false);

// 解析日期值为 Date
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

// 解析日期区间
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

// 格式化日期展示
const formatDate = (value) => {
  if (!value) return '--';
  if (typeof value === 'string') {
    const match = value.match(/\d{4}[-/]\d{1,2}[-/]\d{1,2}/);
    return match ? match[0].replace(/\//g, '-') : value;
  }
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// 表格日期展示格式
const formatDateCell = (value) => {
  if (!value) return '';
  return formatDate(value);
};

// 格式化执行人显示
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

// 提取执行人 ID 列表
const getExecutorIds = (value) => {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value
      .map((item) => {
        if (!item) return '';
        if (typeof item === 'object') return item.user_id || item._id || item.id || '';
        return String(item);
      })
      .filter(Boolean);
  }
  if (typeof value === 'object') {
    return [value.user_id || value._id || value.id || ''].filter(Boolean);
  }
  return [String(value)];
};

// 更新计划时间字段中的开始日期
const updatePlanTimeValue = (rawValue, newStart, fallbackEnd) => {
  if (!newStart) return rawValue;
  const formatEnd = (value) => {
    if (!value) return null;
    if (typeof value === 'string') return value.replace(/\//g, '-');
    return formatDate(value);
  };
  if (Array.isArray(rawValue)) {
    const end = formatEnd(rawValue[1] || fallbackEnd);
    return end ? [newStart, end] : [newStart];
  }
  if (rawValue && typeof rawValue === 'object') {
    const updated = { ...rawValue };
    if ('start' in updated) updated.start = newStart;
    else if ('begin' in updated) updated.begin = newStart;
    else if ('planStart' in updated) updated.planStart = newStart;
    else updated.start = newStart;
    const endValue = updated.end || updated.finish || updated.planEnd || fallbackEnd;
    if ('end' in updated) updated.end = formatEnd(endValue) || updated.end;
    if ('finish' in updated) updated.finish = formatEnd(endValue) || updated.finish;
    if ('planEnd' in updated) updated.planEnd = formatEnd(endValue) || updated.planEnd;
    return updated;
  }
  if (typeof rawValue === 'string') {
    const matches = rawValue.match(/\d{4}[-/]\d{1,2}[-/]\d{1,2}/g);
    if (matches && matches.length >= 2) {
      const end = formatEnd(matches[1]);
      return end ? `${newStart} - ${end}` : newStart;
    }
    return newStart;
  }
  return newStart;
};

// 规范化 ID 列表用于比较
const normalizeIdList = (ids) =>
  (Array.isArray(ids) ? ids : [])
    .map((id) => String(id).trim())
    .filter(Boolean)
    .sort();

// 成员下拉选项
const memberOptions = computed(() =>
  members.value.map((item) => ({
    id: item.user_id,
    label: `${item.name || '未命名'}${item.account ? ` (${item.account})` : ''}`
  }))
);


// 标准化文本展示
const normalizeLabel = (value) => {
  if (value === null || value === undefined) return '';
  if (typeof value === 'string') return value.trim();
  return String(value);
};

// 规范化阶段序号为可比较类型
const normalizeOrderValue = (value) => {
  if (value === null || value === undefined) return null;
  const trimmed = String(value).trim();
  if (!trimmed) return null;
  const numeric = Number(trimmed);
  if (Number.isFinite(numeric)) return numeric;
  return trimmed;
};

// 比较阶段序号（数字优先）
const compareOrderValue = (a, b) => {
  if (a === null || a === undefined) return b === null || b === undefined ? 0 : 1;
  if (b === null || b === undefined) return -1;
  const aIsNumber = typeof a === 'number' && Number.isFinite(a);
  const bIsNumber = typeof b === 'number' && Number.isFinite(b);
  if (aIsNumber && bIsNumber) return a - b;
  return String(a).localeCompare(String(b), 'zh');
};

// 按项目分组记录
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

// 分组变化时同步选中项目
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


// 当前选中的项目
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

// 当前项目标题
const currentProjectLabel = computed(() => {
  const name = currentProject.value.projectName || '暂无项目';
  const code = currentProject.value.projectCode;
  return code ? `${name} (${code})` : name;
});

// 项目下拉选项
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

// 规范化节点数据用于展示
const normalizeNode = (record, index) => {
  const planRange = parseDateRange(record.plan_time);
  const planStartDate = planRange.start || null;
  const planEndDate = planRange.end || null;

  const mainStageLabel = normalizeLabel(record.main_stage || record.mainStage);
  const projectStageLabel = normalizeLabel(record.project_stage || record.projectStage || record.stage);
  const fallbackLabel = projectStageLabel || mainStageLabel || `节点${index + 1}`;
  const nodeLabel = projectStageLabel || (!mainStageLabel ? fallbackLabel : '');

  return {
    id: record._id || `${index}`,
    recordId: record._id,
    name: fallbackLabel,
    mainStageLabel,
    nodeLabel,
    mainStageOrder: normalizeOrderValue(record.main_stage_order),
    projectStageOrder: normalizeOrderValue(record.project_stage_order),
    status: record.status || '未完成',
    warningLevel: record.warning_level || '正常',
    executorName: formatUser(record.executor),
    executorRaw: record.executor,
    rawPlanTime: record.plan_time,
    planStartRaw: planStartDate,
    planEndRaw: planEndDate,
    planStart: formatDateCell(planStartDate),
    planEnd: formatDateCell(planEndDate),
    planStartSort: planStartDate ? planStartDate.getTime() : null,
    originalIndex: index,
    isMilestone: isDone(record.status || '未完成')
  };
};

// 时间轴节点（按序号/时间排序）
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

// 表格数据（按主阶段分组）
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

// 判断节点是否已完成
const isDone = (status) => status === '完成' || status === '超期完成';

// 计算整体完成进度
const overallProgress = computed(() => {
  const total = timelineNodes.value.length;
  const doneCount = timelineNodes.value.filter((node) => isDone(node.status)).length;
  return total === 0 ? 0 : Math.round((doneCount / total) * 100);
});

// 预警统计
const totalWarningLevelCount = computed(
  () => timelineNodes.value.filter((node) => node.status === '超期').length
);
const warningLevelCount = computed(
  () => timelineNodes.value.filter((node) => node.warningLevel && node.warningLevel !== '正常').length
);

// 里程碑统计
const milestoneReachedCount = computed(() => timelineNodes.value.filter((node) => isDone(node.status)).length);
const milestoneTotalCount = computed(() => timelineNodes.value.length);

// 进度标签颜色
const overallProgressType = computed(() => (warningLevelCount.value > 0 ? 'danger' : 'primary'));

// 状态标签样式
const getStatusTag = (status) => {
  if (status === '完成' || status === '超期完成') return 'success';
  if (status === '超期') return 'danger';
  return 'info';
};

// 兜底状态展示
const displayStatus = (status) => {
  if (status === '????') return '??';
  return status || '???';
};

// 分组行样式
const getRowClass = ({ row }) => (row.isGroup ? 'table-group-row' : '');

// 预警等级标签样式
const getWarningTag = (level) => {
  if (level === '三级预警') return 'danger';
  if (level === '二级预警') return 'warning';
  if (level === '一级预警') return 'info';
  return 'success';
};

// 拉取进度数据
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

// 搜索项目进度
const handleSearch = async () => {
  await loadProgressRecords(searchQuery.value.trim());
};

// 拉取成员列表
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

// 打开编辑弹窗
const openEditDialog = async (row) => {
  if (!row || row.isGroup) return;
  editRow.value = row;
  const initialExecutorIds = getExecutorIds(row.executorRaw);
  editForm.value = {
    planStart: row.planStartRaw ? formatDate(row.planStartRaw) : row.planStart || '',
    executorIds: initialExecutorIds
  };
  originalExecutorIds.value = [...initialExecutorIds];
  editDialogVisible.value = true;
  if (!members.value.length) {
    await loadMembers();
  }
  const missingIds = (editForm.value.executorIds || []).filter(
    (id) => !members.value.find((item) => item.user_id === id)
  );
  if (missingIds.length) {
    members.value = [
      ...members.value,
      ...missingIds.map((id) => ({
        user_id: id,
        name: row.executorName || '未知成员'
      }))
    ];
  }
};

// 保存节点编辑
const handleSaveEdit = async () => {
  if (!editRow.value?.recordId) {
    ElMessage.error('无法编辑：缺少记录ID');
    return;
  }
  savingEdit.value = true;
  try {
    const payload = {};
    if (editForm.value.planStart) {
      payload.plan_time = updatePlanTimeValue(
        editRow.value.rawPlanTime,
        editForm.value.planStart,
        editRow.value.planEndRaw
      );
    }
    const currentExecutorIds = normalizeIdList(editForm.value.executorIds);
    const originalIds = normalizeIdList(originalExecutorIds.value);
    if (JSON.stringify(currentExecutorIds) !== JSON.stringify(originalIds)) {
      payload.executor = currentExecutorIds;
    }
    if (Object.keys(payload).length === 0) {
      ElMessage.warning('没有可更新的内容');
      savingEdit.value = false;
      return;
    }
    const result = await api.updateProjectProgress(editRow.value.recordId, payload);
    if (result?.code === 200) {
      ElMessage.success('更新成功');
      editDialogVisible.value = false;
      await loadProgressRecords(searchQuery.value.trim());
    } else {
      ElMessage.error(result?.msg || '更新失败');
    }
  } catch (error) {
    console.error('更新失败：', error);
    ElMessage.error('更新失败');
  } finally {
    savingEdit.value = false;
  }
};

// 页面初始化
onMounted(async () => {
  await loadProgressRecords();
  // 读取 URL 参数（调试用）
  function getQueryParam(paramName) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(paramName);
  }

  // 1. 获取 ID
  const userId = getQueryParam('webpage_user_id');
  console.log('Webpage User ID:', userId);
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
  padding: 32px 20px 64px 20px;
  background: linear-gradient(180deg, #f7f8fb 0%, #ffffff 100%);
  border: 1px solid rgba(60, 60, 67, 0.08);
  border-radius: 16px;
  box-shadow:
    0 8px 24px rgba(15, 23, 42, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.node-markers {
  display: flex;
  justify-content: space-between;
  position: absolute;
  width: calc(100% - 40px);
  top: 18px;
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
  border: 1px solid rgba(60, 60, 67, 0.22);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  position: relative;
  box-shadow:
    0 6px 12px rgba(15, 23, 42, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.marker-dot.is-done {
  border-color: #34c759;
  background: #34c759;
  color: #fff;
  box-shadow: 0 8px 14px rgba(52, 199, 89, 0.4);
}

.marker-dot.is-overdue {
  border-color: #ff3b30;
  color: #ff3b30;
  background: #fff5f5;
  box-shadow: 0 6px 12px rgba(255, 59, 48, 0.28);
}

.marker-label {
  position: absolute;
  top: 40px;
  transform: translateX(-50%);
  left: 50%;
  white-space: nowrap;
  font-size: 12px;
  color: rgba(60, 60, 67, 0.85);
  letter-spacing: 0.2px;
}

.marker-pending-dot {
  width: 6px;
  height: 6px;
  background: rgba(60, 60, 67, 0.4);
  border-radius: 50%;
  display: inline-block;
}

.node-flag-icon {
  position: absolute;
  top: -18px;
  right: -12px;
  color: #ff3b30;
  font-size: 16px;
  animation: wave 2s infinite ease-in-out;
}

.segmented-progress {
  position: relative;
  height: 6px;
  border-radius: 999px;
  background: #e5e5ea;
  overflow: hidden;
}

.segmented-progress__fill {
  height: 100%;
  width: 0;
  background: #34c759;
  transition: width 0.6s ease;
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

.card-header {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.card-label {
  color: #8c8c8c;
  font-size: 14px;
}

.card-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
}

.card-icon.is-primary {
  background: rgba(24, 144, 255, 0.12);
  color: #1890ff;
}

.card-icon.is-warning {
  background: rgba(250, 140, 22, 0.14);
  color: #fa8c16;
}

.card-icon.is-danger {
  background: rgba(245, 34, 45, 0.12);
  color: #f5222d;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  padding-left: 12px;
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
