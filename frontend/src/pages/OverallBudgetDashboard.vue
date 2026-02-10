<template>
  <el-config-provider :locale="zhCn">
    <div class="dashboard-container">
    <!-- 主内容 -->
    <div class="main-content">
      <div class="header">
        <div class="header-left">
          <!-- <div class="brand-text">徽派家私管理平台</div>
          <div class="header-title">整体预算看板</div> -->
          <div class="header-controls">
            <el-select v-model="currentYear" placeholder="选择年份" style="width: 120px;">
              <el-option v-for="year in availableYears" :key="year" :label="`${year}年`" :value="year"></el-option>
            </el-select>
            <el-button type="primary" plain :icon="Refresh" @click="refreshData">刷新数据</el-button>
          </div>
        </div>
      </div>

        <div class="page-container" v-loading="loading">
          <!-- 核心指标卡片 -->
          <div class="dashboard-grid">
            <div class="kpi-card">
              <div class="kpi-title">年度总预算</div>
              <div class="kpi-value">¥ {{ formatMoney(dashboardMetrics.totalBudget) }}</div>
              <div class="kpi-sub">
                <span>项目总数: {{ dashboardMetrics.projectCount }}</span>
                <span :class="budgetYoYClass">{{ budgetYoYText }}</span>
              </div>
            </div>
            <div class="kpi-card">
              <div class="kpi-title">实际发生成本</div>
              <div class="kpi-value">¥ {{ formatMoney(dashboardMetrics.totalActual) }}</div>
              <div class="kpi-sub">
                <span>执行率: {{ dashboardMetrics.executionRate }}%</span>
              </div>
            </div>
            <div class="kpi-card">
              <div class="kpi-title">累计超支金额</div>
              <div class="kpi-value text-danger">¥ {{ formatMoney(dashboardMetrics.overrunAmount) }}</div>
              <div class="kpi-sub">
                <span>超支项目: {{ dashboardMetrics.overrunProjects.length }}</span>
                <span :class="dashboardMetrics.overrunAmount > 0 ? 'text-danger' : ''">超支比例: {{ dashboardMetrics.overrunRate }}%</span>
              </div>
            </div>
            <div class="kpi-card">
              <div class="kpi-title">预算剩余</div>
              <div class="kpi-value" :class="dashboardMetrics.remaining >= 0 ? 'text-success' : 'text-danger'">
                ¥ {{ formatMoney(dashboardMetrics.remaining) }}
              </div>
              <div class="kpi-sub">
                <span>可用占比: {{ dashboardMetrics.remainingRate }}%</span>
              </div>
            </div>
          </div>

        <!-- 图表区域 1 -->
        <div class="chart-row">
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">各项目预算执行对比 (Top 10)</div>
            </div>
            <!-- 使用 ref 引用 DOM 元素 -->
            <div ref="projectBudgetChartRef" style="height: 350px; width: 100%;"></div>
          </div>
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">整体成本构成</div>
            </div>
            <div ref="costCompositionChartRef" style="height: 350px; width: 100%;"></div>
          </div>
        </div>

        <!-- 列表区域 -->
        <div class="chart-row-equal">
          <!-- 预算执行情况排序 -->
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">预算执行率排行 (Top 10)</div>
              <el-radio-group v-model="rankSortType" size="small">
                <el-radio-button label="high">执行率最高</el-radio-button>
                <el-radio-button label="low">执行率最低</el-radio-button>
              </el-radio-group>
            </div>
            <el-table :data="sortedExecutionData" style="width: 100%" size="small">
              <el-table-column prop="rank" label="排名" width="60" align="center">
                <template #default="scope">
                  <span :style="{color: scope.row.rank <= 3 ? '#ff9900' : '#606266', fontWeight: scope.row.rank <= 3 ? 'bold' : 'normal'}">
                    {{ scope.row.rank }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="projectName" label="项目名称" show-overflow-tooltip></el-table-column>
              <el-table-column prop="manager" label="负责人" width="100"></el-table-column>
              <el-table-column prop="rate" label="执行率" width="120" sortable>
                <template #default="scope">
                  <el-progress :percentage="scope.row.rate" :status="getRateStatus(scope.row.rate)"></el-progress>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 超支项目排序 -->
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">超支项目排行</div>
            </div>
            <el-table :data="overrunData" style="width: 100%" size="small">
              <el-table-column prop="projectName" label="项目名称" show-overflow-tooltip></el-table-column>
              <el-table-column prop="budget" label="总预算">
                <template #default="scope">¥{{ formatMoney(scope.row.budget) }}</template>
              </el-table-column>
              <el-table-column prop="actual" label="实际成本">
                <template #default="scope">¥{{ formatMoney(scope.row.actual) }}</template>
              </el-table-column>
              <el-table-column prop="overrun" label="超支金额" sortable>
                <template #default="scope">
                  <span class="text-danger">¥{{ formatMoney(scope.row.overrun) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="ratio" label="超支比例" width="100">
                <template #default="scope">
                  <el-tag type="danger">{{ scope.row.ratio }}%</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <!-- 成本中心预算执行排行 -->
        <div class="panel">
          <div class="panel-header">
            <div class="panel-title">各成本中心预算执行排行</div>
            <el-tag size="small" effect="plain">按年度累计</el-tag>
          </div>
          <el-table :data="costCenterData" style="width: 100%" :default-sort="{ prop: 'rate', order: 'descending' }">
            <el-table-column type="index" label="排名" width="80" align="center">
              <template #default="scope">
                <div :style="{
                  background: scope.$index < 3 ? '#1890ff' : '#f0f2f5',
                  color: scope.$index < 3 ? '#fff' : '#606266',
                  width: '24px',
                  height: '24px',
                  lineHeight: '24px',
                  borderRadius: '50%',
                  margin: '0 auto',
                  fontWeight: 'bold'
                }">{{ scope.$index + 1 }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="成本中心" width="180">
              <template #default="scope">
                <span style="font-weight: 500;">{{ scope.row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="budget" label="年度预算限额" align="right">
              <template #default="scope">
                <span style="color: #606266;">¥ {{ formatMoney(scope.row.budget) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="actual" label="实际累计成本" align="right">
              <template #default="scope">
                <span style="font-weight: bold;">¥ {{ formatMoney(scope.row.actual) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="rate" label="执行率" width="250">
              <template #default="scope">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <el-progress 
                    :percentage="scope.row.rate" 
                    :stroke-width="10" 
                    :color="getCostCenterStatusColor(scope.row.rate)"
                    style="flex: 1;"
                  ></el-progress>
                  <span style="width: 45px; font-size: 12px;">{{ scope.row.rate }}%</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="variance" label="结余/超支" align="right">
              <template #default="scope">
                <span :class="scope.row.variance >= 0 ? 'text-success' : 'text-danger'">
                  {{ scope.row.variance >= 0 ? '+' : '' }}{{ formatMoney(scope.row.variance) }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue';
import * as echarts from 'echarts';
import { Refresh } from '@element-plus/icons-vue';
import { ElMessage, ElConfigProvider } from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import api from '../api/client';

// 状态定义
const currentYear = ref('2024');
const rankSortType = ref('high');
const projectBudgetChartRef = ref(null);
const costCompositionChartRef = ref(null);
let projectBudgetChart = null;
let costCompositionChart = null;
const loading = ref(false);
const allBudgetRecords = ref([]);
const projectRecords = ref([]);

// 通用工具方法
const normalizeLabel = (value) => {
  if (value === null || value === undefined) return '';
  return String(value).trim();
};

const normalizeProjectCode = (value) => {
  const text = normalizeLabel(value);
  if (!text) return '';
  if (text.includes(' - ')) {
    return text.split(' - ')[0].trim();
  }
  const spaceIndex = text.indexOf(' ');
  if (spaceIndex > 0) {
    return text.slice(0, spaceIndex).trim();
  }
  return text;
};

const toNumber = (value) => {
  if (value === null || value === undefined || value === '') return 0;
  if (typeof value === 'number') return Number.isFinite(value) ? value : 0;
  const cleaned = String(value).replace(/,/g, '');
  const numeric = Number(cleaned);
  return Number.isFinite(numeric) ? numeric : 0;
};

const formatMoney = (value) => {
  const amount = toNumber(value);
  return amount.toLocaleString('zh-CN');
};

const extractYearFromDate = (value) => {
  if (!value) return null;
  if (value instanceof Date && !Number.isNaN(value.getTime())) {
    return String(value.getFullYear());
  }
  if (typeof value === 'number') {
    if (value >= 1900 && value <= 2100) {
      return String(value);
    }
    return extractYearFromDate(new Date(value));
  }
  const trimmed = String(value).trim();
  if (!trimmed) return null;
  const match = trimmed.match(/(19|20)\d{2}/);
  if (match) return match[0];
  const parsed = new Date(trimmed.replace(/-/g, '/'));
  if (!Number.isNaN(parsed.getTime())) {
    return String(parsed.getFullYear());
  }
  return null;
};

const resolveProjectCode = (project) =>
  normalizeProjectCode(
    project?.project_code ||
    project?.projectCode ||
    project?.code ||
    project?.['项目编号']
  );

const resolveProjectName = (project) =>
  normalizeLabel(
    project?.project_name ||
    project?.projectName ||
    project?.name ||
    project?.['项目名称']
  );

const resolveProjectPlanStart = (project) => {
  const raw = project?.plan_start ||
    project?.planStart ||
    project?.plan_start_time ||
    project?.['计划开工'];
  if (raw && typeof raw === 'object') {
    return raw.date || raw.value || raw.time || raw.start || raw;
  }
  return raw;
};

const normalizeManagerName = (value) => {
  if (!value) return '';
  if (typeof value === 'string') return value.trim();
  if (Array.isArray(value)) {
    const names = value.map((item) => {
      if (!item) return '';
      if (typeof item === 'string') return item.trim();
      return (item.name || item.username || item.realname || item.user_name || item.label || item.value || item._id || '').toString().trim();
    }).filter(Boolean);
    return names.join('、');
  }
  if (typeof value === 'object') {
    return (value.name || value.username || value.realname || value.user_name || value.label || value.value || value._id || '').toString().trim();
  }
  return String(value).trim();
};

const resolveProjectManager = (project) =>
  normalizeManagerName(
    project?.project_manager ||
    project?.projectManager ||
    project?.manager ||
    project?.owner ||
    project?.leader ||
    project?.principal ||
    project?.['项目经理']
  );

const projectYearMap = computed(() => {
  const map = new Map();
  projectRecords.value.forEach((project) => {
    const code = resolveProjectCode(project);
    if (!code) return;
    const year = extractYearFromDate(resolveProjectPlanStart(project));
    if (year) {
      map.set(code, year);
    }
  });
  return map;
});

const projectManagerMap = computed(() => {
  const map = new Map();
  projectRecords.value.forEach((project) => {
    const code = resolveProjectCode(project);
    const name = resolveProjectName(project);
    const manager = resolveProjectManager(project);
    if (code && manager) {
      map.set(code, manager);
    }
    if (!code && name && manager) {
      map.set(name, manager);
    }
  });
  return map;
});

const projectNameYearMap = computed(() => {
  const map = new Map();
  projectRecords.value.forEach((project) => {
    const name = resolveProjectName(project);
    if (!name) return;
    const year = extractYearFromDate(resolveProjectPlanStart(project));
    if (year) {
      map.set(name, year);
    }
  });
  return map;
});

const availableYears = computed(() => {
  const years = new Set();
  projectRecords.value.forEach((project) => {
    const year = extractYearFromDate(resolveProjectPlanStart(project));
    if (year) {
      years.add(year);
    }
  });
  if (years.size === 0) {
    return ['2025', '2024', '2023'];
  }
  return Array.from(years).sort((a, b) => Number(b) - Number(a));
});

const extractRecordYear = (record) => {
  const candidates = [
    record?.budget_year,
    record?.project_year,
    record?.year,
    record?.budgetYear,
    record?.projectYear
  ];
  for (const value of candidates) {
    const year = extractYearFromDate(value);
    if (year) return year;
  }
  const projectCode = normalizeProjectCode(record?.project_code);
  if (projectCode) {
    const year = projectYearMap.value.get(projectCode);
    if (year) return year;
  }
  const projectName = normalizeLabel(record?.project_name);
  if (projectName) {
    const year = projectNameYearMap.value.get(projectName);
    if (year) return year;
  }
  return null;
};

const recordBelongsToYear = (record, year) => {
  const recordYear = extractRecordYear(record);
  if (recordYear) return recordYear === year;
  if (projectRecords.value.length === 0) return true;
  return false;
};

const getRecordActual = (record) => {
  const actual = toNumber(record?.actual_total);
  const details = Array.isArray(record?.cost_details) ? record.cost_details : [];
  const sumDetails = details.reduce((acc, item) => acc + toNumber(item?.detail_amount), 0);
  if (actual === 0 && sumDetails > 0) return sumDetails;
  return actual;
};

const getRecordActualByYear = (record, year) => {
  if (!recordBelongsToYear(record, year)) return 0;
  const details = Array.isArray(record?.cost_details) ? record.cost_details : [];
  const actualTotal = toNumber(record?.actual_total);
  const sumDetails = details.reduce((acc, item) => acc + toNumber(item?.detail_amount), 0);
  const baseActual = actualTotal > 0 ? actualTotal : sumDetails;

  const hasDatedDetails = details.some((detail) => !!extractYearFromDate(detail?.detail_date));
  if (hasDatedDetails && actualTotal === 0) {
    let sumForYear = 0;
    details.forEach((detail) => {
      const detailYear = extractYearFromDate(detail?.detail_date);
      if (detailYear === year) {
        sumForYear += toNumber(detail?.detail_amount);
      }
    });
    return sumForYear;
  }

  return baseActual;
};

const getRecordBudgetByYear = (record, year) => {
  if (!recordBelongsToYear(record, year)) return 0;
  return toNumber(record?.budget_standard);
};

const buildProjectKey = (record) => {
  const code = normalizeProjectCode(record?.project_code);
  const name = normalizeLabel(record?.project_name);
  const type = normalizeLabel(record?.project_type);
  if (!code && !name && !type) {
    return record?._id ? `unknown-${record._id}` : 'unknown';
  }
  return `${code}||${name}||${type}`;
};

const buildProjectLabel = (code, name) => {
  if (code) return `${code} - ${name || '未命名项目'}`;
  return name || '未命名项目';
};

const resolveManager = (record) => {
  const projectCode = normalizeProjectCode(record?.project_code);
  if (projectCode && projectManagerMap.value.has(projectCode)) {
    return projectManagerMap.value.get(projectCode) || '';
  }
  const projectName = normalizeLabel(record?.project_name);
  if (projectName && projectManagerMap.value.has(projectName)) {
    return projectManagerMap.value.get(projectName) || '';
  }
  return normalizeManagerName(
    record?.project_manager ||
    record?.manager ||
    record?.owner ||
    record?.leader ||
    record?.principal
  );
};

const classifyCost = (label) => {
  const text = label || '';
  if (/材料|采购|五金|板材|木作|原材料|辅料/.test(text)) return 'material';
  if (/人工|工资|劳务|安装/.test(text)) return 'labor';
  if (/设备|机械|工具/.test(text)) return 'equipment';
  if (/管理|办公|行政|差旅|租赁|礼品/.test(text)) return 'manage';
  return 'other';
};

const computeDashboardData = (records, year) => {
  const projectMap = new Map();
  const costCenterMap = new Map();
  const composition = {
    material: 0,
    labor: 0,
    equipment: 0,
    manage: 0,
    other: 0
  };
  let totalBudget = 0;
  let totalActual = 0;

  records.forEach((record) => {
    const budget = getRecordBudgetByYear(record, year);
    const actual = getRecordActualByYear(record, year);
    if (budget === 0 && actual === 0) return;

    totalBudget += budget;
    totalActual += actual;

    const projectKey = buildProjectKey(record);
    const code = normalizeProjectCode(record?.project_code);
    const name = normalizeLabel(record?.project_name);
    const type = normalizeLabel(record?.project_type);
    let entry = projectMap.get(projectKey);
    if (!entry) {
      entry = {
        key: projectKey,
        code,
        name,
        type,
        budget: 0,
        actual: 0,
        manager: resolveManager(record)
      };
      projectMap.set(projectKey, entry);
    } else if (!entry.manager) {
      const manager = resolveManager(record);
      if (manager) entry.manager = manager;
    }
    entry.budget += budget;
    entry.actual += actual;

    const center = normalizeLabel(record?.cost_center) || '未分类';
    let centerEntry = costCenterMap.get(center);
    if (!centerEntry) {
      centerEntry = { name: center, budget: 0, actual: 0 };
      costCenterMap.set(center, centerEntry);
    }
    centerEntry.budget += budget;
    centerEntry.actual += actual;

    if (actual > 0) {
      const bucket = classifyCost(normalizeLabel(record?.cost_item));
      composition[bucket] += actual;
    }
  });

  const projects = Array.from(projectMap.values()).map((entry) => {
    const rate = entry.budget > 0
      ? Number(((entry.actual / entry.budget) * 100).toFixed(1))
      : (entry.actual > 0 ? 100 : 0);
    const overrun = entry.actual - entry.budget;
    const remaining = entry.budget - entry.actual;
    return {
      ...entry,
      label: buildProjectLabel(entry.code, entry.name),
      shortName: entry.code || entry.name || '未命名项目',
      rate,
      overrun,
      remaining
    };
  });

  const costCenters = Array.from(costCenterMap.values()).map((entry) => {
    const rate = entry.budget > 0
      ? Number(((entry.actual / entry.budget) * 100).toFixed(1))
      : (entry.actual > 0 ? 100 : 0);
    const variance = entry.budget - entry.actual;
    return {
      ...entry,
      rate,
      variance
    };
  });

  return {
    totalBudget,
    totalActual,
    projects,
    costCenters,
    composition: [
      { value: composition.material, name: '材料费' },
      { value: composition.labor, name: '人工费' },
      { value: composition.equipment, name: '设备费' },
      { value: composition.manage, name: '管理费' },
      { value: composition.other, name: '其他' }
    ]
  };
};

const hasYearInfo = computed(() =>
  projectRecords.value.some((project) => extractYearFromDate(resolveProjectPlanStart(project))) ||
  allBudgetRecords.value.some((record) => {
    if (extractRecordYear(record)) return true;
    const details = Array.isArray(record?.cost_details) ? record.cost_details : [];
    return details.some((detail) => extractYearFromDate(detail?.detail_date));
  })
);

const dashboardMetrics = computed(() => {
  const year = String(currentYear.value || '');
  const records = allBudgetRecords.value;
  const data = computeDashboardData(records, year);
  const totalBudget = data.totalBudget;
  const totalActual = data.totalActual;
  const executionRate = totalBudget > 0
    ? Number(((totalActual / totalBudget) * 100).toFixed(1))
    : 0;
  const remaining = totalBudget - totalActual;
  const remainingRate = totalBudget > 0
    ? Number(((remaining / totalBudget) * 100).toFixed(1))
    : 0;
  const projectCount = data.projects.length;
  const overrunProjects = data.projects.filter((item) => item.actual > item.budget);
  const overrunAmount = overrunProjects.reduce(
    (acc, item) => acc + Math.max(0, item.actual - item.budget),
    0
  );
  const overrunRate = totalBudget > 0
    ? Number(((overrunAmount / totalBudget) * 100).toFixed(1))
    : 0;

  let budgetYoY = null;
  if (hasYearInfo.value) {
    const yearNum = Number(year);
    if (Number.isFinite(yearNum)) {
      const prevYear = String(yearNum - 1);
      const prevData = computeDashboardData(records, prevYear);
      if (prevData.totalBudget > 0) {
        budgetYoY = Number((((totalBudget - prevData.totalBudget) / prevData.totalBudget) * 100).toFixed(1));
      }
    }
  }

  return {
    ...data,
    totalBudget,
    totalActual,
    executionRate,
    remaining,
    remainingRate,
    projectCount,
    overrunProjects,
    overrunAmount,
    overrunRate,
    budgetYoY
  };
});

const budgetYoYText = computed(() => {
  if (dashboardMetrics.value.budgetYoY === null) return '同比: --';
  const value = dashboardMetrics.value.budgetYoY;
  const sign = value > 0 ? '+' : '';
  return `${sign}${value}% 同比`;
});

const budgetYoYClass = computed(() => {
  if (dashboardMetrics.value.budgetYoY === null) return '';
  return dashboardMetrics.value.budgetYoY >= 0 ? 'text-success' : 'text-danger';
});

// 计算属性：根据排序类型返回排序后的执行数据
const sortedExecutionData = computed(() => {
  const list = dashboardMetrics.value.projects.map((item) => ({
    projectName: item.label,
    manager: item.manager || '--',
    rate: item.rate
  }));
  const sorted = [...list].sort((a, b) => {
    if (rankSortType.value === 'high') {
      return b.rate - a.rate;
    }
    return a.rate - b.rate;
  });
  return sorted.slice(0, 10).map((item, index) => ({
    ...item,
    rank: index + 1
  }));
});

const overrunData = computed(() => {
  const rows = dashboardMetrics.value.overrunProjects.map((item) => ({
    projectName: item.label,
    budget: item.budget,
    actual: item.actual,
    overrun: Math.max(0, item.actual - item.budget),
    ratio: item.budget > 0
      ? Number((((item.actual - item.budget) / item.budget) * 100).toFixed(1))
      : 0
  }));
  return rows.sort((a, b) => b.overrun - a.overrun).slice(0, 10);
});

const costCenterData = computed(() =>
  [...dashboardMetrics.value.costCenters].sort((a, b) => b.rate - a.rate)
);

const toWan = (value) => Number((toNumber(value) / 10000).toFixed(2));

const projectBudgetChartData = computed(() => {
  const list = [...dashboardMetrics.value.projects];
  const sorted = list.sort((a, b) => {
    if (b.budget !== a.budget) return b.budget - a.budget;
    return b.actual - a.actual;
  });
  const topList = sorted.slice(0, 10);
  return {
    labels: topList.map((item) => item.shortName),
    budgets: topList.map((item) => toWan(item.budget)),
    actuals: topList.map((item) => toWan(item.actual))
  };
});

const costCompositionData = computed(() => dashboardMetrics.value.composition);

const getBarWidth = (count) => {
  if (count <= 3) return 36;
  if (count <= 5) return 30;
  if (count <= 7) return 24;
  if (count <= 10) return 18;
  return 14;
};

// 工具方法
const getRateStatus = (rate) => {
  if (rate >= 100) return 'exception';
  if (rate >= 90) return 'warning';
  return 'success';
};

const getCostCenterStatusColor = (rate) => {
  if (rate > 100) return '#F56C6C'; // 超支
  if (rate > 90) return '#E6A23C'; // 预警
  return '#67C23A'; // 正常
};

const loadBudgetRecords = async () => {
  try {
    const result = await api.listProjectBudgets({ skip: 0, limit: 300 });
    if (result?.code === 200 && Array.isArray(result.data)) {
      allBudgetRecords.value = result.data;
      return true;
    }
    allBudgetRecords.value = [];
    ElMessage.error(result?.msg || '加载预算数据失败');
    return false;
  } catch (error) {
    console.error('加载预算数据失败：', error);
    allBudgetRecords.value = [];
    ElMessage.error('加载预算数据失败');
    return false;
  }
};

const loadProjectRecords = async () => {
  try {
    const result = await api.listProjectSummary({ skip: 0, limit: 300 });
    if (result?.code === 200 && Array.isArray(result.data)) {
      projectRecords.value = result.data;
      return true;
    }
    projectRecords.value = [];
    ElMessage.error(result?.msg || '加载项目信息失败');
    return false;
  } catch (error) {
    console.error('加载项目信息失败：', error);
    projectRecords.value = [];
    ElMessage.error('加载项目信息失败');
    return false;
  }
};

const loadDashboardData = async () => {
  loading.value = true;
  try {
    const [budgetOk, projectOk] = await Promise.all([
      loadBudgetRecords(),
      loadProjectRecords()
    ]);
    return budgetOk && projectOk;
  } finally {
    loading.value = false;
  }
};

const refreshData = async () => {
  const ok = await loadDashboardData();
  if (ok) {
    ElMessage.success('数据已刷新');
  }
};

// 图表初始化
const updateCharts = () => {
  if (projectBudgetChartRef.value) {
    if (!projectBudgetChart) {
      projectBudgetChart = echarts.init(projectBudgetChartRef.value);
    }
    const chartData = projectBudgetChartData.value;
    const barWidth = getBarWidth(chartData.labels.length);
    const barMaxWidth = Math.min(40, barWidth + 6);
    projectBudgetChart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      legend: {
        data: ['总预算', '实际成本'],
        top: 0,
        left: 'center'
      },
      grid: {
        left: '3%',
        right: '4%',
        top: 50,
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: chartData.labels,
        axisLabel: { interval: 0, rotate: 30 }
      },
      yAxis: {
        type: 'value',
        name: '金额 (万元)'
      },
      series: [
        {
          name: '总预算',
          type: 'bar',
          barWidth,
          barMaxWidth,
          data: chartData.budgets,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#36D1DC' },
              { offset: 1, color: '#5B86E5' }
            ])
          }
        },
        {
          name: '实际成本',
          type: 'bar',
          barWidth,
          barMaxWidth,
          data: chartData.actuals,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#FF9966' },
              { offset: 1, color: '#FF5E62' }
            ])
          }
        }
      ]
    }, { notMerge: true });
  }

  if (costCompositionChartRef.value) {
    if (!costCompositionChart) {
      costCompositionChart = echarts.init(costCompositionChartRef.value);
    }
    costCompositionChart.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        top: '5%',
        left: 'center'
      },
      series: [
        {
          name: '成本构成',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 20,
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: costCompositionData.value
        }
      ]
    }, { notMerge: true });
  }
};

const handleResize = () => {
  projectBudgetChart?.resize();
  costCompositionChart?.resize();
};

watch(dashboardMetrics, () => {
  nextTick(() => updateCharts());
}, { deep: true });

watch(availableYears, (years) => {
  if (!years || years.length === 0) return;
  if (!years.includes(currentYear.value)) {
    currentYear.value = years[0];
  }
}, { immediate: true });

onMounted(async () => {
  await loadDashboardData();
  nextTick(() => {
    updateCharts();
    window.addEventListener('resize', handleResize);
  });
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  projectBudgetChart?.dispose();
  costCompositionChart?.dispose();
});
</script>

<style scoped>
.dashboard-container {
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  background-color: #f0f2f5;
  color: #333;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  width: 100%;
}

.header {
  height: 64px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px;
  z-index: 10;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.header-controls {
  display: flex; 
  align-items: center; 
  gap: 8px; 
  margin-left: 12px;
}

.brand-text {
  font-size: 20px;
  font-weight: bold;
  color: #001529;
  margin-right: 12px;
  padding-right: 24px;
  border-right: 1px solid #f0f0f0;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
}

.page-container {
  padding: 8px;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 100%;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

/* 看板样式 */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.kpi-card {
  background: #fff;
  padding: 16px;
  border-radius: 4px;
  box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}
.kpi-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.kpi-title {
  color: #909399;
  font-size: 14px;
  margin-bottom: 12px;
}
.kpi-value {
  font-size: 30px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 16px;
}
.kpi-sub {
  font-size: 13px;
  color: #909399;
  display: flex;
  justify-content: space-between;
}

.chart-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 12px;
  min-height: 400px;
}
.chart-row-equal {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  min-height: 450px;
}

.panel {
  background: #fff;
  border-radius: 4px;
  padding: 16px;
  box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}
.panel-title {
  font-size: 16px;
  font-weight: bold;
  border-left: 4px solid #1890ff;
  padding-left: 12px;
}

.text-success { color: #67C23A; }
.text-danger { color: #F56C6C; }
.text-warning { color: #E6A23C; }

/* 响应式调整 */
@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .chart-row, .chart-row-equal {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  .brand-text {
    border-right: none;
    margin-right: 0;
    padding-right: 0;
  }
  .header-controls {
    margin-left: 0;
  }
}
</style>
