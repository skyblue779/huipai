<template>
  <el-config-provider :locale="zhCn">
    <div class="my-budget-page">
      <div class="main-content">
        <div class="header">
          <div class="header-left">
            <div class="header-title">我的负责节点</div>
            <div class="header-subtitle">跨项目查看并处理当前责任人名下的预算节点</div>
          </div>
          <div class="header-actions">
            <el-input
              v-model="keyword"
              clearable
              placeholder="搜索项目/成本中心/成本项"
              style="width: 260px"
            />
            <el-select v-model="statusFilter" clearable placeholder="状态筛选" style="width: 140px">
              <el-option
                v-for="item in statusOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
            <el-button :loading="loading" @click="loadBudgetRecords">刷新</el-button>
          </div>
        </div>

        <div class="page-container">
          <el-alert
            v-if="!userParam"
            title="未获取到网页参数 webpage_user_id，当前无法识别责任人。"
            type="warning"
            show-icon
            :closable="false"
          />

          <div class="summary-grid">
            <div class="summary-card">
              <div class="summary-label">负责项目数</div>
              <div class="summary-value">{{ summary.projectCount }}</div>
              <div class="summary-extra">跨项目平铺展示</div>
            </div>
            <div class="summary-card">
              <div class="summary-label">负责节点数</div>
              <div class="summary-value">{{ summary.recordCount }}</div>
              <div class="summary-extra">仅显示本人节点</div>
            </div>
            <div class="summary-card">
              <div class="summary-label">预算总额</div>
              <div class="summary-value">¥ {{ formatMoney(summary.totalBudget) }}</div>
              <div class="summary-extra">节点预算汇总</div>
            </div>
            <div class="summary-card">
              <div class="summary-label">实际发生</div>
              <div class="summary-value">¥ {{ formatMoney(summary.totalActual) }}</div>
              <div class="summary-extra">超支 {{ summary.overrunCount }} 个</div>
            </div>
          </div>

          <div class="content-panel">
            <div class="panel-toolbar">
              <div class="panel-title">
                <span>我的预算节点清单</span>
                <el-tag size="small" type="info">{{ filteredRows.length }} 条</el-tag>
              </div>
              <div class="panel-hint">{{ panelHint }}</div>
            </div>

            <div v-if="isMobile" class="mobile-records">
              <div v-for="row in filteredRows" :key="row.recordId" class="mobile-record-card">
                <div class="mobile-record-header">
                  <div class="mobile-record-title">{{ row.projectName || row.projectCode || '--' }}</div>
                  <el-tag :type="row.tagType">{{ row.status }}</el-tag>
                </div>
                <div class="mobile-record-code">{{ row.projectCode || '--' }}</div>
                <div class="mobile-record-grid">
                  <div class="mobile-record-item">
                    <span class="mobile-label">项目类型</span>
                    <span class="mobile-value">{{ row.projectType || '--' }}</span>
                  </div>
                  <div class="mobile-record-item">
                    <span class="mobile-label">成本中心</span>
                    <span class="mobile-value">{{ row.centerName || '--' }}</span>
                  </div>
                  <div class="mobile-record-item">
                    <span class="mobile-label">成本项</span>
                    <span class="mobile-value">{{ row.itemName || '--' }}</span>
                  </div>
                  <div class="mobile-record-item">
                    <span class="mobile-label">责任人</span>
                    <span class="mobile-value">{{ row.responsibleName || '--' }}</span>
                  </div>
                  <div class="mobile-record-item">
                    <span class="mobile-label">预算标准</span>
                    <span class="mobile-value">¥ {{ formatMoney(row.budgetStandard) }}</span>
                  </div>
                  <div class="mobile-record-item">
                    <span class="mobile-label">实际发生</span>
                    <span class="mobile-value">¥ {{ formatMoney(row.actualTotal) }}</span>
                  </div>
                  <div class="mobile-record-item">
                    <span class="mobile-label">预算差异</span>
                    <span class="mobile-value" :class="row.diff > 0 ? 'text-danger' : 'text-success'">
                      {{ row.diff > 0 ? '+' : '' }}{{ formatMoney(row.diff) }}
                    </span>
                  </div>
                  <div class="mobile-record-item">
                    <span class="mobile-label">最近发生</span>
                    <span class="mobile-value">{{ row.latestCostDate }}</span>
                  </div>
                </div>
                <el-progress
                  :percentage="row.percentage"
                  :color="row.progressColor"
                  :format="() => `${row.displayPercentage}%`"
                />
                <div class="mobile-actions">
                  <el-button link type="primary" size="small" @click="handleViewDetails(row)">详情</el-button>
                  <el-button
                    v-if="canRecordActualCost"
                    link
                    type="primary"
                    size="small"
                    @click="openEntryDialog(row)"
                  >
                    录入成本
                  </el-button>
                  <el-button link type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
                </div>
              </div>
              <el-empty v-if="!filteredRows.length" description="当前责任人暂无预算节点" />
            </div>

            <el-table
              v-else
              :data="filteredRows"
              border
              stripe
              v-loading="loading"
              height="calc(100vh - 280px)"
            >
              <el-table-column type="index" label="序号" width="70" align="center" />
              <el-table-column prop="projectCode" label="项目编号" min-width="140" />
              <el-table-column prop="projectName" label="项目名称" min-width="180" />
              <el-table-column prop="projectType" label="项目类型" min-width="120" />
              <el-table-column prop="centerName" label="成本中心" min-width="140" />
              <el-table-column prop="itemName" label="成本项" min-width="160" />
              <el-table-column prop="responsibleName" label="责任人" min-width="120" />
              <el-table-column label="预算标准" width="140" align="right">
                <template #default="{ row }">¥ {{ formatMoney(row.budgetStandard) }}</template>
              </el-table-column>
              <el-table-column label="实际发生" width="140" align="right">
                <template #default="{ row }">¥ {{ formatMoney(row.actualTotal) }}</template>
              </el-table-column>
              <el-table-column label="预算差异" width="140" align="right">
                <template #default="{ row }">
                  <span :class="row.diff > 0 ? 'text-danger' : 'text-success'">
                    {{ row.diff > 0 ? '+' : '' }}{{ formatMoney(row.diff) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="执行率" width="180">
                <template #default="{ row }">
                  <el-progress
                    :percentage="row.percentage"
                    :color="row.progressColor"
                    :format="() => `${row.displayPercentage}%`"
                  />
                </template>
              </el-table-column>
              <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.tagType">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="latestCostDate" label="最近发生日期" width="120" align="center" />
              <el-table-column label="操作" width="220" fixed="right" align="center">
                <template #default="{ row }">
                  <div class="table-actions">
                    <el-button link type="primary" size="small" @click="handleViewDetails(row)">详情</el-button>
                    <el-button
                      v-if="canRecordActualCost"
                      link
                      type="primary"
                      size="small"
                      @click="openEntryDialog(row)"
                    >
                      录入成本
                    </el-button>
                    <el-button link type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
                  </div>
                </template>
              </el-table-column>
              <template #empty>
                <el-empty description="当前责任人暂无预算节点" />
              </template>
            </el-table>
          </div>
        </div>
      </div>

      <el-dialog v-model="detailsDialogVisible" title="成本明细" :width="detailDialogWidth">
        <div v-if="currentDetailRow">
          <div class="detail-summary">
            <div>
              <div class="detail-label">项目</div>
              <div class="detail-value">{{ currentDetailRow.projectName || '--' }}</div>
            </div>
            <div>
              <div class="detail-label">成本项</div>
              <div class="detail-value">{{ currentDetailRow.itemName || '--' }}</div>
            </div>
            <div>
              <div class="detail-label">预算标准</div>
              <div class="detail-value">¥ {{ formatMoney(currentDetailRow.budgetStandard) }}</div>
            </div>
            <div>
              <div class="detail-label">实际发生</div>
              <div class="detail-value text-success">¥ {{ formatMoney(currentDetailRow.actualTotal) }}</div>
            </div>
          </div>
          <el-table :data="detailHistoryRows" border size="small">
            <el-table-column prop="date" label="发生日期" width="140" />
            <el-table-column prop="costType" label="费用类型" width="140" />
            <el-table-column prop="item" label="成本项" min-width="140" />
            <el-table-column label="金额" width="140" align="right">
              <template #default="{ row }">¥ {{ formatMoney(row.amount) }}</template>
            </el-table-column>
            <el-table-column prop="remark" label="备注说明" min-width="180" />
          </el-table>
        </div>
      </el-dialog>

      <el-dialog v-model="editDialogVisible" title="编辑负责节点" :width="formDialogWidth">
        <el-form :model="editForm" label-width="100px">
          <el-form-item label="项目名称">
            <el-input :model-value="editForm.projectName" disabled />
          </el-form-item>
          <el-form-item label="成本中心">
            <el-input :model-value="editForm.centerName" disabled />
          </el-form-item>
          <el-form-item label="成本项">
            <el-input :model-value="editForm.costItem" disabled />
          </el-form-item>
          <el-form-item label="责任人">
            <el-select
              v-model="editForm.responsiblePersonId"
              filterable
              clearable
              placeholder="请选择责任人"
              style="width: 100%"
              :loading="userLoading"
            >
              <el-option
                v-for="item in userOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="预算标准">
            <el-input v-model="editForm.budgetStandard" type="number" min="0">
              <template #append>元</template>
            </el-input>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" :loading="editSubmitting" @click="submitEdit">保存</el-button>
          </span>
        </template>
      </el-dialog>

      <el-dialog v-model="entryDialogVisible" title="录入实际成本" :width="formDialogWidth">
        <el-form :model="entryForm" label-width="100px">
          <el-form-item label="项目名称">
            <el-input :model-value="entryForm.projectName" disabled />
          </el-form-item>
          <el-form-item label="成本中心">
            <el-input :model-value="entryForm.centerName" disabled />
          </el-form-item>
          <el-form-item label="成本项">
            <el-input :model-value="entryForm.costItem" disabled />
          </el-form-item>
          <el-form-item label="费用类型">
            <el-select
              v-model="entryForm.costType"
              placeholder="请选择费用类型"
              filterable
              allow-create
              default-first-option
              style="width: 100%"
            >
              <el-option
                v-for="item in costTypeOptions"
                :key="item"
                :label="item.label || item"
                :value="item.value || item"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="发生金额">
            <el-input v-model="entryForm.amount" type="number">
              <template #append>元</template>
            </el-input>
          </el-form-item>
          <el-form-item label="备注说明">
            <el-input v-model="entryForm.remark" type="textarea" />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="entryDialogVisible = false">取消</el-button>
            <el-button type="primary" :loading="entrySubmitting" @click="submitEntry">确认录入</el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { ElConfigProvider, ElMessage } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { useRoute } from 'vue-router'
import api from '../api/client'
import { resolveWebpageUserId } from '../utils/webpageUser'

const route = useRoute()

const loading = ref(false)
const userLoading = ref(false)
const entrySubmitting = ref(false)
const editSubmitting = ref(false)
const isMobile = ref(false)

const allBudgetRecords = ref([])
const users = ref([])
const noActualEntryRoleMembers = ref([])
const userParam = ref('')
const userProfile = ref({
  user_id: '',
  name: '',
  account: ''
})

const keyword = ref('')
const statusFilter = ref('')

const detailsDialogVisible = ref(false)
const editDialogVisible = ref(false)
const entryDialogVisible = ref(false)
const currentDetailRow = ref(null)
const currentEditRecord = ref(null)
const currentEntryRecord = ref(null)
const detailHistoryRows = ref([])

const statusOptions = [
  { label: '正常', value: '正常' },
  { label: '超支', value: '超支' }
]

const costTypeOptions = ['材料费用', '人工费用', '其他费用']
const BUDGET_NO_ACTUAL_ENTRY_ROLE_ID = '2fb04dc18718bca25df50a22'

const editForm = reactive({
  projectName: '',
  centerName: '',
  costItem: '',
  responsiblePersonId: '',
  budgetStandard: ''
})

const entryForm = reactive({
  projectName: '',
  centerName: '',
  costItem: '',
  costType: '',
  amount: '',
  remark: ''
})

const normalizeLabel = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const normalizeToken = (value) => normalizeLabel(value).toLowerCase()

const isSameUserToken = (left, right) => {
  const leftToken = normalizeToken(left)
  const rightToken = normalizeToken(right)
  return Boolean(leftToken && rightToken && leftToken === rightToken)
}

const toNumber = (value) => {
  if (value === null || value === undefined || value === '') return 0
  if (typeof value === 'number') return Number.isFinite(value) ? value : 0
  const numeric = Number(String(value).replace(/,/g, ''))
  return Number.isFinite(numeric) ? numeric : 0
}

const moneyFormatter = new Intl.NumberFormat('zh-CN', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
})

const formatMoney = (value) => moneyFormatter.format(toNumber(value))

const formatDate = (value) => {
  if (!value) return ''
  if (value instanceof Date) {
    const year = value.getFullYear()
    const month = String(value.getMonth() + 1).padStart(2, '0')
    const day = String(value.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  if (typeof value === 'number') return formatDate(new Date(value))
  const text = normalizeLabel(value)
  if (!text) return ''
  const parsed = new Date(text.replace(/-/g, '/'))
  if (!Number.isNaN(parsed.getTime())) return formatDate(parsed)
  const match = text.match(/\d{4}[-/]\d{1,2}[-/]\d{1,2}/)
  return match ? match[0].replace(/\//g, '-') : text
}

const formatDateTime = (date) => {
  const dt = date instanceof Date ? date : new Date()
  const year = dt.getFullYear()
  const month = String(dt.getMonth() + 1).padStart(2, '0')
  const day = String(dt.getDate()).padStart(2, '0')
  const hour = String(dt.getHours()).padStart(2, '0')
  const minute = String(dt.getMinutes()).padStart(2, '0')
  const second = String(dt.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hour}:${minute}:${second}`
}

const normalizeOrderValue = (value) => {
  const text = normalizeLabel(value)
  if (!text) return null
  const numeric = Number(text)
  return Number.isFinite(numeric) ? numeric : text
}

const compareOrderValue = (left, right) => {
  if (left === null || left === undefined) return right === null || right === undefined ? 0 : 1
  if (right === null || right === undefined) return -1
  const leftIsNumber = typeof left === 'number' && Number.isFinite(left)
  const rightIsNumber = typeof right === 'number' && Number.isFinite(right)
  if (leftIsNumber && rightIsNumber) return left - right
  return String(left).localeCompare(String(right), 'zh')
}

const resolveBudgetStatus = (actual, standard) => (actual > standard ? '超支' : '正常')

const getMemberId = (value) => {
  if (!value) return ''
  if (Array.isArray(value)) {
    const first = value.find((item) => getMemberId(item))
    return first ? getMemberId(first) : ''
  }
  if (typeof value === 'object') {
    return normalizeLabel(value.user_id || value._id || value.id)
  }
  return normalizeLabel(value)
}

const getMemberLabel = (value) => {
  if (!value) return ''
  if (Array.isArray(value)) {
    const labels = value.map((item) => getMemberLabel(item)).filter(Boolean)
    return Array.from(new Set(labels)).join(' / ')
  }
  if (typeof value === 'object') {
    return normalizeLabel(value.name || value.realname || value.account || value.user_id || value._id || value.id)
  }
  return normalizeLabel(value)
}

const extractUserTokens = (value) => {
  if (!value) return []
  if (Array.isArray(value)) {
    return Array.from(new Set(value.flatMap((item) => extractUserTokens(item)).filter(Boolean)))
  }
  if (typeof value === 'object') {
    return Array.from(
      new Set(
        [
          value.user_id,
          value._id,
          value.id,
          value.account,
          value.name,
          value.realname,
          value.uniqueid
        ]
          .map(normalizeToken)
          .filter(Boolean)
      )
    )
  }
  const token = normalizeToken(value)
  return token ? [token] : []
}

const normalizeCostType = (value) => {
  if (!value) return ''
  if (Array.isArray(value)) {
    const labels = value.map((item) => normalizeCostType(item)).filter(Boolean)
    return Array.from(new Set(labels)).join('、')
  }
  if (typeof value === 'object') {
    return normalizeLabel(
      value.cost_type ||
        value._widget_1772415164746 ||
        value.type ||
        value.name ||
        value.label ||
        value.value ||
        value.text
    )
  }
  return normalizeLabel(value)
}

const getRecordActual = (record) => {
  const actual = toNumber(record?.actual_total)
  const details = Array.isArray(record?.cost_details) ? record.cost_details : []
  const detailSum = details.reduce((sum, item) => sum + toNumber(item?.detail_amount), 0)
  if (actual === 0 && detailSum > 0) return detailSum
  return actual
}

const getLatestCostDate = (record) => {
  const details = Array.isArray(record?.cost_details) ? record.cost_details : []
  const dates = details
    .map((item) => formatDate(item?.detail_date))
    .filter(Boolean)
    .sort((a, b) => String(b).localeCompare(String(a), 'zh'))
  return dates[0] || '--'
}

const currentUserTokens = computed(() =>
  new Set(
    [
      userParam.value,
      userProfile.value.user_id,
      userProfile.value.account,
      userProfile.value.name
    ]
      .map(normalizeToken)
      .filter(Boolean)
  )
)

const hasCurrentUserInRole = (members) => {
  if (!currentUserTokens.value.size) return false
  return members.some((member) =>
    extractUserTokens(member).some((token) => currentUserTokens.value.has(token))
  )
}

const canRecordActualCost = computed(() => !hasCurrentUserInRole(noActualEntryRoleMembers.value))

const panelHint = computed(() =>
  canRecordActualCost.value
    ? '可直接查看详情、录入实际成本、编辑本人负责节点'
    : '可直接查看详情、编辑本人负责节点'
)

const userOptions = computed(() =>
  users.value
    .map((item) => {
      const value = getMemberId(item)
      const label = getMemberLabel(item)
      if (!value) return null
      return { value, label: label || value }
    })
    .filter(Boolean)
)

const ensureUserOption = (value) => {
  const memberId = getMemberId(value)
  if (!memberId || users.value.some((item) => getMemberId(item) === memberId)) return
  users.value = [
    ...users.value,
    {
      user_id: memberId,
      name: getMemberLabel(value) || memberId
    }
  ]
}

const isResponsibleRecord = (record) => {
  if (!currentUserTokens.value.size) return false
  return extractUserTokens(record?.responsible_person).some((token) => currentUserTokens.value.has(token))
}

const myResponsibleRecords = computed(() =>
  allBudgetRecords.value
    .filter((record) => isResponsibleRecord(record))
    .sort((left, right) => {
      const codeCompare = normalizeLabel(left?.project_code).localeCompare(normalizeLabel(right?.project_code), 'zh')
      if (codeCompare !== 0) return codeCompare
      const nameCompare = normalizeLabel(left?.project_name).localeCompare(normalizeLabel(right?.project_name), 'zh')
      if (nameCompare !== 0) return nameCompare
      const mainCompare = compareOrderValue(
        normalizeOrderValue(left?.main_stage_order),
        normalizeOrderValue(right?.main_stage_order)
      )
      if (mainCompare !== 0) return mainCompare
      const stageCompare = compareOrderValue(
        normalizeOrderValue(left?.project_stage_order),
        normalizeOrderValue(right?.project_stage_order)
      )
      if (stageCompare !== 0) return stageCompare
      const centerCompare = normalizeLabel(left?.cost_center).localeCompare(normalizeLabel(right?.cost_center), 'zh')
      if (centerCompare !== 0) return centerCompare
      return normalizeLabel(left?.cost_item).localeCompare(normalizeLabel(right?.cost_item), 'zh')
    })
)

const filteredRows = computed(() => {
  const search = normalizeLabel(keyword.value).toLowerCase()
  return myResponsibleRecords.value
    .map((record) => {
      const budgetStandard = toNumber(record?.budget_standard)
      const actualTotal = getRecordActual(record)
      const status = resolveBudgetStatus(actualTotal, budgetStandard)
      const rawPercentage =
        budgetStandard > 0 ? Math.round((actualTotal / budgetStandard) * 100) : actualTotal > 0 ? 100 : 0
      const displayPercentage = Math.max(0, rawPercentage)
      const percentage = Math.min(100, displayPercentage)
      return {
        rawRecord: record,
        recordId: String(record?._id || record?.id || ''),
        projectCode: normalizeLabel(record?.project_code),
        projectName: normalizeLabel(record?.project_name),
        projectType: normalizeLabel(record?.project_type),
        centerName: normalizeLabel(record?.cost_center),
        itemName: normalizeLabel(record?.cost_item),
        responsibleName: getMemberLabel(record?.responsible_person) || '--',
        budgetStandard,
        actualTotal,
        diff: actualTotal - budgetStandard,
        percentage,
        displayPercentage,
        progressColor: status === '超支' ? '#f56c6c' : '#409eff',
        status,
        tagType: status === '超支' ? 'danger' : 'success',
        latestCostDate: getLatestCostDate(record)
      }
    })
    .filter((row) => {
      if (statusFilter.value && row.status !== statusFilter.value) return false
      if (!search) return true
      return [
        row.projectCode,
        row.projectName,
        row.projectType,
        row.centerName,
        row.itemName,
        row.responsibleName
      ]
        .join(' ')
        .toLowerCase()
        .includes(search)
    })
})

const summary = computed(() => {
  const projectKeys = new Set()
  let totalBudget = 0
  let totalActual = 0
  let overrunCount = 0

  filteredRows.value.forEach((row) => {
    projectKeys.add(`${row.projectCode}||${row.projectName}`)
    totalBudget += row.budgetStandard
    totalActual += row.actualTotal
    if (row.status === '超支') overrunCount += 1
  })

  return {
    projectCount: projectKeys.size,
    recordCount: filteredRows.value.length,
    totalBudget,
    totalActual,
    overrunCount
  }
})

const formDialogWidth = computed(() => (isMobile.value ? '92%' : '520px'))
const detailDialogWidth = computed(() => (isMobile.value ? '94%' : '760px'))

const syncViewport = () => {
  isMobile.value = typeof window !== 'undefined' ? window.innerWidth <= 768 : false
}

const loadUsers = async () => {
  if (userLoading.value) return
  userLoading.value = true
  try {
    const result = await api.listUsers()
    if (result?.code === 200 && Array.isArray(result.data)) {
      users.value = result.data
    } else {
      users.value = []
    }
  } catch (error) {
    console.error('加载成员失败：', error)
    users.value = []
  } finally {
    userLoading.value = false
  }
}

const loadNoActualEntryRoleMembers = async () => {
  try {
    const result = await api.listRoleMembers(BUDGET_NO_ACTUAL_ENTRY_ROLE_ID)
    noActualEntryRoleMembers.value =
      result?.code === 200 && Array.isArray(result.data) ? result.data : []
  } catch (error) {
    console.error('加载实际成本录入受限角色失败：', error)
    noActualEntryRoleMembers.value = []
  }
}

const resolveCurrentUserProfile = async () => {
  if (!userParam.value) return
  try {
    const result = await api.getUserInfo(userParam.value)
    if (result?.code === 200 && result.data) {
      userProfile.value = {
        user_id: result.data.user_id || result.data._id || result.data.id || userParam.value,
        name: result.data.name || result.data.username || '',
        account: result.data.account || ''
      }
      return
    }
  } catch (error) {
    console.warn('责任人页面用户信息查询失败，尝试成员列表匹配。', error)
  }

  const match = users.value.find(
    (item) =>
      isSameUserToken(item.user_id, userParam.value) ||
      isSameUserToken(item.account, userParam.value) ||
      isSameUserToken(item.name, userParam.value) ||
      isSameUserToken(item.uniqueid, userParam.value)
  )
  if (match) {
    userProfile.value = {
      user_id: match.user_id || userParam.value,
      name: match.name || '',
      account: match.account || ''
    }
  }
}

const syncCurrentUser = async () => {
  const nextUserId = resolveWebpageUserId(route)
  if (nextUserId === userParam.value) return
  userParam.value = nextUserId
  userProfile.value = {
    user_id: '',
    name: '',
    account: ''
  }
  await resolveCurrentUserProfile()
}

const loadBudgetRecords = async () => {
  loading.value = true
  try {
    const pageSize = 300
    let skip = 0
    const records = []
    while (true) {
      const result = await api.listProjectBudgets({ skip, limit: pageSize })
      if (result?.code !== 200 || !Array.isArray(result.data)) {
        throw new Error(result?.msg || '加载预算数据失败')
      }
      records.push(...result.data)
      if (result.data.length < pageSize) break
      skip += pageSize
      if (skip > 3000) break
    }
    allBudgetRecords.value = records
  } catch (error) {
    console.error('加载预算数据失败：', error)
    allBudgetRecords.value = []
    ElMessage.error(error.message || '加载预算数据失败')
  } finally {
    loading.value = false
  }
}

const extractDetailHistory = (record) => {
  const details = Array.isArray(record?.cost_details) ? [...record.cost_details] : []
  return details
    .map((detail) => ({
      date: formatDate(detail?.detail_date),
      costType: normalizeCostType(detail?.cost_type) || '未分类',
      item: detail?.detail_item || normalizeLabel(record?.cost_item),
      amount: toNumber(detail?.detail_amount),
      remark: normalizeLabel(detail?.detail_remark)
    }))
    .sort((left, right) => String(right.date).localeCompare(String(left.date), 'zh'))
}

const handleViewDetails = (row) => {
  currentDetailRow.value = row
  detailHistoryRows.value = extractDetailHistory(row.rawRecord)
  detailsDialogVisible.value = true
}

const resetEditForm = () => {
  editForm.projectName = ''
  editForm.centerName = ''
  editForm.costItem = ''
  editForm.responsiblePersonId = ''
  editForm.budgetStandard = ''
}

const openEditDialog = (row) => {
  currentEditRecord.value = row?.rawRecord || null
  if (!currentEditRecord.value) {
    ElMessage.warning('未找到当前节点数据')
    return
  }
  ensureUserOption(currentEditRecord.value.responsible_person)
  editForm.projectName = row.projectName
  editForm.centerName = row.centerName
  editForm.costItem = row.itemName
  editForm.responsiblePersonId = getMemberId(currentEditRecord.value.responsible_person)
  editForm.budgetStandard = String(toNumber(currentEditRecord.value.budget_standard))
  editDialogVisible.value = true
}

const submitEdit = async () => {
  if (!currentEditRecord.value?._id && !currentEditRecord.value?.id) {
    ElMessage.warning('未找到可编辑节点')
    return
  }
  const budgetStandard = toNumber(editForm.budgetStandard)
  if (budgetStandard < 0) {
    ElMessage.warning('预算标准不能小于0')
    return
  }
  editSubmitting.value = true
  try {
    const actualTotal = getRecordActual(currentEditRecord.value)
    const result = await api.updateProjectBudget(String(currentEditRecord.value._id || currentEditRecord.value.id), {
      responsible_person: editForm.responsiblePersonId || '',
      budget_standard: budgetStandard,
      status: resolveBudgetStatus(actualTotal, budgetStandard)
    })
    if (result?.code !== 200) {
      ElMessage.error(result?.msg || '保存失败')
      return
    }
    ElMessage.success('节点已更新')
    editDialogVisible.value = false
    resetEditForm()
    currentEditRecord.value = null
    await loadBudgetRecords()
  } catch (error) {
    console.error('保存节点失败：', error)
    ElMessage.error('保存节点失败')
  } finally {
    editSubmitting.value = false
  }
}

const resetEntryForm = () => {
  entryForm.projectName = ''
  entryForm.centerName = ''
  entryForm.costItem = ''
  entryForm.costType = ''
  entryForm.amount = ''
  entryForm.remark = ''
}

const openEntryDialog = (row) => {
  if (!canRecordActualCost.value) {
    ElMessage.warning('当前角色无权录入实际成本')
    return
  }
  currentEntryRecord.value = row?.rawRecord || null
  if (!currentEntryRecord.value) {
    ElMessage.warning('未找到当前节点数据')
    return
  }
  resetEntryForm()
  entryForm.projectName = row.projectName
  entryForm.centerName = row.centerName
  entryForm.costItem = row.itemName
  entryDialogVisible.value = true
}

const submitEntry = async () => {
  if (!canRecordActualCost.value) {
    ElMessage.warning('当前角色无权录入实际成本')
    return
  }
  if (!currentEntryRecord.value?._id && !currentEntryRecord.value?.id) {
    ElMessage.warning('未找到可录入节点')
    return
  }
  if (!entryForm.costType) {
    ElMessage.warning('请选择费用类型')
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

  entrySubmitting.value = true
  try {
    const currentDetails = Array.isArray(currentEntryRecord.value.cost_details)
      ? [...currentEntryRecord.value.cost_details]
      : []
    currentDetails.push({
      detail_date: formatDateTime(new Date()),
      detail_item: entryForm.costItem,
      detail_amount: amount,
      detail_remark: entryForm.remark || '',
      cost_type: entryForm.costType
    })
    const nextActual = getRecordActual(currentEntryRecord.value) + amount
    const budgetStandard = toNumber(currentEntryRecord.value.budget_standard)
    const result = await api.updateProjectBudget(String(currentEntryRecord.value._id || currentEntryRecord.value.id), {
      actual_total: nextActual,
      cost_details: currentDetails,
      status: resolveBudgetStatus(nextActual, budgetStandard)
    })
    if (result?.code !== 200) {
      ElMessage.error(result?.msg || '录入成本失败')
      return
    }
    ElMessage.success('成本录入成功')
    entryDialogVisible.value = false
    resetEntryForm()
    currentEntryRecord.value = null
    await loadBudgetRecords()
  } catch (error) {
    console.error('录入成本失败：', error)
    ElMessage.error('录入成本失败')
  } finally {
    entrySubmitting.value = false
  }
}

watch(
  () => route.fullPath,
  async () => {
    await syncCurrentUser()
  }
)

onMounted(async () => {
  syncViewport()
  await Promise.all([loadUsers(), loadNoActualEntryRoleMembers()])
  await syncCurrentUser()
  await loadBudgetRecords()
  window.addEventListener('resize', syncViewport)
})

onUnmounted(() => {
  window.removeEventListener('resize', syncViewport)
})
</script>

<style scoped>
.my-budget-page {
  min-height: 100vh;
  background: #f0f2f5;
  color: #303133;
}

.main-content {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  height: 64px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px;
  z-index: 10;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 16px;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
}

.header-subtitle {
  font-size: 13px;
  color: #909399;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.page-container {
  padding: 8px 4px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  overflow: auto;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.summary-card {
  background: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.summary-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.summary-extra {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}

.content-panel {
  background: #fff;
  border-radius: 4px;
  padding: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;
}

.panel-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.panel-hint {
  font-size: 12px;
  color: #909399;
}

.mobile-records {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mobile-record-card {
  border: 1px solid #ebeef5;
  border-radius: 10px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mobile-record-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.mobile-record-title {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
}

.mobile-record-code {
  margin-top: -4px;
  font-size: 12px;
  color: #909399;
}

.mobile-record-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 12px;
}

.mobile-record-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mobile-label {
  font-size: 12px;
  color: #909399;
}

.mobile-value {
  font-size: 13px;
  line-height: 1.5;
  color: #303133;
  word-break: break-all;
}

.mobile-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.table-actions {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}

.detail-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 16px;
}

.detail-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.detail-value {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.text-success {
  color: #67c23a;
}

.text-danger {
  color: #f56c6c;
}

:deep(.el-table th) {
  background-color: #f5f7fa !important;
}

@media (max-width: 1400px) {
  .summary-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .header {
    height: auto;
    padding: 12px 8px;
    align-items: flex-start;
    flex-direction: column;
  }

  .header-left,
  .header-actions,
  .panel-toolbar {
    width: 100%;
  }

  .summary-grid,
  .detail-summary {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 8px;
  }

  .header-left {
    flex-direction: column;
    gap: 6px;
    align-items: flex-start;
  }

  .header-actions :deep(.el-input),
  .header-actions :deep(.el-select),
  .header-actions :deep(.el-button) {
    width: 100% !important;
  }

  .summary-card {
    padding: 16px;
  }

  .content-panel {
    padding: 12px;
  }

  .mobile-record-grid {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }

  .mobile-actions {
    justify-content: flex-start;
  }
}
</style>
