<template>
  <div class="dashboard-container">
    <div class="main-content">
      <!-- 页面内容容器 -->
      <div class="page-container" v-loading="loading">
        <!-- 顶部筛选栏 (整合了标题) -->
        <div class="filter-bar">
          <div class="filter-left">
            <!-- <span class="page-title">项目管控看板 - 成本视角</span>
            <div class="divider"></div> -->
            <span class="filter-label">当前项目:</span>
            <el-select
              v-model="currentProject"
              placeholder="请选择项目"
              style="width: 300px;"
              :loading="loading"
              filterable
              @change="handleProjectChange"
            >
              <el-option
                v-for="item in projectOptions"
                :key="item.key"
                :label="item.label"
                :value="item.key"
              ></el-option>
            </el-select>
          </div>
          <el-button type="primary" :icon="Refresh" @click="refreshData">刷新数据</el-button>
        </div>

        <!-- 1. 核心 KPI 指标卡 -->
        <div class="dashboard-grid">
          <div class="kpi-card">
            <div class="kpi-title">项目总预算 (含税)</div>
            <div class="kpi-value">¥ {{ formatMoney(kpi.totalBudget) }}</div>
            <div class="kpi-footer">
              <span>预算变更次数</span>
              <span style="font-weight: bold;">3次</span>
            </div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">实际累计成本</div>
            <div class="kpi-value" style="color: #1890ff;">¥ {{ formatMoney(kpi.actualCost) }}</div>
            <div class="kpi-footer">
              <span>预算执行率</span>
              <span :class="kpi.costRate > 90 ? 'text-up' : 'text-down'">{{ kpi.costRate }}%</span>
            </div>
          </div>
        <div class="kpi-card">
          <div class="kpi-title">当前毛利率 (预估)</div>
          <div class="kpi-value" style="color: #52c41a;">{{ kpi.marginRate }}%</div>
          <div class="kpi-footer">
            <span>目标毛利率</span>
            <span>35.0%</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">现金流结余</div>
          <div class="kpi-value" :style="{ color: kpi.cashFlow >= 0 ? '#faad14' : '#f5222d' }">
            ¥ {{ formatMoney(kpi.cashFlow) }}
          </div>
          <div class="kpi-footer">
            <span>收付比</span>
            <span>{{ kpi.cashRatio }}</span>
          </div>
        </div>
        </div>

        <!-- 2. 图表区域：趋势与分布 -->
        <div class="chart-row">
          <!-- 成本趋势图 -->
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">项目成本累计趋势 (S曲线)</div>
              <el-radio-group v-model="trendPeriod" size="small" @change="handlePeriodChange">
                <el-radio-button label="week">周</el-radio-button>
                <el-radio-button label="month">月</el-radio-button>
              </el-radio-group>
            </div>
            <div ref="sCurveChartRef" style="flex: 1; min-height: 300px; width: 100%;"></div>
          </div>
        </div>

        <!-- 3. 成本中心监控与资金流 -->
        <div class="chart-row-equal">
          <!-- 成本中心雷达图 -->
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">各成本中心执行偏差</div>
            </div>
            <div ref="radarChartRef" style="flex: 1; min-height: 300px; width: 100%;"></div>
          </div>
          
          <!-- 资金流向监控 -->
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">资金收支监控</div>
            </div>
            <div ref="cashFlowChartRef" style="flex: 1; min-height: 300px; width: 100%;"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import * as echarts from 'echarts';
import { Refresh } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import api from '../api/client';

// 状态定义
const loading = ref(false);
const currentProject = ref('');
const projectOptions = ref([]);
const allBudgetRecords = ref([]);
const trendPeriod = ref('month');

// DOM 引用
const sCurveChartRef = ref(null);
const radarChartRef = ref(null);
const cashFlowChartRef = ref(null);

// Chart 实例
let sCurveChart = null;
let radarChart = null;
let cashFlowChart = null;

// 工具函数
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

const formatMoney = (val) => {
  const amount = toNumber(val);
  return amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
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

const buildProjectOptions = (records) => {
  const map = new Map();
  records.forEach((record) => {
    const key = buildProjectKey(record);
    if (key === '||') return;
    if (map.has(key)) return;
    const code = normalizeProjectCode(record?.project_code);
    const name = normalizeLabel(record?.project_name);
    const type = normalizeLabel(record?.project_type);
    const label = code ? `${code} - ${name || '未命名项目'}` : (name || '未命名项目');
    map.set(key, {
      key,
      code,
      name,
      type,
      label
    });
  });
  return Array.from(map.values());
};

const getRecordActual = (record) => {
  const actual = toNumber(record?.actual_total);
  const details = Array.isArray(record?.cost_details) ? record.cost_details : [];
  const sumDetails = details.reduce((acc, item) => acc + toNumber(item?.detail_amount), 0);
  if (actual === 0 && sumDetails > 0) return sumDetails;
  return actual;
};

const filteredBudgetRecords = computed(() => {
  if (!currentProject.value) return [];
  return allBudgetRecords.value.filter(
    (record) => buildProjectKey(record) === currentProject.value
  );
});

const kpi = computed(() => {
  const records = filteredBudgetRecords.value;
  const totalBudget = records.reduce((acc, record) => acc + toNumber(record?.budget_standard), 0);
  const actualCost = records.reduce((acc, record) => acc + getRecordActual(record), 0);
  const costRate = totalBudget > 0
    ? Number(((actualCost / totalBudget) * 100).toFixed(1))
    : 0;
  const marginRate = totalBudget > 0
    ? Number((((totalBudget - actualCost) / totalBudget) * 100).toFixed(1))
    : 0;
  const cashFlow = totalBudget - actualCost;
  const cashRatio = actualCost > 0
    ? `${(totalBudget / actualCost).toFixed(2)}:1`
    : '--';

  return {
    totalBudget,
    actualCost,
    costRate,
    marginRate,
    cashFlow,
    cashRatio
  };
});

const parseDate = (value) => {
  if (!value) return null;
  if (value instanceof Date && !Number.isNaN(value.getTime())) return value;
  if (typeof value === 'number') return new Date(value);
  const parsed = new Date(String(value).replace(/-/g, '/'));
  if (!Number.isNaN(parsed.getTime())) return parsed;
  return null;
};

const buildDetails = (records) => {
  const details = [];
  records.forEach((record) => {
    const recordDetails = Array.isArray(record?.cost_details) ? record.cost_details : [];
    recordDetails.forEach((detail) => {
      const amount = toNumber(detail?.detail_amount);
      if (!amount) return;
      const date = parseDate(detail?.detail_date);
      if (!date) return;
      details.push({ date, amount });
    });
  });
  if (details.length === 0) {
    const fallbackActual = records.reduce((acc, record) => acc + getRecordActual(record), 0);
    if (fallbackActual > 0) {
      details.push({ date: new Date(), amount: fallbackActual });
    }
  }
  return details;
};

const getWeekKey = (date) => {
  const temp = new Date(date);
  const day = (temp.getDay() + 6) % 7;
  temp.setDate(temp.getDate() - day);
  const year = temp.getFullYear();
  const firstDay = new Date(year, 0, 1);
  const diffDays = Math.floor((temp - firstDay) / (1000 * 60 * 60 * 24));
  const week = Math.floor(diffDays / 7) + 1;
  return {
    key: `${year}-W${String(week).padStart(2, '0')}`,
    label: `${year}-W${String(week).padStart(2, '0')}`,
    sort: temp.getTime()
  };
};

const getMonthKey = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  return {
    key: `${year}-${month}`,
    label: `${year}-${month}`,
    sort: new Date(year, date.getMonth(), 1).getTime()
  };
};

const buildPeriodBuckets = (details, period) => {
  const map = new Map();
  details.forEach((detail) => {
    const date = detail.date instanceof Date ? detail.date : parseDate(detail.date);
    if (!date) return;
    const keyInfo = period === 'week' ? getWeekKey(date) : getMonthKey(date);
    const entry = map.get(keyInfo.key) || { ...keyInfo, amount: 0 };
    entry.amount += detail.amount;
    map.set(keyInfo.key, entry);
  });
  const items = Array.from(map.values()).sort((a, b) => a.sort - b.sort);
  return {
    labels: items.map((item) => item.label),
    values: items.map((item) => item.amount)
  };
};

const buildCumulative = (values) => {
  let sum = 0;
  return values.map((val) => {
    sum += val;
    return Number(sum.toFixed(2));
  });
};

const buildSCurveData = () => {
  const details = buildDetails(filteredBudgetRecords.value);
  const buckets = buildPeriodBuckets(details, trendPeriod.value);
  const labels = buckets.labels.length > 0 ? buckets.labels : ['暂无数据'];
  const actual = buckets.values.length > 0 ? buckets.values : [0];
  const actualCumulative = buildCumulative(actual);
  const totalBudget = kpi.value.totalBudget;
  const budgetPerPeriod = labels.length > 0 ? totalBudget / labels.length : 0;
  const budgetCumulative = labels.map((_, index) => Number(((index + 1) * budgetPerPeriod).toFixed(2)));
  const earned = actualCumulative.map((val, index) => Math.min(val, budgetCumulative[index] || 0));
  return {
    labels,
    budgetCumulative,
    actualCumulative,
    earned
  };
};

const buildRadarData = () => {
  const map = new Map();
  filteredBudgetRecords.value.forEach((record) => {
    const center = normalizeLabel(record?.cost_center) || '未分类';
    const budget = toNumber(record?.budget_standard);
    const actual = getRecordActual(record);
    const entry = map.get(center) || { name: center, budget: 0, actual: 0 };
    entry.budget += budget;
    entry.actual += actual;
    map.set(center, entry);
  });
  const list = Array.from(map.values()).sort((a, b) => b.budget - a.budget);
  const indicator = list.map((item) => {
    const maxVal = Math.max(item.budget, item.actual, 1);
    return { name: item.name, max: Math.ceil(maxVal * 1.2) };
  });
  return {
    indicator,
    budgetValues: list.map((item) => item.budget),
    actualValues: list.map((item) => item.actual)
  };
};

const buildCashFlowData = () => {
  const details = buildDetails(filteredBudgetRecords.value);
  const buckets = buildPeriodBuckets(details, 'month');
  const labels = buckets.labels.length > 0 ? buckets.labels : ['暂无数据'];
  const payments = buckets.values.length > 0 ? buckets.values : [0];
  const totalBudget = kpi.value.totalBudget;
  const plannedPerPeriod = labels.length > 0 ? totalBudget / labels.length : 0;
  const receipts = labels.map(() => Number(plannedPerPeriod.toFixed(2)));
  const net = labels.map((_, index) => Number((receipts[index] - (payments[index] || 0)).toFixed(2)));
  return { labels, receipts, payments, net };
};

const loadBudgetRecords = async () => {
  loading.value = true;
  try {
    const result = await api.listProjectBudgets({ skip: 0, limit: 300 });
    if (result?.code === 200 && Array.isArray(result.data)) {
      allBudgetRecords.value = result.data;
      projectOptions.value = buildProjectOptions(result.data);
      if (
        projectOptions.value.length > 0 &&
        !projectOptions.value.find((item) => item.key === currentProject.value)
      ) {
        currentProject.value = projectOptions.value[0].key;
      }
      return true;
    }
    allBudgetRecords.value = [];
    projectOptions.value = [];
    ElMessage.error(result?.msg || '加载预算数据失败');
    return false;
  } catch (error) {
    console.error('加载预算数据失败：', error);
    allBudgetRecords.value = [];
    projectOptions.value = [];
    ElMessage.error('加载预算数据失败');
    return false;
  } finally {
    loading.value = false;
  }
};

const refreshData = async () => {
  const ok = await loadBudgetRecords();
  if (ok) {
    ElMessage.success('数据已刷新');
    nextTick(() => updateCharts());
  }
};

const handleProjectChange = () => {
  nextTick(() => updateCharts());
};

const handlePeriodChange = () => {
  ElMessage.info(`已切换至${trendPeriod.value === 'week' ? '周' : '月'}视图`);
  nextTick(() => updateCharts());
};

// 初始化/刷新图表
const updateCharts = () => {
  const sCurve = buildSCurveData();
  if (sCurveChartRef.value) {
    if (!sCurveChart) {
      sCurveChart = echarts.init(sCurveChartRef.value);
    }
    sCurveChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['预算基准(BCWS)', '实际成本(ACWP)', '挣值(BCWP)'], top: 8 },
      grid: { left: '3%', right: '4%', bottom: '3%', top: 50, containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: sCurve.labels
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '预算基准(BCWS)',
          type: 'line',
          smooth: true,
          data: sCurve.budgetCumulative,
          itemStyle: { color: '#909399' },
          lineStyle: { type: 'dashed' }
        },
        {
          name: '实际成本(ACWP)',
          type: 'line',
          smooth: true,
          data: sCurve.actualCumulative,
          itemStyle: { color: '#F56C6C' },
          areaStyle: { color: 'rgba(245, 108, 108, 0.1)' }
        },
        {
          name: '挣值(BCWP)',
          type: 'line',
          smooth: true,
          data: sCurve.earned,
          itemStyle: { color: '#67C23A' }
        }
      ]
    }, { notMerge: true });
  }

  const radarData = buildRadarData();
  if (radarChartRef.value) {
    if (!radarChart) {
      radarChart = echarts.init(radarChartRef.value);
    }
    radarChart.setOption({
      tooltip: {},
      legend: { data: ['预算限额', '实际发生'], bottom: 0 },
      radar: {
        indicator: radarData.indicator.length > 0 ? radarData.indicator : [{ name: '暂无数据', max: 1 }],
        radius: '65%'
      },
      series: [{
        name: '预算 vs 实际',
        type: 'radar',
        data: [
          {
            value: radarData.budgetValues.length > 0 ? radarData.budgetValues : [0],
            name: '预算限额',
            itemStyle: { color: '#409EFF' }
          },
          {
            value: radarData.actualValues.length > 0 ? radarData.actualValues : [0],
            name: '实际发生',
            itemStyle: { color: '#E6A23C' },
            areaStyle: { color: 'rgba(230, 162, 60, 0.2)' }
          }
        ]
      }]
    }, { notMerge: true });
  }

  const cashFlow = buildCashFlowData();
  if (cashFlowChartRef.value) {
    if (!cashFlowChart) {
      cashFlowChart = echarts.init(cashFlowChartRef.value);
    }
    cashFlowChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['预算', '成本', '净结余'], top: 8 },
      grid: { left: '3%', right: '4%', bottom: '3%', top: 50, containLabel: true },
      xAxis: { type: 'category', data: cashFlow.labels },
      yAxis: { type: 'value' },
      series: [
        {
          name: '预算',
          type: 'bar',
          data: cashFlow.receipts,
          itemStyle: { color: '#67C23A' },
          barWidth: '30%'
        },
        {
          name: '成本',
          type: 'bar',
          data: cashFlow.payments,
          itemStyle: { color: '#F56C6C' },
          barWidth: '30%'
        },
        {
          name: '净结余',
          type: 'line',
          data: cashFlow.net,
          itemStyle: { color: '#409EFF' },
          symbolSize: 8
        }
      ]
    }, { notMerge: true });
  }
};

const handleResize = () => {
  sCurveChart?.resize();
  radarChart?.resize();
  cashFlowChart?.resize();
};

onMounted(() => {
  nextTick(async () => {
    await loadBudgetRecords();
    updateCharts();
    window.addEventListener('resize', handleResize);
  });
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  sCurveChart?.dispose();
  radarChart?.dispose();
  cashFlowChart?.dispose();
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

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  width: 100%;
}

.page-container {
  padding: 16px;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  /* 限制最大宽度，避免在大屏上过宽 */
  max-width: 1920px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

/* 顶部筛选栏样式 */
.filter-bar {
  background: #fff;
  padding: 16px 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.divider {
  width: 1px;
  height: 20px;
  background-color: #dcdfe6;
  margin: 0 8px;
}

.filter-label {
  font-weight: 500;
  color: #606266;
}

/* 看板特有样式 */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.kpi-card {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
  position: relative;
  overflow: hidden;
}
.kpi-card::after {
  content: "";
  position: absolute;
  right: -10px;
  top: -10px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(24, 144, 255, 0.1);
  z-index: 0;
}
.kpi-title {
  color: #909399;
  font-size: 14px;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}
.kpi-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}
.kpi-footer {
  border-top: 1px solid #f0f0f0;
  padding-top: 10px;
  font-size: 12px;
  color: #606266;
  display: flex;
  justify-content: space-between;
  position: relative;
  z-index: 1;
}

.chart-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  min-height: 400px;
}
.chart-row-equal {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  min-height: 350px;
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
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}
.panel-title {
  font-size: 16px;
  font-weight: bold;
  border-left: 4px solid #1890ff;
  padding-left: 10px;
}

.text-up { color: #f5222d; }
.text-down { color: #52c41a; }

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
  .filter-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .filter-left {
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
  }
  .divider {
    display: none;
  }
  .el-select {
    width: 100% !important;
  }
}
</style>
