<template>
  <el-config-provider :locale="zhCn">
    <div class="main-content">
    <div class="page-container1">
      <div class="execution-header">
        <div class="header-left">
          <div class="execution-title">项目执行管理</div>
          <div class="execution-subtitle">{{ executionSubtitle }}</div>
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
            <div class="summary-value accent-primary">{{ todoCount }}</div>
          </div>
        </div>
        <div class="summary-card">
          <div class="summary-icon is-warning">
            <el-icon><Flag /></el-icon>
          </div>
          <div class="summary-content">
            <div class="summary-label">待审批</div>
            <div class="summary-value accent-warning">{{ approvalCount }}</div>
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
            <div class="summary-label">已完成</div>
            <div class="summary-value">{{ completedCount }}</div>
          </div>
        </div>
      </div>

      <div class="view-tabs-card">
        <el-tabs v-model="activeTab">
          <el-tab-pane :label="`待执行 (${todoCount})`" name="todo" />
          <el-tab-pane :label="`已完成 (${completedCount})`" name="completed" />
          <el-tab-pane :label="`审批内容 (${approvalCount})`" name="approval" />
          <el-tab-pane :label="`延期申请审核 (${delayReviewCount})`" name="delayReview" />
        </el-tabs>
      </div>

      <div v-if="activeTab !== 'delayReview'" class="table-card desktop-only">
        <el-table
          :data="pagedRows"
          v-loading="loading"
          border
          stripe
          row-key="recordId"
          :empty-text="emptyText"
        >
          <el-table-column label="项目 / 执行阶段" min-width="280">
            <template #default="{ row }">
              <div class="project-cell">
                <div class="project-title">{{ row.projectLabel }}</div>
                <div class="project-stage">{{ row.stageLabel }}</div>
                <div v-if="row.batchLabel" class="project-batch">{{ row.batchLabel }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="计划完成时间" width="190" align="center">
            <template #default="{ row }">
              <span>{{ row.planEnd || '--' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="实际完成时间" width="190" align="center">
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
          <el-table-column label="审批人" width="140" align="center">
            <template #default="{ row }">
              <span>{{ row.approverName || '--' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="290" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="openDetailDialog(row)">详情</el-button>
              <el-button v-if="canSubmitRow(row)" type="success" link @click="openSubmitDialog(row)">提交</el-button>
              <el-button v-if="canCreateDelayRequestRow(row)" type="warning" link @click="openDelayRequestDialog(row)">延期申请</el-button>
              <el-button v-if="canApproveRow(row)" type="primary" link @click="handleApproval(row, 'approve')">通过</el-button>
              <el-button v-if="canApproveRow(row)" type="danger" link @click="handleApproval(row, 'reject')">驳回</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-else class="table-card desktop-only">
        <el-table
          :data="pagedDelayReviewRows"
          v-loading="loading"
          border
          stripe
          row-key="request_id"
          :empty-text="emptyText"
        >
          <el-table-column label="项目 / 批次" min-width="280">
            <template #default="{ row }">
              <div class="project-cell">
                <div class="project-title">{{ buildDelayRequestProjectLabel(row) }}</div>
                <div class="project-batch">{{ buildBatchLabel(row.batch_no, row.batch_name) || '未分批' }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="起始节点" min-width="180">
            <template #default="{ row }">{{ getDelayRequestStartNodeLabel(row) }}</template>
          </el-table-column>
          <el-table-column label="申请人" width="130" align="center">
            <template #default="{ row }">{{ formatUser(row.applicant) || '--' }}</template>
          </el-table-column>
          <el-table-column label="延期天数" width="90" align="center">
            <template #default="{ row }">{{ row.delay_days || 0 }}</template>
          </el-table-column>
          <el-table-column label="节点数" width="80" align="center">
            <template #default="{ row }">{{ row.node_count || row.nodes?.length || 0 }}</template>
          </el-table-column>
          <el-table-column label="申请原因" min-width="200">
            <template #default="{ row }">{{ row.reason || '--' }}</template>
          </el-table-column>
          <el-table-column label="申请时间" width="170" align="center">
            <template #default="{ row }">{{ row.created_at || '--' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="150" align="center" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                :loading="handlingDelayReviewId === row.request_id && handlingDelayReviewAction === 'approve'"
                @click="handleDelayReview(row, 'approve')"
              >
                通过
              </el-button>
              <el-button
                type="danger"
                link
                :loading="handlingDelayReviewId === row.request_id && handlingDelayReviewAction === 'reject'"
                @click="handleDelayReview(row, 'reject')"
              >
                驳回
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="mobile-only">
        <div v-if="activeTab !== 'delayReview' && !tableRows.length && !loading" class="empty-holder">
          <el-empty :description="emptyText" />
        </div>
        <div v-else-if="activeTab !== 'delayReview'" class="mobile-group-list">
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
                    <div v-if="row.batchLabel" class="project-batch">{{ row.batchLabel }}</div>
                  </div>
                  <el-tag :type="getStatusTag(row.status)" effect="dark">
                    {{ row.status || '未完成' }}
                  </el-tag>
                </div>
                <div class="mobile-card-body">
                  <div class="mobile-info">
                    <span class="label">计划完成时间</span>
                    <span class="value">{{ row.planEnd || '--' }}</span>
                  </div>
                  <div class="mobile-info">
                    <span class="label">实际完成时间</span>
                    <span class="value">{{ row.actualFinish || '--' }}</span>
                  </div>
                  <div v-if="row.executorName" class="mobile-info">
                    <span class="label">负责人</span>
                    <span class="value">{{ row.executorName }}</span>
                  </div>
                  <div v-if="row.approverName" class="mobile-info">
                    <span class="label">审批人</span>
                    <span class="value">{{ row.approverName }}</span>
                  </div>
                </div>
                <div class="mobile-card-actions">
                  <el-button size="small" @click="openDetailDialog(row)">详情</el-button>
                  <el-button v-if="canSubmitRow(row)" size="small" type="primary" @click="openSubmitDialog(row)">提交</el-button>
                  <el-button v-if="canCreateDelayRequestRow(row)" size="small" type="warning" @click="openDelayRequestDialog(row)">延期申请</el-button>
                  <el-button v-if="canApproveRow(row)" size="small" type="primary" @click="handleApproval(row, 'approve')">通过</el-button>
                  <el-button v-if="canApproveRow(row)" size="small" type="danger" @click="handleApproval(row, 'reject')">驳回</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else>
          <div v-if="!delayReviewRows.length && !loading" class="empty-holder">
            <el-empty :description="emptyText" />
          </div>
          <div v-else class="mobile-group-list">
            <div
              v-for="row in pagedDelayReviewRows"
              :key="row.request_id"
              class="mobile-card"
            >
              <div class="mobile-card-header">
                <div>
                  <div class="project-title">{{ buildDelayRequestProjectLabel(row) }}</div>
                  <div class="project-stage">{{ getDelayRequestStartNodeLabel(row) }}</div>
                  <div class="project-batch">{{ buildBatchLabel(row.batch_no, row.batch_name) || '未分批' }}</div>
                </div>
                <el-tag type="warning" effect="dark">待审核</el-tag>
              </div>
              <div class="mobile-card-body">
                <div class="mobile-info">
                  <span class="label">申请人</span>
                  <span class="value">{{ formatUser(row.applicant) || '--' }}</span>
                </div>
                <div class="mobile-info">
                  <span class="label">延期天数</span>
                  <span class="value">{{ row.delay_days || 0 }}</span>
                </div>
                <div class="mobile-info">
                  <span class="label">节点数</span>
                  <span class="value">{{ row.node_count || row.nodes?.length || 0 }}</span>
                </div>
                <div class="mobile-info">
                  <span class="label">申请时间</span>
                  <span class="value">{{ row.created_at || '--' }}</span>
                </div>
                <div class="mobile-info mobile-info--stack">
                  <span class="label">申请原因</span>
                  <span class="value">{{ row.reason || '--' }}</span>
                </div>
              </div>
              <div class="mobile-card-actions">
                <el-button size="small" type="primary" @click="handleDelayReview(row, 'approve')">通过</el-button>
                <el-button size="small" type="danger" @click="handleDelayReview(row, 'reject')">驳回</el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="viewTotalCount > 0" class="pagination-row">
        <el-config-provider :locale="zhCn">
          <el-pagination
            :current-page="currentPage"
            :page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="viewTotalCount"
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
          <el-descriptions-item label="批次编号">{{ detailRow.batchNo || '--' }}</el-descriptions-item>
          <el-descriptions-item label="批次名称">{{ detailRow.batchName || '--' }}</el-descriptions-item>
          <el-descriptions-item v-if="false" label="计划开始">{{ detailRow.planStart || '--' }}</el-descriptions-item>
          <el-descriptions-item label="计划完成时间">{{ detailRow.planEnd || '--' }}</el-descriptions-item>
          <el-descriptions-item label="实际完成时间">{{ detailRow.actualFinish || '--' }}</el-descriptions-item>
          <el-descriptions-item label="当前状态">{{ detailRow.status || '未完成' }}</el-descriptions-item>
          <el-descriptions-item label="负责人">{{ detailRow.executorName || '--' }}</el-descriptions-item>
          <el-descriptions-item label="审批人">{{ detailRow.approverName || '--' }}</el-descriptions-item>
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
            <div
              v-for="(item, index) in detailAttachments"
              :key="`att-${index}`"
              class="attachment-item"
            >
              <span class="attachment-name" :title="item.name">{{ item.name }}</span>
              <div class="attachment-actions">
                <el-button link type="primary" @click="previewAttachment(item)">预览</el-button>
                <el-button link type="primary" @click="downloadAttachment(item)">下载</el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="detailDialogVisible = false">知道了</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="imagePreviewVisible"
      :title="previewImageTitle"
      :width="isMobile ? '96%' : '820px'"
      :fullscreen="isMobile"
      top="5vh"
      append-to-body
      :class="{ 'mobile-dialog': isMobile }"
    >
      <div class="image-preview-body">
        <el-image
          v-if="previewImageUrl"
          :src="previewImageUrl"
          fit="contain"
          class="image-preview-main"
        />
        <el-empty v-else description="暂无可预览图片" />
      </div>
      <template #footer>
        <el-button @click="imagePreviewVisible = false">关闭</el-button>
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
            <el-input
              v-model="submitForm.actualFinish"
              readonly
              placeholder="系统自动填入当前时间"
            />
        </el-form-item>
        <el-form-item label="现场资料上传" required>
          <el-upload
            :file-list="uploadFileList"
            action="#"
            multiple
            drag
            :auto-upload="false"
            :limit="20"
            :on-exceed="handleUploadExceed"
            @update:file-list="handleUploadFileListChange"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖拽到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="upload-tip">必填，支持多文件上传，最多 20 个</div>
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
      </el-form>
      <template #footer>
        <el-button @click="submitDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确认提交</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="delayRequestDialogVisible"
      title="延期申请"
      :width="dialogWidth"
      :fullscreen="isMobile"
      :class="{ 'mobile-dialog': isMobile }"
    >
      <el-form :label-width="isMobile ? '90px' : '110px'">
        <el-form-item label="起始节点">
          <el-input :model-value="delayRequestRow?.stageLabel || '--'" disabled />
        </el-form-item>
        <el-form-item label="所属批次">
          <el-input :model-value="delayRequestRow?.batchLabel || '--'" disabled />
        </el-form-item>
        <el-form-item label="延期天数">
          <el-input-number
            v-model="delayRequestForm.days"
            :min="1"
            :step="1"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="申请原因">
          <el-input
            v-model="delayRequestForm.reason"
            type="textarea"
            :rows="4"
            maxlength="200"
            show-word-limit
            placeholder="请填写延期原因"
          />
        </el-form-item>
      </el-form>
      <div class="delay-request-hint">
        {{ delayRequestScopeHint }}
      </div>
      <div v-if="delayRequestAffectedNodes.length" class="delay-request-preview-list">
        <span
          v-for="item in delayRequestPreviewNodes"
          :key="item.recordId"
          class="delay-request-preview-tag"
        >
          {{ item.stageLabel || '--' }}
        </span>
        <span v-if="delayRequestAffectedNodes.length > delayRequestPreviewNodes.length" class="delay-request-preview-more">
          等 {{ delayRequestAffectedNodes.length }} 个节点
        </span>
      </div>
      <template #footer>
        <el-button @click="delayRequestDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="creatingDelayRequest" @click="handleCreateDelayRequest">提交申请</el-button>
      </template>
    </el-dialog>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { ElMessage, ElMessageBox, ElConfigProvider } from 'element-plus';
import { UploadFilled, Bell, Flag, WarningFilled, TrendCharts } from '@element-plus/icons-vue';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { useRoute } from 'vue-router';
import api from '../api/client';
import { resolveWebpageUserId } from '../utils/webpageUser';

const searchQuery = ref('');
const loading = ref(false);
const progressRecords = ref([]);
const projectSummaryRecords = ref([]);
const delayReviewRequests = ref([]);
const activeTab = ref('todo');
const userParam = ref('');
const userProfile = ref({
  user_id: '',
  name: '',
  account: ''
});
const projectManagerMembers = ref([]);
const route = useRoute();

const detailDialogVisible = ref(false);
const submitDialogVisible = ref(false);
const delayRequestDialogVisible = ref(false);
const detailRow = ref(null);
const submitRow = ref(null);
const delayRequestRow = ref(null);
const previewImageItem = ref(null);
const submitting = ref(false);
const creatingDelayRequest = ref(false);
const handlingDelayReviewId = ref('');
const handlingDelayReviewAction = ref('');
const imagePreviewVisible = ref(false);
const isMobile = ref(false);

const submitForm = ref({
  actualFinish: '',
  executionNote: ''
});

const delayRequestForm = ref({
  days: 1,
  reason: ''
});

const uploadFileList = ref([]);

// 是否存在用户标识
const hasUserId = computed(() => Boolean(userParam.value));

// 解析日期值为 Date
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

// 解析日期区间
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

// 格式化日期展示
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

const formatDateTime = (value) => {
  if (!value) return '--';
  const date = value instanceof Date ? value : parseDateValue(value);
  if (!date || Number.isNaN(date.getTime())) return String(value);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hour = String(date.getHours()).padStart(2, '0');
  const minute = String(date.getMinutes()).padStart(2, '0');
  const second = String(date.getSeconds()).padStart(2, '0');
  return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
};

// 表格日期展示格式
const formatDateCell = (value) => {
  if (!value) return '';
  return formatDate(value);
};

const formatDateTimeCell = (value) => {
  if (!value) return '';
  return formatDateTime(value);
};

const getCurrentDateValue = () => formatDateTime(new Date());

// 格式化执行人显示
const formatUser = (value) => {
  if (!value) return '';
  if (Array.isArray(value)) {
    const names = value.map((item) => formatUser(item)).filter(Boolean);
    return names.length ? names.join(' / ') : '';
  }
  if (typeof value === 'object') {
    return (
      value.name ||
      value.username ||
      value.user_name ||
      value.userName ||
      value.nickname ||
      value.realname ||
      value.account ||
      value.user_id ||
      value.userid ||
      value.userId ||
      value._id ||
      value.id ||
      ''
    );
  }
  return String(value);
};

// 提取执行人 ID 列表
const getExecutorIds = (value) => {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value
      .map((item) => {
        if (!item) return '';
        if (typeof item === 'object') return item.user_id || item.userid || item.userId || item._id || item.id || '';
        return String(item);
      })
      .filter(Boolean)
      .map((id) => String(id));
  }
  if (typeof value === 'object') {
    return [value.user_id || value.userid || value.userId || value._id || value.id || ''].filter(Boolean).map((id) => String(id));
  }
  return [String(value)];
};

const getMemberId = (value) => {
  const ids = getExecutorIds(value);
  return ids.length ? ids[0] : '';
};

// 统一 token 格式
const normalizeToken = (value) => {
  if (value === null || value === undefined) return '';
  const text = String(value).trim();
  return text ? text.toLowerCase() : '';
};

const USER_TOKEN_KEYS = [
  'user_id',
  'userid',
  'userId',
  '_id',
  'id',
  'account',
  'name',
  'username',
  'user_name',
  'userName',
  'nickname',
  'realname',
  'uniqueid',
  'mobile',
  'email'
];

const collectUserTokens = (value) => {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value.flatMap((item) => collectUserTokens(item));
  }
  if (typeof value === 'object') {
    return USER_TOKEN_KEYS.flatMap((key) => collectUserTokens(value?.[key]));
  }
  const token = normalizeToken(value);
  return token ? [token] : [];
};

const userValueMatchesCurrentUser = (value) => {
  if (!userTokenSet.value.size) return false;
  return collectUserTokens(value).some((token) => userTokenSet.value.has(token));
};

// 拆分名字文本为 token
const splitNameText = (value) => {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value.flatMap((item) => splitNameText(item));
  }
  if (typeof value === 'object') {
    return splitNameText(
      value.name ||
      value.username ||
      value.user_name ||
      value.userName ||
      value.nickname ||
      value.realname ||
      value.account ||
      ''
    );
  }
  return String(value)
    .split(/[\s,，、/;；|]+/)
    .map((item) => item.trim())
    .filter(Boolean);
};

// 构建 token 集合
const buildTokenSet = (values) => {
  const set = new Set();
  values.forEach((value) => {
    const token = normalizeToken(value);
    if (token) set.add(token);
  });
  return set;
};

// 从执行人字段收集 token
const collectExecutorTokens = (executorRaw) => {
  const tokens = [];
  const walk = (value) => {
    if (!value) return;
    if (Array.isArray(value)) {
      value.forEach(walk);
      return;
    }
    if (typeof value === 'object') {
      tokens.push(...collectUserTokens(value));
      return;
    }
    tokens.push(value);
  };
  walk(executorRaw);
  return buildTokenSet(tokens);
};

// 从执行人字段收集姓名 token
const collectExecutorNameTokens = (executorRaw) => buildTokenSet(splitNameText(executorRaw));

// 当前用户 token 集合
const userTokenSet = computed(() =>
  buildTokenSet(collectUserTokens([
    userParam.value,
    userProfile.value
  ]))
);

// 当前用户名 token 集合
const userNameTokenSet = computed(() => buildTokenSet(splitNameText(userProfile.value.name || userParam.value)));

const isProjectManager = computed(() =>
  projectManagerMembers.value.some((member) => userValueMatchesCurrentUser(member))
);

// 标准化文本展示
const normalizeLabel = (value) => {
  if (value === null || value === undefined) return '';
  if (typeof value === 'string') return value.trim();
  return String(value);
};

const normalizeStatus = (value) => normalizeLabel(value) || '未完成';

const normalizeBatchNo = (value) => {
  if (value === null || value === undefined) return '';
  if (typeof value === 'number' && Number.isFinite(value)) {
    const normalizedNumber = Math.trunc(value);
    return normalizedNumber > 0 ? String(normalizedNumber) : '';
  }
  const text = String(value).trim();
  if (!text) return '';
  const numeric = Number(text);
  if (Number.isFinite(numeric)) {
    const normalizedNumber = Math.trunc(numeric);
    return normalizedNumber > 0 ? String(normalizedNumber) : '';
  }
  return text;
};

const buildBatchLabel = (batchNo, batchName) => {
  const normalizedNo = normalizeBatchNo(batchNo);
  const normalizedName = normalizeLabel(batchName);
  if (normalizedNo && normalizedName) return `${normalizedName}（批次 ${normalizedNo}）`;
  if (normalizedName) return normalizedName;
  if (normalizedNo) return `批次 ${normalizedNo}`;
  return '';
};

const normalizeOrderValue = (value) => {
  if (value === null || value === undefined || value === '') return null;
  const numeric = Number(value);
  if (Number.isFinite(numeric)) return Math.trunc(numeric);
  return normalizeLabel(value);
};

const compareTextValue = (a, b) => String(a || '').localeCompare(String(b || ''), 'zh');

const compareStagePosition = (a, b) => {
  const mainOrderCompare = compareOrderValue(a.mainStageOrder, b.mainStageOrder);
  if (mainOrderCompare !== 0) return mainOrderCompare;

  const mainLabelCompare = compareTextValue(a.mainStageLabel, b.mainStageLabel);
  if (mainLabelCompare !== 0) return mainLabelCompare;

  const stageOrderCompare = compareOrderValue(a.projectStageOrder, b.projectStageOrder);
  if (stageOrderCompare !== 0) return stageOrderCompare;

  const stageLabelCompare = compareTextValue(a.stageLabel, b.stageLabel);
  if (stageLabelCompare !== 0) return stageLabelCompare;

  return a.originalIndex - b.originalIndex;
};

// 规范化记录为前端展示结构
const normalizeRecord = (record, index) => {
  const planRange = parseDateRange(record.plan_time);
  const planStartDate = planRange.start || null;
  const planEndDate = parseDateValue(record.plan_finishtime) || planRange.end || null;
  const actualFinishDate = parseDateValue(record.actual_finish);
  const batchNo = normalizeBatchNo(record.batch_no);
  const batchName = normalizeLabel(record.batch_name);

  const projectName = normalizeLabel(record.project_name) || '未命名项目';
  const projectCode = normalizeLabel(record.project_code);
  const projectLabel = projectCode ? `${projectName} (${projectCode})` : projectName;

  const mainStageLabel = normalizeLabel(record.main_stage || record.mainStage);
  const projectStageLabel = normalizeLabel(record.project_stage || record.projectStage || record.stage);
  const stageLabel = projectStageLabel
    ? mainStageLabel && mainStageLabel !== projectStageLabel
      ? `${mainStageLabel} / ${projectStageLabel}`
      : projectStageLabel
    : mainStageLabel || `阶段${index + 1}`;

  return {
    recordId: record._id || `${index}`,
    status: normalizeStatus(record.status),
    warningLevel: record.warning_level || '',
    projectName,
    projectCode,
    projectLabel,
    mainStageLabel,
    mainStageOrder: normalizeOrderValue(record.main_stage_order),
    projectStageLabel,
    projectStageOrder: normalizeOrderValue(record.project_stage_order),
    stageLabel,
    batchNo,
    batchName,
    batchLabel: buildBatchLabel(batchNo, batchName),
    planStartRaw: planStartDate,
    planEndRaw: planEndDate,
    planStart: formatDateCell(planStartDate),
    planEnd: formatDateTimeCell(planEndDate),
    actualFinishRaw: actualFinishDate,
    actualFinish: formatDateTimeCell(actualFinishDate),
    executorName: formatUser(record.executor),
    executorRaw: record.executor,
    approverName: formatUser(record.approver),
    approverRaw: record.approver,
    executionNote: record.execution_note || '',
    overdueReason: record.overdue_reason || '',
    siteUploadRaw: record.site_upload,
    creatorRaw: record.creator,
    updaterRaw: record.updater,
    rawPlanTime: record.plan_time,
    originalIndex: index
  };
};

// 规范化后的记录列表
const normalizedRecords = computed(() => progressRecords.value.map(normalizeRecord));

// 搜索匹配
const matchesSearch = (row, query) => {
  const pool = [
    row.projectName,
    row.projectCode,
    row.stageLabel,
    row.batchLabel,
    row.executorName,
    row.approverName,
    row.status,
    row.warningLevel
  ]
    .filter(Boolean)
    .map((item) => String(item).toLowerCase());
  return pool.some((item) => item.includes(query));
};

const matchesMemberValue = (memberRaw) => {
  const memberNameTokens = collectExecutorNameTokens(memberRaw);
  const hasNameMatch =
    userNameTokenSet.value.size > 0 &&
    Array.from(userNameTokenSet.value).some((token) => memberNameTokens.has(token));

  if (hasNameMatch) return true;

  const memberIds = getExecutorIds(memberRaw).map((item) => normalizeToken(item));
  const memberTokens = collectExecutorTokens(memberRaw);
  const hasMemberIdMatch = memberIds.some((id) => userTokenSet.value.has(id));
  const hasMemberTokenMatch = Array.from(userTokenSet.value).some((token) =>
    memberTokens.has(token)
  );
  return hasMemberIdMatch || hasMemberTokenMatch;
};

// 统一排序比较方法
const compareOrderValue = (a, b) => {
  if (a === null || a === undefined) return b === null || b === undefined ? 0 : 1;
  if (b === null || b === undefined) return -1;
  if (typeof a === 'number' && typeof b === 'number') return a - b;
  return String(a).localeCompare(String(b), 'zh');
};

const completedStatusSet = new Set(['完成', '超期完成', '已完成']);
const approvalStatusSet = new Set(['待审批', '超期待审批']);
const SUBMITTABLE_STATUS = '未完成';
const DELAY_REQUEST_STATUS_SET = new Set(['未完成', '超期']);
const currentPage = ref(1);
const pageSize = ref(10);
// 归一化搜索关键字
const searchQueryLower = computed(() => searchQuery.value.trim().toLowerCase());

const applySearch = (rows) => {
  const query = searchQueryLower.value;
  if (!query) return rows;
  return rows.filter((row) => matchesSearch(row, query));
};

const isDone = (status) => completedStatusSet.has(status);
const isApprovalPending = (status) => approvalStatusSet.has(status);
const isOverdueStatus = (status) => status === '超期' || status === '超期待审批';

const todoRecords = computed(() => {
  if (!hasUserId.value) return [];
  return applySearch(
    normalizedRecords.value.filter(
      (row) => matchesMemberValue(row.executorRaw) && !isDone(row.status) && !isApprovalPending(row.status)
    )
  );
});

const approvalRecords = computed(() => {
  if (!hasUserId.value) return [];
  return applySearch(
    normalizedRecords.value.filter(
      (row) => matchesMemberValue(row.approverRaw) && isApprovalPending(row.status)
    )
  );
});

const completedRecords = computed(() => {
  if (!hasUserId.value) return [];
  if (isProjectManager.value) {
    return applySearch(normalizedRecords.value.filter((row) => isDone(row.status)));
  }
  return applySearch(
    normalizedRecords.value.filter(
      (row) => matchesMemberValue(row.executorRaw) && isDone(row.status)
    )
  );
});

const projectSummaryMap = computed(() => {
  const map = new Map();
  projectSummaryRecords.value.forEach((item) => {
    const code = normalizeLabel(item?.project_code);
    const name = normalizeLabel(item?.project_name);
    const type = normalizeLabel(item?.project_type);
    if (code) {
      map.set(`code:${code}`, item);
    }
    if (name) {
      map.set(`name:${name}`, item);
    }
    if (code || name || type) {
      map.set(`full:${code}||${name}||${type}`, item);
    }
  });
  return map;
});

const getProjectSummary = (projectCode, projectName) => {
  const code = normalizeLabel(projectCode);
  const name = normalizeLabel(projectName);
  return (
    (code && projectSummaryMap.value.get(`code:${code}`)) ||
    (name && projectSummaryMap.value.get(`name:${name}`)) ||
    projectSummaryMap.value.get(`full:${code}||${name}||`) ||
    null
  );
};

const getDelayRequestBusinessOwner = (requestRecord) =>
  requestRecord?.business_owner ||
  requestRecord?.businessOwner ||
  getProjectSummary(requestRecord?.project_code, requestRecord?.project_name)?.business_owner ||
  '';

const buildDelayRequestProjectLabel = (requestRecord) => {
  const projectName = normalizeLabel(requestRecord?.project_name) || '未命名项目';
  const projectCode = normalizeLabel(requestRecord?.project_code);
  return projectCode ? `${projectName} (${projectCode})` : projectName;
};

const getDelayRequestStartNodeLabel = (requestRecord) => {
  const firstNode = Array.isArray(requestRecord?.nodes) ? requestRecord.nodes[0] : null;
  return firstNode?.node_label || firstNode?.main_stage_label || '--';
};

const matchesDelayReviewSearch = (requestRecord, query) => {
  if (!query) return true;
  const pool = [
    requestRecord?.project_name,
    requestRecord?.project_code,
    buildBatchLabel(requestRecord?.batch_no, requestRecord?.batch_name),
    getDelayRequestStartNodeLabel(requestRecord),
    formatUser(requestRecord?.applicant),
    requestRecord?.reason,
    requestRecord?.created_at
  ]
    .filter(Boolean)
    .map((item) => String(item).toLowerCase());
  return pool.some((item) => item.includes(query));
};

const delayReviewRows = computed(() => {
  if (!hasUserId.value) return [];
  const query = searchQueryLower.value;
  return delayReviewRequests.value
    .filter((item) => userValueMatchesCurrentUser(getDelayRequestBusinessOwner(item)))
    .filter((item) => matchesDelayReviewSearch(item, query))
    .sort((a, b) => String(b?.created_at || '').localeCompare(String(a?.created_at || ''), 'zh'));
});

const activeRecords = computed(() => {
  if (activeTab.value === 'approval') return approvalRecords.value;
  if (activeTab.value === 'completed') return completedRecords.value;
  return todoRecords.value;
});

// 表格展示数据（排序后）
const tableRows = computed(() => {
  const rows = [...activeRecords.value];
  rows.sort((a, b) => {
    const primaryCompare =
      activeTab.value === 'completed'
        ? compareOrderValue(b.actualFinishRaw?.getTime?.(), a.actualFinishRaw?.getTime?.())
        : compareOrderValue(a.planEndRaw?.getTime?.(), b.planEndRaw?.getTime?.());
    if (primaryCompare !== 0) return primaryCompare;
    const startCompare = compareOrderValue(a.planStartRaw?.getTime?.(), b.planStartRaw?.getTime?.());
    if (startCompare !== 0) return startCompare;
    return a.originalIndex - b.originalIndex;
  });
  return rows;
});

// 统计卡片数据
const todoCount = computed(() => todoRecords.value.length);
const approvalCount = computed(() => approvalRecords.value.length);
const completedCount = computed(() => completedRecords.value.length);
const delayReviewCount = computed(() => delayReviewRows.value.length);
const overdueCount = computed(() =>
  [...todoRecords.value, ...approvalRecords.value].filter((row) => isOverdueStatus(row.status)).length
);
const viewTotalCount = computed(() =>
  activeTab.value === 'delayReview' ? delayReviewRows.value.length : tableRows.value.length
);

const executionSubtitle = computed(() => {
  if (activeTab.value === 'delayReview') return '当前页显示需要你审核的延期申请';
  if (activeTab.value === 'approval') return '当前页显示需要你审批的节点';
  if (activeTab.value === 'completed') return '当前页显示全部项目的已完成节点';
  return '当前页显示当前账号负责的未完成与超期节点';
});

const emptyText = computed(() => {
  if (activeTab.value === 'delayReview') return '暂无待审核延期申请';
  if (activeTab.value === 'completed') return '暂无已完成阶段';
  if (!hasUserId.value) return '请通过业务入口访问';
  if (activeTab.value === 'approval') return '暂无待审批阶段';
  return '暂无待执行阶段';
});

// 移动端按项目分组
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

const parsePositiveInt = (value) => {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return 0;
  const normalized = Math.trunc(numeric);
  return normalized > 0 ? normalized : 0;
};

const sameProjectBatch = (row, target) =>
  Boolean(
    row &&
    target &&
    normalizeLabel(row.projectCode) === normalizeLabel(target.projectCode) &&
    normalizeLabel(row.projectName) === normalizeLabel(target.projectName) &&
    normalizeBatchNo(row.batchNo) === normalizeBatchNo(target.batchNo) &&
    normalizeLabel(row.batchName) === normalizeLabel(target.batchName)
  );

const delayRequestAffectedNodes = computed(() => {
  if (!delayRequestRow.value?.recordId) return [];
  const relatedRows = normalizedRecords.value
    .filter((row) => sameProjectBatch(row, delayRequestRow.value))
    .sort(compareStagePosition);
  const startIndex = relatedRows.findIndex((row) => row.recordId === delayRequestRow.value.recordId);
  if (startIndex < 0) return [];
  return relatedRows.slice(startIndex);
});

const delayRequestPreviewNodes = computed(() => delayRequestAffectedNodes.value.slice(0, 8));

const delayRequestScopeHint = computed(() => {
  if (!delayRequestRow.value) return '请选择要申请延期的节点';
  const count = delayRequestAffectedNodes.value.length;
  if (!count) return '当前批次未找到可延期的后续节点';
  if (count === 1) {
    return `将对当前节点申请延期 ${parsePositiveInt(delayRequestForm.value.days) || 1} 天`;
  }
  return `将对当前批次从该节点开始的 ${count} 个节点发起延期申请`;
});

// 弹窗宽度自适应
const dialogWidth = computed(() => (isMobile.value ? '96%' : '680px'));

// 当前分页数据
const pagedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return tableRows.value.slice(start, start + pageSize.value);
});

const pagedDelayReviewRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return delayReviewRows.value.slice(start, start + pageSize.value);
});

// 状态标签样式
const getStatusTag = (status) => {
  if (isDone(status)) return 'success';
  if (isApprovalPending(status)) return 'warning';
  if (status === '超期') return 'danger';
  return 'info';
};

// 计划时间展示
const formatRange = (start, end) => {
  if (!start && !end) return '--';
  if (start && end) return `${start} ~ ${end}`;
  return start || end;
};

const PROJECT_PROGRESS_PAGE_SIZE = 300;
const MAX_FETCH_PAGES = 20;

const fetchAllPages = async (fetcher, pageSize, params = {}) => {
  const records = [];
  for (let page = 0; page < MAX_FETCH_PAGES; page += 1) {
    const result = await fetcher({
      ...params,
      skip: page * pageSize,
      limit: pageSize
    });
    if (result?.code !== 200 || !Array.isArray(result.data)) {
      return {
        ok: false,
        data: records,
        msg: result?.msg || '加载执行数据失败'
      };
    }
    records.push(...result.data);
    if (result.data.length < pageSize) {
      return {
        ok: true,
        data: records
      };
    }
  }
  return {
    ok: true,
    data: records
  };
};

// 拉取执行进度数据
const loadProgressRecords = async () => {
  loading.value = true;
  try {
    const [progressResult, projectSummaryResult] = await Promise.all([
      fetchAllPages(api.listProjectProgress, PROJECT_PROGRESS_PAGE_SIZE),
      fetchAllPages(api.listProjectSummary, PROJECT_PROGRESS_PAGE_SIZE)
    ]);
    if (progressResult?.ok) {
      progressRecords.value = progressResult.data;
    } else {
      progressRecords.value = [];
      ElMessage.error(progressResult?.msg || '加载执行数据失败');
    }
    if (projectSummaryResult?.ok) {
      projectSummaryRecords.value = projectSummaryResult.data;
    } else {
      projectSummaryRecords.value = [];
      console.warn('加载项目简要信息失败：', projectSummaryResult?.msg);
    }
  } catch (error) {
    console.error('加载执行数据失败：', error);
    progressRecords.value = [];
    projectSummaryRecords.value = [];
    ElMessage.error('加载执行数据失败');
  } finally {
    loading.value = false;
  }
};

const loadProjectManagers = async () => {
  try {
    const result = await api.listProjectManagers();
    projectManagerMembers.value = result?.code === 200 && Array.isArray(result.data) ? result.data : [];
  } catch (error) {
    console.error('加载项目管理员成员失败：', error);
    projectManagerMembers.value = [];
  }
};

const loadDelayReviewRequests = async () => {
  if (!hasUserId.value) {
    delayReviewRequests.value = [];
    return;
  }
  loading.value = true;
  try {
    const result = await api.listProjectDelayRequests({ status: 'pending' });
    if (result?.code === 200 && Array.isArray(result.data)) {
      delayReviewRequests.value = result.data;
    } else {
      delayReviewRequests.value = [];
      ElMessage.error(result?.msg || '加载延期申请失败');
    }
  } catch (error) {
    console.error('加载延期申请失败：', error);
    delayReviewRequests.value = [];
    ElMessage.error(error?.message || '加载延期申请失败');
  } finally {
    loading.value = false;
  }
};

// 执行搜索
const handleSearch = async () => {
  currentPage.value = 1;
  await Promise.all([loadProgressRecords(), loadDelayReviewRequests()]);
};

// 切换分页
const handlePageChange = (page) => {
  currentPage.value = page;
};

// 切换每页大小
const handlePageSizeChange = (size) => {
  pageSize.value = size;
  currentPage.value = 1;
};

// 打开详情弹窗
const openDetailDialog = (row) => {
  if (!row) return;
  previewImageItem.value = null;
  imagePreviewVisible.value = false;
  detailRow.value = row;
  detailDialogVisible.value = true;
};

// 打开提交弹窗
const openSubmitDialog = (row) => {
  if (!row) return;
  submitRow.value = row;
  submitForm.value = {
    actualFinish: getCurrentDateValue(),
    executionNote: row.executionNote || ''
  };
  uploadFileList.value = [];
  submitDialogVisible.value = true;
};

const IMAGE_EXT_RE = /\.(png|jpe?g|gif|bmp|webp|svg|heic|heif)(?:$|[?#])/i;

const isImageByText = (value) => {
  if (!value) return false;
  return IMAGE_EXT_RE.test(String(value).trim());
};

const isImageAttachment = (name, url, mimeType) => {
  const normalizedMime = String(mimeType || '').trim().toLowerCase();
  if (normalizedMime.startsWith('image/')) return true;
  return isImageByText(name) || isImageByText(url);
};

const isDirectAttachmentUrl = (value) => /^https?:\/\//i.test(value) || value.startsWith('/');

const formatAttachment = (item) => {
  if (!item) return null;
  if (typeof item === 'string') {
    const text = item.trim();
    if (!text) return null;
    const url = isDirectAttachmentUrl(text) ? text : '';
    return {
      name: text,
      url,
      downloadUrl: '',
      originalUrl: url,
      fileKey: '',
      canDownload: Boolean(url),
      isImage: isImageAttachment(text, url, '')
    };
  }
  if (typeof item !== 'object') return null;

  const name =
    item.name ||
    item.file_name ||
    item.fileName ||
    item.filename ||
    item.url ||
    item.path ||
    item.id ||
    item._id ||
    '';
  const fileKey = String(item.qnKey || item.qn_key || item.key || item.file_key || item.fileKey || '').trim();
  const downloadUrl = String(item.downloadUrl || item.download_url || '').trim();
  const originalUrl = String(item.originalUrl || item.original_url || item.url || item.link || item.path || '').trim();
  const url = originalUrl || downloadUrl;
  const mimeType =
    item.mime_type ||
    item.mimeType ||
    item.content_type ||
    item.contentType ||
    item.file_type ||
    item.fileType ||
    item.type ||
    '';
  const normalizedName = String(name || '').trim();
  const normalizedUrl = String(url || '').trim();
  if (!normalizedName && !normalizedUrl && !fileKey) return null;
  return {
    name: normalizedName || normalizedUrl || fileKey || '未命名附件',
    url: normalizedUrl,
    downloadUrl,
    originalUrl,
    fileKey,
    canDownload: Boolean(downloadUrl || originalUrl || fileKey),
    isImage: isImageAttachment(normalizedName, normalizedUrl, mimeType)
  };
};

const normalizeAttachmentList = (value) => {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value.map(formatAttachment).filter(Boolean);
  }
  const single = formatAttachment(value);
  return single ? [single] : [];
};

const detailAttachments = computed(() => normalizeAttachmentList(detailRow.value?.siteUploadRaw));
const previewImageTitle = computed(() => previewImageItem.value?.name || '图片预览');
const previewImageUrl = computed(() => previewImageItem.value?.url || '');

const triggerDownload = (href, filename) => {
  const link = document.createElement('a');
  link.href = href;
  link.download = filename || '附件';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const parseAttachmentFilename = (contentDisposition) => {
  const headerValue = String(contentDisposition || '').trim();
  if (!headerValue) return '';

  const utf8Match = headerValue.match(/filename\*\s*=\s*UTF-8''([^;]+)/i);
  if (utf8Match?.[1]) {
    try {
      return decodeURIComponent(utf8Match[1].trim()).replace(/^["']|["']$/g, '');
    } catch (error) {
      console.warn('解析 UTF-8 文件名失败：', error);
    }
  }

  const plainMatch = headerValue.match(/filename\s*=\s*("?)([^";]+)\1/i);
  if (plainMatch?.[2]) {
    return plainMatch[2].trim();
  }

  return '';
};

const previewAttachment = (item) => {
  if (!item) return;
  if (item.isImage && item.url) {
    previewImageItem.value = item;
    imagePreviewVisible.value = true;
    return;
  }

  const targetUrl = item.originalUrl || item.downloadUrl || item.url;
  if (!targetUrl) {
    ElMessage.warning('该附件暂无可查看地址');
    return;
  }
  window.open(targetUrl, '_blank', 'noopener,noreferrer');
};

const downloadAttachment = async (item) => {
  if (!item?.canDownload) {
    ElMessage.warning('该附件暂无可下载地址');
    return;
  }

  let objectUrl = '';
  try {
    const response = await fetch(
      api.getProjectProgressAttachmentDownloadUrl({
        url: item.url,
        originalUrl: item.originalUrl,
        downloadUrl: item.downloadUrl,
        fileKey: item.fileKey,
        name: item.name || '附件'
      })
    );

    if (!response.ok) {
      let message = `下载失败（${response.status}）`;
      try {
        const payload = await response.json();
        message = payload?.msg || message;
      } catch (parseError) {
        console.warn('解析下载失败响应失败：', parseError);
      }
      throw new Error(message);
    }

    const contentDisposition = response.headers.get('Content-Disposition');
    const fallbackName = parseAttachmentFilename(contentDisposition) || item.name || '附件';
    const rawBlob = await response.blob();
    const fileBlob = new Blob([rawBlob], { type: 'application/octet-stream' });
    objectUrl = window.URL.createObjectURL(fileBlob);
    triggerDownload(objectUrl, fallbackName);
  } catch (error) {
    console.error('下载附件失败：', error);
    ElMessage.error(error?.message || '下载附件失败');
  } finally {
    if (objectUrl) {
      window.setTimeout(() => window.URL.revokeObjectURL(objectUrl), 1000);
    }
  }
};

// 构建上传表单数据
const buildUploadFormData = (fileList) => {
  const formData = new FormData();
  fileList.forEach((item) => {
    const rawFile = item.raw || item;
    formData.append('files', rawFile, rawFile.name);
  });
  return formData;
};

// 上传附件并返回文件信息
const uploadFiles = async () => {
  if (!uploadFileList.value.length) return [];
  const formData = buildUploadFormData(uploadFileList.value);
  const result = await api.uploadProjectProgressFiles(formData);
  if (result?.code === 200 && Array.isArray(result.data)) {
    return result.data;
  }
  throw new Error(result?.msg || '上传失败');
};

// 合并新旧附件列表
const mergeSiteUploads = (existing, uploaded) => {
  const existingList = Array.isArray(existing) ? existing : existing ? [existing] : [];
  const uploadedList = Array.isArray(uploaded) ? uploaded : uploaded ? [uploaded] : [];
  return [...existingList, ...uploadedList];
};

const canSubmitRow = (row) =>
  activeTab.value === 'todo' && Boolean(row?.recordId) && row.status === SUBMITTABLE_STATUS;
const canCreateDelayRequestRow = (row) =>
  activeTab.value === 'todo' && Boolean(row?.recordId) && DELAY_REQUEST_STATUS_SET.has(row.status);
const canApproveRow = (row) => activeTab.value === 'approval' && Boolean(row?.recordId);

const openDelayRequestDialog = (row) => {
  if (!canCreateDelayRequestRow(row)) return;
  delayRequestRow.value = row;
  delayRequestForm.value = {
    days: 1,
    reason: ''
  };
  delayRequestDialogVisible.value = true;
};

const handleCreateDelayRequest = async () => {
  if (!delayRequestRow.value?.recordId) {
    ElMessage.error('无法提交延期申请：缺少节点记录');
    return;
  }

  const delayDays = parsePositiveInt(delayRequestForm.value.days);
  if (!delayDays) {
    ElMessage.warning('请输入大于 0 的延期天数');
    return;
  }
  if (!delayRequestForm.value.reason.trim()) {
    ElMessage.warning('请填写延期原因');
    return;
  }

  const affectedNodes = delayRequestAffectedNodes.value;
  if (!affectedNodes.length) {
    ElMessage.warning('当前没有可申请延期的节点');
    return;
  }

  const reviewerCandidates = affectedNodes.flatMap((node) => [node.creatorRaw, node.updaterRaw]).filter(Boolean);
  const preparedNodes = affectedNodes.map((node) => ({
    record_id: node.recordId,
    main_stage_label: node.mainStageLabel || '',
    node_label: node.projectStageLabel || node.stageLabel || '',
    before_plan_start: node.planStart || '',
    before_plan_end: node.planEnd || '',
    executor_ids: getExecutorIds(node.executorRaw),
    executor_raw: node.executorRaw
  }));

  creatingDelayRequest.value = true;
  try {
    const result = await api.createProjectDelayRequest({
      project_name: delayRequestRow.value.projectName || '',
      project_code: delayRequestRow.value.projectCode || '',
      batch_no: delayRequestRow.value.batchNo || '',
      batch_name: delayRequestRow.value.batchName || '',
      anchor_record_id: delayRequestRow.value.recordId,
      delay_days: delayDays,
      reason: delayRequestForm.value.reason.trim(),
      applicant: {
        user_id: userProfile.value.user_id || userParam.value || '',
        name: userProfile.value.name || '',
        account: userProfile.value.account || ''
      },
      reviewer_candidates: reviewerCandidates,
      nodes: preparedNodes
    });

    if (result?.code === 200) {
      const responseData = result.data || {};
      const notifyFailedCount = Number(responseData.notify_failed_count || 0);
      const notifiedUserCount = Number(responseData.notified_user_count || 0);
      const notificationDisabled = Boolean(responseData.notification_disabled);
      const reviewerMissing = Boolean(responseData.reviewer_missing);
      const notifyErrorSummary = String(responseData.notify_error_summary || '').trim();
      if (notifyFailedCount > 0 || notificationDisabled || reviewerMissing) {
        const messageParts = ['延期申请已提交'];
        if (notifiedUserCount > 0) {
          messageParts.push(`已通知 ${notifiedUserCount} 位商务负责人`);
        }
        const ccNotifiedUserCount = Number(responseData.cc_notified_user_count || 0);
        if (ccNotifiedUserCount > 0) {
          messageParts.push(`已抄送 ${ccNotifiedUserCount} 位相关人员`);
        }
        if (notifyFailedCount > 0) {
          messageParts.push(`通知失败 ${notifyFailedCount} 位`);
        }
        if (notificationDisabled) {
          messageParts.push('未识别到商务负责人或抄送对象');
        }
        if (reviewerMissing && !notificationDisabled) {
          messageParts.push('未识别到商务负责人，已仅抄送相关人员');
        }
        if (notifyErrorSummary) {
          messageParts.push(notifyErrorSummary);
        }
        ElMessage.warning(messageParts.join('，'));
      } else {
        const ccNotifiedUserCount = Number(responseData.cc_notified_user_count || 0);
        const ccText = ccNotifiedUserCount > 0 ? `，并抄送 ${ccNotifiedUserCount} 位相关人员` : '';
        ElMessage.success(`延期申请已提交，并通知 ${notifiedUserCount} 位商务负责人${ccText}`);
      }
      delayRequestDialogVisible.value = false;
      await loadDelayReviewRequests();
    } else {
      ElMessage.error(result?.msg || '延期申请提交失败');
    }
  } catch (error) {
    console.error('延期申请提交失败：', error);
    ElMessage.error(error?.message || '延期申请提交失败');
  } finally {
    creatingDelayRequest.value = false;
  }
};

// 提交执行信息
const handleSubmit = async () => {
  if (!submitRow.value?.recordId) {
    ElMessage.error('无法提交：缺少记录ID');
    return;
  }
  if (submitRow.value.status !== SUBMITTABLE_STATUS) {
    ElMessage.warning('只有未完成状态才能提交，超期节点请先提交延期申请并通过后再提交');
    return;
  }
  if (!submitForm.value.actualFinish) {
    ElMessage.warning('实际完成时间不能为空');
    return;
  }
  if (!uploadFileList.value.length) {
    ElMessage.warning('请上传现场资料');
    return;
  }

  submitting.value = true;
  try {
    const actualFinish = getCurrentDateValue();
    submitForm.value.actualFinish = actualFinish;

    const payload = {
      actual_finish: actualFinish,
      execution_note: submitForm.value.executionNote
    };

    if (uploadFileList.value.length) {
      const uploadedFiles = await uploadFiles();
      payload.site_upload = mergeSiteUploads(submitRow.value.siteUploadRaw, uploadedFiles);
    }

    payload.status = '完成';
    if (getMemberId(submitRow.value.approverRaw)) {
      payload.submit_for_approval = true;
    }

    if (Object.keys(payload).length === 0) {
      ElMessage.warning('没有可提交的内容');
      submitting.value = false;
      return;
    }

    const result = await api.updateProjectProgress(submitRow.value.recordId, payload);
    if (result?.code === 200) {
      const nextStatus = result?.data?.status || payload.status || '';
      const messageText =
        result?.msg ||
        (isApprovalPending(nextStatus) ? '提交成功，已转审批' : '提交成功');
      if (result?.data?.notify_failed_count > 0) {
        ElMessage.warning(messageText);
      } else {
        ElMessage.success(messageText);
      }
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

const handleApproval = async (row, action) => {
  if (!row?.recordId) {
    ElMessage.error('无法审批：缺少记录ID');
    return;
  }

  const isApprove = action === 'approve';
  const confirmText = isApprove ? '确认审批通过该节点吗？' : '确认驳回该节点吗？';

  try {
    await ElMessageBox.confirm(confirmText, isApprove ? '审批通过' : '驳回审批', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: isApprove ? 'success' : 'warning'
    });
  } catch (error) {
    return;
  }

  loading.value = true;
  try {
    const result = await api.updateProjectProgress(row.recordId, {
      approval_action: action
    });
    if (result?.code === 200) {
      ElMessage.success(result?.msg || (isApprove ? '审批通过' : '已驳回'));
      await loadProgressRecords();
    } else {
      ElMessage.error(result?.msg || (isApprove ? '审批失败' : '驳回失败'));
    }
  } catch (error) {
    console.error('审批失败：', error);
    ElMessage.error(isApprove ? '审批失败' : '驳回失败');
  } finally {
    loading.value = false;
  }
};

const buildCurrentReviewerPayload = () => ({
  user_id: userProfile.value.user_id || userParam.value || '',
  userid: userProfile.value.userid || '',
  userId: userProfile.value.userId || '',
  name: userProfile.value.name || '',
  username: userProfile.value.username || '',
  user_name: userProfile.value.user_name || '',
  nickname: userProfile.value.nickname || '',
  realname: userProfile.value.realname || '',
  account: userProfile.value.account || '',
  uniqueid: userProfile.value.uniqueid || '',
  mobile: userProfile.value.mobile || '',
  email: userProfile.value.email || ''
});

const handleDelayReview = async (row, action) => {
  if (!row?.request_id) {
    ElMessage.error('无法审核：缺少延期申请ID');
    return;
  }
  if (!userValueMatchesCurrentUser(getDelayRequestBusinessOwner(row))) {
    ElMessage.warning('仅当前项目商务负责人可审核延期申请');
    return;
  }

  const isApprove = action === 'approve';
  const confirmText = isApprove
    ? `确认通过该延期申请，并顺延 ${row.node_count || row.nodes?.length || 0} 个节点 ${row.delay_days || 0} 天吗？`
    : '确认驳回该延期申请吗？';

  try {
    await ElMessageBox.confirm(confirmText, isApprove ? '通过延期申请' : '驳回延期申请', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: isApprove ? 'warning' : 'warning'
    });
  } catch (error) {
    return;
  }

  handlingDelayReviewId.value = row.request_id;
  handlingDelayReviewAction.value = action;
  loading.value = true;
  try {
    const requestPayload = {
      reviewer: buildCurrentReviewerPayload()
    };
    const result = isApprove
      ? await api.approveProjectDelayRequest(row.request_id, requestPayload)
      : await api.rejectProjectDelayRequest(row.request_id, requestPayload);
    if (result?.code === 200) {
      if (isApprove) {
        const summary = result?.data?.summary || {};
        const updatedCount = Number(summary.updated_count || 0);
        ElMessage.success(`延期申请已通过，成功顺延 ${updatedCount} 个节点`);
        await Promise.all([loadDelayReviewRequests(), loadProgressRecords()]);
      } else {
        ElMessage.success(result?.msg || '延期申请已驳回');
        await loadDelayReviewRequests();
      }
    } else {
      ElMessage.error(result?.msg || '延期申请审核失败');
    }
  } catch (error) {
    console.error('延期申请审核失败：', error);
    ElMessage.error(error?.message || '延期申请审核失败');
  } finally {
    loading.value = false;
    handlingDelayReviewId.value = '';
    handlingDelayReviewAction.value = '';
  }
};

// 上传超限提示
const handleUploadExceed = () => {
  ElMessage.warning('最多上传 20 个文件');
};

// 同步上传文件列表
const handleUploadFileListChange = (fileList) => {
  uploadFileList.value = Array.isArray(fileList) ? fileList : [];
};

// 关闭提交弹窗时重置状态
watch(submitDialogVisible, (visible) => {
  if (!visible) {
    submitRow.value = null;
    uploadFileList.value = [];
  }
});

watch(delayRequestDialogVisible, (visible) => {
  if (!visible) {
    delayRequestRow.value = null;
    delayRequestForm.value = {
      days: 1,
      reason: ''
    };
  }
});

// 监听窗口尺寸切换布局
const handleResize = () => {
  isMobile.value = window.innerWidth <= 768;
};

// 分页边界修正
watch(
  [tableRows, delayReviewRows, pageSize],
  () => {
    const maxPage = Math.max(1, Math.ceil(viewTotalCount.value / pageSize.value));
    if (currentPage.value > maxPage) {
      currentPage.value = maxPage;
    }
  },
  { immediate: true }
);

watch(activeTab, () => {
  currentPage.value = 1;
});

// 根据用户参数拉取用户信息
const resolveUserProfile = async () => {
  if (!userParam.value) return;
  try {
    const result = await api.getUserInfo(userParam.value);
    if (result?.code === 200 && result.data) {
      userProfile.value = {
        ...result.data,
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
          collectUserTokens(item).includes(normalizeToken(userParam.value))
      );
      if (match) {
        userProfile.value = {
          ...match,
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

const syncCurrentUser = async () => {
  const nextUserId = resolveWebpageUserId(route);
  if (nextUserId === userParam.value) {
    return;
  }

  userParam.value = nextUserId;
  userProfile.value = {
    user_id: '',
    name: '',
    account: ''
  };

  if (!userParam.value) {
    ElMessage.warning('未获取到用户ID，已隐藏执行数据');
    return;
  }

  await resolveUserProfile();
};

watch(
  () => route.fullPath,
  async () => {
    await syncCurrentUser();
    await loadDelayReviewRequests();
  }
);

// 页面初始化
onMounted(async () => {
  handleResize();
  window.addEventListener('resize', handleResize);
  await loadProjectManagers();
  await syncCurrentUser();
  await Promise.all([loadProgressRecords(), loadDelayReviewRequests()]);
  console.log('Webpage User ID:', userParam.value);
});

// 页面卸载时移除监听
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
  gap: 8px;
  /* margin-bottom: 20px; */
  background: #fff;
  /* border-radius: 10px; */
  padding: 8px;
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
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
  gap: 8px;
}

.user-alert {
  margin-bottom: 18px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  /* margin-bottom: 8px; */
}

.view-tabs-card {
  background: #fff;
  border-radius: 10px;
  padding: 0 16px;
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
}

.delay-request-hint {
  margin-top: 4px;
  color: #606266;
  line-height: 1.6;
}

.delay-request-preview-list {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.delay-request-preview-tag,
.delay-request-preview-more {
  padding: 4px 10px;
  border-radius: 999px;
  background: #f5f7fa;
  color: #606266;
  font-size: 12px;
}

.summary-card {
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
  display: flex;
  align-items: center;
  gap: 8px;
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
  gap: 8px;
}

.project-title {
  font-weight: 600;
  color: #303133;
}

.project-stage {
  color: #606266;
  font-size: 13px;
}

.project-batch {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  color: #1677ff;
  background: rgba(22, 119, 255, 0.12);
  border-radius: 999px;
  padding: 2px 10px;
  width: fit-content;
}

.mobile-only {
  display: none;
}

.mobile-group-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
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
  gap: 8px;
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
  gap: 8px;
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

.mobile-info--stack {
  flex-direction: column;
}

.mobile-info .label {
  color: #909399;
}

.mobile-card-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.detail-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
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
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fff;
}

.attachment-name {
  flex: 1;
  min-width: 0;
  color: #303133;
  font-size: 13px;
  line-height: 1.5;
  word-break: break-all;
}

.attachment-actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  gap: 4px;
}

.image-preview-body {
  min-height: 220px;
  max-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-preview-main {
  width: 100%;
  max-height: 68vh;
}

.submit-overdue-alert {
  margin-bottom: 12px;
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

  .attachment-item {
    align-items: flex-start;
    flex-direction: column;
    gap: 6px;
  }

  .attachment-actions {
    width: 100%;
    justify-content: flex-end;
    flex-wrap: wrap;
  }

  .pagination-row {
    display: none;
  }
}
</style>
