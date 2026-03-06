<template>
  <el-config-provider :locale="zhCn">
    <div class="app-layout" v-loading="loading">
      <main class="main-content">
        <header class="header">
          <div class="header-title">主工作台</div>
          <div class="header-actions">
            <!-- <el-dropdown @command="handleRoleChange"> -->
              <!-- <span class="el-dropdown-link">
                当前视角：{{ currentRoleName }}
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </span> -->
              <!-- <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="manager">总经理/项目经理</el-dropdown-item>
                  <el-dropdown-item command="finance">财务中心</el-dropdown-item>
                  <el-dropdown-item command="tech">技术中心</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>

            <el-badge :value="urgentTodoCount" class="item">
              <el-button circle><el-icon><Bell /></el-icon></el-button>
            </el-badge>
            <el-avatar size="small" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
            <span class="user-name">{{ currentRoleName }}</span> -->
          </div>
        </header>

        <div class="page-container">
          <div class="welcome-banner">
            <div class="user-info">
              <h2>早安，{{ currentRoleName }}，祝你开心每一天！</h2>
              <p>{{ roleDescription }}</p>
            </div>
          </div>

          <div class="metrics-grid">
            <div class="metric-card" v-for="(item, index) in currentStats" :key="index">
              <div class="metric-header">
                <span class="metric-title">{{ item.title }}</span>
                <div class="metric-icon" :style="{ backgroundColor: item.color + '1a', color: item.color }">
                  <el-icon><component :is="item.icon" /></el-icon>
                </div>
              </div>
              <div class="metric-value-area">
                <span class="metric-value">{{ item.value }}</span>
                <span class="metric-unit" v-if="item.unit">{{ item.unit }}</span>
              </div>

              <div class="metric-progress" v-if="item.type === 'progress'">
                <div class="metric-progress-bar" :style="{ width: item.progress + '%', backgroundColor: item.color }"></div>
              </div>

              <div class="metric-footer">
                <span>{{ item.subTitle }}</span>
                <span class="metric-trend" :style="{ color: item.trendColor || '#666' }">{{ item.subValue }}</span>
              </div>
            </div>
          </div>

          <div class="quick-nav-card">
            <div class="card-header-simple">
              <span class="card-title">快捷导航</span>
              <el-button type="primary" link @click="loadWorkbenchData">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
            <div class="nav-grid">
              <div class="nav-item" v-for="nav in quickNavs" :key="nav.text" @click="go(nav.path)">
                <div class="nav-icon-box" :style="{ backgroundColor: nav.color + '1a', color: nav.color }">
                  <el-icon><component :is="nav.icon" /></el-icon>
                </div>
                <span class="nav-text">{{ nav.text }}</span>
              </div>
            </div>
          </div>

          <div class="dashboard-card project-info-card">
            <div class="card-header">
              <span class="card-title">项目执行看板</span>
              <div class="header-right">
                <div class="status-legend">
                  <span class="legend-item"><i class="dot red"></i>一级预警</span>
                  <span class="legend-item"><i class="dot orange"></i>二级预警</span>
                  <span class="legend-item"><i class="dot green"></i>正常</span>
                </div>
                <div class="project-filter-actions">
                  <el-date-picker
                    v-model="projectFilterRange"
                    type="daterange"
                    value-format="YYYY-MM-DD"
                    range-separator="至"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    size="small"
                    style="width: 260px"
                  />
                  <el-button size="small" type="primary" @click="applyProjectFilter">查询</el-button>
                  <el-button size="small" @click="resetProjectFilter">重置</el-button>
                </div>
              </div>
            </div>
            <el-table :data="filteredProjectTableData" border stripe>
              <el-table-column type="index" label="序号" width="60" />
              <el-table-column prop="name" label="项目名称" min-width="150" />
              <el-table-column prop="startTime" label="开始时间" width="120" />
              <el-table-column prop="stage" label="当前阶段" />
              <el-table-column prop="owner" label="责任人" width="100" />
              <el-table-column prop="progress" label="进度" width="80" />
              <el-table-column label="预警状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getTagType(row.warningLevel)">{{ row.warningLevel }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="dashboard-grid">
            <div class="dashboard-card main-chart-card">
              <div class="card-header">
                <span class="card-title">{{ chartTitle1 }}</span>
                <el-radio-group v-model="chartPeriod" size="small">
                  <el-radio-button label="week">本周</el-radio-button>
                  <el-radio-button label="month">本月</el-radio-button>
                </el-radio-group>
              </div>
              <div ref="chartRef1" class="chart-box"></div>
            </div>

            <div class="dashboard-card todo-card">
              <div class="card-header">
                <span class="card-title">待办事项</span>
                <el-tag type="danger" size="small" effect="dark">{{ urgentTodoCount }} 项紧急</el-tag>
              </div>
              <el-tabs v-model="activeTab" class="full-height-tabs">
                <el-tab-pane label="待处理" name="todo">
                  <div class="todo-list">
                    <div class="todo-item" v-for="(item, index) in todoList" :key="`todo-${index}`">
                      <el-tag :type="item.tagType" size="small" class="todo-tag">{{ item.tag }}</el-tag>
                      <div class="todo-content">
                        <div class="todo-title">{{ item.title }}</div>
                        <div class="todo-meta">{{ item.time }} | 来源: {{ item.source }}</div>
                      </div>
                      <el-button type="primary" link @click="go(item.path)">处理</el-button>
                    </div>
                  </div>
                </el-tab-pane>
                <el-tab-pane label="已处理" name="done">
                  <div class="todo-list">
                    <div class="todo-item" v-for="(item, index) in doneList" :key="`done-${index}`">
                      <el-tag type="info" size="small" class="todo-tag">已办</el-tag>
                      <div class="todo-content grayed">
                        <div class="todo-title strikethrough">{{ item.title }}</div>
                        <div class="todo-meta">{{ item.time }} | 处理人: 系统</div>
                      </div>
                    </div>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </div>

            <div class="sub-charts-container">
              <div class="dashboard-card flex-1">
                <div class="card-header"><span class="card-title">{{ chartTitle2 }}</span></div>
                <div ref="chartRef2" class="chart-box-small"></div>
              </div>
              <div class="dashboard-card flex-1">
                <div class="card-header"><span class="card-title">{{ chartTitle3 }}</span></div>
                <div ref="chartRef3" class="chart-box-small"></div>
              </div>
            </div>

            <div class="dashboard-card msg-card">
              <div class="card-header">
                <span class="card-title">消息提醒</span>
                <el-button type="text">全部已读</el-button>
              </div>
              <div class="msg-list">
                <div class="msg-item" v-for="(msg, index) in msgList" :key="`msg-${index}`">
                  <div class="msg-icon" :class="msg.type">
                    <el-icon v-if="msg.type === 'warning'"><WarningFilled /></el-icon>
                    <el-icon v-else-if="msg.type === 'info'"><InfoFilled /></el-icon>
                    <el-icon v-else><CircleCheckFilled /></el-icon>
                  </div>
                  <div class="msg-content">
                    <h4>{{ msg.title }}</h4>
                    <p>{{ msg.desc }}</p>
                    <span class="msg-time">{{ msg.time }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import {
  Odometer, Bell, ArrowDown, Box, WarningFilled, Refresh,
  InfoFilled, CircleCheckFilled, FolderAdd, TrendCharts,
  Money, Tickets, DataLine
} from '@element-plus/icons-vue'
import { ElMessage, ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { useRouter } from 'vue-router'
import api from '../api/client'

const router = useRouter()
const loading = ref(false)
const currentRole = ref('manager')
const chartPeriod = ref('week')
const activeTab = ref('todo')
const projectFilterRange = ref([])
const projectQueryRange = ref([])

const roleMap = {
  manager: '总经理/项目经理',
  finance: '财务中心',
  tech: '技术中心'
}
const roleDescMap = {
  manager: '今日重点：关注项目进度、预算执行与风险事项闭环。',
  finance: '今日重点：关注预算执行率、超支项目和应付处理。',
  tech: '今日重点：关注进度阻塞、异常交付和质量风险。'
}

const chartRef1 = ref(null)
const chartRef2 = ref(null)
const chartRef3 = ref(null)
let charts = []

const budgetRecords = ref([])
const progressRecords = ref([])
const deliveryRecords = ref([])
const handoverRecords = ref([])

const quickNavs = [
  { icon: FolderAdd, text: '阶段配置', color: '#1890ff', path: '/stage-config' },
  { icon: Odometer, text: '项目进度', color: '#52c41a', path: '/project-progress' },
  { icon: Money, text: '预算管理', color: '#722ed1', path: '/project-budget-management' },
  { icon: TrendCharts, text: '项目管控', color: '#fa8c16', path: '/project-control-dashboard' },
  { icon: DataLine, text: '预算看板', color: '#13c2c2', path: '/overall-budget-dashboard' },
  { icon: Tickets, text: '发货管理', color: '#f5222d', path: '/delivery-management' }
]

const normalizeLabel = (v) => (v === null || v === undefined ? '' : String(v).trim())
const normalizeStatus = (v) => normalizeLabel(v).replace(/\s+/g, '')

const pickValue = (record, keys, fallback = '') => {
  if (!record || typeof record !== 'object') return fallback
  for (const key of keys) {
    if (!Object.prototype.hasOwnProperty.call(record, key)) continue
    const value = record[key]
    if (value === null || value === undefined) continue
    if (typeof value === 'string' && !value.trim()) continue
    return value
  }
  return fallback
}

const BUDGET_FIELD_KEYS = {
  projectCode: ['project_code', '_widget_1770184687558'],
  projectName: ['project_name', '_widget_1770184687577'],
  costItem: ['cost_item', '_widget_1770184687651'],
  status: ['status', '_widget_1770184688070'],
  budgetStandard: ['budget_standard', '_widget_1770184688128'],
  actualTotal: ['actual_total', '_widget_1770184688149'],
  costDetails: ['cost_details', '_widget_1770184688372']
}

const BUDGET_DETAIL_FIELD_KEYS = {
  detailDate: ['detail_date', '_widget_1770184688515'],
  detailAmount: ['detail_amount', '_widget_1770184688945']
}

const PROGRESS_FIELD_KEYS = {
  projectCode: ['project_code', '_widget_1769239633492'],
  projectName: ['project_name', '_widget_1769239633511'],
  mainStage: ['main_stage', '_widget_1769239633707'],
  projectStage: ['project_stage', '_widget_1769239633603'],
  executor: ['executor', '_widget_1769239633622'],
  planTime: ['plan_time', '_widget_1769239633640'],
  planStart: ['plan_start', 'planStart', '_widget_1769064637850'],
  actualFinish: ['actual_finish', '_widget_1769239633664'],
  status: ['status', '_widget_1769239633688']
}

const DELIVERY_FIELD_KEYS = {
  projectName: ['project_name', '_widget_1770458498418'],
  deliveryNo: ['delivery_no', '_widget_1770458498302'],
  deliveryDate: ['delivery_date', '_widget_1770458498335'],
  status: ['status', '_widget_1770458499012']
}

const HANDOVER_FIELD_KEYS = {
  projectName: ['project_name', '_widget_1770602533948'],
  deliveryNo: ['delivery_no', '_widget_1770599102686'],
  handoverStatus: ['handover_status', '_widget_1770602535781']
}

const DONE_PROGRESS_STATUSES = new Set(['完成', '超期完成'])
const PENDING_DELIVERY_STATUSES = new Set(['运输中', '异常'])
const OVERRUN_BUDGET_STATUS = '超支'
const OVERDUE_PROGRESS_STATUS = '超期'
const ABNORMAL_STATUS = '异常'
const SIGNED_STATUS = '已签收'
const PENDING_HANDOVER_STATUS = '待处理'

const toNumber = (value) => {
  if (value === null || value === undefined || value === '') return 0
  if (typeof value === 'number') return Number.isFinite(value) ? value : 0
  const numeric = Number(String(value).replace(/,/g, ''))
  return Number.isFinite(numeric) ? numeric : 0
}
const formatMoney = (val) => toNumber(val).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
const parseDateValue = (value) => {
  if (!value) return null
  if (value instanceof Date) return value
  if (typeof value === 'number') {
    const date = new Date(value)
    return Number.isNaN(date.getTime()) ? null : date
  }
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed) return null
    const date = new Date(trimmed.replace(/-/g, '/'))
    return Number.isNaN(date.getTime()) ? null : date
  }
  return null
}
const parseDateRange = (value) => {
  if (!value) return { start: null, end: null }
  if (Array.isArray(value)) {
    return {
      start: parseDateValue(value[0]),
      end: parseDateValue(value[1])
    }
  }
  if (typeof value === 'object') {
    const start = parseDateValue(value.start || value.begin || value.planStart)
    const end = parseDateValue(value.end || value.finish || value.planEnd)
    if (start || end) return { start, end }
  }
  if (typeof value === 'string') {
    const matches = value.match(/\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?/g)
    if (matches && matches.length >= 2) {
      return {
        start: parseDateValue(matches[0]),
        end: parseDateValue(matches[1])
      }
    }
  }
  return { start: parseDateValue(value), end: null }
}
const formatDateCell = (value) => {
  const date = parseDateValue(value)
  if (!date) return '-'
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const formatExecutor = (value) => {
  if (!value) return ''
  if (Array.isArray(value)) {
    const labels = value.map((item) => formatExecutor(item)).filter(Boolean)
    return Array.from(new Set(labels)).join(' / ')
  }
  if (typeof value === 'object') {
    return normalizeLabel(value.name || value.user_name || value.account || value._id || value.id || '')
  }
  return normalizeLabel(value)
}

const getBudgetProjectCode = (record) => normalizeLabel(pickValue(record, BUDGET_FIELD_KEYS.projectCode))
const getBudgetProjectName = (record) => normalizeLabel(pickValue(record, BUDGET_FIELD_KEYS.projectName))
const getBudgetCostItem = (record) => normalizeLabel(pickValue(record, BUDGET_FIELD_KEYS.costItem))
const getBudgetStatus = (record) => normalizeStatus(pickValue(record, BUDGET_FIELD_KEYS.status))
const getBudgetStandard = (record) => toNumber(pickValue(record, BUDGET_FIELD_KEYS.budgetStandard, 0))
const getBudgetActualTotal = (record) => toNumber(pickValue(record, BUDGET_FIELD_KEYS.actualTotal, 0))
const getBudgetCostDetails = (record) => {
  const details = pickValue(record, BUDGET_FIELD_KEYS.costDetails, [])
  return Array.isArray(details) ? details : []
}
const getBudgetDetailDate = (detail) => normalizeLabel(pickValue(detail, BUDGET_DETAIL_FIELD_KEYS.detailDate))
const getBudgetDetailAmount = (detail) => toNumber(pickValue(detail, BUDGET_DETAIL_FIELD_KEYS.detailAmount, 0))

const getProgressProjectCode = (record) => normalizeLabel(pickValue(record, PROGRESS_FIELD_KEYS.projectCode))
const getProgressProjectName = (record) => normalizeLabel(pickValue(record, PROGRESS_FIELD_KEYS.projectName))
const getProgressMainStage = (record) => normalizeLabel(pickValue(record, PROGRESS_FIELD_KEYS.mainStage))
const getProgressProjectStage = (record) => normalizeLabel(pickValue(record, PROGRESS_FIELD_KEYS.projectStage))
const getProgressExecutor = (record) => pickValue(record, PROGRESS_FIELD_KEYS.executor)
const getProgressPlanTime = (record) => pickValue(record, PROGRESS_FIELD_KEYS.planTime, null)
const getProgressStartRaw = (record) => {
  const range = parseDateRange(getProgressPlanTime(record))
  if (range.start) return range.start
  return parseDateValue(pickValue(record, PROGRESS_FIELD_KEYS.planStart, ''))
}
const getProgressActualFinish = (record) => normalizeLabel(pickValue(record, PROGRESS_FIELD_KEYS.actualFinish))
const getProgressStatus = (record) => normalizeStatus(pickValue(record, PROGRESS_FIELD_KEYS.status))

const getDeliveryProjectName = (record) => normalizeLabel(pickValue(record, DELIVERY_FIELD_KEYS.projectName))
const getDeliveryNo = (record) => normalizeLabel(pickValue(record, DELIVERY_FIELD_KEYS.deliveryNo))
const getDeliveryDate = (record) => normalizeLabel(pickValue(record, DELIVERY_FIELD_KEYS.deliveryDate))
const getDeliveryStatus = (record) => normalizeStatus(pickValue(record, DELIVERY_FIELD_KEYS.status))

const getHandoverProjectName = (record) => normalizeLabel(pickValue(record, HANDOVER_FIELD_KEYS.projectName))
const getHandoverDeliveryNo = (record) => normalizeLabel(pickValue(record, HANDOVER_FIELD_KEYS.deliveryNo))
const getHandoverStatus = (record) => normalizeStatus(pickValue(record, HANDOVER_FIELD_KEYS.handoverStatus))

const getRecordActual = (record) => {
  const actual = getBudgetActualTotal(record)
  const details = getBudgetCostDetails(record)
  const sum = details.reduce((acc, item) => acc + getBudgetDetailAmount(item), 0)
  if (actual === 0 && sum > 0) return sum
  return actual
}

const summary = computed(() => {
  const projectSet = new Set()
  budgetRecords.value.forEach((r) => {
    const code = getBudgetProjectCode(r)
    if (code) projectSet.add(code)
  })
  progressRecords.value.forEach((r) => {
    const code = getProgressProjectCode(r)
    if (code) projectSet.add(code)
  })

  const totalBudget = budgetRecords.value.reduce((acc, r) => acc + getBudgetStandard(r), 0)
  const totalActual = budgetRecords.value.reduce((acc, r) => acc + getRecordActual(r), 0)
  const budgetRate = totalBudget > 0 ? Number(((totalActual / totalBudget) * 100).toFixed(1)) : 0

  const doneCount = progressRecords.value.filter((r) => DONE_PROGRESS_STATUSES.has(getProgressStatus(r))).length
  const progressRate = progressRecords.value.length > 0 ? Number(((doneCount / progressRecords.value.length) * 100).toFixed(1)) : 0

  const deliveryPending = deliveryRecords.value.filter((r) => PENDING_DELIVERY_STATUSES.has(getDeliveryStatus(r))).length
  const overrunCount = budgetRecords.value.filter((r) => getBudgetStatus(r) === OVERRUN_BUDGET_STATUS).length
  const abnormalDelivery = deliveryRecords.value.filter((r) => getDeliveryStatus(r) === ABNORMAL_STATUS).length
  const pendingHandover = handoverRecords.value.filter((r) => {
    const s = getHandoverStatus(r)
    return !s || s === PENDING_HANDOVER_STATUS
  }).length

  return {
    projectCount: projectSet.size,
    totalBudget,
    totalActual,
    budgetRate,
    progressRate,
    deliveryPending,
    overrunCount,
    warningCount: overrunCount + abnormalDelivery + pendingHandover
  }
})

const currentRoleName = computed(() => roleMap[currentRole.value])
const roleDescription = computed(() => roleDescMap[currentRole.value] || roleDescMap.manager)

const currentStats = computed(() => [
  {
    title: '项目进度完成率',
    value: summary.value.progressRate,
    unit: '%',
    subTitle: '已完成节点',
    subValue: `${progressRecords.value.filter((r) => DONE_PROGRESS_STATUSES.has(getProgressStatus(r))).length}个`,
    color: '#1890ff',
    icon: Odometer,
    type: 'progress',
    progress: summary.value.progressRate
  },
  {
    title: '成本预算执行',
    value: summary.value.budgetRate,
    unit: '%',
    subTitle: '预算总额',
    subValue: `¥${formatMoney(summary.value.totalBudget)}`,
    color: '#722ed1',
    icon: Money,
    type: 'progress',
    progress: Math.min(100, summary.value.budgetRate)
  },
  {
    title: '待交付订单',
    value: summary.value.deliveryPending,
    unit: '个',
    subTitle: '含运输中/异常',
    subValue: `${deliveryRecords.value.length}总单`,
    color: '#fa8c16',
    icon: Tickets,
    type: 'number'
  },
  {
    title: '预警事项',
    value: summary.value.warningCount,
    unit: '条',
    subTitle: '预算/发货/交付',
    subValue: '需处理',
    color: '#f5222d',
    icon: WarningFilled,
    type: 'number'
  }
])

const todoList = computed(() => {
  const list = []
  budgetRecords.value
    .filter((r) => getBudgetStatus(r) === OVERRUN_BUDGET_STATUS)
    .slice(0, 3)
    .forEach((r) => list.push({
      tag: '紧急', tagType: 'danger',
      title: `${getBudgetProjectName(r) || '未命名项目'} - 成本超支`,
      time: '预算管理',
      source: getBudgetCostItem(r) || '成本项',
      path: '/project-budget-management'
    }))

  deliveryRecords.value
    .filter((r) => getDeliveryStatus(r) === ABNORMAL_STATUS)
    .slice(0, 2)
    .forEach((r) => list.push({
      tag: '重要', tagType: 'warning',
      title: `${getDeliveryProjectName(r) || '未命名项目'} - 发货异常`,
      time: '发货管理',
      source: getDeliveryNo(r) || '运单',
      path: '/delivery-management'
    }))

  handoverRecords.value
    .filter((r) => {
      const s = getHandoverStatus(r)
      return !s || s === PENDING_HANDOVER_STATUS
    })
    .slice(0, 2)
    .forEach((r) => list.push({
      tag: '待办', tagType: 'info',
      title: `${getHandoverProjectName(r) || '未命名项目'} - 检测交付待处理`,
      time: '交付管理',
      source: getHandoverDeliveryNo(r) || '交付单',
      path: '/inspection-delivery-management'
    }))

  return list
})

const doneList = computed(() => {
  const list = []
  progressRecords.value
    .filter((r) => DONE_PROGRESS_STATUSES.has(getProgressStatus(r)))
    .slice(0, 3)
    .forEach((r) => list.push({
      title: `${getProgressProjectName(r) || '未命名项目'} - ${getProgressProjectStage(r) || '节点完成'}`,
      time: getProgressActualFinish(r) || '已完成'
    }))

  deliveryRecords.value
    .filter((r) => getDeliveryStatus(r) === SIGNED_STATUS)
    .slice(0, 2)
    .forEach((r) => list.push({
      title: `${getDeliveryProjectName(r) || '未命名项目'} - 发货已签收`,
      time: getDeliveryDate(r) || '已完成'
    }))

  return list
})

const msgList = computed(() => [
  { type: 'warning', title: '预算预警', desc: `当前超支条目 ${summary.value.overrunCount} 项，请关注成本控制。`, time: '刚刚' },
  { type: 'info', title: '交付提醒', desc: `当前待处理交付记录 ${handoverRecords.value.filter((r) => !getHandoverStatus(r) || getHandoverStatus(r) === PENDING_HANDOVER_STATUS).length} 条。`, time: '刚刚' },
  { type: 'success', title: '经营概览', desc: `预算执行率 ${summary.value.budgetRate}% ，项目覆盖 ${summary.value.projectCount} 个。`, time: '刚刚' }
])

const urgentTodoCount = computed(() => todoList.value.filter((i) => i.tagType === 'danger').length)
const chartTitle1 = computed(() => '成本发生趋势')
const chartTitle2 = computed(() => '项目状态分布')
const chartTitle3 = computed(() => '预算执行率')

const projectTableData = computed(() => {
  const map = new Map()
  progressRecords.value.forEach((r) => {
    const code = getProgressProjectCode(r) || getProgressProjectName(r) || '未知'
    const startRaw = getProgressStartRaw(r)
    if (!map.has(code)) {
      map.set(code, {
        name: getProgressProjectName(r) || code,
        total: 0,
        done: 0,
        owner: formatExecutor(getProgressExecutor(r)),
        stage: getProgressMainStage(r) || getProgressProjectStage(r),
        overdue: 0,
        startRaw
      })
    }
    const item = map.get(code)
    item.total += 1
    if (DONE_PROGRESS_STATUSES.has(getProgressStatus(r))) item.done += 1
    if (getProgressStatus(r) === OVERDUE_PROGRESS_STATUS) item.overdue += 1
    if (!item.owner) item.owner = formatExecutor(getProgressExecutor(r))
    if (!item.stage) item.stage = getProgressMainStage(r) || getProgressProjectStage(r)
    if (startRaw && (!item.startRaw || startRaw.getTime() < item.startRaw.getTime())) {
      item.startRaw = startRaw
    }
  })

  // 仅有预算数据时，项目看板也展示基础行，避免工作台为空
  if (map.size === 0) {
    budgetRecords.value.forEach((r) => {
      const code = getBudgetProjectCode(r) || getBudgetProjectName(r)
      if (!code || map.has(code)) return
      map.set(code, {
        name: getBudgetProjectName(r) || code,
        total: 0,
        done: 0,
        owner: '-',
        stage: '-',
        overdue: 0,
        startRaw: null
      })
    })
  }

  return Array.from(map.values())
    .sort((a, b) => a.name.localeCompare(b.name, 'zh'))
    .map((p) => {
    const rate = p.total > 0 ? Math.round((p.done / p.total) * 100) : 0
    let warningLevel = '正常'
    if (p.overdue >= 2) warningLevel = '一级'
    else if (p.overdue === 1) warningLevel = '二级'
    return {
      name: p.name,
      startRaw: p.startRaw || null,
      startTime: formatDateCell(p.startRaw),
      stage: p.stage || '-',
      owner: p.owner || '-',
      progress: `${rate}%`,
      warningLevel
    }
  })
})

const filteredProjectTableData = computed(() => {
  const range = Array.isArray(projectQueryRange.value) ? projectQueryRange.value : []
  const startDate = parseDateValue(range[0])
  const endDate = parseDateValue(range[1])
  if (!startDate && !endDate) return projectTableData.value

  const startTs = startDate
    ? new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate()).getTime()
    : null
  const endTs = endDate
    ? new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate(), 23, 59, 59, 999).getTime()
    : null

  return projectTableData.value.filter((item) => {
    if (!(item.startRaw instanceof Date) || Number.isNaN(item.startRaw.getTime())) return false
    const time = item.startRaw.getTime()
    if (startTs !== null && time < startTs) return false
    if (endTs !== null && time > endTs) return false
    return true
  })
})

const go = (path) => { if (path) router.push(path) }
const handleRoleChange = (role) => { currentRole.value = role; ElMessage.success(`视角已切换至：${roleMap[role]}`) }
const getTagType = (level) => (level === '一级' ? 'danger' : level === '二级' ? 'warning' : 'success')
const applyProjectFilter = () => {
  projectQueryRange.value = Array.isArray(projectFilterRange.value) ? [...projectFilterRange.value] : []
}
const resetProjectFilter = () => {
  projectFilterRange.value = []
  projectQueryRange.value = []
}

const buildTrend = () => {
  const map = new Map()
  const now = new Date()
  if (chartPeriod.value === 'week') {
    for (let i = 6; i >= 0; i -= 1) {
      const d = new Date(now)
      d.setDate(now.getDate() - i)
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
      map.set(key, 0)
    }
  } else {
    for (let i = 5; i >= 0; i -= 1) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
      map.set(key, 0)
    }
  }

  const keys = Array.from(map.keys())
  const latestKey = keys[keys.length - 1] || ''

  budgetRecords.value.forEach((r) => {
    const details = getBudgetCostDetails(r)
    if (!details.length) {
      const fallbackAmount = getRecordActual(r)
      if (latestKey && fallbackAmount > 0) {
        map.set(latestKey, (map.get(latestKey) || 0) + fallbackAmount)
      }
      return
    }

    details.forEach((d) => {
      const date = getBudgetDetailDate(d)
      if (!date) return
      const dt = new Date(date.replace(/-/g, '/'))
      if (Number.isNaN(dt.getTime())) return
      const key = chartPeriod.value === 'week'
        ? `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`
        : `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}`
      if (!map.has(key)) return
      map.set(key, (map.get(key) || 0) + getBudgetDetailAmount(d))
    })
  })
  return { labels: Array.from(map.keys()), values: Array.from(map.values()) }
}

const initCharts = () => {
  charts.forEach((c) => c.dispose())
  charts = []
  if (!chartRef1.value || !chartRef2.value || !chartRef3.value) return

  const trend = buildTrend()
  const c1 = echarts.init(chartRef1.value)
  c1.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: trend.labels },
    yAxis: { type: 'value' },
    series: [{ data: trend.values, type: 'line', smooth: true, color: '#1890ff', areaStyle: { opacity: 0.1 } }]
  })
  charts.push(c1)

  const statusMap = new Map()
  progressRecords.value.forEach((r) => {
    const s = getProgressStatus(r) || '未完成'
    statusMap.set(s, (statusMap.get(s) || 0) + 1)
  })
  const c2 = echarts.init(chartRef2.value)
  c2.setOption({
    tooltip: { trigger: 'item' },
    series: [{ type: 'pie', radius: ['40%', '70%'], data: Array.from(statusMap.entries()).map(([name, value]) => ({ name, value })) }]
  })
  charts.push(c2)

  const c3 = echarts.init(chartRef3.value)
  c3.setOption({
    series: [{
      type: 'gauge',
      progress: { show: true, width: 8 },
      axisLine: { lineStyle: { width: 8 } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      detail: { valueAnimation: true, offsetCenter: [0, 0], fontSize: 24, formatter: '{value}%' },
      data: [{ value: summary.value.budgetRate }]
    }]
  })
  charts.push(c3)
}

const handleResize = () => { charts.forEach((c) => c.resize()) }

const loadWorkbenchData = async () => {
  loading.value = true
  try {
    const [budgetRes, progressRes, deliveryRes, handoverRes] = await Promise.all([
      api.listProjectBudgets({ skip: 0, limit: 300 }),
      api.listProjectProgress({ skip: 0, limit: 300 }),
      api.listDeliveries({ skip: 0, limit: 300 }),
      api.listInspectionDeliveries({ skip: 0, limit: 300 })
    ])

    const extractRows = (response) => (Array.isArray(response?.data) ? response.data : [])
    budgetRecords.value = extractRows(budgetRes)
    progressRecords.value = extractRows(progressRes)
    deliveryRecords.value = extractRows(deliveryRes)
    handoverRecords.value = extractRows(handoverRes)

    nextTick(initCharts)
  } catch (error) {
    console.error('加载工作台数据失败：', error)
    ElMessage.error('加载工作台数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadWorkbenchData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  charts.forEach((c) => c.dispose())
})

watch(chartPeriod, () => initCharts())
</script>

<style scoped>
.app-layout { min-height: 100vh; background-color: #f0f2f5; color: #333; }
.main-content { display: flex; flex-direction: column; min-height: 100vh; overflow: hidden; width: 100%; }
.header { height: 64px; background: #fff; padding: 0 8px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08); z-index: 10; }
.header-title { font-size: 18px; font-weight: 600; }
.header-actions { display: flex; align-items: center; gap: 8px; }
.el-dropdown-link { cursor: pointer; display: flex; align-items: center; color: #666; }
.page-container { padding: 8px 0px; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 12px; max-width: 100%; margin: 0 auto; width: 100%; box-sizing: border-box; }

.welcome-banner { background: #fff; padding: 24px; border-radius: 8px; margin-bottom: 0; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.welcome-banner h2 { margin: 0 0 8px; font-size: 20px; }
.welcome-banner p { color: #666; margin: 0; }

.metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 0; }
.metric-card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.metric-header { display: flex; justify-content: space-between; margin-bottom: 12px; }
.metric-title { color: #8c8c8c; font-size: 14px; }
.metric-icon { padding: 8px; border-radius: 6px; display: flex; }
.metric-value-area { display: flex; align-items: baseline; gap: 4px; margin-bottom: 12px; }
.metric-value { font-size: 28px; font-weight: bold; }
.metric-progress { height: 4px; background: #f0f0f0; border-radius: 2px; margin-bottom: 12px; overflow: hidden; }
.metric-progress-bar { height: 100%; transition: width 0.6s ease; }
.metric-footer { font-size: 12px; color: #8c8c8c; display: flex; justify-content: space-between; border-top: 1px solid #f0f0f0; padding-top: 12px; }
.metric-trend { display: flex; align-items: center; }

.quick-nav-card { background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 0; }
.card-header-simple { display: flex; justify-content: space-between; margin-bottom: 16px; align-items: center; }
.card-title { font-weight: bold; border-left: 4px solid #1890ff; padding-left: 12px; }
.nav-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 16px; }
.nav-item { display: flex; flex-direction: column; align-items: center; padding: 16px; background: #fafafa; border-radius: 8px; cursor: pointer; transition: all 0.3s; }
.nav-item:hover { background: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.1); transform: translateY(-2px); }
.nav-icon-box { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 8px; }
.nav-text { font-size: 13px; color: #666; }

.dashboard-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
.dashboard-card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid #f0f0f0; padding-bottom: 12px; }
.chart-box { height: 350px; }
.chart-box-small { height: 200px; }
.todo-card { display: flex; flex-direction: column; }
.full-height-tabs { flex: 1; }
.todo-item { display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.todo-tag { margin-right: 12px; }
.todo-content { flex: 1; }
.todo-title { font-size: 14px; margin-bottom: 4px; }
.todo-meta { font-size: 12px; color: #999; }
.grayed { opacity: 0.6; }
.strikethrough { text-decoration: line-through; }

.sub-charts-container { display: flex; gap: 20px; }
.msg-item { display: flex; gap: 12px; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.msg-icon { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.msg-icon.warning { background: #fff2f0; color: #f5222d; }
.msg-icon.success { background: #f6ffed; color: #52c41a; }
.msg-icon.info { background: #e6f7ff; color: #1890ff; }
.msg-content h4 { margin: 0 0 4px; font-size: 14px; }
.msg-content p { margin: 0; font-size: 12px; color: #666; }
.msg-time { font-size: 11px; color: #999; }

.project-info-card { margin-bottom: 0; }
.header-right { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; justify-content: flex-end; }
.status-legend { display: flex; gap: 12px; font-size: 12px; color: #8c8c8c; }
.project-filter-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 4px; }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot.red { background: #f5222d; }
.dot.orange { background: #fa8c16; }
.dot.green { background: #52c41a; }
.flex-1 { flex: 1; }

@media (max-width: 1200px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .nav-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>
