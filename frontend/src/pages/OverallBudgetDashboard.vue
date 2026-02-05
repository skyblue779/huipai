<template>
  <div class="dashboard-container">
    <!-- 主内容 -->
    <div class="main-content">
      <div class="header">
        <div class="header-left">
          <div class="brand-text">徽派家私管理平台</div>
          <div class="header-title">整体预算看板</div>
          <div class="header-controls">
            <el-select v-model="currentYear" placeholder="选择年份" style="width: 120px;">
              <el-option label="2024年" value="2024"></el-option>
              <el-option label="2023年" value="2023"></el-option>
            </el-select>
            <el-button type="primary" plain :icon="Refresh" @click="refreshData">刷新数据</el-button>
          </div>
        </div>
      </div>

      <div class="page-container">
        <!-- 核心指标卡片 -->
        <div class="dashboard-grid">
          <div class="kpi-card">
            <div class="kpi-title">年度总预算</div>
            <div class="kpi-value">¥ 12,580,000</div>
            <div class="kpi-sub">
              <span>项目总数: 15</span>
              <span class="text-success">+8.5% 同比</span>
            </div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">实际发生成本</div>
            <div class="kpi-value">¥ 8,450,200</div>
            <div class="kpi-sub">
              <span>执行率: 67.1%</span>
            </div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">累计超支金额</div>
            <div class="kpi-value text-danger">¥ 320,500</div>
            <div class="kpi-sub">
              <span>超支项目: 3</span>
              <span class="text-danger">+12% 环比</span>
            </div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">预算剩余</div>
            <div class="kpi-value text-success">¥ 4,129,800</div>
            <div class="kpi-sub">
              <span>可用占比: 32.9%</span>
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
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue';
import * as echarts from 'echarts';
import { Refresh } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

// 状态定义
const currentYear = ref('2024');
const rankSortType = ref('high');
const projectBudgetChartRef = ref(null);
const costCompositionChartRef = ref(null);
let projectBudgetChart = null;
let costCompositionChart = null;

// 模拟数据 - 预算执行排行
const executionData = [
  { rank: 1, projectName: 'P2023005 - 深圳湾壹号豪宅定制', manager: '张三', rate: 95 },
  { rank: 2, projectName: 'P2023002 - 上海浦东某办公楼装修', manager: '李四', rate: 88 },
  { rank: 3, projectName: 'P2023008 - 广州天河商业中心', manager: '王五', rate: 82 },
  { rank: 4, projectName: 'P2023001 - 杭州西湖某别墅全屋定制', manager: '赵六', rate: 76 },
  { rank: 5, projectName: 'P2023006 - 北京朝阳区公寓', manager: '孙七', rate: 65 },
  { rank: 6, projectName: 'P2023009 - 成都高新区展厅', manager: '周八', rate: 58 },
  { rank: 7, projectName: 'P2023003 - 武汉光谷科技园', manager: '吴九', rate: 45 },
  { rank: 8, projectName: 'P2023007 - 西安曲江新区住宅', manager: '郑十', rate: 32 },
];

// 模拟数据 - 超支项目
const overrunData = ref([
  { projectName: 'P2023005 - 深圳湾壹号豪宅定制', budget: 2000000, actual: 2150000, overrun: 150000, ratio: 7.5 },
  { projectName: 'P2023004 - 苏州工业园区厂房', budget: 1500000, actual: 1620000, overrun: 120000, ratio: 8.0 },
  { projectName: 'P2023010 - 南京建邺区写字楼', budget: 800000, actual: 850500, overrun: 50500, ratio: 6.3 },
]);

// 模拟数据 - 成本中心预算执行排行
const costCenterData = ref([
  { name: '生产制造中心', budget: 5000000, actual: 4800000, rate: 96, variance: 200000 },
  { name: '采购中心', budget: 3500000, actual: 3600000, rate: 102.8, variance: -100000 },
  { name: '研发设计中心', budget: 1500000, actual: 1200000, rate: 80, variance: 300000 },
  { name: '物流中心', budget: 800000, actual: 750000, rate: 93.7, variance: 50000 },
  { name: '工程安装中心', budget: 1200000, actual: 1250000, rate: 104.1, variance: -50000 },
  { name: '营销中心', budget: 600000, actual: 450000, rate: 75, variance: 150000 },
  { name: '职能管理中心', budget: 400000, actual: 380000, rate: 95, variance: 20000 },
  { name: '售后服务中心', budget: 200000, actual: 180000, rate: 90, variance: 20000 }
]);

// 计算属性：根据排序类型返回排序后的执行数据
const sortedExecutionData = computed(() => {
  let sorted = [...executionData];
  if (rankSortType.value === 'high') {
    sorted.sort((a, b) => b.rate - a.rate);
  } else {
    sorted.sort((a, b) => a.rate - b.rate);
  }
  // 重新计算排名
  return sorted.map((item, index) => ({
    ...item,
    rank: index + 1
  }));
});

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

const formatMoney = (value) => {
  return value.toLocaleString();
};

const refreshData = () => {
  ElMessage.success('数据已刷新');
  // 这里添加重新获取数据的逻辑
};

// 图表初始化
const initCharts = () => {
  // 1. 各项目预算执行对比图
  if (projectBudgetChartRef.value) {
    projectBudgetChart = echarts.init(projectBudgetChartRef.value);
    const projectNames = executionData.slice(0, 10).map(item => item.projectName.split(' - ')[0]); // 简化名称
    const budgetValues = [200, 150, 180, 220, 120, 160, 140, 190]; // 模拟预算 (万)
    const actualValues = [215, 132, 147, 167, 78, 92, 63, 60]; // 模拟实际 (万)

    projectBudgetChart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      legend: {
        data: ['总预算', '实际成本']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: projectNames,
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
          data: budgetValues,
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
          data: actualValues,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#FF9966' },
              { offset: 1, color: '#FF5E62' }
            ])
          }
        }
      ]
    });
  }

  // 2. 整体成本构成饼图
  if (costCompositionChartRef.value) {
    costCompositionChart = echarts.init(costCompositionChartRef.value);
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
          data: [
            { value: 4500000, name: '材料费' },
            { value: 2800000, name: '人工费' },
            { value: 800000, name: '设备费' },
            { value: 350200, name: '管理费' },
            { value: 0, name: '其他' }
          ]
        }
      ]
    });
  }
};

const handleResize = () => {
  projectBudgetChart?.resize();
  costCompositionChart?.resize();
};

onMounted(() => {
  nextTick(() => {
    initCharts();
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
  padding: 0 24px;
  z-index: 10;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 24px;
  width: 100%;
}

.header-controls {
  display: flex; 
  align-items: center; 
  gap: 12px; 
  margin-left: 20px;
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
  padding: 24px;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

/* 看板样式 */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.kpi-card {
  background: #fff;
  padding: 24px;
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
  gap: 20px;
  min-height: 400px;
}
.chart-row-equal {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  min-height: 450px;
}

.panel {
  background: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
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