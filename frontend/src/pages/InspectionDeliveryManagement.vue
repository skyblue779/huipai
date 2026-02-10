<template>
  <el-config-provider :locale="zhCn">
    <div class="dashboard-container">
    <div class="main-content">
      <div class="page-container" v-loading="loading">
        <div class="filter-bar">
          <div class="filter-left">
            <span class="page-title">样品检测交付管理</span>
            <div class="divider"></div>
            <div class="filter-inputs">
              <el-input v-model="filters.deliveryNo" placeholder="发货单号" clearable style="width: 160px;" />
              <el-input v-model="filters.projectName" placeholder="项目名称" clearable style="width: 160px;" />
              <el-input v-model="filters.handoverStatus" placeholder="交付状态" clearable style="width: 140px;" />
            </div>
          </div>
          <div class="filter-right">
            <el-button type="primary" plain @click="loadRecords">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </div>
        </div>

        <div class="dashboard-grid">
          <div class="dashboard-card">
            <div class="card-header">
              <div class="card-icon is-primary">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="card-label">交付记录总数</div>
            </div>
            <div class="card-value accent-blue">{{ kpiStats.total }}</div>
          </div>
          <div class="dashboard-card">
            <div class="card-header">
              <div class="card-icon is-success">
                <el-icon><Check /></el-icon>
              </div>
              <div class="card-label">已签收</div>
            </div>
            <div class="card-value accent-success">{{ kpiStats.signed }}</div>
          </div>
          <div class="dashboard-card">
            <div class="card-header">
              <div class="card-icon is-danger">
                <el-icon><WarningFilled /></el-icon>
              </div>
              <div class="card-label">异常</div>
            </div>
            <div class="card-value accent-danger">{{ kpiStats.abnormal }}</div>
          </div>
          <div class="dashboard-card">
            <div class="card-header">
              <div class="card-icon is-warning">
                <el-icon><Bell /></el-icon>
              </div>
              <div class="card-label">待处理</div>
            </div>
            <div class="card-value accent-warning">{{ kpiStats.pending }}</div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header">
            <div class="panel-title">交付记录列表</div>
          </div>
          <el-table :data="records" border stripe style="width: 100%" row-key="_id">
            <el-table-column type="expand">
              <template #default="scope">
                <div class="subform-wrapper">
                  <div class="subform-title">货物信息</div>
                  <el-table
                    :data="normalizeList(scope.row.cargo_items)"
                    size="small"
                    border
                    style="width: 100%; background-color: #fafafa;"
                  >
                    <el-table-column prop="product_name" label="产品名称" min-width="160" />
                    <el-table-column prop="spec_model" label="规格型号" min-width="140" />
                    <el-table-column prop="quantity" label="数量" width="100" align="right" />
                    <el-table-column prop="unit" label="单位" width="80" />
                  </el-table>
                </div>
                <div class="subform-wrapper" style="margin-top: 12px;">
                  <div class="subform-title">检测信息</div>
                  <el-table
                    :data="normalizeList(scope.row.inspection_info)"
                    size="small"
                    border
                    style="width: 100%; background-color: #fafafa;"
                  >
                    <el-table-column prop="inspection_project" label="检测项目" min-width="180" />
                    <el-table-column label="检测人员" min-width="140">
                      <template #default="row">
                        {{ formatUser(row.row.inspector) }}
                      </template>
                    </el-table-column>
                    <el-table-column prop="inspection_status" label="检测状态" min-width="120" />
                    <el-table-column prop="description" label="说明" min-width="160" />
                  </el-table>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="handover_no" label="交付单号" min-width="140" />
            <el-table-column prop="delivery_no" label="发货单号" min-width="140" />
            <el-table-column prop="project_name" label="项目名称" min-width="160" show-overflow-tooltip />
            <el-table-column prop="delivery_date" label="发货日期" min-width="120">
              <template #default="scope">{{ formatDate(scope.row.delivery_date) }}</template>
            </el-table-column>
            <el-table-column prop="delivery_address" label="收货地址" min-width="200" show-overflow-tooltip />
            <el-table-column prop="order_no" label="订单编号" min-width="140" />
            <el-table-column prop="handover_date" label="交付日期" min-width="120">
              <template #default="scope">{{ formatDate(scope.row.handover_date) }}</template>
            </el-table-column>
            <el-table-column prop="handover_status" label="交付状态" min-width="100">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.handover_status)">
                  {{ scope.row.handover_status || '-' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="receiver_customer" label="接收客户" min-width="140" />
            <el-table-column prop="abnormal_reason" label="异常原因" min-width="160" show-overflow-tooltip />
            <el-table-column prop="remark" label="备注" min-width="160" show-overflow-tooltip />
            <el-table-column prop="handover_person" label="交付人员" min-width="120">
              <template #default="scope">{{ formatUser(scope.row.handover_person) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="160" align="center" fixed="right">
              <template #default="scope">
                <el-button link type="primary" size="small" @click="openDetail(scope.row)">详情</el-button>
                <el-button
                  link
                  type="primary"
                  size="small"
                  @click="openDeliver(scope.row)"
                >
                  交付
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 详情弹窗 -->
        <el-dialog v-model="detailDialogVisible" title="交付详情" width="760px" align-center>
          <el-form label-width="90px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="交付单号">
                  <el-input :model-value="detailRecord.handover_no" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="发货单号">
                  <el-input :model-value="detailRecord.delivery_no" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="项目名称">
                  <el-input :model-value="detailRecord.project_name" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="订单编号">
                  <el-input :model-value="detailRecord.order_no" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="发货日期">
                  <el-input :model-value="formatDate(detailRecord.delivery_date)" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="交付日期">
                  <el-input :model-value="formatDate(detailRecord.handover_date)" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="收货地址">
                  <el-input :model-value="detailRecord.delivery_address" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="接收客户">
                  <el-input :model-value="detailRecord.receiver_customer" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="交付人员">
                  <el-input :model-value="formatUser(detailRecord.handover_person)" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="交付状态">
                  <el-tag :type="getStatusType(detailRecord.handover_status)">
                    {{ detailRecord.handover_status || '-' }}
                  </el-tag>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="异常原因">
                  <el-input :model-value="detailRecord.abnormal_reason" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="备注">
                  <el-input :model-value="detailRecord.remark" type="textarea" :rows="2" disabled />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
          <div class="subform-wrapper">
            <div class="subform-title">货物信息</div>
            <el-table
              :data="normalizeList(detailRecord.cargo_items)"
              size="small"
              border
              style="width: 100%; background-color: #fafafa;"
            >
              <el-table-column prop="product_name" label="产品名称" min-width="160" />
              <el-table-column prop="spec_model" label="规格型号" min-width="140" />
              <el-table-column prop="quantity" label="数量" width="100" align="right" />
              <el-table-column prop="unit" label="单位" width="80" />
            </el-table>
          </div>
          <div class="subform-wrapper" style="margin-top: 12px;">
            <div class="subform-title">检测信息</div>
            <el-table
              :data="normalizeList(detailRecord.inspection_info)"
              size="small"
              border
              style="width: 100%; background-color: #fafafa;"
            >
              <el-table-column prop="inspection_project" label="检测项目" min-width="180" />
              <el-table-column label="检测人员" min-width="140">
                <template #default="row">
                  {{ formatUser(row.row.inspector) }}
                </template>
              </el-table-column>
              <el-table-column prop="inspection_status" label="检测状态" min-width="120" />
              <el-table-column prop="description" label="说明" min-width="160" />
            </el-table>
          </div>
          <template #footer>
            <div class="dialog-footer">
              <el-button @click="detailDialogVisible = false">关闭</el-button>
            </div>
          </template>
        </el-dialog>

        <!-- 交付弹窗 -->
        <el-dialog v-model="deliverDialogVisible" title="交付信息" width="560px" align-center>
          <el-form label-width="90px">
            <el-form-item label="接收客户">
              <el-input v-model="deliverForm.receiver_customer" placeholder="请输入接收客户" />
            </el-form-item>
            <el-form-item label="交付日期">
              <el-date-picker
                v-model="deliverForm.handover_date"
                type="datetime"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%;"
              />
            </el-form-item>
            <el-form-item label="交付状态">
              <el-select v-model="deliverForm.handover_status" placeholder="请选择交付状态" style="width: 100%;">
                <el-option label="已签收" value="已签收" />
                <el-option label="异常" value="异常" />
              </el-select>
            </el-form-item>
            <el-form-item label="异常原因" v-if="deliverForm.handover_status === '异常'">
              <el-input v-model="deliverForm.abnormal_reason" type="textarea" :rows="2" placeholder="请输入异常原因" />
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="deliverForm.remark" type="textarea" :rows="2" placeholder="备注信息" />
            </el-form-item>
            <el-form-item label="交付人员">
              <el-select
                v-model="deliverForm.handover_person"
                filterable
                placeholder="请选择交付人员"
                style="width: 100%;"
              >
                <el-option
                  v-for="item in userOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-form>
          <template #footer>
            <div class="dialog-footer">
              <el-button @click="deliverDialogVisible = false">取消</el-button>
              <el-button type="primary" :loading="deliverLoading" @click="submitDeliver">提交</el-button>
            </div>
          </template>
        </el-dialog>
      </div>
    </div>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElConfigProvider } from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { TrendCharts, Check, WarningFilled, Bell } from '@element-plus/icons-vue';
import api from '../api/client';

const loading = ref(false);
const records = ref([]);
const userOptions = ref([]);
const userNameMap = ref({});
const detailDialogVisible = ref(false);
const detailRecord = ref({});
const deliverDialogVisible = ref(false);
const deliverLoading = ref(false);
const deliverForm = reactive({
  receiver_customer: '',
  handover_date: '',
  handover_status: '已签收',
  abnormal_reason: '',
  remark: '',
  handover_person: ''
});
const currentDeliverId = ref('');

const filters = reactive({
  deliveryNo: '',
  projectName: '',
  handoverStatus: ''
});

const normalizeList = (items) => (Array.isArray(items) ? items : []);

const formatDate = (value) => {
  if (!value) return '';
  if (value instanceof Date) {
    const year = value.getFullYear();
    const month = String(value.getMonth() + 1).padStart(2, '0');
    const day = String(value.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
  const parsed = new Date(String(value).replace(/-/g, '/'));
  if (!Number.isNaN(parsed.getTime())) {
    return formatDate(parsed);
  }
  return String(value);
};

const formatUser = (value) => {
  if (!value) return '';
  if (Array.isArray(value)) {
    return value.map((item) => item?.name || item?._id || '').filter(Boolean).join('、');
  }
  if (typeof value === 'object') {
    return value.name || value._id || '';
  }
  const key = String(value);
  return userNameMap.value[key] || key;
};

const getStatusType = (status) => {
  if (status === '已签收') return 'success';
  if (status === '异常') return 'danger';
  return 'info';
};

const kpiStats = computed(() => {
  const total = records.value.length;
  const signed = records.value.filter((item) => item.handover_status === '已签收').length;
  const abnormal = records.value.filter((item) => item.handover_status === '异常').length;
  const pending = records.value.filter((item) => !item.handover_status || item.handover_status === '待处理').length;
  return { total, signed, abnormal, pending };
});

const openDetail = (row) => {
  detailRecord.value = { ...(row || {}) };
  detailDialogVisible.value = true;
};

const resetDeliverForm = () => {
  deliverForm.receiver_customer = '';
  deliverForm.handover_date = '';
  deliverForm.handover_status = '已签收';
  deliverForm.abnormal_reason = '';
  deliverForm.remark = '';
  deliverForm.handover_person = '';
};

const openDeliver = (row) => {
  currentDeliverId.value = row?._id || '';
  resetDeliverForm();
  deliverForm.receiver_customer = row?.receiver_customer || '';
  deliverForm.handover_date = row?.handover_date || '';
  deliverForm.handover_status = row?.handover_status || '已签收';
  deliverForm.abnormal_reason = row?.abnormal_reason || '';
  deliverForm.remark = row?.remark || '';
  if (row?.handover_person && typeof row.handover_person === 'object') {
    deliverForm.handover_person = row.handover_person.user_id || row.handover_person._id || row.handover_person.id || '';
  } else {
    deliverForm.handover_person = row?.handover_person || '';
  }
  deliverDialogVisible.value = true;
};

const submitDeliver = async () => {
  if (!currentDeliverId.value) {
    ElMessage.warning('缺少记录ID，无法更新');
    return;
  }
  if (!deliverForm.receiver_customer) {
    ElMessage.warning('请填写接收客户');
    return;
  }
  if (!deliverForm.handover_date) {
    ElMessage.warning('请选择交付日期');
    return;
  }
  if (!deliverForm.handover_status) {
    ElMessage.warning('请选择交付状态');
    return;
  }
  if (deliverForm.handover_status === '异常' && !deliverForm.abnormal_reason) {
    ElMessage.warning('请填写异常原因');
    return;
  }
  deliverLoading.value = true;
  try {
    const payload = {
      receiver_customer: deliverForm.receiver_customer,
      handover_date: deliverForm.handover_date,
      handover_status: deliverForm.handover_status,
      abnormal_reason: deliverForm.handover_status === '异常' ? deliverForm.abnormal_reason : '',
      remark: deliverForm.remark,
      handover_person: deliverForm.handover_person
    };
    const result = await api.updateInspectionDelivery(currentDeliverId.value, payload);
    if (result?.code === 200) {
      ElMessage.success('交付信息已更新');
      deliverDialogVisible.value = false;
      loadRecords();
    } else {
      ElMessage.error(result?.msg || '更新失败');
    }
  } catch (error) {
    console.error('更新交付失败：', error);
    ElMessage.error('更新失败');
  } finally {
    deliverLoading.value = false;
  }
};

const buildUserOptions = (users) => {
  const options = [];
  const map = {};
  users.forEach((user) => {
    if (!user || typeof user !== 'object') return;
    const id = user.user_id || user._id || user.id;
    if (!id) return;
    const name = user.name || user.real_name || user.account || id;
    options.push({ label: name, value: id });
    map[String(id)] = name;
  });
  return { options, map };
};

const loadUsers = async () => {
  try {
    const result = await api.listUsers();
    if (result?.code === 200 && Array.isArray(result.data)) {
      const { options, map } = buildUserOptions(result.data);
      userOptions.value = options;
      userNameMap.value = map;
    } else {
      userOptions.value = [];
      userNameMap.value = {};
    }
  } catch (error) {
    console.error('加载交付人员失败：', error);
    userOptions.value = [];
    userNameMap.value = {};
  }
};

const loadRecords = async () => {
  loading.value = true;
  try {
    const result = await api.listInspectionDeliveries({
      skip: 0,
      limit: 300,
      deliveryNo: filters.deliveryNo,
      projectName: filters.projectName,
      handoverStatus: filters.handoverStatus
    });
    if (result?.code === 200 && Array.isArray(result.data)) {
      records.value = result.data;
    } else {
      records.value = [];
      ElMessage.error(result?.msg || '加载交付数据失败');
    }
  } catch (error) {
    console.error('加载交付数据失败：', error);
    records.value = [];
    ElMessage.error('加载交付数据失败');
  } finally {
    loading.value = false;
  }
};

const resetFilters = () => {
  filters.deliveryNo = '';
  filters.projectName = '';
  filters.handoverStatus = '';
  loadRecords();
};

onMounted(() => {
  loadRecords();
  loadUsers();
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
  max-width: 1920px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.filter-bar {
  background: #fff;
  padding: 16px 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
  flex-wrap: wrap;
  gap: 16px;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
}

.divider {
  width: 1px;
  height: 20px;
  background-color: #dcdfe6;
  margin: 0 8px;
}

.filter-inputs {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-right {
  display: flex;
  gap: 12px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.dashboard-card {
  background: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.card-icon.is-primary {
  background: rgba(24, 144, 255, 0.12);
  color: #1890ff;
}

.card-icon.is-success {
  background: rgba(82, 196, 26, 0.12);
  color: #52c41a;
}

.card-icon.is-warning {
  background: rgba(250, 140, 22, 0.14);
  color: #fa8c16;
}

.card-icon.is-danger {
  background: rgba(245, 34, 45, 0.12);
  color: #f5222d;
}

.card-label {
  color: #909399;
  font-size: 14px;
}

.card-value {
  font-size: 26px;
  font-weight: bold;
}

.accent-blue {
  color: #1890ff;
}

.accent-success {
  color: #52c41a;
}

.accent-warning {
  color: #fa8c16;
}

.accent-danger {
  color: #f5222d;
}

.panel {
  background: #fff;
  border-radius: 4px;
  padding: 16px;
  box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  flex: 1;
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

.subform-wrapper {
  padding: 12px 16px;
  background: #fafafa;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.subform-title {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
  margin-bottom: 8px;
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-left, .filter-inputs, .filter-right {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }
  .filter-inputs .el-input {
    width: 100% !important;
  }
  .divider {
    display: none;
  }
}
</style>
