<template>
  <el-config-provider :locale="zhCn">
    <div class="mobile-page">
      <div class="mobile-header">
        <div class="header-title">检测信息填报</div>
        <div class="header-controls">
          <el-select
            v-model="currentProject"
            filterable
            clearable
            placeholder="请选择项目"
            style="width: 100%;"
            @change="loadRecords"
          >
            <el-option
              v-for="option in projectOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
          <div class="search-row">
            <el-input v-model="filters.deliveryNo" placeholder="发货单号" clearable />
            <el-button type="primary" @click="loadRecords">查询</el-button>
          </div>
        </div>
      </div>

      <div class="mobile-body" v-loading="loading">
        <el-empty v-if="!displayRecords.length" description="暂无检测信息"></el-empty>
        <div v-else class="card-list">
          <div class="record-card" v-for="record in displayRecords" :key="record._id + '-' + record._inspection_index">
            <div class="card-top">
              <div>
                <div class="card-title">{{ record.project_name || '未命名项目' }}</div>
                <div class="card-subtitle">{{ record.inspection_project || '未填写检测项目' }}</div>
              </div>
              <el-tag size="small" :type="getStatusType(record.handover_status || '未处理')">
                {{ record.handover_status || '未处理' }}
              </el-tag>
            </div>
            <div class="card-info">
              <div class="info-row">
                <span class="info-label">发货单号</span>
                <span class="info-value">{{ record.delivery_no || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">交付单号</span>
                <span class="info-value">{{ record.handover_no || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">收货地址</span>
                <span class="info-value">{{ record.delivery_address || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">检测项目</span>
                <span class="info-value">{{ record.inspection_project || '未填写检测项目' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">检测状态</span>
                <span class="info-value">
                  <el-tag size="small" :type="getInspectionStatusTagType(record.inspection_status)">
                    {{ record.inspection_status || '未填写' }}
                  </el-tag>
                </span>
              </div>
              <div class="info-row">
                <span class="info-label">填报状态</span>
                <span class="info-value">
                  <el-tag size="small" :type="record.reported ? 'success' : 'warning'">
                    {{ record.reported ? '已填报' : '未填报' }}
                  </el-tag>
                </span>
              </div>
            </div>
            <div class="card-actions">
              <el-button type="primary" size="small" @click="openEdit(record)">填报检测</el-button>
            </div>
          </div>
        </div>
      </div>

      <el-dialog
        v-model="editDialogVisible"
        title="检测信息填报"
        width="100%"
        align-center
        :fullscreen="true"
        class="mobile-dialog"
      >
        <div class="dialog-header">
          <div>项目：{{ currentRecord.project_name || '-' }}</div>
          <div>发货单号：{{ currentRecord.delivery_no || '-' }}</div>
        </div>
        <div class="dialog-content">
          <el-empty v-if="!editInspectionInfo.length" description="暂无检测项目"></el-empty>
          <el-card
            v-for="(item, index) in editInspectionInfo"
            :key="index"
            class="inspection-card"
            shadow="never"
          >
            <div class="inspection-title">检测项目 {{ index + 1 }}</div>
            <el-form label-width="78px">
              <el-form-item label="项目">
                <el-input v-model="item.inspection_project" disabled />
              </el-form-item>
              <el-form-item label="检测人员">
                <el-select
                  v-model="item.inspector"
                  filterable
                  placeholder="请选择检测人员"
                  style="width: 100%;"
                >
                  <el-option
                    v-for="user in userOptions"
                    :key="user.value"
                    :label="user.label"
                    :value="user.value"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="检测状态">
                <el-select
                  v-model="item.inspection_status"
                  filterable
                  allow-create
                  default-first-option
                  placeholder="请选择或输入状态"
                  style="width: 100%;"
                >
                  <el-option
                    v-for="status in inspectionStatusOptions"
                    :key="status"
                    :label="status"
                    :value="status"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="说明">
                <el-input
                  v-model="item.description"
                  type="textarea"
                  :rows="2"
                  placeholder="填写说明"
                />
              </el-form-item>
            </el-form>
          </el-card>
        </div>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" :loading="saveLoading" @click="submitInspection">提交</el-button>
          </div>
        </template>
      </el-dialog>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElConfigProvider } from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import api from '../api/client';

const loading = ref(false);
const saveLoading = ref(false);
const records = ref([]);
const projectOptions = ref([]);
const currentProject = ref('');
const userOptions = ref([]);
const editDialogVisible = ref(false);
const currentRecord = ref({});
const currentInspectionIndex = ref(-1);
const fullInspectionInfo = ref([]);
const editInspectionInfo = ref([]);

const filters = reactive({
  deliveryNo: ''
});

const normalizeList = (items) => (Array.isArray(items) ? items : []);

const flattenRecords = (items) => {
  const list = [];
  normalizeList(items).forEach((record) => {
    const inspections = normalizeList(record?.inspection_info);
    if (inspections.length) {
      inspections.forEach((inspection, index) => {
        const inspectorValue = normalizeInspectorValue(inspection?.inspector);
        const statusValue = inspection?.inspection_status || '';
        const descValue = inspection?.description || '';
        const reported = Boolean(inspectorValue || statusValue || descValue);
        list.push({
          ...record,
          inspection_project: inspection?.inspection_project || '',
          inspection_status: statusValue,
          inspection_inspector: inspectorValue,
          inspection_description: descValue,
          reported,
          inspection_item: inspection || {},
          _inspection_index: index
        });
      });
    } else {
      list.push({
        ...record,
        inspection_project: '',
        inspection_status: '',
        inspection_inspector: '',
        inspection_description: '',
        reported: false,
        inspection_item: null,
        _inspection_index: -1
      });
    }
  });
  return list;
};

const displayRecords = computed(() => {
  const list = flattenRecords(records.value);
  return list.sort((a, b) => {
    const aReported = a.reported ? 1 : 0;
    const bReported = b.reported ? 1 : 0;
    if (aReported !== bReported) return aReported - bReported;
    return 0;
  });
});

const getInspectionStatusTagType = (status) => {
  if (status === '合格') return 'success';
  if (status === '不合格') return 'danger';
  if (status) return 'warning';
  return 'info';
};

const getStatusType = (status) => {
  if (status === '已签收') return 'success';
  if (status === '异常') return 'danger';
  return 'info';
};

const normalizeInspectorValue = (value) => {
  if (!value) return '';
  if (Array.isArray(value)) {
    return normalizeInspectorValue(value[0]);
  }
  if (typeof value === 'object') {
    return value.user_id || value._id || value.id || '';
  }
  return String(value);
};

const normalizeInspectionInfo = (items) =>
  normalizeList(items).map((item) => ({
    inspection_project: item?.inspection_project || '',
    inspector: normalizeInspectorValue(item?.inspector),
    inspection_status: item?.inspection_status || '',
    description: item?.description || ''
  }));

const inspectionStatusOptions = computed(() => {
  const base = ['待检测', '合格', '不合格'];
  const set = new Set(base);
  records.value.forEach((record) => {
    normalizeList(record.inspection_info).forEach((item) => {
      if (item?.inspection_status) {
        set.add(item.inspection_status);
      }
    });
  });
  return Array.from(set);
});

const buildUserOptions = (items) =>
  normalizeList(items)
    .map((item) => {
      const id = item?.id || item?._id || item?.user_id;
      const name = item?.name || item?.nickname || item?.realname;
      if (!id || !name) return null;
      return { value: id, label: name };
    })
    .filter(Boolean);

const loadProjects = async () => {
  try {
    const result = await api.listProjectSummary({ skip: 0, limit: 300 });
    if (result?.code === 200 && Array.isArray(result.data)) {
      projectOptions.value = result.data.map((item) => {
        const label = item.project_code
          ? `${item.project_code} - ${item.project_name || '未命名项目'}`
          : (item.project_name || '未命名项目');
        return { label, value: item.project_name || '' };
      }).filter((item) => item.value);
    } else {
      projectOptions.value = [];
    }
  } catch (error) {
    console.error('加载项目失败：', error);
    projectOptions.value = [];
  }
};

const loadUsers = async () => {
  try {
    const result = await api.listUsers();
    if (result?.code === 200 && Array.isArray(result.data)) {
      userOptions.value = buildUserOptions(result.data);
    } else {
      userOptions.value = [];
    }
  } catch (error) {
    console.error('加载检测人员失败：', error);
    userOptions.value = [];
  }
};

const loadRecords = async () => {
  loading.value = true;
  try {
    const result = await api.listInspectionDeliveries({
      skip: 0,
      limit: 300,
      deliveryNo: filters.deliveryNo,
      projectName: currentProject.value || ''
    });
    if (result?.code === 200 && Array.isArray(result.data)) {
      records.value = result.data;
    } else {
      records.value = [];
      ElMessage.error(result?.msg || '加载检测信息失败');
    }
  } catch (error) {
    console.error('加载检测信息失败：', error);
    records.value = [];
    ElMessage.error('加载检测信息失败');
  } finally {
    loading.value = false;
  }
};

const openEdit = (record) => {
  currentRecord.value = record || {};
  const sourceList = normalizeInspectionInfo(record?.inspection_info);
  fullInspectionInfo.value = sourceList;
  if (typeof record?._inspection_index === 'number' && record._inspection_index >= 0) {
    currentInspectionIndex.value = record._inspection_index;
    editInspectionInfo.value = [
      sourceList[record._inspection_index] || {
        inspection_project: record?.inspection_project || '',
        inspector: '',
        inspection_status: '',
        description: ''
      }
    ];
  } else {
    currentInspectionIndex.value = -1;
    editInspectionInfo.value = [{
      inspection_project: record?.inspection_project || '',
      inspector: '',
      inspection_status: '',
      description: ''
    }];
  }
  editDialogVisible.value = true;
};

const submitInspection = async () => {
  if (!currentRecord.value?._id) {
    ElMessage.warning('缺少记录ID，无法提交');
    return;
  }
  saveLoading.value = true;
  try {
    const currentItem = editInspectionInfo.value[0] || {};
    const merged = Array.isArray(fullInspectionInfo.value) ? [...fullInspectionInfo.value] : [];
    if (currentInspectionIndex.value >= 0 && currentInspectionIndex.value < merged.length) {
      merged[currentInspectionIndex.value] = { ...merged[currentInspectionIndex.value], ...currentItem };
    } else {
      merged.push(currentItem);
    }
    const payload = {
      inspection_info: merged
    };
    const result = await api.updateInspectionDelivery(currentRecord.value._id, payload);
    if (result?.code === 200) {
      ElMessage.success('检测信息已提交');
      editDialogVisible.value = false;
      loadRecords();
    } else {
      ElMessage.error(result?.msg || '提交失败');
    }
  } catch (error) {
    console.error('提交检测信息失败：', error);
    ElMessage.error('提交失败');
  } finally {
    saveLoading.value = false;
  }
};

onMounted(() => {
  loadProjects();
  loadUsers();
  loadRecords();
});
</script>

<style scoped>
.mobile-page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.mobile-header {
  padding: 16px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-row {
  display: flex;
  gap: 8px;
}

.mobile-body {
  flex: 1;
  padding: 16px;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.card-subtitle {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;
  color: #606266;
}

.info-label {
  color: #909399;
  flex-shrink: 0;
}

.info-value {
  text-align: right;
  word-break: break-all;
}

.card-actions {
  margin-top: 12px;
  text-align: right;
}

.mobile-dialog :deep(.el-dialog__body) {
  padding: 16px;
}

.dialog-header {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.inspection-card {
  border-radius: 10px;
  border: 1px solid #ebeef5;
}

.inspection-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
