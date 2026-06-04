<template>
  <el-config-provider :locale="zhCn">
    <div class="page-root">
    <div class="main-content">
    <div class="page-container">
      <div class="progress-visual-card">
        <div class="visual-header">
          <div class="search-row">
            <el-select
              v-model="currentProjectKey"
              placeholder="选择项目"
              filterable
              style="width: 320px"
            >
              <el-option
                v-for="item in projectOptions"
                :key="item.key"
                :label="item.label"
                :value="item.key"
              />
            </el-select>
            <!-- <el-input
              v-model="searchQuery"
              placeholder="搜索项目名称/编号..."
              style="width: 240px"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input> -->
            <el-button type="primary" :loading="loading" @click="handleSearch">查询</el-button>
          </div>

          <div class="project-name-large">
            {{ currentProjectLabel }}
          </div>

          <div class="status-tags">
            <!-- <el-tag type="info" size="large" effect="plain">非线性节点看板</el-tag> -->
            <el-tag :type="overallProgressType" size="large" effect="dark">
              {{ overallProgress }}% 完成
            </el-tag>
          </div>
        </div>

        <div v-if="timelineMainNodes.length" class="segmented-timeline-wrapper">

          <div class="segmented-progress">
            <div class="segmented-progress__fill" :style="{ width: `${overallProgress}%` }"></div>
          </div>

          <div class="node-markers">
            <div
              v-for="(node, index) in timelineMainNodes"
              :key="`${node.id || 'marker'}-${index}`"
              class="marker-cell"
            >
              <div
                class="marker-dot"
                :class="{
                  'is-done': isDone(node.status),
                  'is-overdue': node.status === '超期',
                  'is-pending': node.status === '未完成'
                }"
              >
                <el-icon v-if="isDone(node.status)" size="14"><Check /></el-icon>
                <el-icon v-else-if="node.status === '超期'" size="14"><WarningFilled /></el-icon>
                <span v-else class="marker-pending-dot"></span>
                <el-icon v-if="isDone(node.status) && node.isMilestone" class="node-flag-icon">
                  <Flag />
                </el-icon>
              </div>
              <div class="marker-label">{{ node.name }}</div>
            </div>
          </div>
        </div>
        <div v-else class="empty-timeline">
          <el-empty description="暂无进度数据" />
        </div>
      </div>

      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="card-header">
            <div class="card-icon is-primary">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="card-label">整体进度</div>
          </div>
          <div class="card-value accent-blue">{{ overallProgress }}%</div>
        </div>
        <div class="dashboard-card">
          <div class="card-header">
            <div class="card-icon is-danger">
              <el-icon><WarningFilled /></el-icon>
            </div>
            <div class="card-label">预警节点总数(个)</div>
          </div>
          <div class="card-value accent-danger">{{ totalWarningLevelCount }}</div>
        </div>
        <div class="dashboard-card">
          <div class="card-header">
            <div class="card-icon is-warning">
              <el-icon><Flag /></el-icon>
            </div>
            <div class="card-label">里程碑达成</div>
          </div>
          <div class="card-value accent-warning">
            {{ milestoneReachedCount }}
            <span class="muted">/ {{ milestoneTotalCount }}</span>
          </div>
        </div>
        <div class="dashboard-card">
          <div class="card-header">
            <div class="card-icon is-danger">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="card-label">预警数量(个)</div>
          </div>
          <div class="card-value accent-danger">
            {{ warningLevelCount }}
          </div>
        </div>
      </div>

      <div class="progress-table-card">
        <div class="table-header">
          <div class="table-title">
            <h3>项目节点执行明细</h3>
          </div>
          <div class="table-actions">
            <el-button
              type="primary"
              plain
              size="small"
              :disabled="!currentBatchCard"
              @click="openBatchAttachmentDialog"
            >
              附件管理
            </el-button>
            <el-button
              v-if="isProjectManager"
              type="primary"
              size="small"
              :disabled="!stageOptions.length || !currentBatchCard"
              @click="openCreateNodeDialog()"
            >
              新增节点
            </el-button>
            <el-button
              v-if="isProjectManager"
              type="primary"
              plain
              size="small"
              :disabled="!currentBatchCard"
              @click="openEditBatchDialog"
            >
              编辑批次
            </el-button>
            <el-button
              v-if="isProjectManager"
              type="primary"
              plain
              size="small"
              :disabled="!batchTemplateRecords.length"
              @click="openCreateBatchDialog"
            >
              新增批次
            </el-button>
          </div>

        </div>
                <div v-if="batchCards.length" class="batch-card-panel">
          <div class="batch-card-header">
            <div class="batch-card-title">批次列表</div>
            <div class="batch-card-desc">点击卡片查看对应批次</div>
          </div>
          <div class="batch-card-grid">
            <button
              v-for="card in batchCards"
              :key="card.key"
              type="button"
              class="batch-card-item"
              :class="{ 'is-active': card.key === currentBatchKey }"
              @click="handleBatchCardClick(card.key)"
            >
              <div class="batch-card-main">{{ card.label }}</div>
              <div class="batch-card-sub">{{ card.subLabel }}</div>
            </button>
          </div>
        </div>

        <el-table
          :data="tableRows"
          style="width: 100%"
          stripe
          border
          v-loading="loading"
          row-key="id"
          :tree-props="{ children: 'children' }"
          :default-expand-all="true"
          :row-class-name="getRowClass"
        >
          <el-table-column label="主阶段" min-width="100" fixed="left">
            <template #default="{ row }">
              <span v-if="row.isGroup" class="stage-group-title">{{ row.mainStageLabel || row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column label="节点名称" min-width="100">
            <template #default="{ row }">
              <span v-if="row.isGroup" class="stage-node-count">{{ row.nodeCount }} 个节点</span>
              <div v-else class="stage-node-item">
                <span class="stage-node-dot"></span>
                <span class="stage-node-text">{{ row.nodeLabel || row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="责任人" width="140" align="center">
            <template #default="{ row }">
              <span v-if="!row.isGroup">{{ row.executorName }}</span>
              <span v-else class="stage-placeholder">--</span>
            </template>
          </el-table-column>
          <el-table-column label="审批人" width="140" align="center">
            <template #default="{ row }">
              <span v-if="!row.isGroup">{{ row.approverName }}</span>
              <span v-else class="stage-placeholder">--</span>
            </template>
          </el-table-column>
          <el-table-column label="计划结束日期" width="140" align="center">
            <template #default="{ row }">
              <span v-if="!row.isGroup">{{ row.planEnd }}</span>
              <span v-else class="stage-placeholder">--</span>
            </template>
          </el-table-column>
          <el-table-column label="完成时间" width="140" align="center">
            <template #default="{ row }">
              <span v-if="!row.isGroup">{{ row.actualFinish }}</span>
              <span v-else class="stage-placeholder">--</span>
            </template>
          </el-table-column>
          <el-table-column label="节点序号" width="90" align="center">
            <template #default="{ row }">
              <span v-if="!row.isGroup && row.projectStageOrder !== null">{{ row.projectStageOrder }}</span>
              <span v-else class="stage-placeholder">--</span>
            </template>
          </el-table-column>
          <!-- <el-table-column label="批次" width="200" align="center">
            <template #default="{ row }">
              <span v-if="!row.isGroup">{{ row.batchCardLabel }}</span>
              <span v-else class="stage-placeholder">--</span>
            </template>
          </el-table-column> -->
          <el-table-column label="当前状态" width="120" align="center">
            <template #default="{ row }">
              <el-tag v-if="!row.isGroup" :type="getStatusTag(row.status)" effect="dark">
                {{ displayStatus(row.status) }}
              </el-tag>
              <span v-else class="stage-placeholder">--</span>
            </template>
             </el-table-column>
              <el-table-column v-if="false" label="计划开始日期" width="140" align="center">
                <template #default="{ row }">
                  <span v-if="!row.isGroup">{{ row.planStart }}</span>
                  <span v-else class="stage-placeholder">--</span>
                </template>
              </el-table-column>
          <el-table-column label="预警等级" width="130" align="center">
            <template #default="{ row }">
              <el-tag v-if="!row.isGroup" :type="getWarningTag(row.warningLevel)" effect="plain">
                {{ row.warningLevel || '正常' }}
              </el-tag>
              <span v-else class="stage-placeholder">--</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" :width="isProjectManager ? 220 : 90" align="center" fixed="right">
            <template #default="{ row }">
              <div v-if="!row.isGroup" class="action-buttons">
                <el-button
                  v-if="isProjectManager && row.mainStageLabel"
                  class="action-link"
                  type="primary"
                  link
                  size="small"
                  @click="openCreateNodeDialog(row)"
                >
                  新增
                </el-button>
                <el-button
                  class="action-link"
                  type="primary"
                  link
                  size="small"
                  @click="openDetailDialog(row)"
                >
                  详情
                </el-button>
                <el-button
                  v-if="canManageNode(row)"
                  class="action-link"
                  type="primary"
                  link
                  size="small"
                  @click="openDelayDialog(row)"
                >
                  一键延期
                </el-button>
                <el-button
                  v-if="canManageNode(row)"
                  class="action-link"
                  type="primary"
                  link
                  size="small"
                  @click="openEditDialog(row)"
                >
                  编辑
                </el-button>
                <el-button
                  v-if="canManageNode(row)"
                  class="action-link action-link--danger"
                  type="danger"
                  link
                  size="small"
                  @click="handleDeleteNode(row)"
                >
                  删除
                </el-button>
              </div>
              <span v-else class="stage-placeholder">--</span>
            </template>
          </el-table-column>
          </el-table>

      </div>
    </div>
  </div>

    <el-dialog v-model="detailDialogVisible" title="节点填报详情" width="720px">
      <div v-if="detailRow" class="detail-body">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="项目名称">{{ detailRow.projectName || '--' }}</el-descriptions-item>
          <el-descriptions-item label="项目编号">{{ detailRow.projectCode || '--' }}</el-descriptions-item>
          <el-descriptions-item label="主阶段">{{ detailRow.mainStageLabel || '--' }}</el-descriptions-item>
          <el-descriptions-item label="节点名称">{{ detailRow.nodeLabel || detailRow.name || '--' }}</el-descriptions-item>
          <el-descriptions-item label="批次编号">{{ detailRow.batchNo || '--' }}</el-descriptions-item>
          <el-descriptions-item label="批次名称">{{ detailRow.batchName || '--' }}</el-descriptions-item>
          <el-descriptions-item v-if="false" label="计划开始日期">{{ detailRow.planStart || '--' }}</el-descriptions-item>
          <el-descriptions-item label="计划结束日期">{{ detailRow.planEnd || '--' }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ detailRow.actualFinish || '--' }}</el-descriptions-item>
          <el-descriptions-item label="当前状态">{{ displayStatus(detailRow.status) }}</el-descriptions-item>
          <el-descriptions-item label="预警等级">{{ detailRow.warningLevel || '正常' }}</el-descriptions-item>
          <el-descriptions-item label="责任人">{{ detailRow.executorName || '--' }}</el-descriptions-item>
          <el-descriptions-item label="审批人">{{ detailRow.approverName || '--' }}</el-descriptions-item>
          <el-descriptions-item label="执行说明" :span="2">
            {{ detailRow.executionNote || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="超期原因" :span="2">
            {{ detailRow.overdueReason || '--' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-attachments">
          <div class="attachment-label">现场资料</div>
          <div class="attachment-list">
            <el-tag v-if="!detailAttachments.length" type="info">暂无附件</el-tag>
            <div v-else class="attachment-grid">
              <div
                v-for="(item, index) in detailAttachments"
                :key="'detail-attachment-' + index"
                class="attachment-item"
              >
                <div class="attachment-name" :title="item.name">{{ item.name }}</div>
                <div class="attachment-actions">
                  <template v-if="isProjectManager">
                    <el-button
                      v-if="item.isImage && item.url"
                      link
                      type="primary"
                      @click="previewAttachmentImage(item)"
                    >
                      预览图片
                    </el-button>
                    <el-button v-if="item.canDownload" link type="primary" @click="downloadAttachment(item)">
                      下载
                    </el-button>
                    <span v-if="!item.canDownload" class="attachment-text">无可用链接</span>
                  </template>
                  <span v-else class="attachment-text">请在附件管理中下载</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无详情数据" />
      <template #footer>
        <el-button type="primary" @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="imagePreviewVisible"
      :title="previewImageTitle"
      width="820px"
      top="5vh"
      append-to-body
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
        <el-button
          v-if="isProjectManager"
          type="primary"
          :disabled="!previewImageUrl"
          @click="downloadAttachment(previewImageItem)"
        >
          下载图片
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="batchAttachmentDialogVisible"
      :title="batchAttachmentDialogTitle"
      width="920px"
      append-to-body
    >
      <div class="batch-attachment-summary">
        {{ batchAttachmentSummaryText }}
      </div>
      <div v-if="batchAttachmentEntries.length" class="batch-attachment-grid">
        <div
          v-for="item in batchAttachmentEntries"
          :key="item.pinId"
          class="batch-attachment-card"
          :class="{ 'is-pinned': item.isPinned }"
        >
          <div class="batch-attachment-card__main">
            <div class="batch-attachment-card__title">
              <span class="batch-attachment-card__name" :title="item.name">{{ item.name }}</span>
              <el-tag v-if="item.isPinned" size="small" type="warning" effect="plain">已置顶</el-tag>
            </div>
            <div class="batch-attachment-card__meta">
              <span>主阶段：{{ item.mainStageLabel || '--' }}</span>
              <span>节点：{{ item.nodeLabel || '--' }}</span>
              <span>责任人：{{ item.executorName || '--' }}</span>
            </div>
          </div>
          <div class="batch-attachment-card__actions">
            <el-button link type="warning" @click="toggleBatchAttachmentPin(item)">
              {{ item.isPinned ? '取消置顶' : '置顶' }}
            </el-button>
            <el-button
              v-if="item.canView"
              link
              type="primary"
              @click="viewBatchAttachment(item)"
            >
              查看
            </el-button>
            <el-button
              v-if="item.canDownload"
              link
              type="primary"
              @click="downloadAttachment(item)"
            >
              下载
            </el-button>
            <template v-if="isProjectManager">
              <el-button
                link
                type="primary"
                :disabled="Boolean(attachmentActionKey)"
                :loading="attachmentActionKey === getAttachmentActionKey(item)"
                @click="handleEditBatchAttachment(item)"
              >
                编辑
              </el-button>
              <el-button
                link
                type="danger"
                :disabled="Boolean(attachmentActionKey)"
                :loading="attachmentActionKey === getAttachmentActionKey(item)"
                @click="handleDeleteBatchAttachment(item)"
              >
                删除
              </el-button>
            </template>
            <span v-if="!item.canView && !item.canDownload" class="attachment-text">无可用链接</span>
          </div>
        </div>
      </div>
      <el-empty v-else description="当前批次暂无附件" />
      <template #footer>
        <el-button @click="batchAttachmentDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="createNodeDialogVisible" title="新增节点" width="560px">
    <el-form label-width="110px">
      <el-form-item label="主阶段">
        <el-select
          v-model="createNodeForm.stageKey"
          placeholder="请选择主阶段"
          filterable
          style="width: 100%"
        >
          <el-option
            v-for="item in stageOptions"
            :key="item.key"
            :label="item.order !== null ? `${item.label}（阶段 ${item.order}）` : item.label"
            :value="item.key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="节点名称">
        <el-input
          v-model="createNodeForm.nodeName"
          maxlength="40"
          show-word-limit
          placeholder="请输入节点名称"
        />
      </el-form-item>
      <el-form-item label="插入序号">
        <el-input-number
          v-model="createNodeForm.orderNo"
          :min="1"
          :max="Math.max(createNodeOrderMax, 1)"
          :step="1"
          :precision="0"
          controls-position="right"
          style="width: 100%"
        />
        <div class="dialog-hint">{{ createNodeScopeHint }}</div>
      </el-form-item>
      <el-form-item v-if="false" label="计划开始日期">
        <el-date-picker
          v-model="createNodeForm.planStart"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="请选择日期"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="计划结束日期">
        <el-date-picker
          v-model="createNodeForm.planEnd"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="请选择日期"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="责任人">
        <el-select
          v-model="createNodeForm.executorIds"
          multiple
          collapse-tags
          collapse-tags-tooltip
          filterable
          placeholder="请选择成员"
          style="width: 100%"
          :loading="memberLoading"
        >
          <el-option
            v-for="item in memberOptions"
            :key="item.id"
            :label="item.label"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="审批人">
        <el-select
          v-model="createNodeForm.approverId"
          filterable
          clearable
          placeholder="请选择成员"
          style="width: 100%"
          :loading="memberLoading"
        >
          <el-option
            v-for="item in memberOptions"
            :key="item.id"
            :label="item.label"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="同步所有批次">
        <div class="dialog-switch-wrap">
          <el-switch v-model="createNodeForm.syncAllBatches" />
          <span class="dialog-switch-label">
            开启后会在当前项目所有批次的同主阶段插入该节点
          </span>
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="createNodeDialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="creatingNode" @click="handleCreateNode">确定新增</el-button>
    </template>
    </el-dialog>

    <el-dialog v-model="editDialogVisible" title="编辑节点" width="560px">
    <el-form label-width="110px">
      <el-form-item label="主阶段">
        <el-input :model-value="editRow?.mainStageLabel || '--'" disabled />
      </el-form-item>
      <el-form-item label="节点名称">
        <el-input
          v-model="editForm.nodeName"
          maxlength="40"
          show-word-limit
          placeholder="请输入节点名称"
        />
      </el-form-item>
      <el-form-item label="节点序号">
        <el-input-number
          v-model="editForm.orderNo"
          :min="1"
          :max="Math.max(editNodeOrderMax, 1)"
          :step="1"
          :precision="0"
          controls-position="right"
          style="width: 100%"
        />
        <div class="dialog-hint">{{ editNodeOrderHint }}</div>
      </el-form-item>
      <el-form-item v-if="false" label="计划开始日期">
        <el-date-picker
          v-model="editForm.planStart"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="请选择日期"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="计划结束日期">
        <el-date-picker
          v-model="editForm.planEnd"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="请选择日期"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="责任人">
        <el-select
          v-model="editForm.executorIds"
          multiple
          collapse-tags
          collapse-tags-tooltip
          filterable
          placeholder="请选择成员"
          style="width: 100%"
          :loading="memberLoading"
        >
          <el-option
            v-for="item in memberOptions"
            :key="item.id"
            :label="item.label"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="审批人">
        <el-select
          v-model="editForm.approverId"
          filterable
          clearable
          placeholder="请选择成员"
          style="width: 100%"
          :loading="memberLoading"
        >
          <el-option
            v-for="item in memberOptions"
            :key="item.id"
            :label="item.label"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="editDialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="savingEdit" @click="handleSaveEdit">保存</el-button>
    </template>
    </el-dialog>

    <el-dialog v-model="delayDialogVisible" title="一键延期" width="520px">
      <el-form label-width="110px">
        <el-form-item label="起始节点">
          <el-input :model-value="delayRow?.nodeLabel || delayRow?.name || '--'" disabled />
        </el-form-item>
        <el-form-item label="所属批次">
          <el-input :model-value="currentBatchCard?.label || '--'" disabled />
        </el-form-item>
        <el-form-item label="延期天数">
          <el-input-number
            v-model="delayForm.days"
            :min="1"
            :step="1"
            :precision="0"
            controls-position="right"
            style="width: 100%"
            placeholder="请输入延期天数"
          />
        </el-form-item>
      </el-form>
      <div class="delay-dialog-hint">
        {{ delayScopeHint }}
      </div>
      <div v-if="delayAffectedNodes.length" class="delay-preview-list">
        <span
          v-for="item in delayAffectedPreviewNodes"
          :key="item.recordId || item.id"
          class="delay-preview-tag"
        >
          {{ item.nodeLabel || item.name || '--' }}
        </span>
        <span v-if="delayAffectedNodes.length > delayAffectedPreviewNodes.length" class="delay-preview-more">
          等 {{ delayAffectedNodes.length }} 个节点
        </span>
      </div>
      <template #footer>
        <el-button @click="delayDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="delayingNodes" @click="handleApplyDelay">
          确认延期
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="delayRequestReviewDialogVisible" title="延期申请审核" width="920px">
      <el-table
        :data="delayRequests"
        stripe
        border
        v-loading="delayRequestReviewLoading"
        empty-text="当前项目暂无待审核延期申请"
      >
        <el-table-column label="申请时间" width="170" align="center">
          <template #default="{ row }">{{ row.created_at || '--' }}</template>
        </el-table-column>
        <el-table-column label="批次" min-width="140">
          <template #default="{ row }">{{ buildBatchCardLabel(row.batch_no, row.batch_name) || '--' }}</template>
        </el-table-column>
        <el-table-column label="起始节点" min-width="180">
          <template #default="{ row }">{{ row.nodes?.[0]?.node_label || row.nodes?.[0]?.main_stage_label || '--' }}</template>
        </el-table-column>
        <el-table-column label="申请人" width="120" align="center">
          <template #default="{ row }">{{ formatUser(row.applicant) }}</template>
        </el-table-column>
        <el-table-column label="延期天数" width="90" align="center">
          <template #default="{ row }">{{ row.delay_days || 0 }}</template>
        </el-table-column>
        <el-table-column label="申请原因" min-width="180">
          <template #default="{ row }">{{ row.reason || '--' }}</template>
        </el-table-column>
        <el-table-column label="节点数" width="80" align="center">
          <template #default="{ row }">{{ row.node_count || row.nodes?.length || 0 }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              size="small"
              :loading="handlingDelayRequestId === row.request_id && handlingDelayRequestAction === 'approve'"
              @click="handleApproveDelayRequest(row)"
            >
              通过
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              :loading="handlingDelayRequestId === row.request_id && handlingDelayRequestAction === 'reject'"
              @click="handleRejectDelayRequest(row)"
            >
              驳回
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="delayRequestReviewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="createBatchDialogVisible" title="新增批次" width="460px">
      <el-form label-width="96px">
        <el-form-item label="批次编号">
          <el-input-number
            v-model="createBatchForm.batchNo"
            :min="1"
            :step="1"
            :precision="0"
            controls-position="right"
            style="width: 100%"
            placeholder="请输入批次编号"
          />
        </el-form-item>
        <el-form-item label="批次名称">
          <el-input
            v-model="createBatchForm.batchName"
            maxlength="40"
            show-word-limit
            placeholder="请输入批次名称"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createBatchDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="creatingBatch" @click="handleCreateBatch">确定新增</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editBatchDialogVisible" title="编辑批次" width="460px">
      <el-form label-width="96px">
        <el-form-item label="批次编号">
          <el-input-number
            v-model="editBatchForm.batchNo"
            :min="1"
            :step="1"
            :precision="0"
            controls-position="right"
            style="width: 100%"
            placeholder="请输入批次编号"
          />
        </el-form-item>
        <el-form-item label="批次名称">
          <el-input
            v-model="editBatchForm.batchName"
            maxlength="40"
            show-word-limit
            placeholder="请输入批次名称"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editBatchDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editingBatch" @click="handleEditBatch">保存批次</el-button>
      </template>
    </el-dialog>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { ElMessage, ElMessageBox, ElConfigProvider } from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { useRoute } from 'vue-router';
import {
  Search,
  Check,
  WarningFilled,
  Flag,
  TrendCharts,
  Bell
} from '@element-plus/icons-vue';
import api from '../api/client';
import { resolveWebpageUserId } from '../utils/webpageUser';

const buildEmptyCreateNodeForm = () => ({
  stageKey: '',
  nodeName: '',
  orderNo: 1,
  planStart: '',
  planEnd: '',
  executorIds: [],
  approverId: '',
  syncAllBatches: false
});

const buildEmptyEditForm = () => ({
  nodeName: '',
  orderNo: 1,
  planStart: '',
  planEnd: '',
  executorIds: [],
  approverId: ''
});

const buildEmptyDelayForm = () => ({
  days: 1
});

const searchQuery = ref('');
const loading = ref(false);
const progressRecords = ref([]);
const projectSummaryRecords = ref([]);
const orderCache = ref(new Map());
const currentProjectKey = ref('');
const currentBatchKey = ref('');
const detailDialogVisible = ref(false);
const detailRow = ref(null);
const imagePreviewVisible = ref(false);
const previewImageItem = ref(null);
const batchAttachmentDialogVisible = ref(false);
const batchAttachmentPinnedIds = ref([]);
const attachmentActionKey = ref('');
const createNodeDialogVisible = ref(false);
const creatingNode = ref(false);
const createNodeForm = ref(buildEmptyCreateNodeForm());
const editDialogVisible = ref(false);
const savingEdit = ref(false);
const editForm = ref(buildEmptyEditForm());
const editRow = ref(null);
const delayDialogVisible = ref(false);
const delayingNodes = ref(false);
const delayForm = ref(buildEmptyDelayForm());
const delayRow = ref(null);
const delayRequestReviewDialogVisible = ref(false);
const delayRequestReviewLoading = ref(false);
const delayRequests = ref([]);
const handlingDelayRequestId = ref('');
const handlingDelayRequestAction = ref('');
const originalExecutorIds = ref([]);
const originalApproverId = ref('');
const originalPlanRange = ref({
  planStart: '',
  planEnd: ''
});
const members = ref([]);
const memberLoading = ref(false);
const createBatchDialogVisible = ref(false);
const creatingBatch = ref(false);
const createBatchForm = ref({
  batchNo: null,
  batchName: ''
});
const editBatchDialogVisible = ref(false);
const editingBatch = ref(false);
const editBatchForm = ref({
  batchNo: null,
  batchName: ''
});
const editBatchSourceKey = ref('');
const userParam = ref('');
const userProfile = ref({
  user_id: '',
  name: '',
  account: ''
});
const projectManagerMembers = ref([]);
const projectManagerLoading = ref(false);
const route = useRoute();

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

const addDaysToDate = (value, days) => {
  const parsed = parseDateValue(value);
  if (!parsed) return '';
  const next = new Date(parsed.getTime());
  next.setDate(next.getDate() + days);
  return formatDate(next);
};

// 表格日期展示格式
const formatDateCell = (value) => {
  if (!value) return '';
  return formatDate(value);
};

// 去除姓名末尾括号中的账号信息，例如 "张三 (zhangsan)" -> "张三"
const stripAccountSuffix = (value) => {
  if (value === null || value === undefined) return '';
  return String(value)
    .replace(/\s*[\(（][^()（）]*[\)）]\s*$/g, '')
    .trim();
};

// 格式化执行人显示
const formatUser = (value) => {
  if (!value) return '--';
  if (Array.isArray(value)) {
    const names = value
      .map((item) => {
        if (!item) return '';
        if (typeof item === 'object') {
          return stripAccountSuffix(item.name) || String(item._id || item.user_id || item.id || '').trim();
        }
        return stripAccountSuffix(item);
      })
      .filter(Boolean);
    return names.length ? names.join(' / ') : '--';
  }
  if (typeof value === 'object') {
    return stripAccountSuffix(value.name) || value._id || '--';
  }
  return stripAccountSuffix(value) || '--';
};

// 提取执行人 ID 列表
const getExecutorIds = (value) => {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value
      .map((item) => {
        if (!item) return '';
        if (typeof item === 'object') return item.user_id || item._id || item.id || '';
        return String(item);
      })
      .filter(Boolean);
  }
  if (typeof value === 'object') {
    return [value.user_id || value._id || value.id || ''].filter(Boolean);
  }
  return [String(value)];
};

const getMemberId = (value) => {
  const ids = getExecutorIds(value);
  return ids.length ? ids[0] : '';
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

const formatAttachment = (item) => {
  if (!item) return null;
  if (typeof item === 'string') {
    const text = item.trim();
    if (!text) return null;
    const url = /^https?:\/\//i.test(text) ? text : '';
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
  const fileKey = String(item.qnKey || item.qn_key || item.key || item.file_key || '').trim();
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
  if (!normalizedName && !normalizedUrl) return null;
  return {
    name: normalizedName || normalizedUrl,
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

const normalizeAttachmentPayloadList = (value) => {
  if (!value) return [];
  return Array.isArray(value) ? [...value] : [value];
};

const detailAttachments = computed(() => normalizeAttachmentList(detailRow.value?.siteUploadRaw));
const previewImageTitle = computed(() => previewImageItem.value?.name || '图片预览');
const previewImageUrl = computed(() => previewImageItem.value?.url || '');

const BATCH_ATTACHMENT_PIN_STORAGE_KEY = 'project-progress-batch-attachment-pins';

const currentBatchAttachmentScopeKey = computed(() => [
  currentProject.value.projectCode || '',
  currentProject.value.projectName || '',
  currentProject.value.projectType || '',
  currentBatchDescriptor.value?.key || ''
].join('||'));

const loadBatchAttachmentPinnedIds = () => {
  if (typeof window === 'undefined') return [];
  const scopeKey = currentBatchAttachmentScopeKey.value;
  if (!scopeKey) return [];
  try {
    const raw = window.localStorage.getItem(BATCH_ATTACHMENT_PIN_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    const ids = parsed?.[scopeKey];
    return Array.isArray(ids) ? ids.map((item) => String(item)).filter(Boolean) : [];
  } catch (error) {
    console.warn('读取批次附件置顶配置失败：', error);
    return [];
  }
};

const saveBatchAttachmentPinnedIds = (ids) => {
  if (typeof window === 'undefined') return;
  const scopeKey = currentBatchAttachmentScopeKey.value;
  if (!scopeKey) return;
  try {
    const raw = window.localStorage.getItem(BATCH_ATTACHMENT_PIN_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    parsed[scopeKey] = Array.from(new Set((ids || []).map((item) => String(item)).filter(Boolean)));
    window.localStorage.setItem(BATCH_ATTACHMENT_PIN_STORAGE_KEY, JSON.stringify(parsed));
  } catch (error) {
    console.warn('保存批次附件置顶配置失败：', error);
  }
};

const buildBatchAttachmentPinId = (attachment, node, index) =>
  [
    node.recordId || node.id || '',
    attachment.fileKey || attachment.originalUrl || attachment.downloadUrl || attachment.url || '',
    attachment.name || '',
    index
  ].join('::');

const batchAttachmentEntries = computed(() => {
  const pinnedSet = new Set(batchAttachmentPinnedIds.value);
  const entries = [];
  timelineNodes.value.forEach((node, nodeIndex) => {
    const sourceAttachments = normalizeAttachmentPayloadList(node.siteUploadRaw);
    sourceAttachments.forEach((sourceAttachment, attachmentIndex) => {
      const attachment = formatAttachment(sourceAttachment);
      if (!attachment) return;
      const pinId = buildBatchAttachmentPinId(attachment, node, attachmentIndex);
      entries.push({
        ...attachment,
        pinId,
        recordId: node.recordId || '',
        attachmentIndex,
        isPinned: pinnedSet.has(pinId),
        canView: Boolean(attachment.originalUrl || attachment.downloadUrl || attachment.url),
        nodeLabel: node.nodeLabel || node.name || '--',
        mainStageLabel: node.mainStageLabel || '--',
        executorName: node.executorName || '--',
        nodeOrder: nodeIndex,
        attachmentOrder: attachmentIndex
      });
    });
  });

  return entries.sort((a, b) => {
    if (a.isPinned !== b.isPinned) return a.isPinned ? -1 : 1;
    if (a.nodeOrder !== b.nodeOrder) return a.nodeOrder - b.nodeOrder;
    if (a.attachmentOrder !== b.attachmentOrder) return a.attachmentOrder - b.attachmentOrder;
    return String(a.name || '').localeCompare(String(b.name || ''), 'zh');
  });
});

const batchAttachmentDialogTitle = computed(() => {
  if (!currentBatchCard.value) return '批次附件管理';
  return `批次附件管理 - ${currentBatchCard.value.label}`;
});

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

const shiftPlanTimeValue = (rawValue, days) => {
  if (!rawValue || !days) return rawValue;

  const shiftTextValue = (value) => {
    const shifted = addDaysToDate(value, days);
    return shifted || value;
  };

  if (Array.isArray(rawValue)) {
    return rawValue.map((item, index) => (index < 2 ? shiftTextValue(item) : item));
  }

  if (rawValue && typeof rawValue === 'object') {
    const updated = { ...rawValue };
    ['start', 'begin', 'planStart', 'end', 'finish', 'planEnd'].forEach((key) => {
      if (key in updated) {
        updated[key] = shiftTextValue(updated[key]);
      }
    });
    return updated;
  }

  if (typeof rawValue === 'string') {
    const datePattern = /\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?/g;
    const matches = rawValue.match(datePattern);
    if (matches?.length) {
      return rawValue.replace(datePattern, (matched) => shiftTextValue(matched));
    }
  }

  return shiftTextValue(rawValue);
};

// 更新计划时间字段中的开始日期
const updatePlanTimeValue = (rawValue, newStart, fallbackEnd) => {
  if (!newStart) return rawValue;
  const formatEnd = (value) => {
    if (!value) return null;
    if (typeof value === 'string') return value.replace(/\//g, '-');
    return formatDate(value);
  };
  if (Array.isArray(rawValue)) {
    const end = formatEnd(rawValue[1] || fallbackEnd);
    return end ? [newStart, end] : [newStart];
  }
  if (rawValue && typeof rawValue === 'object') {
    const updated = { ...rawValue };
    if ('start' in updated) updated.start = newStart;
    else if ('begin' in updated) updated.begin = newStart;
    else if ('planStart' in updated) updated.planStart = newStart;
    else updated.start = newStart;
    const endValue = updated.end || updated.finish || updated.planEnd || fallbackEnd;
    if ('end' in updated) updated.end = formatEnd(endValue) || updated.end;
    if ('finish' in updated) updated.finish = formatEnd(endValue) || updated.finish;
    if ('planEnd' in updated) updated.planEnd = formatEnd(endValue) || updated.planEnd;
    return updated;
  }
  if (typeof rawValue === 'string') {
    const matches = rawValue.match(/\d{4}[-/]\d{1,2}[-/]\d{1,2}/g);
    if (matches && matches.length >= 2) {
      const end = formatEnd(matches[1]);
      return end ? `${newStart} - ${end}` : newStart;
    }
    return newStart;
  }
  return newStart;
};

// 规范化 ID 列表用于比较
const normalizeIdList = (ids) =>
  (Array.isArray(ids) ? ids : [])
    .map((id) => String(id).trim())
    .filter(Boolean)
    .sort();

// 成员下拉选项
const memberOptions = computed(() =>
  members.value.map((item) => ({
    id: item.user_id,
    label: stripAccountSuffix(item.name || '未命名')
  }))
);


// 标准化文本展示
const normalizeLabel = (value) => {
  if (value === null || value === undefined) return '';
  if (typeof value === 'string') return value.trim();
  return String(value);
};

const normalizeToken = (value) => normalizeLabel(value).toLowerCase();

const isSameUserToken = (left, right) => {
  const leftToken = normalizeToken(left);
  const rightToken = normalizeToken(right);
  return Boolean(leftToken && rightToken && leftToken === rightToken);
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

const currentUserTokens = computed(
  () =>
    new Set(
      collectUserTokens([
        userParam.value,
        userProfile.value
      ])
    )
);

const userValueMatchesCurrentUser = (value) => {
  const currentTokens = currentUserTokens.value;
  if (!currentTokens.size) return false;
  return collectUserTokens(value).some((token) => currentTokens.has(token));
};

const isProjectManager = computed(() => {
  return projectManagerMembers.value.some((member) =>
    userValueMatchesCurrentUser(member)
  );
});

const batchAttachmentSummaryText = computed(() => {
  const count = batchAttachmentEntries.value.length;
  return isProjectManager.value
    ? `当前批次共汇总 ${count} 个附件，支持置顶、查看、下载、编辑和删除。`
    : `当前批次共汇总 ${count} 个附件，支持置顶、查看和下载。`;
});

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

const parseBatchNoNumber = (value) => {
  const normalized = normalizeBatchNo(value);
  if (!normalized) return null;
  const numeric = Number(normalized);
  if (!Number.isFinite(numeric)) return null;
  const asInt = Math.trunc(numeric);
  return asInt > 0 ? asInt : null;
};

const buildBatchKey = (batchNo, batchName) => {
  const normalizedNo = normalizeBatchNo(batchNo);
  const normalizedName = normalizeLabel(batchName);
  if (!normalizedNo && !normalizedName) return '__default_batch__';
  return `${normalizedNo}||${normalizedName}`;
};

const buildBatchCardLabel = (batchNo, batchName) => {
  const normalizedNo = normalizeBatchNo(batchNo);
  const normalizedName = normalizeLabel(batchName);
  if (normalizedNo && normalizedName) return `${normalizedName}（批次 ${normalizedNo}）`;
  if (normalizedName) return normalizedName;
  if (normalizedNo) return `批次 ${normalizedNo}`;
  return '未分批';
};

const buildBatchCardSubLabel = (batchNo, batchName) => {
  const normalizedNo = normalizeBatchNo(batchNo);
  const normalizedName = normalizeLabel(batchName);
  if (!normalizedNo && !normalizedName) return '历史节点';
  if (normalizedNo && normalizedName) return `编号 ${normalizedNo}`;
  if (normalizedNo) return `编号 ${normalizedNo}`;
  return '未设置编号';
};

// 规范化阶段序号为可比较类型
const normalizeOrderValue = (value) => {
  if (value === null || value === undefined) return null;
  const trimmed = String(value).trim();
  if (!trimmed) return null;
  const numeric = Number(trimmed);
  if (Number.isFinite(numeric)) return numeric;
  return trimmed;
};

// 比较阶段序号（数字优先）
const compareOrderValue = (a, b) => {
  if (a === null || a === undefined) return b === null || b === undefined ? 0 : 1;
  if (b === null || b === undefined) return -1;
  const aIsNumber = typeof a === 'number' && Number.isFinite(a);
  const bIsNumber = typeof b === 'number' && Number.isFinite(b);
  if (aIsNumber && bIsNumber) return a - b;
  return String(a).localeCompare(String(b), 'zh');
};

const compareTextValue = (a, b) => String(a || '').localeCompare(String(b || ''), 'zh');

const parsePositiveInt = (value) => {
  if (value === null || value === undefined || value === '') return null;
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return null;
  const normalizedNumber = Math.trunc(numeric);
  return normalizedNumber > 0 ? normalizedNumber : null;
};

const buildStageKey = (mainStage, mainStageOrder) =>
  `${normalizeLabel(mainStage)}||${normalizeLabel(mainStageOrder)}`;

const getProgressRecordId = (record) =>
  record?._id || record?.id || record?.record_id || record?.recordId || '';

const getMainStageLabel = (record) =>
  normalizeLabel(record?.main_stage || record?.mainStage || record?.mainStageLabel);

const getMainStageOrder = (record) =>
  normalizeOrderValue(record?.main_stage_order ?? record?.mainStageOrder);

const getProjectStageLabel = (record) =>
  normalizeLabel(record?.project_stage || record?.projectStage || record?.stage || record?.nodeLabel);

const getProjectStageOrder = (record) =>
  normalizeOrderValue(record?.project_stage_order ?? record?.projectStageOrder);

const hasProjectStageRecord = (record) => Boolean(getProjectStageLabel(record));

const buildStageOptionFromRecord = (record) => {
  const label = getMainStageLabel(record);
  if (!label) return null;
  const order = getMainStageOrder(record);
  return {
    key: buildStageKey(label, order),
    label,
    order
  };
};

const compareStageNodePosition = (a, b) => {
  const mainOrderCompare = compareOrderValue(getMainStageOrder(a), getMainStageOrder(b));
  if (mainOrderCompare !== 0) return mainOrderCompare;

  const mainLabelCompare = compareTextValue(getMainStageLabel(a), getMainStageLabel(b));
  if (mainLabelCompare !== 0) return mainLabelCompare;

  const aHasStage = hasProjectStageRecord(a);
  const bHasStage = hasProjectStageRecord(b);
  if (aHasStage !== bHasStage) {
    return aHasStage ? 1 : -1;
  }

  const stageOrderCompare = compareOrderValue(getProjectStageOrder(a), getProjectStageOrder(b));
  if (stageOrderCompare !== 0) return stageOrderCompare;

  const stageLabelCompare = compareTextValue(getProjectStageLabel(a), getProjectStageLabel(b));
  if (stageLabelCompare !== 0) return stageLabelCompare;

  return compareOrderValue(a?.originalIndex, b?.originalIndex);
};

const compareBatchGroup = (a, b) => {
  if (a.isDefault && !b.isDefault) return -1;
  if (!a.isDefault && b.isDefault) return 1;
  const aNo = parseBatchNoNumber(a.batchNo);
  const bNo = parseBatchNoNumber(b.batchNo);
  if (aNo !== null && bNo !== null && aNo !== bNo) return aNo - bNo;
  if (aNo !== null && bNo === null) return -1;
  if (aNo === null && bNo !== null) return 1;
  const labelCompare = String(a.label || '').localeCompare(String(b.label || ''), 'zh');
  if (labelCompare !== 0) return labelCompare;
  return String(a.subLabel || '').localeCompare(String(b.subLabel || ''), 'zh');
};

const getRecordKey = (record) => {
  if (!record || typeof record !== 'object') return '';
  return (
    record._id ||
    record.id ||
    record.record_id ||
    record.recordId ||
    `${record.project_stage || record.main_stage || ''}-${record.project_stage_order || ''}-${record.main_stage_order || ''}`
  );
};

const ensureOrderMap = (projectKey) => {
  if (!orderCache.value.has(projectKey)) {
    orderCache.value.set(projectKey, new Map());
  }
  return orderCache.value.get(projectKey);
};

// 按项目分组记录
const groupedProjects = computed(() => {
  const map = new Map();
  progressRecords.value.forEach((item) => {
    const projectCode = item.project_code || '';
    const projectName = item.project_name || '';
    const projectType = item.project_type || '';
    const key = `${projectCode}||${projectName}||${projectType}`;
    if (!map.has(key)) {
      map.set(key, {
        key,
        projectCode,
        projectName,
        projectType,
        records: []
      });
    }
    map.get(key).records.push(item);
  });
  const groups = Array.from(map.values());
  groups.forEach((group) => {
    const orderMap = ensureOrderMap(group.key);
    group.records.forEach((record) => {
      const recordKey = getRecordKey(record);
      if (!recordKey) return;
      if (!orderMap.has(recordKey)) {
        orderMap.set(recordKey, orderMap.size);
      }
    });
    group.records.sort((a, b) => {
      const aKey = getRecordKey(a);
      const bKey = getRecordKey(b);
      const aIndex = orderMap.has(aKey) ? orderMap.get(aKey) : Number.MAX_SAFE_INTEGER;
      const bIndex = orderMap.has(bKey) ? orderMap.get(bKey) : Number.MAX_SAFE_INTEGER;
      return aIndex - bIndex;
    });
  });
  return groups;
});

// 分组变化时同步选中项目
watch(
  groupedProjects,
  (groups) => {
    if (!groups.length) {
      currentProjectKey.value = '';
      return;
    }
    if (!groups.find((item) => item.key === currentProjectKey.value)) {
      currentProjectKey.value = groups[0].key;
    }
  },
  { immediate: true }
);


// 当前选中的项目
const currentProject = computed(() => {
  if (!groupedProjects.value.length) {
    return {
      projectName: '暂无项目',
      projectCode: '',
      projectType: '',
      records: []
    };
  }
  return (
    groupedProjects.value.find((item) => item.key === currentProjectKey.value) ||
    groupedProjects.value[0]
  );
});

const delayRequestCount = computed(() => delayRequests.value.length);

const batchCards = computed(() => {
  const grouped = new Map();
  currentProject.value.records.forEach((record) => {
    const batchNo = normalizeBatchNo(record.batch_no);
    const batchName = normalizeLabel(record.batch_name);
    const key = buildBatchKey(batchNo, batchName);
    if (!grouped.has(key)) {
      grouped.set(key, {
        key,
        batchNo,
        batchName,
        label: buildBatchCardLabel(batchNo, batchName),
        subLabel: buildBatchCardSubLabel(batchNo, batchName),
        isDefault: !batchNo && !batchName,
        recordCount: 0,
        records: []
      });
    }
    const target = grouped.get(key);
    target.recordCount += 1;
    target.records.push(record);
  });
  return Array.from(grouped.values())
    .sort(compareBatchGroup)
    .map((item) => ({
      ...item,
      subLabel: `${item.subLabel} · ${item.recordCount} 个节点`
    }));
});

watch(
  batchCards,
  (cards) => {
    if (!cards.length) {
      currentBatchKey.value = '';
      return;
    }
    if (!cards.some((item) => item.key === currentBatchKey.value)) {
      currentBatchKey.value = cards[0].key;
    }
  },
  { immediate: true }
);

const currentBatchCard = computed(() => {
  if (!batchCards.value.length) return null;
  return batchCards.value.find((item) => item.key === currentBatchKey.value) || batchCards.value[0];
});

const currentBatchRecords = computed(() => currentBatchCard.value?.records || []);

const getTemplateStageKey = (record) => {
  if (!record || typeof record !== 'object') return '';
  return [
    normalizeLabel(record.main_stage || record.mainStage),
    normalizeLabel(record.project_stage || record.projectStage || record.stage),
    normalizeLabel(record.main_stage_order),
    normalizeLabel(record.project_stage_order)
  ].join('||');
};

const dedupeTemplateRecords = (records) => {
  const source = Array.isArray(records) ? records : [];
  const map = new Map();
  source.forEach((record, index) => {
    const key = getTemplateStageKey(record) || `__fallback__${index}`;
    if (!map.has(key)) {
      map.set(key, record);
    }
  });
  return Array.from(map.values());
};

const batchTemplateRecords = computed(() => {
  if (currentBatchRecords.value.length) {
    return dedupeTemplateRecords(currentBatchRecords.value);
  }
  if (currentProject.value.records.length) {
    return dedupeTemplateRecords(currentProject.value.records);
  }
  return [];
});

const stageOptions = computed(() => {
  const map = new Map();
  currentProject.value.records.forEach((record) => {
    const option = buildStageOptionFromRecord(record);
    if (!option || map.has(option.key)) return;
    map.set(option.key, option);
  });
  return Array.from(map.values()).sort((a, b) => {
    const orderCompare = compareOrderValue(a.order, b.order);
    if (orderCompare !== 0) return orderCompare;
    return compareTextValue(a.label, b.label);
  });
});

const currentBatchDescriptor = computed(() => {
  if (!currentBatchCard.value) return null;
  return {
    key: currentBatchCard.value.key,
    batchNo: currentBatchCard.value.batchNo,
    batchName: currentBatchCard.value.batchName
  };
});

const getStageOptionByKey = (stageKey) =>
  stageOptions.value.find((item) => item.key === stageKey) || null;

const getTargetBatchDescriptors = (syncAllBatches = false) => {
  if (syncAllBatches) {
    return batchCards.value.map((item) => ({
      key: item.key,
      batchNo: item.batchNo,
      batchName: item.batchName
    }));
  }
  return currentBatchDescriptor.value ? [currentBatchDescriptor.value] : [];
};

const getStageNodeRecords = ({
  stageOption,
  batchKey,
  records = currentProject.value.records,
  excludeRecordId = ''
} = {}) => {
  if (!stageOption || !batchKey) return [];
  const stageOrderText = normalizeLabel(stageOption.order);
  const matched = [];
  records.forEach((record, index) => {
    if (buildBatchKey(record.batch_no, record.batch_name) !== batchKey) return;
    if (!hasProjectStageRecord(record)) return;
    if (getMainStageLabel(record) !== stageOption.label) return;
    if (normalizeLabel(getMainStageOrder(record)) !== stageOrderText) return;
    const recordId = getProgressRecordId(record);
    if (excludeRecordId && recordId === excludeRecordId) return;
    matched.push({
      record,
      originalIndex: index
    });
  });
  matched.sort((a, b) =>
    compareStageNodePosition(
      { ...a.record, originalIndex: a.originalIndex },
      { ...b.record, originalIndex: b.originalIndex }
    )
  );
  return matched.map((item) => item.record);
};

const resolveNodePosition = (row) => {
  if (!row) return 1;
  const stageOption = buildStageOptionFromRecord(row);
  const batchKey = row.batchKey || currentBatchDescriptor.value?.key || '';
  if (!stageOption || !batchKey) return parsePositiveInt(row.projectStageOrder) || 1;
  const records = getStageNodeRecords({ stageOption, batchKey });
  const index = records.findIndex((record) => getProgressRecordId(record) === row.recordId);
  if (index >= 0) return index + 1;
  return parsePositiveInt(row.projectStageOrder) || 1;
};

const createNodeStageOption = computed(() => getStageOptionByKey(createNodeForm.value.stageKey));

const createNodeOrderMax = computed(() => {
  if (!createNodeStageOption.value) return 1;
  const targetBatches = getTargetBatchDescriptors(createNodeForm.value.syncAllBatches);
  if (!targetBatches.length) return 1;
  const maxOrder = targetBatches.reduce((minValue, batch) => {
    const count = getStageNodeRecords({
      stageOption: createNodeStageOption.value,
      batchKey: batch.key
    }).length;
    return Math.min(minValue, count + 1);
  }, Number.MAX_SAFE_INTEGER);
  return Number.isFinite(maxOrder) && maxOrder > 0 ? maxOrder : 1;
});

const createNodeScopeHint = computed(() => {
  if (!createNodeStageOption.value) return '请选择主阶段';
  const targetBatches = getTargetBatchDescriptors(createNodeForm.value.syncAllBatches);
  if (!targetBatches.length) return '当前没有可操作的批次';
  const currentCount = currentBatchDescriptor.value
    ? getStageNodeRecords({
        stageOption: createNodeStageOption.value,
        batchKey: currentBatchDescriptor.value.key
      }).length
    : 0;
  if (createNodeForm.value.syncAllBatches) {
    return `将同步 ${targetBatches.length} 个批次；为避免序号断档，插入序号范围为 1 - ${createNodeOrderMax.value}`;
  }
  return `当前批次该主阶段共有 ${currentCount} 个节点，可插入序号范围为 1 - ${createNodeOrderMax.value}`;
});

const editNodeStageOption = computed(() => {
  if (!editRow.value) return null;
  return buildStageOptionFromRecord(editRow.value);
});

const editNodeOrderMax = computed(() => {
  if (!editNodeStageOption.value || !currentBatchDescriptor.value) return 1;
  const records = getStageNodeRecords({
    stageOption: editNodeStageOption.value,
    batchKey: currentBatchDescriptor.value.key
  });
  return records.length || 1;
});

const editNodeOrderHint = computed(() => {
  if (!editNodeStageOption.value || !currentBatchDescriptor.value) return '当前无法调整节点序号';
  const count = getStageNodeRecords({
    stageOption: editNodeStageOption.value,
    batchKey: currentBatchDescriptor.value.key
  }).length;
  return `保存后会按新的序号重排当前批次该主阶段的 ${count} 个节点`;
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

const getProjectSummaryCode = (project) => normalizeLabel(project?.projectCode || project?.project_code);

const getProjectSummaryOrderNo = (summary) =>
  normalizeLabel(
    summary?.order_no ||
    summary?.contract_name ||
    summary?.['订单号'] ||
    summary?.['合同名称'] ||
    summary?._widget_1769064437829
  );

const projectOrderNoMap = computed(() => {
  const map = new Map();
  projectSummaryRecords.value.forEach((item) => {
    const code = normalizeLabel(item?.project_code || item?.['项目编号'] || item?._widget_1769064437789);
    const orderNo = getProjectSummaryOrderNo(item);
    if (code && orderNo) {
      map.set(code, orderNo);
    }
  });
  return map;
});

const getProjectSummary = (project) => {
  const code = normalizeLabel(project?.projectCode);
  const name = normalizeLabel(project?.projectName);
  const type = normalizeLabel(project?.projectType);
  return (
    (code && projectSummaryMap.value.get(`code:${code}`)) ||
    (name && projectSummaryMap.value.get(`name:${name}`)) ||
    projectSummaryMap.value.get(`full:${code}||${name}||${type}`) ||
    null
  );
};

const currentProjectSummary = computed(() => getProjectSummary(currentProject.value) || {});

const getProjectOrderNo = (project) => {
  const code = getProjectSummaryCode(project);
  if (code && projectOrderNoMap.value.has(code)) {
    return projectOrderNoMap.value.get(code);
  }
  const summary = getProjectSummary(project);
  return getProjectSummaryOrderNo(summary);
};

// 当前项目标题
const currentProjectLabel = computed(() => getProjectOrderNo(currentProject.value) || '未找到订单号');

const currentProjectBusinessOwner = computed(
  () =>
    currentProjectSummary.value?.business_owner ||
    currentProjectSummary.value?.businessOwner ||
    currentProject.value?.business_owner ||
    currentProject.value?.businessOwner ||
    ''
);

const isCurrentProjectBusinessOwner = computed(() =>
  userValueMatchesCurrentUser(currentProjectBusinessOwner.value)
);

const buildProjectOptionLabel = (project) => {
  return getProjectOrderNo(project) || '未找到订单号';
};

// 项目下拉选项
const projectOptions = computed(() =>
  groupedProjects.value.map((item) => {
    return {
      key: item.key,
      label: buildProjectOptionLabel(item)
    };
  })
);

// 规范化节点数据用于展示
const normalizeNode = (record, index) => {
  const planRange = parseDateRange(record.plan_time);
  const planStartDate = planRange.start || null;
  const planEndDate = parseDateValue(record.plan_finishtime) || planRange.end || null;
  const actualFinishDate = parseDateValue(record.actual_finish) || null;
  const batchNo = normalizeBatchNo(record.batch_no);
  const batchName = normalizeLabel(record.batch_name);

  const mainStageLabel = normalizeLabel(record.main_stage || record.mainStage);
  const projectStageLabel = normalizeLabel(record.project_stage || record.projectStage || record.stage);
  const fallbackLabel = projectStageLabel || mainStageLabel || `节点${index + 1}`;
  const nodeLabel = projectStageLabel || (!mainStageLabel ? fallbackLabel : '');

  return {
    id: record._id || `${index}`,
    recordId: record._id,
    projectName: normalizeLabel(record.project_name),
    projectCode: normalizeLabel(record.project_code),
    name: fallbackLabel,
    mainStageLabel,
    nodeLabel,
    batchNo,
    batchName,
    batchKey: buildBatchKey(batchNo, batchName),
    batchCardLabel: buildBatchCardLabel(batchNo, batchName),
    mainStageOrder: normalizeOrderValue(record.main_stage_order),
    projectStageOrder: normalizeOrderValue(record.project_stage_order),
    status: record.status || '未完成',
    warningLevel: record.warning_level || '正常',
    executorName: formatUser(record.executor),
    executorRaw: record.executor,
    approverName: formatUser(record.approver),
    approverRaw: record.approver,
    executionNote: normalizeLabel(record.execution_note),
    overdueReason: normalizeLabel(record.overdue_reason),
    siteUploadRaw: record.site_upload,
    rawPlanTime: record.plan_time,
    planStartRaw: planStartDate,
    planEndRaw: planEndDate,
    planStart: formatDateCell(planStartDate),
    planEnd: formatDateCell(planEndDate),
    actualFinishRaw: actualFinishDate,
    actualFinish: formatDateCell(actualFinishDate),
    planStartSort: planStartDate ? planStartDate.getTime() : null,
    originalIndex: index,
    isMilestone: isDone(record.status || '未完成')
  };
};

// 时间轴节点（按序号/时间排序）
const timelineNodes = computed(() => {
  const nodes = currentBatchRecords.value.map((record, index) => normalizeNode(record, index));
  nodes.sort(compareStageNodePosition);

  const grouped = new Map();
  const groupOrder = [];
  nodes.forEach((node) => {
    const key = node.mainStageLabel
      ? `${node.mainStageLabel}||${node.mainStageOrder ?? ''}`
      : `__single__${node.id}`;
    if (!grouped.has(key)) {
      grouped.set(key, []);
      groupOrder.push(key);
    }
    grouped.get(key).push(node);
  });

  const ordered = [];
  groupOrder.forEach((key) => {
    ordered.push(...(grouped.get(key) || []));
  });
  return ordered;
});

const delayAffectedNodes = computed(() => {
  if (!canManageNode(delayRow.value)) return [];
  const startIndex = timelineNodes.value.findIndex(
    (node) => node.recordId && node.recordId === delayRow.value.recordId
  );
  if (startIndex < 0) return [];
  return timelineNodes.value
    .slice(startIndex)
    .filter((node) => canManageNode(node));
});

const delayAffectedPreviewNodes = computed(() => delayAffectedNodes.value.slice(0, 8));

const delayScopeHint = computed(() => {
  if (!delayRow.value) return '请选择要延期的节点';
  const count = delayAffectedNodes.value.length;
  if (!count) return '当前批次未找到可延期的后续节点';
  if (count === 1) {
    return `将顺延当前节点的计划时间 ${parsePositiveInt(delayForm.value.days) || 1} 天`;
  }
  return `将顺延当前批次从该节点开始的 ${count} 个节点，后续节点会一并延后`;
});

// 表格数据（按主阶段分组）
const tableRows = computed(() => {
  const rows = [];
  const groupMap = new Map();
  timelineNodes.value.forEach((node, index) => {
    const mainLabel = node.mainStageLabel;
    if (!mainLabel) {
      rows.push({
        ...node,
        id: `node-${node.id ?? index}`,
        isGroup: false
      });
      return;
    }
    const key = `${mainLabel}||${node.mainStageOrder ?? ''}`;
    let group = groupMap.get(key);
    if (!group) {
      group = {
        id: `group-${groupMap.size}-${String(mainLabel)}`,
        isGroup: true,
        name: mainLabel,
        mainStageLabel: mainLabel,
        mainStageOrder: node.mainStageOrder,
        children: [],
        nodeCount: 0
      };
      groupMap.set(key, group);
      rows.push(group);
    }
    group.children.push({
      ...node,
      id: `node-${node.id ?? `${index}`}`,
      isGroup: false
    });
    group.nodeCount = group.children.length;
  });
  return rows;
});

// 仅保留主阶段节点用于进度展示
const isMainStageNode = (node) => Boolean(node?.mainStageLabel) && !node?.nodeLabel;

const aggregateStatus = (nodes) => {
  if (nodes.some((node) => node.status === '超期')) return '超期';
  const allDone =
    nodes.length > 0 &&
    nodes.every((node) => node.status === '完成' || node.status === '超期完成');
  return allDone ? '完成' : '未完成';
};

const aggregateWarningLevel = (nodes) => {
  const rank = {
    '三级预警': 3,
    '二级预警': 2,
    '一级预警': 1,
    正常: 0
  };
  let best = '正常';
  let bestScore = 0;
  nodes.forEach((node) => {
    const level = node.warningLevel || '正常';
    const score = rank[level] ?? 0;
    if (score > bestScore) {
      bestScore = score;
      best = level;
    }
  });
  return best;
};

const buildAggregatedNode = (group) => {
  const status = aggregateStatus(group.nodes);
  const warningLevel = aggregateWarningLevel(group.nodes);
  const base = group.nodes[0] || {};
  return {
    ...base,
    id: `agg-${group.key}`,
    name: group.label,
    mainStageLabel: group.mainStageLabel || group.label,
    nodeLabel: '',
    status,
    warningLevel,
    isMilestone: status === '完成' || status === '超期完成'
  };
};

const timelineMainNodes = computed(() => {
  const grouped = new Map();
  const order = [];

  timelineNodes.value.forEach((node, index) => {
    const key = node.mainStageLabel
      ? `${node.mainStageLabel}||${node.mainStageOrder ?? ''}`
      : `__single__${node.id ?? index}`;
    if (!grouped.has(key)) {
      grouped.set(key, {
        key,
        label: node.mainStageLabel || node.name || `节点${index + 1}`,
        mainStageLabel: node.mainStageLabel || '',
        nodes: [],
        mainNode: null
      });
      order.push(key);
    }
    const group = grouped.get(key);
    group.nodes.push(node);
    if (isMainStageNode(node) && !group.mainNode) {
      group.mainNode = node;
    }
  });

  return order
    .map((key) => {
      const group = grouped.get(key);
      if (!group) return null;
      if (group.mainNode) return group.mainNode;
      return buildAggregatedNode(group);
    })
    .filter(Boolean);
});

// 判断节点是否已完成
const isDone = (status) => status === '完成' || status === '超期完成';

// 计算整体完成进度
const overallProgress = computed(() => {
  const total = timelineMainNodes.value.length;
  const doneCount = timelineMainNodes.value.filter((node) => isDone(node.status)).length;
  return total === 0 ? 0 : Math.round((doneCount / total) * 100);
});

// 预警统计
const totalWarningLevelCount = computed(
  () => timelineMainNodes.value.filter((node) => node.status === '超期').length
);
const warningLevelCount = computed(
  () => timelineMainNodes.value.filter((node) => node.warningLevel && node.warningLevel !== '正常').length
);

// 里程碑统计
const milestoneReachedCount = computed(() => timelineMainNodes.value.filter((node) => isDone(node.status)).length);
const milestoneTotalCount = computed(() => timelineMainNodes.value.length);

// 进度标签颜色
const overallProgressType = computed(() => (warningLevelCount.value > 0 ? 'danger' : 'primary'));

// 状态标签样式
const getStatusTag = (status) => {
  if (status === '完成' || status === '超期完成') return 'success';
  if (status === '待审批' || status === '超期待审批') return 'warning';
  if (status === '超期') return 'danger';
  return 'info';
};

// 兜底状态展示
const displayStatus = (status) => {
  if (status === '????') return '??';
  return status || '???';
};

// 分组行样式
const getRowClass = ({ row }) => (row.isGroup ? 'table-group-row' : '');

// 预警等级标签样式
const getWarningTag = (level) => {
  if (level === '三级预警') return 'danger';
  if (level === '二级预警') return 'warning';
  if (level === '一级预警') return 'info';
  return 'success';
};

const ensureProjectManagerAction = (message = '仅项目管理员可操作') => {
  if (isProjectManager.value) return true;
  ElMessage.warning(message);
  return false;
};

const ensureDelayRequestReviewerAction = (message = '仅当前项目商务负责人可审核延期申请') => {
  if (isCurrentProjectBusinessOwner.value) return true;
  ElMessage.warning(message);
  return false;
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

const canManageNode = (row) =>
  Boolean(isProjectManager.value && row && !row.isGroup && row.recordId && getProjectStageLabel(row));

const summarizeMutationResults = (results) => {
  const successCount = results.filter(
    (item) => item.status === 'fulfilled' && item.value?.code === 200
  ).length;
  return {
    total: results.length,
    successCount,
    failedCount: results.length - successCount
  };
};

const applyStageOrderAssignments = async (assignments, extraPayloadMap = new Map()) => {
  const tasks = assignments.reduce((list, { record, orderNo }) => {
    const recordId = getProgressRecordId(record);
    if (!recordId) return list;
    const payload = { ...(extraPayloadMap.get(recordId) || {}) };
    const currentOrder = parsePositiveInt(record.project_stage_order);
    if (currentOrder !== orderNo) {
      payload.project_stage_order = orderNo;
    }
    if (!Object.keys(payload).length) return list;
    list.push(() => api.updateProjectProgress(recordId, payload));
    return list;
  }, []);

  if (!tasks.length) {
    return {
      total: 0,
      successCount: 0,
      failedCount: 0
    };
  }

  const results = await Promise.allSettled(tasks.map((task) => task()));
  return summarizeMutationResults(results);
};

const buildNodeCreatePayload = ({
  stageOption,
  batchDescriptor,
  nodeName,
  orderNo,
  planStart,
  planEnd,
  executorIds,
  approverId
}) => ({
  project_code: normalizeLabel(currentProject.value.projectCode),
  project_name: normalizeLabel(currentProject.value.projectName),
  project_type: normalizeLabel(currentProject.value.projectType),
  batch_no: batchDescriptor?.batchNo ?? '',
  batch_name: batchDescriptor?.batchName ?? '',
  main_stage: stageOption?.label || '',
  main_stage_order: stageOption?.order ?? '',
  project_stage: nodeName,
  project_stage_order: orderNo,
  executor: executorIds,
  approver: approverId || '',
  plan_time: planStart || '',
  plan_finishtime: planEnd || '',
  status: '未完成',
  warning_level: '正常',
  actual_finish: '',
  site_upload: [],
  execution_note: '',
  overdue_reason: ''
});

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
        msg: result?.msg || '加载数据失败'
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

const loadAllProgressRecords = (search = '') =>
  fetchAllPages(api.listProjectProgress, PROJECT_PROGRESS_PAGE_SIZE, { search });

const loadAllProjectSummaryRecords = (search = '') =>
  fetchAllPages(api.listProjectSummary, PROJECT_PROGRESS_PAGE_SIZE, { search });

// 拉取进度数据
const loadProgressRecords = async (search = '') => {
  loading.value = true;
  try {
    const [progressResult, projectSummaryResult] = await Promise.all([
      loadAllProgressRecords(search),
      loadAllProjectSummaryRecords()
    ]);

    if (progressResult.ok) {
      progressRecords.value = progressResult.data;
    } else {
      progressRecords.value = [];
      ElMessage.error(progressResult.msg || '加载进度数据失败');
    }
    if (projectSummaryResult.ok) {
      projectSummaryRecords.value = projectSummaryResult.data;
    } else {
      projectSummaryRecords.value = [];
      console.warn('加载项目简要信息失败：', projectSummaryResult.msg);
    }
  } catch (error) {
    console.error('加载进度数据失败：', error);
    progressRecords.value = [];
    projectSummaryRecords.value = [];
    ElMessage.error('加载进度数据失败');
  } finally {
    loading.value = false;
  }
};

const loadProjectManagers = async () => {
  if (projectManagerLoading.value) return;
  projectManagerLoading.value = true;
  try {
    const result = await api.listProjectManagers();
    if (result?.code === 200 && Array.isArray(result.data)) {
      projectManagerMembers.value = result.data;
    } else {
      projectManagerMembers.value = [];
      ElMessage.warning(result?.msg || '项目管理员权限加载失败，当前按只读模式处理');
    }
  } catch (error) {
    console.error('加载项目管理员成员失败：', error);
    projectManagerMembers.value = [];
    ElMessage.warning('项目管理员权限加载失败，当前按只读模式处理');
  } finally {
    projectManagerLoading.value = false;
  }
};

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
    console.warn('用户信息查询失败，尝试使用项目管理员列表匹配。', error);
  }

  const matchedMember = projectManagerMembers.value.find(
    (item) =>
      isSameUserToken(item?.user_id, userParam.value) ||
      isSameUserToken(item?.account, userParam.value) ||
      isSameUserToken(item?.name, userParam.value) ||
      isSameUserToken(item?.uniqueid, userParam.value)
  );

  if (matchedMember) {
    userProfile.value = {
      ...matchedMember,
      user_id: matchedMember.user_id || userParam.value,
      name: matchedMember.name || '',
      account: matchedMember.account || ''
    };
    return;
  }

  try {
    const result = await api.listUsers();
    if (result?.code === 200 && Array.isArray(result.data)) {
      const match = result.data.find(
        (item) =>
          isSameUserToken(item?.user_id, userParam.value) ||
          isSameUserToken(item?.account, userParam.value) ||
          isSameUserToken(item?.name, userParam.value) ||
          isSameUserToken(item?.uniqueid, userParam.value)
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
    ElMessage.warning('未获取到用户ID，当前按只读模式处理');
    return;
  }

  await resolveUserProfile();
};

const loadDelayRequests = async () => {
  if (!isCurrentProjectBusinessOwner.value) {
    delayRequests.value = [];
    return;
  }
  if (!currentProject.value.projectCode && !currentProject.value.projectName) {
    delayRequests.value = [];
    return;
  }

  delayRequestReviewLoading.value = true;
  try {
    const result = await api.listProjectDelayRequests({
      projectCode: currentProject.value.projectCode || '',
      projectName: currentProject.value.projectName || '',
      status: 'pending'
    });
    if (result?.code === 200 && Array.isArray(result.data)) {
      delayRequests.value = result.data;
    } else {
      delayRequests.value = [];
      ElMessage.error(result?.msg || '加载延期申请失败');
    }
  } catch (error) {
    console.error('加载延期申请失败：', error);
    delayRequests.value = [];
  } finally {
    delayRequestReviewLoading.value = false;
  }
};

// 搜索项目进度
const handleSearch = async () => {
  await loadProgressRecords(searchQuery.value.trim());
  await loadDelayRequests();
};

const openCreateNodeDialog = (row = null) => {
  if (!ensureProjectManagerAction()) return;
  if (!currentProject.value.records.length || !currentBatchDescriptor.value) {
    ElMessage.warning('当前项目暂无可新增节点的数据');
    return;
  }
  if (!stageOptions.value.length) {
    ElMessage.warning('当前项目暂无可用主阶段');
    return;
  }

  const preferredStage =
    (row && buildStageOptionFromRecord(row)) || stageOptions.value[0] || null;
  if (!preferredStage) {
    ElMessage.warning('当前项目暂无可用主阶段');
    return;
  }

  const stageRecords = getStageNodeRecords({
    stageOption: preferredStage,
    batchKey: currentBatchDescriptor.value.key
  });
  const defaultOrder =
    row && canManageNode(row)
      ? Math.min(resolveNodePosition(row) + 1, stageRecords.length + 1)
      : stageRecords.length + 1;

  createNodeForm.value = {
    ...buildEmptyCreateNodeForm(),
    stageKey: preferredStage.key,
    orderNo: defaultOrder
  };
  createNodeDialogVisible.value = true;
  if (!members.value.length) {
    loadMembers();
  }
};

const handleCreateNode = async () => {
  if (!ensureProjectManagerAction()) return;
  const stageOption = createNodeStageOption.value;
  const nodeName = normalizeLabel(createNodeForm.value.nodeName);
  const orderNo = parsePositiveInt(createNodeForm.value.orderNo);
  const targetBatches = getTargetBatchDescriptors(createNodeForm.value.syncAllBatches);
  const executorIds = normalizeIdList(createNodeForm.value.executorIds);
  const approverId = normalizeLabel(createNodeForm.value.approverId);
  const maxOrder = createNodeOrderMax.value;

  if (!stageOption) {
    ElMessage.warning('请选择主阶段');
    return;
  }
  if (!nodeName) {
    ElMessage.warning('请输入节点名称');
    return;
  }
  if (orderNo === null || orderNo > maxOrder) {
    ElMessage.warning(`插入序号必须在 1 - ${maxOrder} 之间`);
    return;
  }
  if (!targetBatches.length) {
    ElMessage.warning('当前没有可操作的批次');
    return;
  }

  creatingNode.value = true;
  let createdCount = 0;
  let reorderedCount = 0;
  let failedBatchCount = 0;

  try {
    for (const batch of targetBatches) {
      const stageRecords = getStageNodeRecords({
        stageOption,
        batchKey: batch.key
      });
      if (orderNo > stageRecords.length + 1) {
        failedBatchCount += 1;
        continue;
      }

      const reorderedRecords = [...stageRecords];
      reorderedRecords.splice(orderNo - 1, 0, null);
      const assignments = reorderedRecords
        .map((item, index) => (item ? { record: item, orderNo: index + 1 } : null))
        .filter(Boolean);

      const orderSummary = await applyStageOrderAssignments(assignments);
      reorderedCount += orderSummary.successCount;
      if (orderSummary.failedCount > 0) {
        failedBatchCount += 1;
        continue;
      }

      const result = await api.createProjectProgress(
        buildNodeCreatePayload({
          stageOption,
          batchDescriptor: batch,
          nodeName,
          orderNo,
          planStart: normalizeLabel(createNodeForm.value.planStart),
          planEnd: normalizeLabel(createNodeForm.value.planEnd),
          executorIds,
          approverId
        })
      );

      if (result?.code === 200) {
        createdCount += 1;
      } else {
        failedBatchCount += 1;
      }
    }

    if (!createdCount) {
      ElMessage.error('新增节点失败');
      return;
    }

    if (failedBatchCount > 0) {
      ElMessage.warning(
        `新增节点完成：成功新增 ${createdCount} 个批次节点，重排 ${reorderedCount} 条，失败 ${failedBatchCount} 个批次`
      );
    } else {
      ElMessage.success(
        `新增节点成功：成功新增 ${createdCount} 个批次节点，重排 ${reorderedCount} 条`
      );
    }

    createNodeDialogVisible.value = false;
    await loadProgressRecords(searchQuery.value.trim());
  } catch (error) {
    console.error('新增节点失败：', error);
    ElMessage.error('新增节点失败');
  } finally {
    creatingNode.value = false;
  }
};

const handleBatchCardClick = (batchKey) => {
  currentBatchKey.value = batchKey;
};

const getNextBatchNo = () => {
  let maxBatchNo = 0;
  batchCards.value.forEach((item) => {
    const numeric = parseBatchNoNumber(item.batchNo);
    if (numeric !== null && numeric > maxBatchNo) {
      maxBatchNo = numeric;
    }
  });
  return maxBatchNo + 1;
};

const hasDuplicatedBatchNo = (batchNo, excludeKey = '') =>
  batchCards.value.some(
    (item) => item.key !== excludeKey && normalizeBatchNo(item.batchNo) === String(batchNo)
  );

const hasDuplicatedBatchName = (batchName, excludeKey = '') =>
  batchCards.value.some(
    (item) =>
      item.key !== excludeKey &&
      normalizeLabel(item.batchName) &&
      normalizeLabel(item.batchName) === batchName
  );

const openCreateBatchDialog = () => {
  if (!ensureProjectManagerAction()) return;
  if (!currentProject.value.records.length) {
    ElMessage.warning('当前项目暂无可新增批次的节点');
    return;
  }
  if (!batchTemplateRecords.value.length) {
    ElMessage.warning('当前批次暂无可复制的节点');
    return;
  }
  const nextBatchNo = getNextBatchNo();
  createBatchForm.value = {
    batchNo: nextBatchNo,
    batchName: `第${nextBatchNo}批`
  };
  createBatchDialogVisible.value = true;
};

const openEditBatchDialog = () => {
  if (!ensureProjectManagerAction()) return;
  if (!currentBatchCard.value) {
    ElMessage.warning('请先选择要编辑的批次');
    return;
  }
  const targetBatch = currentBatchCard.value;
  const currentBatchNo = parseBatchNoNumber(targetBatch.batchNo);
  editBatchSourceKey.value = targetBatch.key;
  editBatchForm.value = {
    batchNo: currentBatchNo,
    batchName: normalizeLabel(targetBatch.batchName)
  };
  editBatchDialogVisible.value = true;
};

const buildBatchCreatePayload = (record, batchNo, batchName) => {
  const payload = {
    project_code: normalizeLabel(record.project_code),
    project_name: normalizeLabel(record.project_name),
    project_type: normalizeLabel(record.project_type),
    main_stage: normalizeLabel(record.main_stage || record.mainStage),
    main_stage_order: record.main_stage_order ?? '',
    project_stage: normalizeLabel(record.project_stage || record.projectStage || record.stage),
    project_stage_order: record.project_stage_order ?? '',
    executor: record.executor || [],
    approver: record.approver || '',
    plan_time: record.plan_time ?? '',
    plan_finishtime: record.plan_finishtime ?? '',
    status: '未完成',
    warning_level: '正常',
    actual_finish: '',
    site_upload: [],
    execution_note: '',
    overdue_reason: '',
    batch_no: batchNo,
    batch_name: batchName
  };
  return Object.fromEntries(Object.entries(payload).filter(([, value]) => value !== undefined));
};

const handleCreateBatch = async () => {
  if (!ensureProjectManagerAction()) return;
  const batchNo = parseBatchNoNumber(createBatchForm.value.batchNo);
  const batchName = normalizeLabel(createBatchForm.value.batchName);

  if (batchNo === null) {
    ElMessage.warning('批次编号必须为正整数');
    return;
  }
  if (!batchName) {
    ElMessage.warning('请输入批次名称');
    return;
  }

  const batchKey = buildBatchKey(batchNo, batchName);
  if (hasDuplicatedBatchNo(batchNo)) {
    ElMessage.warning('该批次编号已存在，请使用其他编号');
    return;
  }
  if (hasDuplicatedBatchName(batchName) || batchCards.value.some((item) => item.key === batchKey)) {
    ElMessage.warning('该批次名称已存在，请使用其他名称');
    return;
  }

  const templates = batchTemplateRecords.value;
  if (!templates.length) {
    ElMessage.warning('当前没有可复制的节点模板');
    return;
  }

  creatingBatch.value = true;
  try {
    const createTasks = templates.map((record) =>
      api.createProjectProgress(buildBatchCreatePayload(record, batchNo, batchName))
    );
    const results = await Promise.allSettled(createTasks);
    const successCount = results.filter(
      (item) => item.status === 'fulfilled' && item.value?.code === 200
    ).length;
    const failedCount = results.length - successCount;

    if (!successCount) {
      ElMessage.error('新增批次失败');
      return;
    }
    if (failedCount > 0) {
      ElMessage.warning(`新增批次完成：成功 ${successCount} 条，失败 ${failedCount} 条`);
    } else {
      ElMessage.success(`新增批次成功：共创建 ${successCount} 条节点`);
    }
    createBatchDialogVisible.value = false;
    await loadProgressRecords(searchQuery.value.trim());
    currentBatchKey.value = batchKey;
  } catch (error) {
    console.error('新增批次失败：', error);
    ElMessage.error('新增批次失败');
  } finally {
    creatingBatch.value = false;
  }
};

const handleEditBatch = async () => {
  if (!ensureProjectManagerAction()) return;
  const sourceKey = editBatchSourceKey.value;
  const sourceBatch = batchCards.value.find((item) => item.key === sourceKey);
  if (!sourceBatch) {
    ElMessage.error('未找到要编辑的批次');
    return;
  }

  const batchNo = parseBatchNoNumber(editBatchForm.value.batchNo);
  const batchName = normalizeLabel(editBatchForm.value.batchName);
  if (batchNo === null) {
    ElMessage.warning('批次编号必须为正整数');
    return;
  }
  if (!batchName) {
    ElMessage.warning('请输入批次名称');
    return;
  }

  const nextBatchKey = buildBatchKey(batchNo, batchName);
  if (hasDuplicatedBatchNo(batchNo, sourceKey)) {
    ElMessage.warning('该批次编号已存在，请使用其他编号');
    return;
  }
  if (hasDuplicatedBatchName(batchName, sourceKey) || batchCards.value.some((item) => item.key === nextBatchKey && item.key !== sourceKey)) {
    ElMessage.warning('该批次名称已存在，请使用其他名称');
    return;
  }

  if (nextBatchKey === sourceKey) {
    ElMessage.warning('批次信息未变化');
    return;
  }

  const records = Array.isArray(sourceBatch.records) ? sourceBatch.records : [];
  const validRecords = records.filter((item) => item && (item._id || item.id));
  if (!validRecords.length) {
    ElMessage.error('该批次没有可更新的节点记录');
    return;
  }

  editingBatch.value = true;
  try {
    const updateTasks = validRecords.map((record) =>
      api.updateProjectProgress(record._id || record.id, {
        batch_no: batchNo,
        batch_name: batchName
      })
    );
    const results = await Promise.allSettled(updateTasks);
    const successCount = results.filter(
      (item) => item.status === 'fulfilled' && item.value?.code === 200
    ).length;
    const failedCount = results.length - successCount;

    if (!successCount) {
      ElMessage.error('批次编辑失败');
      return;
    }
    if (failedCount > 0) {
      ElMessage.warning(`批次编辑完成：成功 ${successCount} 条，失败 ${failedCount} 条`);
    } else {
      ElMessage.success(`批次编辑成功：共更新 ${successCount} 条节点`);
    }
    editBatchDialogVisible.value = false;
    await loadProgressRecords(searchQuery.value.trim());
    currentBatchKey.value = nextBatchKey;
  } catch (error) {
    console.error('批次编辑失败：', error);
    ElMessage.error('批次编辑失败');
  } finally {
    editingBatch.value = false;
  }
};

watch(createNodeDialogVisible, (visible) => {
  if (visible) return;
  createNodeForm.value = buildEmptyCreateNodeForm();
});

watch(
  () => [createNodeDialogVisible.value, createNodeForm.value.stageKey, createNodeForm.value.syncAllBatches],
  ([visible]) => {
    if (!visible) return;
    const maxOrder = createNodeOrderMax.value;
    const currentOrder = parsePositiveInt(createNodeForm.value.orderNo);
    if (currentOrder === null || currentOrder > maxOrder) {
      createNodeForm.value.orderNo = maxOrder;
    }
  }
);

watch(editDialogVisible, (visible) => {
  if (visible) return;
  editRow.value = null;
  editForm.value = buildEmptyEditForm();
  originalExecutorIds.value = [];
  originalPlanRange.value = {
    planStart: '',
    planEnd: ''
  };
});

watch(delayDialogVisible, (visible) => {
  if (visible) return;
  delayRow.value = null;
  delayForm.value = buildEmptyDelayForm();
});

watch(currentProjectKey, () => {
  loadDelayRequests();
});

watch(
  () => [editDialogVisible.value, editNodeOrderMax.value],
  ([visible]) => {
    if (!visible) return;
    const maxOrder = editNodeOrderMax.value;
    const currentOrder = parsePositiveInt(editForm.value.orderNo);
    if (currentOrder === null || currentOrder > maxOrder) {
      editForm.value.orderNo = maxOrder;
    }
  }
);

watch(createBatchDialogVisible, (visible) => {
  if (visible) return;
  createBatchForm.value = {
    batchNo: null,
    batchName: ''
  };
});

watch(editBatchDialogVisible, (visible) => {
  if (visible) return;
  editBatchSourceKey.value = '';
  editBatchForm.value = {
    batchNo: null,
    batchName: ''
  };
});

watch(
  currentBatchAttachmentScopeKey,
  () => {
    batchAttachmentPinnedIds.value = loadBatchAttachmentPinnedIds();
  },
  { immediate: true }
);

watch(
  () => route.fullPath,
  async () => {
    await syncCurrentUser();
    await loadDelayRequests();
  }
);

// 拉取成员列表
const loadMembers = async () => {
  if (memberLoading.value) return;
  memberLoading.value = true;
  try {
    const result = await api.listUsers();
    if (result?.code === 200 && Array.isArray(result.data)) {
      members.value = result.data;
    } else {
      members.value = [];
      ElMessage.error(result?.msg || '加载成员失败');
    }
  } catch (error) {
    console.error('加载成员失败：', error);
    members.value = [];
    ElMessage.error('加载成员失败');
  } finally {
    memberLoading.value = false;
  }
};

const previewAttachmentImage = (item) => {
  if (!item?.url || !item?.isImage) {
    ElMessage.warning('该附件不支持图片预览');
    return;
  }
  previewImageItem.value = item;
  imagePreviewVisible.value = true;
};

const openBatchAttachmentDialog = () => {
  batchAttachmentPinnedIds.value = loadBatchAttachmentPinnedIds();
  batchAttachmentDialogVisible.value = true;
};

const toggleBatchAttachmentPin = (item) => {
  const pinId = String(item?.pinId || '').trim();
  if (!pinId) return;
  const currentIds = batchAttachmentPinnedIds.value.map((id) => String(id));
  const nextIds = currentIds.includes(pinId)
    ? currentIds.filter((id) => id !== pinId)
    : [pinId, ...currentIds];
  batchAttachmentPinnedIds.value = Array.from(new Set(nextIds));
  saveBatchAttachmentPinnedIds(batchAttachmentPinnedIds.value);
};

const getAttachmentActionKey = (item) => `${item?.recordId || ''}::${item?.attachmentIndex ?? ''}`;

const findProgressRecordById = (recordId) => {
  const normalizedId = String(recordId || '').trim();
  if (!normalizedId) return null;
  return (
    currentProject.value.records.find((record) => getProgressRecordId(record) === normalizedId) ||
    progressRecords.value.find((record) => getProgressRecordId(record) === normalizedId) ||
    null
  );
};

const updateAttachmentPayloadName = (attachment, nextName) => {
  if (attachment && typeof attachment === 'object' && !Array.isArray(attachment)) {
    return {
      ...attachment,
      name: nextName,
      file_name: nextName,
      fileName: nextName
    };
  }

  const text = String(attachment || '').trim();
  if (/^https?:\/\//i.test(text)) {
    return {
      name: nextName,
      url: text
    };
  }
  return nextName;
};

const updateBatchAttachmentList = async (item, updater, successMessage, options = {}) => {
  if (!ensureProjectManagerAction('仅项目管理员可管理附件')) return;
  const recordId = String(item?.recordId || '').trim();
  const attachmentIndex = Number(item?.attachmentIndex);
  const record = findProgressRecordById(recordId);

  if (!record || !recordId || !Number.isInteger(attachmentIndex) || attachmentIndex < 0) {
    ElMessage.error('未找到附件所属节点');
    return;
  }

  const attachments = normalizeAttachmentPayloadList(record.site_upload);
  if (attachmentIndex >= attachments.length) {
    ElMessage.error('未找到要操作的附件');
    return;
  }

  const nextAttachments = updater(attachments, attachmentIndex);
  if (!Array.isArray(nextAttachments)) return;

  attachmentActionKey.value = getAttachmentActionKey(item);
  try {
    const result = await api.updateProjectProgress(recordId, {
      site_upload: nextAttachments
    });
    if (result?.code === 200) {
      ElMessage.success(successMessage);
      if (item?.pinId) {
        const withoutCurrentPin = batchAttachmentPinnedIds.value.filter((id) => id !== item.pinId);
        batchAttachmentPinnedIds.value =
          item.isPinned && options.nextPinId
            ? Array.from(new Set([options.nextPinId, ...withoutCurrentPin]))
            : withoutCurrentPin;
        saveBatchAttachmentPinnedIds(batchAttachmentPinnedIds.value);
      }
      await loadProgressRecords(searchQuery.value.trim());
    } else {
      ElMessage.error(result?.msg || '附件更新失败');
    }
  } catch (error) {
    console.error('附件更新失败：', error);
    ElMessage.error(error?.message || '附件更新失败');
  } finally {
    attachmentActionKey.value = '';
  }
};

const handleEditBatchAttachment = async (item) => {
  if (!ensureProjectManagerAction('仅项目管理员可编辑附件')) return;
  let promptResult;
  try {
    promptResult = await ElMessageBox.prompt('请输入新的附件名称', '编辑附件', {
      inputValue: item?.name || '',
      inputPattern: /\S/,
      inputErrorMessage: '请输入附件名称',
      confirmButtonText: '保存',
      cancelButtonText: '取消'
    });
  } catch {
    return;
  }

  const nextName = normalizeLabel(promptResult?.value);
  if (!nextName) {
    ElMessage.warning('请输入附件名称');
    return;
  }
  if (nextName === normalizeLabel(item?.name)) {
    ElMessage.warning('附件名称未变化');
    return;
  }

  await updateBatchAttachmentList(
    item,
    (attachments, attachmentIndex) => {
      const nextAttachments = [...attachments];
      nextAttachments[attachmentIndex] = updateAttachmentPayloadName(nextAttachments[attachmentIndex], nextName);
      return nextAttachments;
    },
    '附件已更新',
    {
      nextPinId: buildBatchAttachmentPinId(
        { ...item, name: nextName },
        { recordId: item?.recordId || '' },
        item?.attachmentIndex ?? ''
      )
    }
  );
};

const handleDeleteBatchAttachment = async (item) => {
  if (!ensureProjectManagerAction('仅项目管理员可删除附件')) return;
  try {
    await ElMessageBox.confirm(
      `确认删除附件“${item?.name || '附件'}”吗？`,
      '删除附件',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消'
      }
    );
  } catch {
    return;
  }

  await updateBatchAttachmentList(
    item,
    (attachments, attachmentIndex) => attachments.filter((_, index) => index !== attachmentIndex),
    '附件已删除'
  );
};

const viewBatchAttachment = (item) => {
  if (!item) return;
  if (item.isImage && item.url) {
    previewAttachmentImage(item);
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

const handleDeleteNode = async (row) => {
  if (!canManageNode(row)) {
    ElMessage.warning('仅支持删除具体节点');
    return;
  }

  try {
    await ElMessageBox.confirm(
      `删除节点“${row.nodeLabel || row.name}”后，将重排当前批次该主阶段下的后续序号，是否继续？`,
      '删除节点',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消'
      }
    );
  } catch {
    return;
  }

  const stageOption = buildStageOptionFromRecord(row);
  const batchKey = row.batchKey || currentBatchDescriptor.value?.key || '';
  if (!stageOption || !batchKey || !row.recordId) {
    ElMessage.error('当前节点缺少主阶段或批次信息');
    return;
  }

  try {
    const deleteResult = await api.deleteProjectProgress(row.recordId);
    if (deleteResult?.code !== 200) {
      ElMessage.error(deleteResult?.msg || '删除失败');
      return;
    }

    const remainingRecords = getStageNodeRecords({
      stageOption,
      batchKey,
      excludeRecordId: row.recordId
    });
    const assignments = remainingRecords.map((record, index) => ({
      record,
      orderNo: index + 1
    }));
    const summary = await applyStageOrderAssignments(assignments);

    if (summary.failedCount > 0) {
      ElMessage.warning(
        `节点删除完成：已删除节点，序号重排成功 ${summary.successCount} 条，失败 ${summary.failedCount} 条`
      );
    } else {
      ElMessage.success('节点删除成功');
    }

    await loadProgressRecords(searchQuery.value.trim());
  } catch (error) {
    console.error('删除节点失败：', error);
    ElMessage.error('删除节点失败');
  }
};

// 打开详情弹窗
const openDetailDialog = (row) => {
  if (!row || row.isGroup) return;
  previewImageItem.value = null;
  imagePreviewVisible.value = false;
  detailRow.value = row;
  detailDialogVisible.value = true;
};

const openDelayDialog = (row) => {
  if (!canManageNode(row)) {
    ElMessage.warning('仅支持对具体节点执行延期');
    return;
  }
  delayRow.value = row;
  delayForm.value = buildEmptyDelayForm();
  delayDialogVisible.value = true;
};

const buildDelayPayload = (node, days) => {
  const payload = {};
  const shiftedPlanTime = shiftPlanTimeValue(node.rawPlanTime, days);
  const shiftedPlanEnd = addDaysToDate(node.planEndRaw, days);

  if (JSON.stringify(shiftedPlanTime) !== JSON.stringify(node.rawPlanTime)) {
    payload.plan_time = shiftedPlanTime;
  }
  if (node.planEndRaw && shiftedPlanEnd && shiftedPlanEnd !== formatDate(node.planEndRaw)) {
    payload.plan_finishtime = shiftedPlanEnd;
  }
  return payload;
};

const handleApplyDelay = async () => {
  if (!canManageNode(delayRow.value)) {
    ElMessage.error('请选择要延期的节点');
    return;
  }

  const delayDays = parsePositiveInt(delayForm.value.days);
  if (!delayDays) {
    ElMessage.warning('请输入大于 0 的延期天数');
    return;
  }

  const affectedNodes = delayAffectedNodes.value;
  if (!affectedNodes.length) {
    ElMessage.warning('当前没有可延期的节点');
    return;
  }

  delayingNodes.value = true;
  let skippedCount = 0;
  try {
    const preparedNodes = affectedNodes.reduce((list, node) => {
      const payload = buildDelayPayload(node, delayDays);
      if (!node.recordId || !Object.keys(payload).length) {
        skippedCount += 1;
        return list;
      }
      list.push({
        record_id: node.recordId,
        main_stage_label: node.mainStageLabel || '',
        node_label: node.nodeLabel || node.name || '',
        before_plan_start: node.planStart || '',
        after_plan_start: addDaysToDate(node.planStartRaw, delayDays),
        before_plan_end: node.planEnd || '',
        after_plan_end: addDaysToDate(node.planEndRaw, delayDays),
        executor_ids: getExecutorIds(node.executorRaw),
        executor_raw: node.executorRaw,
        payload
      });
      return list;
    }, []);

    if (!preparedNodes.length) {
      ElMessage.warning('所选节点及后续节点暂无可延期的计划日期');
      return;
    }

    const result = await api.delayProjectProgress({
      project_name: currentProject.value.projectName || delayRow.value.projectName || '',
      project_code: currentProject.value.projectCode || delayRow.value.projectCode || '',
      batch_no: currentBatchDescriptor.value?.batchNo || delayRow.value.batchNo || '',
      batch_name: currentBatchDescriptor.value?.batchName || delayRow.value.batchName || '',
      delay_days: delayDays,
      nodes: preparedNodes
    });

    const summary = result?.data || {};
    const updatedCount = Number(summary.updated_count || 0);
    const failedCount = Number(summary.failed_count || 0);
    const skippedTotal = skippedCount + Number(summary.skipped_count || 0);
    const notifiedUserCount = Number(summary.notified_user_count || 0);
    const notifyFailedCount = Number(summary.notify_failed_count || 0);
    const notificationDisabled = Boolean(summary.notification_disabled);
    const notifyErrorSummary = String(summary.notify_error_summary || '').trim();

    if (updatedCount === 0) {
      ElMessage.error('延期失败');
      return;
    }

    if (failedCount > 0 || skippedTotal > 0 || notifyFailedCount > 0 || notificationDisabled) {
      const messageParts = [
        `延期完成：成功 ${updatedCount} 个节点`
      ];
      if (failedCount > 0) {
        messageParts.push(`失败 ${failedCount} 个`);
      }
      if (skippedTotal > 0) {
        messageParts.push(`跳过 ${skippedTotal} 个`);
      }
      if (notifiedUserCount > 0) {
        messageParts.push(`已通知 ${notifiedUserCount} 位责任人`);
      } else if (notificationDisabled) {
        messageParts.push('钉钉通知未发送');
      }
      if (notifyFailedCount > 0) {
        messageParts.push(`通知失败 ${notifyFailedCount} 位`);
      }
      if (notifyErrorSummary) {
        messageParts.push(notifyErrorSummary);
      }
      ElMessage.warning(
        messageParts.join('，')
      );
    } else {
      ElMessage.success(
        `延期成功：已顺延 ${updatedCount} 个节点 ${delayDays} 天，并通知 ${notifiedUserCount} 位责任人`
      );
    }

    delayDialogVisible.value = false;
    await loadProgressRecords(searchQuery.value.trim());
  } catch (error) {
    console.error('延期失败：', error);
    ElMessage.error('延期失败');
  } finally {
    delayingNodes.value = false;
  }
};

const openDelayRequestReviewDialog = async () => {
  if (!ensureDelayRequestReviewerAction()) return;
  delayRequestReviewDialogVisible.value = true;
  await loadDelayRequests();
};

const handleApproveDelayRequest = async (row) => {
  if (!ensureDelayRequestReviewerAction()) return;
  if (!row?.request_id) {
    ElMessage.error('缺少延期申请ID');
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确认通过该延期申请，并顺延 ${row.node_count || row.nodes?.length || 0} 个节点 ${row.delay_days || 0} 天吗？`,
      '通过延期申请',
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    );
  } catch {
    return;
  }

  handlingDelayRequestId.value = row.request_id;
  handlingDelayRequestAction.value = 'approve';
  try {
    const result = await api.approveProjectDelayRequest(row.request_id, {
      reviewer: buildCurrentReviewerPayload()
    });
    if (result?.code === 200) {
      const summary = result?.data?.summary || {};
      const updatedCount = Number(summary.updated_count || 0);
      const notifiedUserCount = Number(summary.notified_user_count || 0);
      const notifyFailedCount = Number(summary.notify_failed_count || 0);
      const notifyErrorSummary = String(summary.notify_error_summary || '').trim();
      if (notifyFailedCount > 0) {
        const parts = [`延期申请已通过，成功顺延 ${updatedCount} 个节点`];
        if (notifiedUserCount > 0) {
          parts.push(`已通知 ${notifiedUserCount} 位责任人`);
        }
        parts.push(`通知失败 ${notifyFailedCount} 位`);
        if (notifyErrorSummary) {
          parts.push(notifyErrorSummary);
        }
        ElMessage.warning(parts.join('，'));
      } else {
        ElMessage.success(`延期申请已通过，成功顺延 ${updatedCount} 个节点，并通知 ${notifiedUserCount} 位责任人`);
      }
      await loadDelayRequests();
      await loadProgressRecords(searchQuery.value.trim());
    } else {
      ElMessage.error(result?.msg || '延期申请审核失败');
    }
  } catch (error) {
    console.error('延期申请审核失败：', error);
    ElMessage.error(error?.message || '延期申请审核失败');
  } finally {
    handlingDelayRequestId.value = '';
    handlingDelayRequestAction.value = '';
  }
};

const handleRejectDelayRequest = async (row) => {
  if (!ensureDelayRequestReviewerAction()) return;
  if (!row?.request_id) {
    ElMessage.error('缺少延期申请ID');
    return;
  }

  try {
    await ElMessageBox.confirm('确认驳回该延期申请吗？', '驳回延期申请', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    });
  } catch {
    return;
  }

  handlingDelayRequestId.value = row.request_id;
  handlingDelayRequestAction.value = 'reject';
  try {
    const result = await api.rejectProjectDelayRequest(row.request_id, {
      reviewer: buildCurrentReviewerPayload()
    });
    if (result?.code === 200) {
      ElMessage.success(result?.msg || '延期申请已驳回');
      await loadDelayRequests();
    } else {
      ElMessage.error(result?.msg || '延期申请驳回失败');
    }
  } catch (error) {
    console.error('延期申请驳回失败：', error);
    ElMessage.error(error?.message || '延期申请驳回失败');
  } finally {
    handlingDelayRequestId.value = '';
    handlingDelayRequestAction.value = '';
  }
};

// 打开编辑弹窗
const openEditDialog = async (row) => {
  if (!canManageNode(row)) {
    ElMessage.warning('仅支持编辑具体节点');
    return;
  }
  editRow.value = row;
  const initialExecutorIds = getExecutorIds(row.executorRaw);
  const initialApproverId = getMemberId(row.approverRaw);
  const initialPlanStart = row.planStartRaw ? formatDate(row.planStartRaw) : row.planStart || '';
  const initialPlanEnd = row.planEndRaw ? formatDate(row.planEndRaw) : row.planEnd || '';
  editForm.value = {
    nodeName: row.nodeLabel || row.name || '',
    orderNo: resolveNodePosition(row),
    planStart: initialPlanStart,
    planEnd: initialPlanEnd,
    executorIds: initialExecutorIds,
    approverId: initialApproverId
  };
  originalPlanRange.value = {
    planStart: initialPlanStart,
    planEnd: initialPlanEnd
  };
  originalExecutorIds.value = [...initialExecutorIds];
  originalApproverId.value = initialApproverId;
  editDialogVisible.value = true;
  if (!members.value.length) {
    await loadMembers();
  }
  const missingIds = (editForm.value.executorIds || []).filter(
    (id) => !members.value.find((item) => item.user_id === id)
  );
  if (missingIds.length) {
    members.value = [
      ...members.value,
      ...missingIds.map((id) => ({
        user_id: id,
        name: row.executorName || '未知成员'
      }))
    ];
  }
  if (initialApproverId && !members.value.find((item) => item.user_id === initialApproverId)) {
    members.value = [
      ...members.value,
      {
        user_id: initialApproverId,
        name: row.approverName || '未知成员'
      }
    ];
  }
};

// 保存节点编辑
const handleSaveEdit = async () => {
  if (!canManageNode(editRow.value)) {
    ElMessage.error('无法编辑：缺少记录ID');
    return;
  }

  const stageOption = editNodeStageOption.value;
  const batchKey = editRow.value.batchKey || currentBatchDescriptor.value?.key || '';
  if (!stageOption || !batchKey) {
    ElMessage.error('当前节点缺少主阶段或批次信息');
    return;
  }

  const stageRecords = getStageNodeRecords({
    stageOption,
    batchKey
  });
  const currentRecord = stageRecords.find(
    (record) => getProgressRecordId(record) === editRow.value.recordId
  );
  if (!currentRecord) {
    ElMessage.error('未找到要编辑的节点记录');
    return;
  }

  const nodeName = normalizeLabel(editForm.value.nodeName);
  const orderNo = parsePositiveInt(editForm.value.orderNo);
  if (!nodeName) {
    ElMessage.warning('请输入节点名称');
    return;
  }
  if (orderNo === null || orderNo > editNodeOrderMax.value) {
    ElMessage.warning(`节点序号必须在 1 - ${editNodeOrderMax.value} 之间`);
    return;
  }

  savingEdit.value = true;
  try {
    const nextPlanStart = normalizeLabel(editForm.value.planStart);
    const nextPlanEnd = normalizeLabel(editForm.value.planEnd);
    const payload = {};
    const currentName = normalizeLabel(editRow.value.nodeLabel || editRow.value.name);

    if (nodeName !== currentName) {
      payload.project_stage = nodeName;
    }

    if (nextPlanStart !== originalPlanRange.value.planStart) {
      payload.plan_time = nextPlanStart
        ? updatePlanTimeValue(editRow.value.rawPlanTime, nextPlanStart, nextPlanEnd || editRow.value.planEndRaw)
        : '';
    }
    if (nextPlanEnd !== originalPlanRange.value.planEnd) {
      payload.plan_finishtime = nextPlanEnd || '';
    }

    const currentExecutorIds = normalizeIdList(editForm.value.executorIds);
    const originalIds = normalizeIdList(originalExecutorIds.value);
    if (JSON.stringify(currentExecutorIds) !== JSON.stringify(originalIds)) {
      payload.executor = currentExecutorIds;
    }

    const currentApproverId = normalizeLabel(editForm.value.approverId);
    const previousApproverId = normalizeLabel(originalApproverId.value);
    if (currentApproverId !== previousApproverId) {
      payload.approver = currentApproverId || '';
    }

    const reorderedRecords = stageRecords.filter(
      (record) => getProgressRecordId(record) !== editRow.value.recordId
    );
    reorderedRecords.splice(orderNo - 1, 0, currentRecord);
    const assignments = reorderedRecords.map((record, index) => ({
      record,
      orderNo: index + 1
    }));
    const currentPosition = resolveNodePosition(editRow.value);
    if (Object.keys(payload).length === 0 && currentPosition === orderNo) {
      ElMessage.warning('没有可更新的内容');
      savingEdit.value = false;
      return;
    }

    const extraPayloadMap = new Map([[editRow.value.recordId, payload]]);
    const summary = await applyStageOrderAssignments(assignments, extraPayloadMap);
    if (summary.failedCount === 0) {
      ElMessage.success('更新成功');
      editDialogVisible.value = false;
      await loadProgressRecords(searchQuery.value.trim());
    } else if (summary.successCount > 0) {
      ElMessage.warning(`节点编辑已部分完成：成功 ${summary.successCount} 条，失败 ${summary.failedCount} 条`);
      editDialogVisible.value = false;
      await loadProgressRecords(searchQuery.value.trim());
    } else {
      ElMessage.error('更新失败');
    }
  } catch (error) {
    console.error('更新失败：', error);
    ElMessage.error('更新失败');
  } finally {
    savingEdit.value = false;
  }
};

// 页面初始化
onMounted(async () => {
  await loadProjectManagers();
  await syncCurrentUser();
  await loadProgressRecords();
  await loadDelayRequests();
  console.log('ProjectProgress Current URL:', window.location.href);
  console.log('Webpage User ID:', userParam.value);
});
</script>

<style scoped>
.page-container {
  padding: 0;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 100%;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.progress-visual-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.visual-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.search-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.project-name-large {
  font-size: 22px;
  font-weight: 600;
  text-align: center;
  flex: 1 1 auto;
  min-width: 200px;
}

.status-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.segmented-timeline-wrapper {
  position: relative;
  padding: 24px 16px 48px 16px;
  background: linear-gradient(180deg, #f7f8fb 0%, #ffffff 100%);
  border: 1px solid rgba(60, 60, 67, 0.08);
  border-radius: 16px;
  box-shadow:
    0 8px 24px rgba(15, 23, 42, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.node-markers {
  display: flex;
  justify-content: space-between;
  position: absolute;
  width: calc(100% - 40px);
  top: 18px;
}

.marker-cell {
  position: relative;
  flex: 1;
  display: flex;
  justify-content: center;
}

.marker-dot {
  width: 28px;
  height: 28px;
  background: #fff;
  border: 1px solid rgba(60, 60, 67, 0.22);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  position: relative;
  box-shadow:
    0 6px 12px rgba(15, 23, 42, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.marker-dot.is-done {
  border-color: #34c759;
  background: #34c759;
  color: #fff;
  box-shadow: 0 8px 14px rgba(52, 199, 89, 0.4);
}

.marker-dot.is-overdue {
  border-color: #ff3b30;
  color: #ff3b30;
  background: #fff5f5;
  box-shadow: 0 6px 12px rgba(255, 59, 48, 0.28);
}

.marker-label {
  position: absolute;
  top: 40px;
  transform: translateX(-50%);
  left: 50%;
  white-space: nowrap;
  font-size: 12px;
  color: rgba(60, 60, 67, 0.85);
  letter-spacing: 0.2px;
}

.marker-pending-dot {
  width: 6px;
  height: 6px;
  background: rgba(60, 60, 67, 0.4);
  border-radius: 50%;
  display: inline-block;
}

.node-flag-icon {
  position: absolute;
  top: -18px;
  right: -12px;
  color: #ff3b30;
  font-size: 16px;
  animation: wave 2s infinite ease-in-out;
}

.segmented-progress {
  position: relative;
  height: 6px;
  border-radius: 999px;
  background: #e5e5ea;
  overflow: hidden;
}

.segmented-progress__fill {
  height: 100%;
  width: 0;
  background: #34c759;
  transition: width 0.6s ease;
}

@keyframes wave {
  0%,
  100% {
    transform: rotate(0deg);
  }
  50% {
    transform: rotate(15deg);
  }
}

.empty-timeline {
  padding: 12px 0;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 0;
}

.dashboard-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  margin-bottom: 12px;
}

.card-label {
  color: #8c8c8c;
  font-size: 14px;
}

.card-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
}

.card-icon.is-primary {
  background: rgba(24, 144, 255, 0.12);
  color: #1890ff;
}

.card-icon.is-warning {
  background: rgba(250, 140, 22, 0.14);
  color: #fa8c16;
}

.card-icon.is-danger {
  background: rgba(245, 34, 45, 0.12);
  color: #f5222d;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  padding-left: 12px;
}

.accent-blue {
  color: #1890ff;
}

.accent-danger {
  color: #f5222d;
}

.accent-warning {
  color: #fa8c16;
}

.muted {
  font-size: 14px;
  font-weight: normal;
  color: #999;
}

.progress-table-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.table-header {
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-title h3 {
  margin: 0;
  font-size: 16px;
}

.table-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.batch-card-panel {
  margin-top: 14px;
  border-top: 1px solid #f0f2f5;
  padding-top: 12px;
}

.batch-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.batch-card-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.batch-card-desc {
  font-size: 12px;
  color: #909399;
}

.batch-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
  padding: 10px 0;
}

.batch-card-item {
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  background: #fff;
  padding: 10px 12px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #303133;
}

.batch-card-item:hover {
  border-color: #b9ddff;
  box-shadow: 0 6px 12px rgba(24, 144, 255, 0.08);
}

.batch-card-item.is-active {
  border-color: #1890ff;
  background: #e6f4ff;
}

.batch-card-main {
  font-size: 14px;
  line-height: 1.3;
  font-weight: 600;
}

.batch-card-sub {
  margin-top: 5px;
  font-size: 12px;
  color: #8c8c8c;
}

:deep(.table-group-row) td {
  background: #fafafa;
}

.stage-group-title {
  font-weight: 600;
  color: #303133;
}

.stage-node-count {
  font-size: 12px;
  color: #909399;
}

.stage-node-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #303133;
}

.stage-node-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #c0c4cc;
  flex-shrink: 0;
}

.stage-node-text {
  line-height: 1.2;
}

.stage-placeholder {
  color: #c0c4cc;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  justify-items: center;
  align-items: center;
  gap: 1px 4px;
  width: 100%;
}

.action-link {
  margin: 0 !important;
  min-width: auto;
  padding: 0;
  font-size: 12px;
  line-height: 1.2;
}

.action-link--danger {
  color: #f56c6c;
}

.dialog-hint {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.5;
  color: #909399;
}

.dialog-switch-wrap {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.dialog-switch-label {
  font-size: 13px;
  color: #606266;
}

.detail-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.detail-attachments {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 12px;
}

.attachment-label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.attachment-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.attachment-grid {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.attachment-item {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  background: #fff;
}

.attachment-name {
  color: #303133;
  font-size: 13px;
  line-height: 1.4;
  word-break: break-all;
}

.attachment-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.attachment-text {
  color: #606266;
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

.batch-attachment-summary {
  margin-bottom: 12px;
  font-size: 13px;
  color: #606266;
}

.batch-attachment-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.batch-attachment-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px 14px;
  background: #fff;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.batch-attachment-card.is-pinned {
  border-color: #e6a23c;
  background: #fff9f0;
  box-shadow: 0 4px 14px rgba(230, 162, 60, 0.12);
}

.batch-attachment-card__main {
  flex: 1;
  min-width: 0;
}

.batch-attachment-card__title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.batch-attachment-card__name {
  font-size: 14px;
  line-height: 1.4;
  font-weight: 600;
  color: #303133;
  word-break: break-all;
}

.batch-attachment-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  font-size: 12px;
  line-height: 1.5;
  color: #909399;
}

.batch-attachment-card__actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.delay-dialog-hint {
  margin-top: 4px;
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
}

.delay-preview-list {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.delay-preview-tag {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  background: #f4f4f5;
  color: #606266;
  font-size: 12px;
  line-height: 1.4;
}

.delay-preview-more {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  color: #909399;
  font-size: 12px;
}


@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 0;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .visual-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .project-name-large {
    text-align: left;
  }

  .batch-card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .batch-attachment-card {
    flex-direction: column;
  }

  .batch-attachment-card__actions {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}
</style>

