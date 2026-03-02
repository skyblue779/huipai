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
            <el-button plain @click="openPrintTemplateDrawer">打印模板配置</el-button>
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
            <el-table-column label="操作" width="240" align="center" fixed="right">
              <template #default="scope">
                <el-button type="primary" link size="small" @click="openDetail(scope.row)">详情</el-button>
                <el-button type="primary" link size="small" @click="printRecord(scope.row)">打印</el-button>
                <el-button
                  type="primary"
                  link
                  size="small"
                  :disabled="scope.row.status === '已签收'"
                  @click="handleSign(scope.row)"
                >
                  确认到货
                </el-button>
                <!-- <el-button
                  type="danger"
                  link
                  size="small"
                  :disabled="scope.row.status !== '异常'"
                  @click="openException(scope.row)"
                >
                  处理异常
                </el-button> -->
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

        <!-- 打印模板侧边栏 -->
        <el-drawer
          v-model="printTemplateDrawerVisible"
          title="打印模板配置"
          size="520px"
          direction="rtl"
        >
          <div class="print-setting">
            <div class="print-setting-title">选择打印字段</div>
            <el-checkbox-group v-model="printTemplateDraft" class="print-setting-group">
              <el-checkbox v-for="item in printFieldOptions" :key="item.value" :label="item.value">
                {{ item.label }}
              </el-checkbox>
            </el-checkbox-group>
          </div>
          <div class="print-preview">
            <div class="print-preview-title">打印预览</div>
            <div class="print-preview-scale">
              <div class="ticket-sheet">
                <div class="ticket-header">
                  <div class="ticket-title">发货票据</div>
                  <div class="ticket-no">票据编号：{{ previewData.delivery_no || '-' }}</div>
                </div>

                <div class="ticket-meta">
                  <div class="ticket-row" v-if="hasTemplateField('project_name')">
                    <span class="ticket-label">项目名称</span>
                    <span class="ticket-value">{{ previewData.project_name || '-' }}</span>
                  </div>
                  <div class="ticket-row" v-if="hasTemplateField('delivery_date')">
                    <span class="ticket-label">发货日期</span>
                    <span class="ticket-value">{{ formatDate(previewData.delivery_date) || '-' }}</span>
                  </div>
                  <div class="ticket-row" v-if="hasTemplateField('order_no')">
                    <span class="ticket-label">订单编号</span>
                    <span class="ticket-value">{{ previewData.order_no || '-' }}</span>
                  </div>
                  <div class="ticket-row" v-if="hasTemplateField('logistics')">
                    <span class="ticket-label">物流公司</span>
                    <span class="ticket-value">{{ previewData.logistics_company || '-' }}</span>
                  </div>
                  <div class="ticket-row" v-if="hasTemplateField('logistics')">
                    <span class="ticket-label">物流单号</span>
                    <span class="ticket-value">{{ previewData.logistics_no || '-' }}</span>
                  </div>
                  <div class="ticket-row">
                    <span class="ticket-label">状态</span>
                    <span class="ticket-value">{{ previewData.status || '-' }}</span>
                  </div>
                  <div class="ticket-row ticket-row--full" v-if="hasTemplateField('delivery_address')">
                    <span class="ticket-label">收货地址</span>
                    <span class="ticket-value">{{ previewData.delivery_address || '-' }}</span>
                  </div>
                </div>

                <div class="ticket-divider"></div>

                <template v-if="hasTemplateField('cargo_items')">
                  <div class="ticket-section-title">货物明细</div>
                  <table class="ticket-table">
                    <thead>
                      <tr>
                        <th style="width: 48px;">序号</th>
                        <th>产品名称</th>
                        <th>规格型号</th>
                        <th style="width: 80px;">数量</th>
                        <th style="width: 80px;">单位</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(item, index) in normalizeCargo(previewData.cargo_items)" :key="index">
                        <td class="text-center">{{ index + 1 }}</td>
                        <td>{{ item.product_name || '-' }}</td>
                        <td>{{ item.spec_model || '-' }}</td>
                        <td class="text-right">{{ item.quantity ?? '-' }}</td>
                        <td class="text-center">{{ item.unit || '-' }}</td>
                      </tr>
                      <tr v-if="normalizeCargo(previewData.cargo_items).length === 0">
                        <td colspan="5" class="text-center">暂无货物明细</td>
                      </tr>
                    </tbody>
                  </table>
                  <div class="ticket-divider"></div>
                </template>

                <div class="ticket-footer">
                  <div class="ticket-footer-row" v-if="hasTemplateField('remark')">
                    <span class="ticket-label">备注</span>
                    <span class="ticket-value">{{ previewData.remark || '-' }}</span>
                  </div>
                  <div class="ticket-footer-row">
                    <span class="ticket-label">打印时间</span>
                    <span class="ticket-value">{{ formatDateTime(previewData.print_time) || '-' }}</span>
                  </div>
                  <div class="ticket-sign">
                    <div>发货人签字：__________</div>
                    <div>收货人签字：__________</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="drawer-footer">
            <el-button @click="resetPrintTemplate">恢复默认</el-button>
            <el-button type="primary" @click="savePrintTemplate">保存模板</el-button>
          </div>
        </el-drawer>
      </div>
    </div>

    <div id="printSection" class="print-area">
      <div class="ticket-sheet">
        <div class="ticket-header">
          <div class="ticket-title">发货票据</div>
          <div class="ticket-no">票据编号：{{ printData.delivery_no || '-' }}</div>
        </div>

        <div class="ticket-meta">
          <div class="ticket-row" v-if="hasPrintField('project_name')">
            <span class="ticket-label">项目名称</span>
            <span class="ticket-value">{{ printData.project_name || '-' }}</span>
          </div>
          <div class="ticket-row" v-if="hasPrintField('delivery_date')">
            <span class="ticket-label">发货日期</span>
            <span class="ticket-value">{{ formatDate(printData.delivery_date) || '-' }}</span>
          </div>
          <div class="ticket-row" v-if="hasPrintField('order_no')">
            <span class="ticket-label">订单编号</span>
            <span class="ticket-value">{{ printData.order_no || '-' }}</span>
          </div>
          <div class="ticket-row" v-if="hasPrintField('logistics')">
            <span class="ticket-label">物流公司</span>
            <span class="ticket-value">{{ printData.logistics_company || '-' }}</span>
          </div>
          <div class="ticket-row" v-if="hasPrintField('logistics')">
            <span class="ticket-label">物流单号</span>
            <span class="ticket-value">{{ printData.logistics_no || '-' }}</span>
          </div>
          <div class="ticket-row">
            <span class="ticket-label">状态</span>
            <span class="ticket-value">{{ printData.status || '-' }}</span>
          </div>
          <div class="ticket-row ticket-row--full" v-if="hasPrintField('delivery_address')">
            <span class="ticket-label">收货地址</span>
            <span class="ticket-value">{{ printData.delivery_address || '-' }}</span>
          </div>
        </div>

        <div class="ticket-divider"></div>

        <template v-if="hasPrintField('cargo_items')">
          <div class="ticket-section-title">货物明细</div>
          <table class="ticket-table">
            <thead>
              <tr>
                <th style="width: 48px;">序号</th>
                <th>产品名称</th>
                <th>规格型号</th>
                <th style="width: 80px;">数量</th>
                <th style="width: 80px;">单位</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in normalizeCargo(printData.cargo_items)" :key="index">
                <td class="text-center">{{ index + 1 }}</td>
                <td>{{ item.product_name || '-' }}</td>
                <td>{{ item.spec_model || '-' }}</td>
                <td class="text-right">{{ item.quantity ?? '-' }}</td>
                <td class="text-center">{{ item.unit || '-' }}</td>
              </tr>
              <tr v-if="normalizeCargo(printData.cargo_items).length === 0">
                <td colspan="5" class="text-center">暂无货物明细</td>
              </tr>
            </tbody>
          </table>
          <div class="ticket-divider"></div>
        </template>

        <div class="ticket-footer">
          <div class="ticket-footer-row" v-if="hasPrintField('remark')">
            <span class="ticket-label">备注</span>
            <span class="ticket-value">{{ printData.remark || '-' }}</span>
          </div>
          <div class="ticket-footer-row">
            <span class="ticket-label">打印时间</span>
            <span class="ticket-value">{{ formatDateTime(printData.print_time) || '-' }}</span>
          </div>
          <div class="ticket-sign">
            <div>发货人签字：__________</div>
            <div>收货人签字：__________</div>
          </div>
        </div>
      </div>
    </div>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue';
import { ElMessage, ElMessageBox, ElConfigProvider } from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { Plus, Delete, Select } from '@element-plus/icons-vue';
// 假设您有这个 api 文件，保持原样引入
import api from '../api/client';

const loading = ref(false);
const records = ref([]);
const projectOptions = ref([]);
const statusOptions = ref([ '运输中', '已签收']);
const createDialogVisible = ref(false);
const createLoading = ref(false);
const detailDialogVisible = ref(false);
const detailRecord = ref({});
const printData = ref({});
const printTemplateDrawerVisible = ref(false);
const defaultPrintFields = [
  'project_name',
  'delivery_date',
  'order_no',
  'delivery_address',
  'logistics',
  'remark',
  'cargo_items'
];
const printFields = ref([...defaultPrintFields]);
const printTemplateDraft = ref([...defaultPrintFields]);
const printFieldOptions = ref([
  { label: '项目名称', value: 'project_name' },
  { label: '发货日期', value: 'delivery_date' },
  { label: '订单编号', value: 'order_no' },
  { label: '收货地址', value: 'delivery_address' },
  { label: '物流信息（物流公司+单号）', value: 'logistics' },
  { label: '备注', value: 'remark' },
  { label: '货物明细', value: 'cargo_items' }
]);
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

const formatDateTime = (value) => {
  if (!value) return '';
  if (value instanceof Date) {
    const year = value.getFullYear();
    const month = String(value.getMonth() + 1).padStart(2, '0');
    const day = String(value.getDate()).padStart(2, '0');
    const hour = String(value.getHours()).padStart(2, '0');
    const minute = String(value.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hour}:${minute}`;
  }
  const parsed = new Date(String(value).replace(/-/g, '/'));
  if (!Number.isNaN(parsed.getTime())) {
    return formatDateTime(parsed);
  }
  return String(value);
};

const normalizeCargo = (items) => (Array.isArray(items) ? items : []);
const hasPrintField = (key) => printFields.value.includes(key);
const hasTemplateField = (key) => printTemplateDraft.value.includes(key);
const printTemplateStorageKey = 'delivery_print_template_fields';
const previewTime = ref(new Date());
const previewData = computed(() => {
  const current = printData.value && Object.keys(printData.value).length > 0
    ? printData.value
    : (records.value[0] || {});
  return { ...(current || {}), print_time: previewTime.value };
});

const sanitizePrintFields = (fields) => {
  const allowSet = new Set(printFieldOptions.value.map((item) => item.value));
  return (Array.isArray(fields) ? fields : []).filter((item) => allowSet.has(item));
};

const loadPrintTemplate = () => {
  if (typeof window === 'undefined') return;
  const cached = window.localStorage.getItem(printTemplateStorageKey);
  if (!cached) return;
  try {
    const parsed = JSON.parse(cached);
    const sanitized = sanitizePrintFields(parsed);
    printFields.value = sanitized;
  } catch (error) {
    console.warn('读取打印模板配置失败：', error);
  }
};

const openPrintTemplateDrawer = () => {
  printTemplateDraft.value = [...printFields.value];
  previewTime.value = new Date();
  printTemplateDrawerVisible.value = true;
};

const savePrintTemplate = () => {
  printFields.value = sanitizePrintFields(printTemplateDraft.value);
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(
      printTemplateStorageKey,
      JSON.stringify(printFields.value)
    );
  }
  ElMessage.success('打印模板已保存');
  printTemplateDrawerVisible.value = false;
};

const resetPrintTemplate = () => {
  printTemplateDraft.value = [...defaultPrintFields];
};

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

const printRecord = async (row) => {
  if (!row) {
    ElMessage.warning('缺少记录，无法打印');
    return;
  }
  printData.value = { ...(row || {}), print_time: new Date() };
  await nextTick();
  window.print();
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
  loadPrintTemplate();
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
.text-center { text-align: center; }
.text-right { text-align: right; }

.print-setting {
  padding: 8px 4px;
}

.print-setting-title {
  font-weight: 600;
  margin-bottom: 12px;
}

.print-setting-group {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px 12px;
}

.print-preview {
  margin-top: 16px;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background: #fafafa;
}

.print-preview-title {
  font-weight: 600;
  margin-bottom: 8px;
}

.print-preview-scale {
  max-height: 520px;
  overflow: auto;
}

.print-preview-scale .ticket-sheet {
  margin: 0;
}

@supports (zoom: 1) {
  .print-preview-scale .ticket-sheet {
    zoom: 0.68;
  }
}

@supports not (zoom: 1) {
  .print-preview-scale .ticket-sheet {
    transform: scale(0.68);
    transform-origin: top left;
  }
}

.drawer-footer {
  margin-top: 16px;
  padding-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  border-top: 1px solid #ebeef5;
}

.print-area {
  display: none;
  background: #fff;
}

.ticket-sheet {
  width: 720px;
  margin: 0 auto;
  padding: 16px 20px 20px;
  color: #000;
  border: 1px solid #000;
  font-size: 12px;
  box-sizing: border-box;
}

.ticket-header {
  text-align: center;
  border-bottom: 1px dashed #000;
  padding-bottom: 10px;
  margin-bottom: 10px;
}

.ticket-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 6px;
}

.ticket-no {
  margin-top: 6px;
  font-weight: 600;
}

.ticket-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px 16px;
  margin-bottom: 10px;
}

.ticket-row {
  display: flex;
  gap: 8px;
  border-bottom: 1px dotted #000;
  padding-bottom: 2px;
}

.ticket-row--full {
  grid-column: 1 / -1;
}

.ticket-label {
  width: 72px;
  font-weight: 600;
  flex-shrink: 0;
}

.ticket-value {
  flex: 1;
  word-break: break-all;
}

.ticket-divider {
  border-top: 1px dashed #000;
  margin: 10px 0;
}

.ticket-section-title {
  font-weight: 600;
  margin-bottom: 6px;
}

.ticket-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 8px;
}

.ticket-table th,
.ticket-table td {
  border: 1px solid #000;
  padding: 6px 8px;
  font-size: 12px;
}

.ticket-footer {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ticket-footer-row {
  display: flex;
  gap: 8px;
}

.ticket-sign {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 8px;
}

@media print {
  :global(body) {
    margin: 0;
  }
  :global(body *) {
    visibility: hidden;
  }
  :global(#printSection),
  :global(#printSection *) {
    visibility: visible;
  }
  :global(#printSection) {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
  }
  .main-content {
    display: none !important;
  }
  .print-area {
    display: block !important;
  }
  .dashboard-container {
    background: #fff;
  }
}

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
