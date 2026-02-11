<template>
  <el-config-provider :locale="zhCn">
    <div class="dashboard-container">
    <div class="main-content">
      <div class="page-container" v-loading="loading">
        <!-- 顶部筛选栏 -->
        <div class="filter-bar">
          <div class="filter-left">
            <!-- <span class="page-title">发货管理</span> -->
            <!-- <div class="divider"></div> -->
            <!-- 筛选条件组 -->
            <div class="filter-inputs">
              <el-input v-model="filters.deliveryNo" placeholder="发货单号" clearable style="width: 160px;" />
              <el-input v-model="filters.projectName" placeholder="项目名称" clearable style="width: 160px;" />
              <el-input v-model="filters.orderNo" placeholder="订单编号" clearable style="width: 160px;" />
              <el-select v-model="filters.status" placeholder="状态" clearable style="width: 120px;">
                <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </div>
          </div>
          <div class="filter-right">
            <el-button type="primary" plain @click="loadDeliveries">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
            <el-button type="primary" @click="openCreateDialog">新增发货</el-button>
          </div>
        </div>

        <!-- 核心 KPI 指标卡 -->
        <div class="dashboard-grid">
          <div class="kpi-card">
            <div class="kpi-title">发货单总数</div>
            <div class="kpi-value">{{ kpiStats.total }}</div>
            <div class="kpi-footer">
              <span>全部记录</span>
              <span class="text-primary">100%</span>
            </div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">运输中</div>
            <div class="kpi-value text-primary">{{ kpiStats.pending }}</div>
            <div class="kpi-footer">
              <span>当前在途</span>
              <el-tag size="small" effect="plain">监控中</el-tag>
            </div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">异常状态</div>
            <div class="kpi-value text-danger">{{ kpiStats.inTransit }}</div>
            <div class="kpi-footer">
              <span>需处理异常</span>
              <span class="text-danger" v-if="kpiStats.inTransit > 0">请关注</span>
              <span class="text-success" v-else>正常</span>
            </div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">已签收</div>
            <div class="kpi-value text-success">{{ kpiStats.signed }}</div>
            <div class="kpi-footer">
              <span>累计完成</span>
              <el-icon class="text-success"><Select /></el-icon>
            </div>
          </div>
        </div>

        <!-- 表格面板 -->
        <div class="panel">
          <div class="panel-header">
            <div class="panel-title">发货记录列表</div>
          </div>
          <el-table :data="records" border stripe style="width: 100%" row-key="_id">
            <el-table-column type="expand">
              <template #default="scope">
                <div class="subform-wrapper">
                  <div class="subform-title">货物明细</div>
                  <el-table
                    :data="normalizeCargo(scope.row.cargo_items)"
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
              </template>
            </el-table-column>
            <el-table-column prop="delivery_no" label="发货单号" min-width="140" />
            <el-table-column prop="project_name" label="项目名称" min-width="160" show-overflow-tooltip />
            <el-table-column prop="delivery_date" label="发货日期" min-width="120">
              <template #default="scope">{{ formatDate(scope.row.delivery_date) }}</template>
            </el-table-column>
            <el-table-column prop="order_no" label="订单编号" min-width="140" />
            <el-table-column prop="delivery_address" label="收货地址" min-width="200" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
               <template #default="scope">
                  <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
               </template>
            </el-table-column>
            <el-table-column prop="logistics_company" label="物流公司" min-width="120" />
            <el-table-column prop="logistics_no" label="物流单号" min-width="140" />
            <el-table-column label="操作" width="200" align="center" fixed="right">
              <template #default="scope">
                <el-button type="primary" link size="small" @click="openDetail(scope.row)">详情</el-button>
                <el-button
                  type="primary"
                  link
                  size="small"
                  :disabled="scope.row.status === '已签收'"
                  @click="handleSign(scope.row)"
                >
                  确认到货
                </el-button>
                <el-button
                  type="danger"
                  link
                  size="small"
                  :disabled="scope.row.status !== '异常'"
                  @click="openException(scope.row)"
                >
                  处理异常
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 异常处理弹窗 -->
        <el-dialog v-model="exceptionDialogVisible" title="异常处理" width="480px" align-center>
          <el-form :model="exceptionForm" label-width="90px">
            <el-form-item label="处理状态">
              <el-select v-model="exceptionForm.status" placeholder="请选择处理状态" style="width: 100%;">
                <el-option v-for="item in exceptionStatusOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
            <el-form-item label="备注说明">
              <el-input v-model="exceptionForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
            </el-form-item>
          </el-form>
          <template #footer>
            <div class="dialog-footer">
              <el-button @click="exceptionDialogVisible = false">取消</el-button>
              <el-button type="primary" :loading="exceptionLoading" @click="submitException">提交</el-button>
            </div>
          </template>
        </el-dialog>

        <!-- 新增弹窗 -->
        <el-dialog v-model="createDialogVisible" title="新增发货" width="800px" align-center>
          <el-form :model="createForm" label-width="90px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="发货单号">
                  <el-input v-model="createForm.delivery_no" readonly placeholder="系统自动生成" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="项目名称">
                  <el-select
                    v-model="createForm.project_name"
                    filterable
                    placeholder="请选择项目"
                    style="width: 100%;"
                  >
                    <el-option
                      v-for="item in projectOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="发货日期">
                  <el-date-picker v-model="createForm.delivery_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="订单编号">
                  <el-input v-model="createForm.order_no" placeholder="请输入订单编号" />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="收货地址">
                  <el-input v-model="createForm.delivery_address" placeholder="请输入收货地址" />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="检测项目">
                  <el-select
                    v-model="createForm.inspection_items"
                    filterable
                    multiple
                    placeholder="请选择检测项目"
                    style="width: 100%;"
                  >
                    <el-option
                      v-for="item in inspectionOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="物流公司">
                  <el-input v-model="createForm.logistics_company" placeholder="请输入物流公司" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="物流单号">
                  <el-input v-model="createForm.logistics_no" placeholder="请输入物流单号" />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="备注">
                  <el-input v-model="createForm.remark" type="textarea" :rows="2" placeholder="备注信息" />
                </el-form-item>
              </el-col>
            </el-row>

            <div class="subform-wrapper">
              <div class="subform-header">
                  <span class="subform-title">货物信息</span>
                  <el-button type="primary" link @click="addCargoItem">
                      <el-icon><Plus /></el-icon> 新增一行
                  </el-button>
              </div>
              <el-table :data="createForm.cargo_items" size="small" border style="width: 100%;">
                <el-table-column label="产品名称">
                  <template #default="scope">
                    <el-input v-model="scope.row.product_name" placeholder="名称" />
                  </template>
                </el-table-column>
                <el-table-column label="规格型号">
                  <template #default="scope">
                    <el-input v-model="scope.row.spec_model" placeholder="规格" />
                  </template>
                </el-table-column>
                <el-table-column label="数量" width="120">
                  <template #default="scope">
                    <el-input-number v-model="scope.row.quantity" :min="0" controls-position="right" style="width: 100%;" />
                  </template>
                </el-table-column>
                <el-table-column label="单位" width="100">
                  <template #default="scope">
                    <el-input v-model="scope.row.unit" placeholder="单位" />
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="60" align="center">
                  <template #default="scope">
                    <el-button type="danger" link @click="removeCargoItem(scope.$index)">
                        <el-icon><Delete /></el-icon>
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-form>
          <template #footer>
            <div class="dialog-footer">
              <el-button @click="createDialogVisible = false">取消</el-button>
              <el-button type="primary" :loading="createLoading" @click="submitCreate">提交</el-button>
            </div>
          </template>
        </el-dialog>

        <!-- 详情弹窗 -->
        <el-dialog v-model="detailDialogVisible" title="发货详情" width="720px" align-center>
          <el-form label-width="90px">
            <el-row :gutter="20">
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
                <el-form-item label="发货日期">
                  <el-input :model-value="formatDate(detailRecord.delivery_date)" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="订单编号">
                  <el-input :model-value="detailRecord.order_no" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="收货地址">
                  <el-input :model-value="detailRecord.delivery_address" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="检测项目">
                  <el-input :model-value="formatList(detailRecord.inspection_items)" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="物流公司">
                  <el-input :model-value="detailRecord.logistics_company" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="物流单号">
                  <el-input :model-value="detailRecord.logistics_no" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="状态">
                  <el-input :model-value="detailRecord.status" disabled />
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
            <div class="subform-title">货物明细</div>
            <el-table
              :data="normalizeCargo(detailRecord.cargo_items)"
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
          <template #footer>
            <div class="dialog-footer">
              <el-button @click="detailDialogVisible = false">关闭</el-button>
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
import { ElMessage, ElMessageBox, ElConfigProvider } from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { Plus, Delete, Select } from '@element-plus/icons-vue';
// 假设您有这个 api 文件，保持原样引入
import api from '../api/client';

const loading = ref(false);
const records = ref([]);
const projectOptions = ref([]);
const inspectionOptions = ref([]);
const statusOptions = ref([ '运输中', '已签收', '异常', '退货', '重新发货']);
const createDialogVisible = ref(false);
const createLoading = ref(false);
const detailDialogVisible = ref(false);
const detailRecord = ref({});
const exceptionDialogVisible = ref(false);
const exceptionLoading = ref(false);
const exceptionForm = reactive({
  status: '',
  remark: ''
});
const exceptionStatusOptions = ref(['退货', '重新发货']);
const currentExceptionId = ref('');

const filters = reactive({
  deliveryNo: '',
  projectName: '',
  orderNo: '',
  status: ''
});

const createForm = reactive({
  delivery_no: '',
  project_name: '',
  delivery_date: '',
  order_no: '',
  delivery_address: '',
  inspection_items: [],
  status: '运输中',
  logistics_company: '',
  logistics_no: '',
  remark: '',
  cargo_items: [
    {
      product_name: '',
      spec_model: '',
      quantity: 0,
      unit: ''
    }
  ]
});

const getStatusType = (status) => {
    switch(status) {
        case '已签收': return 'success';
        case '异常': return 'danger';
        case '退货': return 'primary';
        case '重新发货': return 'primary';
        case '运输中': return 'primary';
        default: return 'warning';
    }
};

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

const formatList = (value) => {
  if (Array.isArray(value)) return value.join('、');
  if (value === null || value === undefined) return '';
  return String(value);
};

const normalizeCargo = (items) => (Array.isArray(items) ? items : []);

const buildProjectOptions = (projects) => {
  const map = new Map();
  projects.forEach((project) => {
    const code = project?.project_code ? String(project.project_code).trim() : '';
    const name = project?.project_name ? String(project.project_name).trim() : '';
    if (!code && !name) return;
    const label = code ? `${code} - ${name || '未命名项目'}` : (name || '未命名项目');
    const value = name || label;
    if (!map.has(value)) {
      map.set(value, { label, value });
    }
  });
  return Array.from(map.values());
};

const buildInspectionOptions = (items) => {
  const map = new Map();
  items.forEach((item) => {
    const name = item?.inspection_project ? String(item.inspection_project).trim() : '';
    const code = item?.inspection_no ? String(item.inspection_no).trim() : '';
    const label = name || code;
    if (!label) return;
    const value = name || label;
    if (!map.has(value)) {
      map.set(value, { label, value });
    }
  });
  return Array.from(map.values());
};

const loadProjects = async () => {
  try {
    const result = await api.listProjectSummary({ skip: 0, limit: 300 });
    if (result?.code === 200 && Array.isArray(result.data)) {
      projectOptions.value = buildProjectOptions(result.data);
    } else {
      projectOptions.value = [];
    }
  } catch (error) {
    console.error('加载项目列表失败：', error);
    projectOptions.value = [];
  }
};

const loadInspections = async () => {
  try {
    const result = await api.listInspections({ skip: 0, limit: 300 });
    if (result?.code === 200 && Array.isArray(result.data)) {
      inspectionOptions.value = buildInspectionOptions(result.data);
    } else {
      inspectionOptions.value = [];
    }
  } catch (error) {
    console.error('加载检测项目失败：', error);
    inspectionOptions.value = [];
  }
};

const kpiStats = computed(() => {
  const total = records.value.length;
  const pending = records.value.filter((item) => item.status === '运输中').length;
  const inTransit = records.value.filter((item) => item.status === '异常').length;
  const signed = records.value.filter((item) => item.status === '已签收').length;
  return { total, pending, inTransit, signed };
});

const resetCreateForm = () => {
  Object.assign(createForm, {
    delivery_no: '',
    project_name: '',
    delivery_date: '',
    order_no: '',
    delivery_address: '',
    inspection_items: [],
    status: '运输中',
    logistics_company: '',
    logistics_no: '',
    remark: '',
    cargo_items: [{ product_name: '', spec_model: '', quantity: 0, unit: '' }]
  });
};

const openCreateDialog = () => {
  resetCreateForm();
  createDialogVisible.value = true;
};

const openDetail = (row) => {
  detailRecord.value = { ...(row || {}) };
  detailDialogVisible.value = true;
};

const addCargoItem = () => {
  createForm.cargo_items.push({
    product_name: '',
    spec_model: '',
    quantity: 0,
    unit: ''
  });
};

const removeCargoItem = (index) => {
  if (createForm.cargo_items.length <= 1) {
    createForm.cargo_items = [
      { product_name: '', spec_model: '', quantity: 0, unit: '' }
    ];
    return;
  }
  createForm.cargo_items.splice(index, 1);
};

const submitCreate = async () => {
  // if (!createForm.delivery_no) {
  //   ElMessage.warning('请填写发货单号');
  //   return;
  // }
  if (!createForm.project_name) {
    ElMessage.warning('请填写项目名称');
    return;
  }
  createLoading.value = true;
  try {
    const inspectionItems = Array.isArray(createForm.inspection_items)
      ? createForm.inspection_items
      : (createForm.inspection_items ? [createForm.inspection_items] : []);
    const payload = {
      ...createForm,
      inspection_items: inspectionItems,
      cargo_items: createForm.cargo_items.filter((item) =>
        item.product_name || item.spec_model || item.quantity || item.unit
      )
    };
    const result = await api.createDelivery(payload);
    if (result?.code === 200) {
      ElMessage.success('新增成功');
      createDialogVisible.value = false;
      loadDeliveries();
    } else {
      ElMessage.error(result?.msg || '新增失败');
    }
  } catch (error) {
    console.error('新增发货失败：', error);
    ElMessage.error('新增失败');
  } finally {
    createLoading.value = false;
  }
};

const handleSign = async (row) => {
  if (!row?._id) {
    ElMessage.warning('缺少记录ID，无法更新状态');
    return;
  }
  try {
    await ElMessageBox.confirm('确认订单是否到货？该操作不可撤销。', '确认到货', {
      type: 'warning',
      confirmButtonText: '确认签收',
      cancelButtonText: '取消'
    });
    const result = await api.updateDelivery(row._id, { status: '已签收' });
    if (result?.code === 200) {
      ElMessage.success('状态已更新为已签收');
      loadDeliveries();
    } else {
      ElMessage.error(result?.msg || '更新状态失败');
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('更新状态失败：', error);
      ElMessage.error('更新状态失败');
    }
  }
};

const openException = (row) => {
  if (!row?._id) {
    ElMessage.warning('缺少记录ID，无法处理异常');
    return;
  }
  currentExceptionId.value = row._id;
  exceptionForm.status = '';
  exceptionForm.remark = row?.remark || '';
  exceptionDialogVisible.value = true;
};

const submitException = async () => {
  if (!currentExceptionId.value) {
    ElMessage.warning('缺少记录ID，无法提交');
    return;
  }
  if (!exceptionForm.status) {
    ElMessage.warning('请选择处理状态');
    return;
  }
  exceptionLoading.value = true;
  try {
    const payload = {
      status: exceptionForm.status,
      remark: exceptionForm.remark || ''
    };
    const result = await api.updateDelivery(currentExceptionId.value, payload);
    if (result?.code === 200) {
      ElMessage.success('异常处理已更新');
      exceptionDialogVisible.value = false;
      loadDeliveries();
    } else {
      ElMessage.error(result?.msg || '异常处理失败');
    }
  } catch (error) {
    console.error('异常处理失败：', error);
    ElMessage.error('异常处理失败');
  } finally {
    exceptionLoading.value = false;
  }
};

const loadDeliveries = async () => {
  loading.value = true;
  try {
    const result = await api.listDeliveries({
      skip: 0,
      limit: 300,
      deliveryNo: filters.deliveryNo,
      projectName: filters.projectName,
      orderNo: filters.orderNo,
      status: filters.status
    });
    if (result?.code === 200 && Array.isArray(result.data)) {
      records.value = result.data;
    } else {
      records.value = [];
      ElMessage.error(result?.msg || '加载发货数据失败');
    }
  } catch (error) {
    console.error('加载发货数据失败：', error);
    records.value = [];
    ElMessage.error('加载发货数据失败');
  } finally {
    loading.value = false;
  }
};

const resetFilters = () => {
  filters.deliveryNo = '';
  filters.projectName = '';
  filters.orderNo = '';
  filters.status = '';
  loadDeliveries();
};

onMounted(() => {
  loadDeliveries();
  loadProjects();
  loadInspections();
});
</script>

<style scoped>
/* 核心布局容器 */
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
  padding: 0px;
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

/* 顶部筛选栏 */
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

/* KPI 网格 */
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
  display: flex;
  flex-direction: column;
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
  align-items: center;
  position: relative;
  z-index: 1;
}

/* 内容面板 */
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

/* 表格内嵌子表单样式 */
.subform-wrapper {
  padding: 12px 16px;
  background: #fafafa;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.subform-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.subform-title {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

/* 文本颜色工具类 */
.text-danger { color: #F56C6C; }
.text-warning { color: #E6A23C; }
.text-success { color: #67C23A; }
.text-primary { color: #409EFF; }

/* 响应式适配 */
@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
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
  .filter-inputs .el-input,
  .filter-inputs .el-select {
    width: 100% !important;
  }
  .divider {
    display: none;
  }
}
</style>
