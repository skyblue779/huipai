<template>
  <el-config-provider :locale="zhCn">
    <div class="project-budget-management">
    <!-- 主内容 -->
    <div class="main-content">
      <div class="header">
        <div style="display: flex; align-items: center; gap: 24px;">
          <div class="header-title">项目预算管理</div>
          <el-select
            v-model="currentProject"
            placeholder="请选择项目"
            style="width: 240px;"
            :loading="loading"
            filterable
            @change="handleProjectChange"
          >
            <el-option
              v-for="item in projectOptions"
              :key="item.key"
              :label="item.label"
              :value="item.key"
            />
          </el-select>
        </div>
      </div>

      <div class="page-container">
        <!-- 概览卡片 -->
        <div class="overview-cards">
          <div class="card-box">
            <div class="card-title">项目总预算</div>
            <div class="card-value">¥ {{ formatMoney(summary.totalBudget) }}</div>
            <div class="card-sub">
              <span>含税</span>
              <el-tag size="small" type="info">V1.2</el-tag>
            </div>
          </div>
          <div class="card-box">
            <div class="card-title">实际发生成本</div>
            <div class="card-value">¥ {{ formatMoney(summary.actualCost) }}</div>
            <div class="card-sub">
              <span>执行率</span>
              <span :class="getRateColor(summary.costRate)">{{ summary.costRate }}%</span>
            </div>
          </div>
          <div class="card-box">
            <div class="card-title">累计收款</div>
            <div class="card-value text-success">¥ {{ formatMoney(summary.received) }}</div>
            <div class="card-sub">
              <span>收款率</span>
              <span>{{ summary.receiveRate }}%</span>
            </div>
          </div>
          <div class="card-box">
            <div class="card-title">累计付款</div>
            <div class="card-value text-warning">¥ {{ formatMoney(summary.paid) }}</div>
            <div class="card-sub">
              <span>付款率</span>
              <span>{{ summary.payRate }}%</span>
            </div>
          </div>
          <div class="card-box">
            <div class="card-title">收支结余</div>
            <div class="card-value" :class="summary.balance >= 0 ? 'text-success' : 'text-danger'">
              ¥ {{ formatMoney(summary.balance) }}
            </div>
            <div class="card-sub">
              <span>状态</span>
              <el-tag size="small" :type="summary.balance >= 0 ? 'success' : 'danger'">
                {{ summary.balance >= 0 ? '盈余' : '赤字' }}
              </el-tag>
            </div>
          </div>

          <!-- 核心功能区 -->
          <div class="content-panel" style="grid-column: span 5;">
            <div style="position: relative;">
              <div style="position: absolute; right: 0; top: 0; z-index: 1;">
                <el-button type="primary" :icon="Plus" @click="handleEntryCost">录入实际成本</el-button>
                <!-- <el-button :icon="Download">导出报表</el-button> -->
              </div>
              <el-tabs v-model="activeTab">
                <!-- 预算执行监控 -->
                <el-tab-pane label="预算执行监控" name="execution">
                  <el-table
                    :data="budgetData"
                    row-key="id"
                    border
                    default-expand-all
                    :row-class-name="tableRowClassName"
                    v-loading="loading"
                  >
                    <el-table-column prop="centerName" label="成本中心" width="150"></el-table-column>
                    <el-table-column prop="item" label="成本项" width="150"></el-table-column>
                    <el-table-column prop="standard" label="预算标准" width="150" align="right">
                      <template #default="scope">¥ {{ formatMoney(scope.row.standard) }}</template>
                    </el-table-column>
                    <el-table-column prop="actual" label="实际发生" width="150" align="right">
                      <template #default="scope">¥ {{ formatMoney(scope.row.actual) }}</template>
                    </el-table-column>
                    <el-table-column prop="diff" label="差异金额" width="150" align="right">
                      <template #default="scope">
                        <span :class="scope.row.diff > 0 ? 'text-danger' : 'text-success'">
                          {{ scope.row.diff > 0 ? '+' : '' }}{{ formatMoney(scope.row.diff) }}
                        </span>
                      </template>
                    </el-table-column>
                    <el-table-column label="执行进度" min-width="200">
                      <template #default="scope">
                        <el-progress
                          :percentage="scope.row.percentage"
                          :color="scope.row.progressColor"
                          :format="() => `${scope.row.displayPercentage}%`"
                        />
                      </template>
                    </el-table-column>
                    <el-table-column label="状态" width="100" align="center">
                      <template #default="scope">
                        <el-tag :type="scope.row.tagType">{{ scope.row.tagName }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="120" align="center">
                      <template #default="scope">
                        <el-button link type="primary" size="small" @click="handleViewDetails(scope.row)">详情</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-tab-pane>

                <!-- 收支同步跟踪 -->
                <el-tab-pane label="收支同步跟踪" name="finance">
                  <div style="display: flex; gap: 20px;">
                    <div style="flex: 1;">
                      <div style="margin-bottom: 10px; font-weight: bold; border-left: 4px solid #67C23A; padding-left: 10px;">收款记录</div>
                      <el-table :data="receiveData" border size="small">
                        <el-table-column prop="date" label="日期" width="120"></el-table-column>
                        <el-table-column prop="stage" label="阶段"></el-table-column>
                        <el-table-column prop="amount" label="金额" align="right">
                          <template #default="scope">¥ {{ formatMoney(scope.row.amount) }}</template>
                        </el-table-column>
                        <el-table-column prop="type" label="类型" width="100">
                          <template #default="scope">
                            <el-tag size="small" :type="scope.row.isPlan ? 'info' : 'success'">{{ scope.row.isPlan ? '计划' : '实收' }}</el-tag>
                          </template>
                        </el-table-column>
                      </el-table>
                    </div>
                    <div style="flex: 1;">
                      <div style="margin-bottom: 10px; font-weight: bold; border-left: 4px solid #E6A23C; padding-left: 10px;">付款记录</div>
                      <el-table :data="payData" border size="small">
                        <el-table-column prop="date" label="日期" width="120"></el-table-column>
                        <el-table-column prop="item" label="款项内容"></el-table-column>
                        <el-table-column prop="amount" label="金额" align="right">
                          <template #default="scope">¥ {{ formatMoney(scope.row.amount) }}</template>
                        </el-table-column>
                        <el-table-column prop="type" label="类型" width="100">
                          <template #default="scope">
                            <el-tag size="small" :type="scope.row.isPlan ? 'info' : 'warning'">{{ scope.row.isPlan ? '计划' : '实付' }}</el-tag>
                          </template>
                        </el-table-column>
                      </el-table>
                    </div>
                  </div>
                </el-tab-pane>

                <!-- 预算执行分析图表 -->
                <el-tab-pane label="预算执行分析" name="analysis">
                  <div class="charts-container">
                    <!-- 预算 vs 实际 对比图 (左) -->
                    <div class="chart-wrapper chart-large">
                      <div class="chart-title">各阶段预算执行对比</div>
                      <!-- 使用 ref 替代 id -->
                      <div ref="chartBudgetActualRef" style="height: 350px;"></div>
                    </div>
                    
                    <!-- 成本构成饼图 (右) -->
                    <div class="chart-wrapper chart-medium">
                      <div class="chart-title">实际成本构成分析</div>
                      <div ref="chartCostPieRef" style="height: 350px;"></div>
                    </div>
                    
                    <!-- 月度成本趋势图 (下) -->
                    <div class="chart-wrapper chart-full">
                      <div class="chart-title">月度成本发生趋势</div>
                      <div ref="chartTrendRef" style="height: 300px;"></div>
                    </div>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 录入成本弹窗 -->
    <el-dialog v-model="entryDialogVisible" title="录入实际成本" width="500px">
      <el-form :model="entryForm" label-width="100px">
        <el-form-item label="成本中心">
          <el-select
            v-model="entryForm.centerName"
            placeholder="选择成本中心"
            filterable
            :disabled="!costCenterOptions.length"
          >
            <el-option
              v-for="item in costCenterOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="成本项">
          <el-select
            v-model="entryForm.costItem"
            placeholder="选择成本项"
            filterable
            :disabled="!entryForm.centerName || !costItemOptions.length"
          >
            <el-option
              v-for="item in costItemOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="发生金额">
          <el-input v-model="entryForm.amount" type="number">
            <template #append>元</template>
          </el-input>
        </el-form-item>
        <!-- <el-form-item label="凭证附件">
          <el-upload action="#" list-type="picture-card" :auto-upload="false">
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item> -->
        <el-form-item label="备注说明">
          <el-input v-model="entryForm.remark" type="textarea"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="entryDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEntry">确认录入</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 成本明细弹窗 -->
    <el-dialog v-model="detailsDialogVisible" title="成本明细" width="700px">
      <div v-if="currentDetailItem">
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px; background: #f5f7fa; padding: 15px; border-radius: 4px;">
          <div>
            <div style="font-size: 12px; color: #909399;">成本项</div>
            <div style="font-size: 16px; font-weight: bold;">{{ currentDetailItem.item }}</div>
          </div>
          <div>
            <div style="font-size: 12px; color: #909399;">预算标准</div>
            <div style="font-size: 16px; font-weight: bold;">¥ {{ formatMoney(currentDetailItem.standard) }}</div>
          </div>
          <div>
            <div style="font-size: 12px; color: #909399;">实际发生</div>
            <div style="font-size: 16px; font-weight: bold; color: #67C23A;">¥ {{ formatMoney(currentDetailItem.actual) }}</div>
          </div>
          <div>
            <div style="font-size: 12px; color: #909399;">差异</div>
            <div style="font-size: 16px; font-weight: bold;" :class="currentDetailItem.diff > 0 ? 'text-danger' : 'text-success'">
              {{ currentDetailItem.diff > 0 ? '+' : '' }}{{ formatMoney(currentDetailItem.diff) }}
            </div>
          </div>
        </div>

        <div style="margin-bottom: 10px; font-weight: bold; border-left: 4px solid #409EFF; padding-left: 10px;">历史发生记录</div>
        <el-table :data="detailHistoryData" border size="small" style="width: 100%">
          <el-table-column prop="date" label="发生日期" width="120"></el-table-column>
          <el-table-column prop="type" label="费用类型" width="100"></el-table-column>
          <el-table-column prop="amount" label="金额" align="right">
            <template #default="scope">¥ {{ formatMoney(scope.row.amount) }}</template>
          </el-table-column>
          <el-table-column prop="remark" label="备注说明"></el-table-column>
          <el-table-column prop="operator" label="经办人" width="100"></el-table-column>
        </el-table>
      </div>
    </el-dialog>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { Plus, Download } from '@element-plus/icons-vue'
import { ElMessage, ElNotification, ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as echarts from 'echarts'
import api from '../api/client'

const loading = ref(false)
const allBudgetRecords = ref([])
const projectOptions = ref([])
const currentProject = ref('')
const activeTab = ref('execution')
const entryDialogVisible = ref(false)
const detailsDialogVisible = ref(false)
const currentDetailItem = ref(null)
const detailHistoryData = ref([])
const receiveData = ref([])
const payData = ref([])
const budgetData = ref([])

const entryForm = reactive({
  centerName: '',
  costItem: '',
  amount: '',
  remark: ''
})

// 引用图表 DOM 元素
const chartBudgetActualRef = ref(null)
const chartCostPieRef = ref(null)
const chartTrendRef = ref(null)

// 概览数据
const summary = reactive({
  totalBudget: 0,
  actualCost: 0,
  costRate: 0,
  received: 0,
  receiveRate: 0,
  paid: 0,
  payRate: 0,
  balance: 0
})

// 规范化文本值为去空格字符串
const normalizeLabel = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

// 规范化阶段序号为可比较类型
const normalizeOrderValue = (value) => {
  if (value === null || value === undefined) return null
  const trimmed = String(value).trim()
  if (!trimmed) return null
  const numeric = Number(trimmed)
  if (Number.isFinite(numeric)) return numeric
  return trimmed
}

// 比较阶段序号（数字优先）
const compareOrderValue = (a, b) => {
  if (a === null || a === undefined) return b === null || b === undefined ? 0 : 1
  if (b === null || b === undefined) return -1
  const aIsNumber = typeof a === 'number' && Number.isFinite(a)
  const bIsNumber = typeof b === 'number' && Number.isFinite(b)
  if (aIsNumber && bIsNumber) return a - b
  return String(a).localeCompare(String(b), 'zh')
}

// 合并时选择最小的有效序号
const mergeOrderValue = (current, next) => {
  if (next === null || next === undefined) return current
  if (current === null || current === undefined) return next
  return compareOrderValue(next, current) < 0 ? next : current
}

// 构建项目分组键
const buildProjectKey = (record) => {
  const code = normalizeLabel(record?.project_code)
  const name = normalizeLabel(record?.project_name)
  const type = normalizeLabel(record?.project_type)
  return `${code}||${name}||${type}`
}

// 根据记录生成项目下拉选项
const buildProjectOptions = (records) => {
  const map = new Map()
  records.forEach((record) => {
    const key = buildProjectKey(record)
    if (key === '||') return
    if (map.has(key)) return
    const code = normalizeLabel(record.project_code)
    const name = normalizeLabel(record.project_name)
    const type = normalizeLabel(record.project_type)
    const label = code ? `${code} - ${name || '未命名项目'}` : (name || '未命名项目')
    map.set(key, {
      key,
      code,
      name,
      type,
      label
    })
  })
  return Array.from(map.values())
}

// 当前选中项目元信息
const currentProjectMeta = computed(() =>
  projectOptions.value.find((item) => item.key === currentProject.value) || {}
)

// 当前项目对应的记录
const filteredBudgetRecords = computed(() => {
  if (!currentProject.value) return []
  return allBudgetRecords.value.filter(
    (record) => buildProjectKey(record) === currentProject.value
  )
})

// 成本中心下拉（按主阶段序号排序）
const costCenterOptions = computed(() => {
  const map = new Map()
  filteredBudgetRecords.value.forEach((record) => {
    const center = normalizeLabel(record.cost_center)
    if (!center) return
    const mainOrder = normalizeOrderValue(record.main_stage_order)
    const current = map.get(center) ?? null
    map.set(center, mergeOrderValue(current, mainOrder))
  })
  return Array.from(map.entries())
    .sort((a, b) => {
      const orderCompare = compareOrderValue(a[1], b[1])
      if (orderCompare !== 0) return orderCompare
      return a[0].localeCompare(b[0], 'zh')
    })
    .map(([center]) => center)
})

// 成本项下拉（按阶段序号排序）
const costItemOptions = computed(() => {
  const map = new Map()
  const selectedCenter = normalizeLabel(entryForm.centerName)
  if (!selectedCenter) return []
  filteredBudgetRecords.value.forEach((record) => {
    const center = normalizeLabel(record.cost_center)
    if (selectedCenter && center !== selectedCenter) return
    const item = normalizeLabel(record.cost_item)
    if (!item) return
    const mainOrder = normalizeOrderValue(record.main_stage_order)
    const stageOrder = normalizeOrderValue(record.project_stage_order)
    const current = map.get(item) || { mainOrder: null, stageOrder: null }
    current.mainOrder = mergeOrderValue(current.mainOrder, mainOrder)
    current.stageOrder = mergeOrderValue(current.stageOrder, stageOrder)
    map.set(item, current)
  })
  return Array.from(map.entries())
    .sort((a, b) => {
      const mainCompare = compareOrderValue(a[1].mainOrder, b[1].mainOrder)
      if (mainCompare !== 0) return mainCompare
      const stageCompare = compareOrderValue(a[1].stageOrder, b[1].stageOrder)
      if (stageCompare !== 0) return stageCompare
      return a[0].localeCompare(b[0], 'zh')
    })
    .map(([item]) => item)
})

// 成本中心变化时重置成本项
watch(
  () => entryForm.centerName,
  (value, oldValue) => {
    if (value !== oldValue) {
      entryForm.costItem = ''
    }
  }
)

// 安全转换为数字
const toNumber = (value) => {
  if (value === null || value === undefined || value === '') return 0
  if (typeof value === 'number') return Number.isFinite(value) ? value : 0
  const cleaned = String(value).replace(/,/g, '')
  const numeric = Number(cleaned)
  return Number.isFinite(numeric) ? numeric : 0
}

// 计算实际成本（总额或明细汇总）
const getRecordActual = (record) => {
  const actual = toNumber(record?.actual_total)
  const details = Array.isArray(record?.cost_details) ? record.cost_details : []
  const sumDetails = details.reduce((acc, item) => acc + toNumber(item?.detail_amount), 0)
  if (actual === 0 && sumDetails > 0) return sumDetails
  return actual
}

// 根据实际/预算计算状态
const resolveBudgetStatus = (actual, standard) => (actual > standard ? '超支' : '正常')

// 构建进度展示所需状态数据
const buildStatusMeta = (actual, standard) => {
  if (standard <= 0) {
    if (actual > 0) {
      return { percentage: 100, displayPercentage: 100, progressColor: '#f5222d', tagType: 'danger', tagName: '超支' }
    }
    return { percentage: 0, displayPercentage: 0, progressColor: '#1890ff', tagType: 'success', tagName: '正常' }
  }
  const rawPercentage = Math.round((actual / standard) * 100)
  const displayPercentage = Math.max(0, rawPercentage)
  const percentage = Math.min(100, displayPercentage)
  if (actual > standard) {
    return { percentage, displayPercentage, progressColor: '#f5222d', tagType: 'danger', tagName: '超支' }
  }
  return { percentage, displayPercentage, progressColor: '#1890ff', tagType: 'success', tagName: '正常' }
}

// 将原始记录组装成表格分组数据
const buildBudgetData = (records) => {
  if (!records.length) return []
  const centerMap = new Map()

  records.forEach((record) => {
    const center = normalizeLabel(record.cost_center) || '未分类'
    const item = normalizeLabel(record.cost_item) || '未命名'
    const standard = toNumber(record.budget_standard)
    const actual = getRecordActual(record)
    const mainOrder = normalizeOrderValue(record.main_stage_order)
    const stageOrder = normalizeOrderValue(record.project_stage_order)

    if (!centerMap.has(center)) {
      centerMap.set(center, { itemMap: new Map(), order: mainOrder })
    }
    const centerEntry = centerMap.get(center)
    centerEntry.order = mergeOrderValue(centerEntry.order, mainOrder)
    const itemMap = centerEntry.itemMap
    if (!itemMap.has(item)) {
      itemMap.set(item, {
        standard: 0,
        actual: 0,
        records: [],
        mainOrder,
        stageOrder
      })
    }
    const entry = itemMap.get(item)
    entry.standard += standard
    entry.actual += actual
    entry.records.push(record)
    entry.mainOrder = mergeOrderValue(entry.mainOrder, mainOrder)
    entry.stageOrder = mergeOrderValue(entry.stageOrder, stageOrder)
  })

  const rows = []
  let rowIndex = 0
  const centers = Array.from(centerMap.entries())
    .map(([center, meta]) => ({ center, ...meta }))
    .sort((a, b) => {
      const orderCompare = compareOrderValue(a.order, b.order)
      if (orderCompare !== 0) return orderCompare
      return a.center.localeCompare(b.center, 'zh')
    })

  centers.forEach((centerEntry) => {
    const { center, itemMap } = centerEntry
    const sortedItems = Array.from(itemMap.entries())
      .map(([item, entry]) => ({ item, ...entry }))
      .sort((a, b) => {
        const mainCompare = compareOrderValue(a.mainOrder, b.mainOrder)
        if (mainCompare !== 0) return mainCompare
        const stageCompare = compareOrderValue(a.stageOrder, b.stageOrder)
        if (stageCompare !== 0) return stageCompare
        return a.item.localeCompare(b.item, 'zh')
      })
    const children = []
    let totalStandard = 0
    let totalActual = 0

    sortedItems.forEach((entry) => {
      const item = entry.item
      totalStandard += entry.standard
      totalActual += entry.actual
      const statusMeta = buildStatusMeta(entry.actual, entry.standard)
      children.push({
        id: `item-${rowIndex++}`,
        centerName: '',
        item,
        standard: entry.standard,
        actual: entry.actual,
        diff: entry.actual - entry.standard,
        percentage: statusMeta.percentage,
        displayPercentage: statusMeta.displayPercentage,
        progressColor: statusMeta.progressColor,
        tagType: statusMeta.tagType,
        tagName: statusMeta.tagName,
        _records: entry.records
      })
    })

    const totalStatus = buildStatusMeta(totalActual, totalStandard)
    rows.push({
      id: `center-${rowIndex++}`,
      centerName: center,
      item: '总计',
      standard: totalStandard,
      actual: totalActual,
      diff: totalActual - totalStandard,
      percentage: totalStatus.percentage,
      displayPercentage: totalStatus.displayPercentage,
      progressColor: totalStatus.progressColor,
      tagType: totalStatus.tagType,
      tagName: totalStatus.tagName,
      children,
      _records: children.flatMap((child) => child._records || [])
    })
  })

  return rows
}

// 金额格式化（千分位）
const formatMoney = (val) => {
  const amount = toNumber(val)
  return amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// 根据比例返回颜色样式
const getRateColor = (rate) => {
  if (rate > 100) return 'text-danger'
  if (rate > 90) return 'text-warning'
  return 'text-success'
}

// 表格总计行高亮
const tableRowClassName = ({ row }) => {
  if (row.item === '总计') {
    return 'total-row'
  }
  return ''
}

// 日期格式化展示
const formatDate = (value) => {
  if (!value) return ''
  if (value instanceof Date) {
    const year = value.getFullYear()
    const month = String(value.getMonth() + 1).padStart(2, '0')
    const day = String(value.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  if (typeof value === 'number') {
    return formatDate(new Date(value))
  }
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed) return ''
    const parsed = new Date(trimmed.replace(/-/g, '/'))
    if (!Number.isNaN(parsed.getTime())) {
      return formatDate(parsed)
    }
    const match = trimmed.match(/\d{4}[-/]\d{1,2}[-/]\d{1,2}/)
    return match ? match[0].replace(/\//g, '-') : trimmed
  }
  return String(value)
}

// 明细时间格式化
const formatDateTime = (date) => {
  const dt = date instanceof Date ? date : new Date()
  const year = dt.getFullYear()
  const month = String(dt.getMonth() + 1).padStart(2, '0')
  const day = String(dt.getDate()).padStart(2, '0')
  const hours = String(dt.getHours()).padStart(2, '0')
  const minutes = String(dt.getMinutes()).padStart(2, '0')
  const seconds = String(dt.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 根据明细生成付款记录
const buildPayData = (records) => {
  const items = []
  records.forEach((record) => {
    const details = Array.isArray(record.cost_details) ? record.cost_details : []
    details.forEach((detail) => {
      const amount = toNumber(detail?.detail_amount)
      items.push({
        date: formatDate(detail?.detail_date),
        item: detail?.detail_item || record.cost_item || '',
        amount,
        isPlan: false
      })
    })
  })
  return items
}

// 根据记录刷新汇总卡片
const refreshSummary = (records) => {
  const totalBudget = records.reduce((acc, record) => acc + toNumber(record?.budget_standard), 0)
  const actualCost = records.reduce((acc, record) => acc + getRecordActual(record), 0)
  const costRate = totalBudget > 0 ? Number(((actualCost / totalBudget) * 100).toFixed(1)) : 0
  const paid = actualCost
  const payRate = totalBudget > 0 ? Number(((paid / totalBudget) * 100).toFixed(1)) : 0

  summary.totalBudget = totalBudget
  summary.actualCost = actualCost
  summary.costRate = costRate
  summary.received = 0
  summary.receiveRate = 0
  summary.paid = paid
  summary.payRate = payRate
  summary.balance = summary.received - summary.paid
}

// 刷新表格/汇总/图表数据
const refreshViewData = () => {
  const records = filteredBudgetRecords.value
  budgetData.value = buildBudgetData(records)
  payData.value = buildPayData(records)
  receiveData.value = []
  refreshSummary(records)
  if (activeTab.value === 'analysis') {
    nextTick(() => initCharts())
  }
}

// 从后端加载预算记录并初始化项目选择
const loadBudgetRecords = async () => {
  loading.value = true
  try {
    const result = await api.listProjectBudgets({ skip: 0, limit: 300 })
    if (result?.code === 200 && Array.isArray(result.data)) {
      allBudgetRecords.value = result.data
      projectOptions.value = buildProjectOptions(result.data)
      if (
        projectOptions.value.length > 0 &&
        !projectOptions.value.find((item) => item.key === currentProject.value)
      ) {
        currentProject.value = projectOptions.value[0].key
      }
    } else {
      allBudgetRecords.value = []
      projectOptions.value = []
      ElMessage.error(result?.msg || '加载预算数据失败')
    }
  } catch (error) {
    console.error('加载预算数据失败：', error)
    allBudgetRecords.value = []
    projectOptions.value = []
    ElMessage.error('加载预算数据失败')
  } finally {
    loading.value = false
    refreshViewData()
  }
}

// 切换项目时刷新视图
const handleProjectChange = () => {
  refreshViewData()
}

// 校验后打开录入弹窗
const handleEntryCost = () => {
  if (!currentProject.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  entryDialogVisible.value = true
}

// 整理明细弹窗历史记录
const extractDetailHistory = (records) => {
  const rows = []
  records.forEach((record) => {
    const details = Array.isArray(record.cost_details) ? record.cost_details : []
    details.forEach((detail) => {
      rows.push({
        date: formatDate(detail?.detail_date),
        type: detail?.detail_item || record.cost_item || '',
        amount: toNumber(detail?.detail_amount),
        remark: detail?.detail_remark || '',
        operator: detail?.operator || '--'
      })
    })
  })
  return rows
}

// 打开明细弹窗
const handleViewDetails = (row) => {
  currentDetailItem.value = row
  const records = row?._records || []
  detailHistoryData.value = extractDetailHistory(records)
  detailsDialogVisible.value = true
}

// 重置录入表单
const resetEntryForm = () => {
  entryForm.centerName = ''
  entryForm.costItem = ''
  entryForm.amount = ''
  entryForm.remark = ''
}

// 提交成本录入并刷新数据
const submitEntry = async () => {
  if (!currentProject.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  if (!entryForm.centerName) {
    ElMessage.warning('请选择成本中心')
    return
  }
  if (!entryForm.costItem) {
    ElMessage.warning('请选择成本项')
    return
  }
  if (!entryForm.amount) {
    ElMessage.warning('请输入金额')
    return
  }

  const amount = toNumber(entryForm.amount)
  if (amount <= 0) {
    ElMessage.warning('金额必须大于0')
    return
  }

  const detail = {
    detail_date: formatDateTime(new Date()),
    detail_item: entryForm.costItem,
    detail_amount: amount,
    detail_remark: entryForm.remark || ''
  }

  try {
    const existingRecord = filteredBudgetRecords.value.find(
      (record) =>
        normalizeLabel(record.cost_center) === normalizeLabel(entryForm.centerName) &&
        normalizeLabel(record.cost_item) === normalizeLabel(entryForm.costItem)
    )

    if (existingRecord?._id) {
      const existingDetails = Array.isArray(existingRecord.cost_details)
        ? [...existingRecord.cost_details]
        : []
      existingDetails.push(detail)
      const newActual = getRecordActual(existingRecord) + amount
      const budgetStandard = toNumber(existingRecord.budget_standard)
      const status = resolveBudgetStatus(newActual, budgetStandard)
      const result = await api.updateProjectBudget(existingRecord._id, {
        actual_total: newActual,
        cost_details: existingDetails,
        status
      })
      if (result?.code !== 200) {
        ElMessage.error(result?.msg || '成本录入失败')
        return
      }
    } else {
      const budgetStandard = 0
      const status = resolveBudgetStatus(amount, budgetStandard)
      const payload = {
        project_code: currentProjectMeta.value.code || '',
        project_name: currentProjectMeta.value.name || '',
        project_type: currentProjectMeta.value.type || '',
        cost_center: entryForm.centerName,
        cost_item: entryForm.costItem,
        budget_standard: budgetStandard,
        actual_total: amount,
        status,
        cost_details: [detail]
      }
      const result = await api.createProjectBudget(payload)
      if (result?.code !== 200) {
        ElMessage.error(result?.msg || '成本录入失败')
        return
      }
    }

    if (amount > 50000) {
      ElNotification({
        title: '异常自动推送',
        message: `监测到 ${entryForm.centerName} 成本异常超支，已推送到钉钉管理群 @项目经理 @财务总监`,
        type: 'error',
        duration: 5000
      })
    }

    ElMessage.success('成本录入成功')
    entryDialogVisible.value = false
    resetEntryForm()
    await loadBudgetRecords()
  } catch (error) {
    console.error('成本录入失败：', error)
    ElMessage.error('成本录入失败')
  }
}

// 图表相关
let chartInstances = []

// 生成成本中心柱状图数据
const getCenterChartData = () => {
  const rows = budgetData.value.filter((row) => row.item === '总计')
  return {
    labels: rows.map((row) => row.centerName),
    standard: rows.map((row) => row.standard),
    actual: rows.map((row) => row.actual)
  }
}

// 生成成本构成饼图数据
const getCostPieData = () => {
  const itemRows = budgetData.value.flatMap((row) => row.children || [])
  let materialCost = 0
  let laborCost = 0
  let otherCost = 0

  // 成本项分类汇总
  const classifyCost = (item, amount) => {
    const label = item || ''
    if (label.includes('材料') || label.includes('采购') || label.includes('五金')) {
      materialCost += amount
    } else if (label.includes('人工') || label.includes('工资')) {
      laborCost += amount
    } else {
      otherCost += amount
    }
  }

  itemRows.forEach((row) => {
    classifyCost(row.item, toNumber(row.actual))
  })

  return [
    { value: materialCost, name: '材料费用' },
    { value: laborCost, name: '人工费用' },
    { value: otherCost, name: '其他费用' }
  ]
}

// 汇总月度趋势数据
const buildTrendData = (records) => {
  const map = new Map()
  records.forEach((record) => {
    const details = Array.isArray(record.cost_details) ? record.cost_details : []
    details.forEach((detail) => {
      const dateValue = detail?.detail_date
      if (!dateValue) return
      const parsed = new Date(String(dateValue).replace(/-/g, '/'))
      if (Number.isNaN(parsed.getTime())) return
      const year = parsed.getFullYear()
      const month = String(parsed.getMonth() + 1).padStart(2, '0')
      const key = `${year}-${month}`
      const amount = toNumber(detail?.detail_amount)
      map.set(key, (map.get(key) || 0) + amount)
    })
  })
  const labels = Array.from(map.keys()).sort()
  const values = labels.map((key) => map.get(key) || 0)
  return { labels, values }
}

// 初始化/刷新图表实例
const initCharts = () => {
  if (chartInstances.length > 0) {
    chartInstances.forEach((chart) => chart.dispose())
    chartInstances = []
  }

  nextTick(() => {
    if (!chartBudgetActualRef.value || !chartCostPieRef.value || !chartTrendRef.value) return

    const centerChart = getCenterChartData()
    const chart1 = echarts.init(chartBudgetActualRef.value)
    chart1.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['预算标准', '实际发生'], top: 12 },
      grid: { left: '3%', right: '4%', bottom: '3%', top: 60, containLabel: true },
      xAxis: { type: 'category', data: centerChart.labels },
      yAxis: { type: 'value' },
      series: [
        { name: '预算标准', type: 'bar', data: centerChart.standard, itemStyle: { color: '#409EFF' } },
        { name: '实际发生', type: 'bar', data: centerChart.actual, itemStyle: { color: '#67C23A' } }
      ]
    })
    chartInstances.push(chart1)

    const chart2 = echarts.init(chartCostPieRef.value)
    chart2.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: { orient: 'vertical', left: 'left' },
      color: ['#409EFF', '#E6A23C', '#909399'],
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
              fontSize: '20',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: getCostPieData()
        }
      ]
    })
    chartInstances.push(chart2)

    const chart3 = echarts.init(chartTrendRef.value)
    const trend = buildTrendData(filteredBudgetRecords.value)
    chart3.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: trend.labels },
      yAxis: { type: 'value' },
      series: [{
        name: '实际成本',
        data: trend.values,
        type: 'line',
        smooth: true,
        itemStyle: { color: '#67C23A' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.5)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.1)' }
          ])
        }
      }]
    })
    chartInstances.push(chart3)
  })
}

// 切换分析页时重绘图表
watch(activeTab, (newVal) => {
  if (newVal === 'analysis') {
    initCharts()
  }
})

// 窗口大小改变时重绘
// 窗口变化时重绘图表
const handleResize = () => {
  chartInstances.forEach((chart) => chart && chart.resize())
}

// 挂载时加载数据并绑定监听
onMounted(async () => {
  await loadBudgetRecords()
  window.addEventListener('resize', handleResize)
})

// 卸载时清理监听与图表
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstances.forEach((chart) => chart.dispose())
})
</script>

<style scoped>
.project-budget-management {
  display: flex;
  min-height: 100vh;
  background-color: #f0f2f5;
  color: #333;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部导航 */
.header {
  height: 64px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 10;
}
.header-title {
  font-size: 18px;
  font-weight: 600;
}

/* 页面内容容器 */
.page-container {
  padding: 16px;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 概览卡片 */
.overview-cards {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}
.card-box {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.card-title {
  color: #909399;
  font-size: 14px;
  margin-bottom: 8px;
}
.card-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}
.card-sub {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  display: flex;
  justify-content: space-between;
}
.text-success { color: #67C23A; }
.text-danger { color: #F56C6C; }
.text-warning { color: #E6A23C; }

/* 内容面板 */
.content-panel {
  background: #fff;
  border-radius: 4px;
  padding: 16px 24px;
  flex: 1;
  box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
}

/* 表格样式微调 - 注意：scoped 样式下修改 element 内部样式需要使用 :deep() */
:deep(.el-table th) {
  background-color: #f5f7fa !important;
}
:deep(.el-progress-bar__outer) {
  background-color: #ebeef5;
}
:deep(.el-table .total-row) {
  --el-table-tr-bg-color: #fffbee;
  font-weight: bold;
}
:deep(.el-table .total-row td) {
  border-top: 1px solid #faad14 !important;
  border-bottom: 1px solid #faad14 !important;
}

/* 图表容器样式 */
.charts-container {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
.chart-wrapper {
  background: #fff;
  border-radius: 4px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  border: 1px solid #ebeef5;
  box-sizing: border-box;
}
/* 第一行左侧：预算对比 (60%) */
.chart-large {
  width: calc(60% - 8px);
}
/* 第一行右侧：成本构成 (40%) */
.chart-medium {
  width: calc(40% - 8px);
}
/* 第二行：趋势图 (100%) */
.chart-full {
  width: 100%;
}
.chart-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 4px solid #1890ff;
}
</style>
