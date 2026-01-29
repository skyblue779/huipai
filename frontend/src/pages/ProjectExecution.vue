<template>
  <div class="main-content">
    <div class="page-container">
      <div class="execution-header">
        <div class="header-left">
          <div class="execution-title">项目执行管理</div>
          <div class="execution-subtitle">仅显示当前账号负责的执行阶段</div>
        </div>
        <div class="execution-actions">
          <el-input
            v-model="searchQuery"
            clearable
            placeholder="搜索项目/阶段/状态"
            style="width: 260px"
            @keyup.enter="handleSearch"
          />
          <el-button type="primary" :loading="loading" @click="handleSearch">查询</el-button>
        </div>
      </div>

      <el-alert
        v-if="!hasUserId"
        class="user-alert"
        type="warning"
        show-icon
        :closable="false"
        title="未获取到用户ID，无法限定执行阶段。请通过业务入口访问。"
      />

      <div class="summary-grid">
        <div class="summary-card">
          <div class="summary-icon is-primary">
            <el-icon><Bell /></el-icon>
          </div>
          <div class="summary-content">
            <div class="summary-label">待执行</div>
            <div class="summary-value accent-primary">{{ totalCount }}</div>
          </div>
        </div>
        <div class="summary-card">
          <div class="summary-icon is-warning">
            <el-icon><Flag /></el-icon>
          </div>
          <div class="summary-content">
            <div class="summary-label">未完成</div>
            <div class="summary-value accent-warning">{{ waitingCount }}</div>
          </div>
        </div>
        <div class="summary-card">
          <div class="summary-icon is-danger">
            <el-icon><WarningFilled /></el-icon>
          </div>
          <div class="summary-content">
            <div class="summary-label">超期</div>
            <div class="summary-value accent-danger">{{ overdueCount }}</div>
          </div>
        </div>
        <div class="summary-card">
          <div class="summary-icon is-neutral">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="summary-content">
            <div class="summary-label">总阶段</div>
            <div class="summary-value">{{ totalCount }}</div>
          </div>
        </div>
      </div>

      <div class="table-card desktop-only">
        <el-table
          :data="pagedRows"
          v-loading="loading"
          border
          stripe
          row-key="recordId"
          :empty-text="hasUserId ? '暂无可执行阶段' : '请通过业务入口访问'"
        >
          <el-table-column label="项目 / 执行阶段" min-width="280">
            <template #default="{ row }">
              <div class="project-cell">
                <div class="project-title">{{ row.projectLabel }}</div>
                <div class="project-stage">{{ row.stageLabel }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="计划时间" min-width="200" align="center">
            <template #default="{ row }">
              <span>{{ formatRange(row.planStart, row.planEnd) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="实际完成" width="140" align="center">
            <template #default="{ row }">
              <span>{{ row.actualFinish || '--' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusTag(row.status)" effect="dark">
                {{ row.status || '未完成' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="openDetailDialog(row)">详情</el-button>
              <el-button type="success" link @click="openSubmitDialog(row)">提交</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="mobile-only">
        <div v-if="!tableRows.length && !loading" class="empty-holder">
          <el-empty :description="hasUserId ? '暂无可执行阶段' : '请通过业务入口访问'" />
        </div>
        <div v-else class="mobile-group-list">
          <div v-for="group in mobileGroups" :key="group.key" class="mobile-group">
            <div class="mobile-group-header">
              <div class="mobile-group-title">{{ group.title }}</div>
              <div class="mobile-group-count">{{ group.rows.length }} 项</div>
            </div>
            <div class="mobile-card-list">
              <div v-for="row in group.rows" :key="row.recordId" class="mobile-card">
                <div class="mobile-card-header">
                  <div>
                    <div class="project-title">{{ row.projectLabel }}</div>
                    <div class="project-stage">{{ row.stageLabel }}</div>
                  </div>
                  <el-tag :type="getStatusTag(row.status)" effect="dark">
                    {{ row.status || '未完成' }}
                  </el-tag>
                </div>
                <div class="mobile-card-body">
                  <div class="mobile-info">
                    <span class="label">计划时间</span>
                    <span class="value">{{ formatRange(row.planStart, row.planEnd) }}</span>
                  </div>
                  <div class="mobile-info">
                    <span class="label">实际完成</span>
                    <span class="value">{{ row.actualFinish || '--' }}</span>
                  </div>
                  <div v-if="row.executorName" class="mobile-info">
                    <span class="label">负责人</span>
                    <span class="value">{{ row.executorName }}</span>
                  </div>
                </div>
                <div class="mobile-card-actions">
                  <el-button size="small" @click="openDetailDialog(row)">详情</el-button>
                  <el-button size="small" type="primary" @click="openSubmitDialog(row)">提交</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="totalCount > 0" class="pagination-row">
        <el-config-provider :locale="zhCn">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalCount"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
          />
        </el-config-provider>
      </div>
    </div>

    <el-dialog
      v-model="detailDialogVisible"
      title="执行详情"
      :width="dialogWidth"
      :fullscreen="isMobile"
      :class="{ 'mobile-dialog': isMobile }"
    >
      <div v-if="detailRow" class="detail-body">
        <el-descriptions :column="isMobile ? 1 : 2" border>
          <el-descriptions-item label="项目">{{ detailRow.projectLabel }}</el-descriptions-item>
          <el-descriptions-item label="执行阶段">{{ detailRow.stageLabel }}</el-descriptions-item>
          <el-descriptions-item label="计划开始">{{ detailRow.planStart || '--' }}</el-descriptions-item>
          <el-descriptions-item label="计划完成">{{ detailRow.planEnd || '--' }}</el-descriptions-item>
          <el-descriptions-item label="实际完成">{{ detailRow.actualFinish || '--' }}</el-descriptions-item>
          <el-descriptions-item label="当前状态">{{ detailRow.status || '未完成' }}</el-descriptions-item>
          <el-descriptions-item label="负责人">{{ detailRow.executorName || '--' }}</el-descriptions-item>
          <el-descriptions-item label="预警等级">{{ detailRow.warningLevel || '正常' }}</el-descriptions-item>
          <el-descriptions-item label="执行说明" :span="isMobile ? 1 : 2">
            {{ detailRow.executionNote || '--' }}
          </el-descriptions-item>
          <el-descriptions-item v-if="detailRow.overdueReason" label="超期原因" :span="isMobile ? 1 : 2">
            {{ detailRow.overdueReason }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-attachments">
          <div class="attachment-label">现场资料</div>
          <div class="attachment-list">
            <el-tag v-if="!detailAttachments.length" type="info">暂无附件</el-tag>
            <el-tag
              v-for="(item, index) in detailAttachments"
              :key="`att-${index}`"
              type="info"
              class="attachment-item"
            >
              {{ item }}
            </el-tag>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="detailDialogVisible = false">知道了</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="submitDialogVisible"
      title="执行提交"
      :width="dialogWidth"
      :fullscreen="isMobile"
      :class="{ 'mobile-dialog': isMobile }"
    >
      <el-form :label-width="isMobile ? '90px' : '110px'">
        <el-form-item label="实际完成时间">
          <el-date-picker
            v-model="submitForm.actualFinish"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="请选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="现场资料上传">
          <el-upload
            v-model:file-list="uploadFileList"
            action="#"
            multiple
            drag
            :auto-upload="false"
            :limit="5"
            :on-exceed="handleUploadExceed"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖拽到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="upload-tip">支持多文件上传，最多 5 个</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="执行情况说明">
          <el-input
            v-model="submitForm.executionNote"
            type="textarea"
            :rows="4"
            placeholder="请输入执行情况说明"
          />
        </el-form-item>
        <el-form-item v-if="submitIsOverdue" label="超期原因">
          <el-input
            v-model="submitForm.overdueReason"
            type="textarea"
            :rows="3"
            placeholder="请输入超期原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="submitDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确认提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { UploadFilled, Bell, Flag, WarningFilled, TrendCharts } from '@element-plus/icons-vue';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import api from '../api/client';

const searchQuery = ref('');
const loading = ref(false);
const progressRecords = ref([]);
const userParam = ref('');
const userProfile = ref({
  user_id: '',
  name: '',
  account: ''
});

const detailDialogVisible = ref(false);
const submitDialogVisible = ref(false);
const detailRow = ref(null);
const submitRow = ref(null);
const submitting = ref(false);
const isMobile = ref(false);

const submitForm = ref({
  actualFinish: '',
  executionNote: '',
  overdueReason: ''
});

const uploadFileList = ref([]);

const getQueryParam = (paramName) => {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(paramName);
};

const hasUserId = computed(() => Boolean(userParam.value));

const parseDateValue = (value) => {
  if (!value) return null;
  if (value instanceof Date) return value;
  if (typeof value === 'number') return new Date(value);
  if (typeof value === 'string') {
    const trimmed = value.trim();
    if (!trimmed) return null;
    const parsed = new Date(trimmed.replace(/-/g, '/'));
    if (!Number.isNaN(parsed.getTime())) return parsed;
  }
  return null;
};

const parseDateRange = (value) => {
  if (!value) return { start: null, end: null };
  if (Array.isArray(value)) {
    return {
      start: parseDateValue(value[0]),
      end: parseDateValue(value[1])
    };
  }
  if (typeof value === 'object') {
    const start = parseDateValue(value.start || value.begin || value.planStart);
    const end = parseDateValue(value.end || value.finish || value.planEnd);
    if (start || end) return { start, end };
  }
  if (typeof value === 'string') {
    const matches = value.match(
      /\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?/g
    );
    if (matches && matches.length >= 2) {
      return {
        start: parseDateValue(matches[0]),
        end: parseDateValue(matches[1])
      };
    }
  }
  const single = parseDateValue(value);
  return { start: single, end: null };
};

const formatDate = (value) => {
  if (!value) return '--';
  if (typeof value === 'string') {
    const match = value.match(/\d{4}[-/]\d{1,2}[-/]\d{1,2}/);
    return match ? match[0].replace(/\//g, '-') : value;
  }
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const formatDateCell = (value) => {
  if (!value) return '';
  return formatDate(value);
};

const formatUser = (value) => {
  if (!value) return '';
  if (Array.isArray(value)) {
    const names = value.map((item) => item?.name || item?._id || item).filter(Boolean);
    return names.length ? names.join(' / ') : '';
  }
  if (typeof value === 'object') {
    return value.name || value._id || '';
  }
  return String(value);
};

const getExecutorIds = (value) => {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value
      .map((item) => {
        if (!item) return '';
        if (typeof item === 'object') return item.user_id || item._id || item.id || '';
        return String(item);
      })
      .filter(Boolean)
      .map((id) => String(id));
  }
  if (typeof value === 'object') {
    return [value.user_id || value._id || value.id || ''].filter(Boolean).map((id) => String(id));
  }
  return [String(value)];
};

const normalizeToken = (value) => {
  if (value === null || value === undefined) return '';
  const text = String(value).trim();
  return text ? text.toLowerCase() : '';
};

const splitNameText = (value) => {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value.flatMap((item) => splitNameText(item));
  }
  if (typeof value === 'object') {
    return splitNameText(value.name || value.user_name || value.account || '');
  }
  return String(value)
    .split(/[\s,，、/;；|]+/)
    .map((item) => item.trim())
    .filter(Boolean);
};

const buildTokenSet = (values) => {
  const set = new Set();
  values.forEach((value) => {
    const token = normalizeToken(value);
    if (token) set.add(token);
  });
  return set;
};

const collectExecutorTokens = (executorRaw) => {
  const tokens = [];
  const walk = (value) => {
    if (!value) return;
    if (Array.isArray(value)) {
      value.forEach(walk);
      return;
    }
    if (typeof value === 'object') {
      tokens.push(value.user_id, value._id, value.id, value.name, value.account);
      return;
    }
    tokens.push(value);
  };
  walk(executorRaw);
  return buildTokenSet(tokens);
};

const collectExecutorNameTokens = (executorRaw) => buildTokenSet(splitNameText(executorRaw));

const userTokenSet = computed(() =>
  buildTokenSet([
    userParam.value,
    userProfile.value.user_id,
    userProfile.value.id,
    userProfile.value.name,
    userProfile.value.account
  ])
);

const userNameTokenSet = computed(() => buildTokenSet(splitNameText(userProfile.value.name || userParam.value)));

const normalizeLabel = (value) => {
  if (value === null || value === undefined) return '';
  if (typeof value === 'string') return value.trim();
  return String(value);
};

const normalizeRecord = (record, index) => {
  const planRange = parseDateRange(record.plan_time);
  const planStartDate = planRange.start || null;
  const planEndDate = planRange.end || null;
  const actualFinishDate = parseDateValue(record.actual_finish);

  const projectName = normalizeLabel(record.project_name) || '未命名项目';
  const projectCode = normalizeLabel(record.project_code);
  const projectLabel = projectCode ? `${projectName} (${projectCode})` : projectName;

  const mainStageLabel = normalizeLabel(record.main_stage || record.mainStage);
  const projectStageLabel = normalizeLabel(record.project_stage || record.projectStage || record.stage);
  const stageParts = [mainStageLabel, projectStageLabel].filter(Boolean);
  const stageLabel = stageParts.length ? stageParts.join(' / ') : `阶段${index + 1}`;

  return {
    recordId: record._id || `${index}`,
    status: record.status || '未完成',
    warningLevel: record.warning_level || '',
    projectName,
    projectCode,
    projectLabel,
    mainStageLabel,
    projectStageLabel,
    stageLabel,
    planStartRaw: planStartDate,
    planEndRaw: planEndDate,
    planStart: formatDateCell(planStartDate),
    planEnd: formatDateCell(planEndDate),
    actualFinishRaw: actualFinishDate,
    actualFinish: formatDateCell(actualFinishDate),
    executorName: formatUser(record.executor),
    executorRaw: record.executor,
    executionNote: record.execution_note || '',
    overdueReason: record.overdue_reason || '',
    siteUploadRaw: record.site_upload,
    originalIndex: index
  };
};

const normalizedRecords = computed(() => progressRecords.value.map(normalizeRecord));

const matchesSearch = (row, query) => {
  const pool = [
    row.projectName,
    row.projectCode,
    row.stageLabel,
    row.executorName,
    row.status,
    row.warningLevel
  ]
    .filter(Boolean)
    .map((item) => String(item).toLowerCase());
  return pool.some((item) => item.includes(query));
};

const matchesUser = (row) => {
  const executorNameTokens = collectExecutorNameTokens(row.executorRaw);
  const hasNameMatch =
    userNameTokenSet.value.size > 0 &&
    Array.from(userNameTokenSet.value).some((token) => executorNameTokens.has(token));

  if (hasNameMatch) return true;

  const executorIds = getExecutorIds(row.executorRaw).map((item) => normalizeToken(item));
  const executorTokens = collectExecutorTokens(row.executorRaw);
  const hasExecutorIdMatch = executorIds.some((id) => userTokenSet.value.has(id));
  const hasExecutorTokenMatch = Array.from(userTokenSet.value).some((token) =>
    executorTokens.has(token)
  );
  return hasExecutorIdMatch || hasExecutorTokenMatch;
};

const compareOrderValue = (a, b) => {
  if (a === null || a === undefined) return b === null || b === undefined ? 0 : 1;
  if (b === null || b === undefined) return -1;
  if (typeof a === 'number' && typeof b === 'number') return a - b;
  return String(a).localeCompare(String(b), 'zh');
};

const hiddenStatuses = new Set(['完成', '超期完成']);
const currentPage = ref(1);
const pageSize = ref(10);
const searchQueryLower = computed(() => searchQuery.value.trim().toLowerCase());

const userMatchedRecords = computed(() => {
  if (!hasUserId.value) return [];
  return normalizedRecords.value.filter(matchesUser);
});

const searchedUserRecords = computed(() => {
  const query = searchQueryLower.value;
  if (!query) return userMatchedRecords.value;
  return userMatchedRecords.value.filter((row) => matchesSearch(row, query));
});

const filteredRecords = computed(() => {
  return searchedUserRecords.value.filter((row) => !hiddenStatuses.has(row.status));
});

const tableRows = computed(() => {
  const rows = [...filteredRecords.value];
  rows.sort((a, b) => {
    const endCompare = compareOrderValue(a.planEndRaw?.getTime?.(), b.planEndRaw?.getTime?.());
    if (endCompare !== 0) return endCompare;
    const startCompare = compareOrderValue(a.planStartRaw?.getTime?.(), b.planStartRaw?.getTime?.());
    if (startCompare !== 0) return startCompare;
    return a.originalIndex - b.originalIndex;
  });
  return rows;
});

const isDone = (status) => status === '完成' || status === '超期完成';

const isOverdueRow = (row) => row?.status === '超期';

const totalCount = computed(() => tableRows.value.length);
const doneCount = computed(() => tableRows.value.filter((row) => isDone(row.status)).length);
const overdueCount = computed(() => tableRows.value.filter((row) => isOverdueRow(row)).length);
const pendingCount = computed(() => Math.max(totalCount.value - doneCount.value, 0));
const waitingCount = computed(() => tableRows.value.filter((row) => row.status !== '超期').length);
const overallCount = computed(() => searchedUserRecords.value.length);

const mobileGroups = computed(() => {
  const map = new Map();
  tableRows.value.forEach((row) => {
    const key = row.projectLabel || '未命名项目';
    if (!map.has(key)) {
      map.set(key, { key, title: key, rows: [] });
    }
    map.get(key).rows.push(row);
  });
  return Array.from(map.values());
});

const dialogWidth = computed(() => (isMobile.value ? '96%' : '680px'));

const pagedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return tableRows.value.slice(start, start + pageSize.value);
});

const getStatusTag = (status) => {
  if (status === '完成' || status === '超期完成') return 'success';
  if (status === '超期') return 'danger';
  return 'info';
};

const formatRange = (start, end) => {
  if (!start && !end) return '--';
  if (start && end) return `${start} ~ ${end}`;
  return start || end;
};

const loadProgressRecords = async () => {
  loading.value = true;
  try {
    const result = await api.listProjectProgress({
      skip: 0,
      limit: 300
    });
    if (result?.code === 200 && Array.isArray(result.data)) {
      progressRecords.value = result.data;
    } else {
      progressRecords.value = [];
      ElMessage.error(result?.msg || '加载执行数据失败');
    }
  } catch (error) {
    console.error('加载执行数据失败：', error);
    progressRecords.value = [];
    ElMessage.error('加载执行数据失败');
  } finally {
    loading.value = false;
  }
};

const handleSearch = async () => {
  await loadProgressRecords();
};

const handlePageChange = (page) => {
  currentPage.value = page;
};

const handlePageSizeChange = (size) => {
  pageSize.value = size;
  currentPage.value = 1;
};

const openDetailDialog = (row) => {
  if (!row) return;
  detailRow.value = row;
  detailDialogVisible.value = true;
};

const openSubmitDialog = (row) => {
  if (!row) return;
  submitRow.value = row;
  submitForm.value = {
    actualFinish: row.actualFinish || '',
    executionNote: row.executionNote || '',
    overdueReason: row.overdueReason || ''
  };
  uploadFileList.value = [];
  submitDialogVisible.value = true;
};

const submitIsOverdue = computed(() => {
  if (!submitRow.value) return false;
  if (submitRow.value.status === '超期') return true;
  const planEnd = submitRow.value.planEndRaw;
  if (!planEnd) return false;
  const actualDate = parseDateValue(submitForm.value.actualFinish);
  const checkDate = actualDate || new Date();
  return checkDate.getTime() > planEnd.getTime();
});

const formatAttachmentName = (item) => {
  if (!item) return '';
  if (typeof item === 'string') return item;
  return (
    item.name ||
    item.file_name ||
    item.fileName ||
    item.filename ||
    item.url ||
    item.path ||
    item.id ||
    item._id ||
    '未命名附件'
  );
};

const normalizeAttachmentList = (value) => {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value.map(formatAttachmentName).filter(Boolean).map((item) => String(item));
  }
  const single = formatAttachmentName(value);
  return single ? [String(single)] : [];
};

const detailAttachments = computed(() => normalizeAttachmentList(detailRow.value?.siteUploadRaw));

const buildUploadFormData = (fileList) => {
  const formData = new FormData();
  fileList.forEach((item) => {
    const rawFile = item.raw || item;
    formData.append('files', rawFile, rawFile.name);
  });
  return formData;
};

const uploadFiles = async () => {
  if (!uploadFileList.value.length) return [];
  const formData = buildUploadFormData(uploadFileList.value);
  const result = await api.uploadProjectProgressFiles(formData);
  if (result?.code === 200 && Array.isArray(result.data)) {
    return result.data;
  }
  throw new Error(result?.msg || '上传失败');
};

const mergeSiteUploads = (existing, uploaded) => {
  const existingList = Array.isArray(existing) ? existing : existing ? [existing] : [];
  const uploadedList = Array.isArray(uploaded) ? uploaded : uploaded ? [uploaded] : [];
  return [...existingList, ...uploadedList];
};

const handleSubmit = async () => {
  if (!submitRow.value?.recordId) {
    ElMessage.error('无法提交：缺少记录ID');
    return;
  }
  if (!submitForm.value.actualFinish) {
    ElMessage.warning('请选择实际完成时间');
    return;
  }
  if (submitIsOverdue.value && !submitForm.value.overdueReason.trim()) {
    ElMessage.warning('请填写超期原因');
    return;
  }

  submitting.value = true;
  try {
    const payload = {
      actual_finish: submitForm.value.actualFinish,
      execution_note: submitForm.value.executionNote
    };

    if (submitIsOverdue.value) {
      payload.overdue_reason = submitForm.value.overdueReason;
    }

    if (uploadFileList.value.length) {
      const uploadedFiles = await uploadFiles();
      payload.site_upload = mergeSiteUploads(submitRow.value.siteUploadRaw, uploadedFiles);
    }

    if (!isDone(submitRow.value.status)) {
      payload.status = submitIsOverdue.value ? '超期完成' : '完成';
    }

    if (Object.keys(payload).length === 0) {
      ElMessage.warning('没有可提交的内容');
      submitting.value = false;
      return;
    }

    const result = await api.updateProjectProgress(submitRow.value.recordId, payload);
    if (result?.code === 200) {
      ElMessage.success('提交成功');
      submitDialogVisible.value = false;
      await loadProgressRecords();
    } else {
      ElMessage.error(result?.msg || '提交失败');
    }
  } catch (error) {
    console.error('提交失败：', error);
    ElMessage.error(error?.message || '提交失败');
  } finally {
    submitting.value = false;
  }
};

const handleUploadExceed = () => {
  ElMessage.warning('最多上传 5 个文件');
};

watch(submitDialogVisible, (visible) => {
  if (!visible) {
    submitRow.value = null;
    uploadFileList.value = [];
  }
});

const handleResize = () => {
  isMobile.value = window.innerWidth <= 768;
};

watch(
  [tableRows, pageSize],
  () => {
    const maxPage = Math.max(1, Math.ceil(totalCount.value / pageSize.value));
    if (currentPage.value > maxPage) {
      currentPage.value = maxPage;
    }
  },
  { immediate: true }
);

const resolveUserProfile = async () => {
  if (!userParam.value) return;
  try {
    const result = await api.getUserInfo(userParam.value);
    if (result?.code === 200 && result.data) {
      userProfile.value = {
        user_id: result.data.user_id || result.data._id || result.data.id || userParam.value,
        name: result.data.name || '',
        account: result.data.account || ''
      };
      return;
    }
  } catch (error) {
    console.warn('用户信息查询失败，尝试使用成员列表匹配。', error);
  }

  try {
    const result = await api.listUsers();
    if (result?.code === 200 && Array.isArray(result.data)) {
      const match = result.data.find(
        (item) =>
          normalizeToken(item.user_id) === normalizeToken(userParam.value) ||
          normalizeToken(item.account) === normalizeToken(userParam.value) ||
          normalizeToken(item.name) === normalizeToken(userParam.value)
      );
      if (match) {
        userProfile.value = {
          user_id: match.user_id || userParam.value,
          name: match.name || '',
          account: match.account || ''
        };
      }
    }
  } catch (error) {
    console.warn('成员列表匹配失败。', error);
  }
};

onMounted(async () => {
  handleResize();
  window.addEventListener('resize', handleResize);
  userParam.value = getQueryParam('webpage_user_id') || '';
  if (!userParam.value) {
    ElMessage.warning('未获取到用户ID，已隐藏执行数据');
  } else {
    await resolveUserProfile();
  }
  await loadProgressRecords();
    function getQueryParam(paramName) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(paramName);
  }

  // 1. 获取 ID
  const userId = getQueryParam('webpage_user_id');
  console.log('Webpage User ID:', userId);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
});

</script>

<style scoped>
.execution-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 20px;
}

.execution-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f1f1f;
}

.execution-subtitle {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.execution-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-alert {
  margin-bottom: 18px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.summary-card {
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
  display: flex;
  align-items: center;
  gap: 12px;
}

.summary-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
}

.summary-icon.is-primary {
  background: rgba(22, 119, 255, 0.12);
  color: #1677ff;
}

.summary-icon.is-warning {
  background: rgba(250, 140, 22, 0.14);
  color: #fa8c16;
}

.summary-icon.is-danger {
  background: rgba(245, 34, 45, 0.12);
  color: #f5222d;
}

.summary-icon.is-neutral {
  background: rgba(24, 144, 255, 0.08);
  color: #3a7afe;
}

.summary-content {
  display: flex;
  flex-direction: column;
}

.summary-label {
  font-size: 13px;
  color: #8c8c8c;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 24px;
  font-weight: 600;
  color: #1f1f1f;
}

.accent-primary {
  color: #1677ff;
}

.accent-success {
  color: #52c41a;
}

.accent-danger {
  color: #f5222d;
}

.accent-warning {
  color: #fa8c16;
}

.table-card {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
}

.project-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.project-title {
  font-weight: 600;
  color: #303133;
}

.project-stage {
  color: #606266;
  font-size: 13px;
}

.mobile-only {
  display: none;
}

.mobile-group-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mobile-group {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 14px;
  padding: 12px;
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
}

.mobile-group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.mobile-group-title {
  font-weight: 600;
  color: #303133;
}

.mobile-group-count {
  font-size: 12px;
  color: #909399;
}

.mobile-card-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.mobile-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
}

.mobile-card-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.mobile-card-body {
  display: grid;
  gap: 8px;
  font-size: 13px;
  color: #606266;
  margin-bottom: 12px;
}

.mobile-info {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.mobile-info .label {
  color: #909399;
}

.mobile-card-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.detail-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-attachments {
  background: #f9fafb;
  border-radius: 8px;
  padding: 12px 16px;
}

.attachment-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.attachment-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.attachment-item {
  max-width: 240px;
}

.upload-icon {
  font-size: 26px;
  color: #1677ff;
  margin-bottom: 8px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}

.empty-holder {
  padding: 20px 0;
}

.pagination-row {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.mobile-dialog :deep(.el-dialog__body) {
  padding: 16px;
}

.mobile-dialog :deep(.el-dialog__footer) {
  padding: 12px 16px 16px;
}

@media (max-width: 1200px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .execution-actions {
    width: 100%;
  }

  .execution-actions .el-input {
    flex: 1;
  }

  .summary-grid {
    display: none;
  }

  .table-card {
    display: none;
  }

  .mobile-only {
    display: block;
  }

  .pagination-row {
    display: none;
  }
}
</style>
