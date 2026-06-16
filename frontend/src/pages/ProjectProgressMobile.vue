<template>
  <el-config-provider :locale="zhCn">
    <div class="progress-mobile-page">
      <header class="progress-mobile-header">
        <div class="page-title">项目节点执行明细</div>
        <el-select
          v-model="selectedProjectKey"
          filterable
          clearable
          :loading="projectLoading"
          placeholder="请选择项目"
          class="project-select"
          @change="handleProjectChange"
        >
          <el-option
            v-for="option in projectOptions"
            :key="option.key"
            :label="option.label"
            :value="option.key"
          >
            <div class="project-option">
              <span class="project-option-title">{{ option.label }}</span>
              <span class="project-option-subtitle">{{ option.subtitle }}</span>
            </div>
          </el-option>
        </el-select>
      </header>

      <main class="progress-mobile-body" v-loading="loading">
        <el-empty v-if="!selectedProjectKey" description="请选择项目" />
        <el-empty v-else-if="!progressRecords.length && !loading" description="暂无项目节点" />
        <template v-else>
          <section v-if="batchCards.length" class="batch-section">
            <div class="section-heading">
              <span>批次</span>
              <span>{{ batchCards.length }} 个</span>
            </div>
            <div class="batch-scroll">
              <button
                v-for="batch in batchCards"
                :key="batch.key"
                type="button"
                class="batch-card"
                :class="{ active: batch.key === currentBatchKey }"
                @click="currentBatchKey = batch.key"
              >
                <span class="batch-title">{{ batch.label }}</span>
                <span class="batch-subtitle">{{ batch.subLabel }}</span>
              </button>
            </div>
          </section>

          <section v-if="currentBatchCard" class="mobile-action-section">
            <div class="section-heading">
              <span>批次操作</span>
              <span v-if="isProjectManager">项目管理员</span>
            </div>
            <div class="mobile-action-grid">
              <el-button
                type="primary"
                plain
                size="small"
                :icon="PaperclipIcon"
                @click="openBatchAttachmentDialog"
              >
                附件管理
              </el-button>
              <template v-if="isProjectManager">
                <el-button
                  type="primary"
                  size="small"
                  :icon="PlusIcon"
                  :disabled="!stageOptions.length || !currentBatchCard"
                  @click="openCreateNodeDialog()"
                >
                  新增节点
                </el-button>
                <el-button
                  type="primary"
                  plain
                  size="small"
                  :icon="EditIcon"
                  :disabled="!currentBatchCard"
                  @click="openEditBatchDialog"
                >
                  编辑批次
                </el-button>
                <el-button
                  type="primary"
                  plain
                  size="small"
                  :icon="CirclePlusIcon"
                  :disabled="!batchTemplateRecords.length"
                  @click="openCreateBatchDialog"
                >
                  新增批次
                </el-button>
              </template>
            </div>
          </section>

          <section class="summary-section">
            <div class="summary-card completion-card">
              <div class="summary-label">完成率</div>
              <div class="summary-value">{{ progressSummary.completionRate }}%</div>
              <el-progress
                :percentage="progressSummary.completionRate"
                :stroke-width="8"
                :show-text="false"
                :color="progressSummary.warningCount > 0 ? '#f56c6c' : '#1677ff'"
              />
            </div>
            <button
              type="button"
              class="summary-card summary-card-button"
              :class="{ active: activeNodeFilter === NODE_FILTER_OVERDUE }"
              @click="handleOverdueSummaryClick"
            >
              <div class="summary-label">超期节点数</div>
              <div class="summary-value danger">{{ progressSummary.overdueCount }}</div>
            </button>
            <div class="summary-card">
              <div class="summary-label">预警节点数</div>
              <div class="summary-value warning">{{ progressSummary.warningCount }}</div>
            </div>
            <div class="summary-card">
              <div class="summary-label">里程碑</div>
              <div class="summary-value">
                {{ progressSummary.doneCount }} / {{ progressSummary.totalCount }}
              </div>
            </div>
          </section>

          <section class="node-section">
            <div class="section-heading">
              <span>{{ nodeSectionTitle }}</span>
              <div class="section-heading-actions">
                <el-button v-if="activeNodeFilter" link type="primary" @click="clearNodeFilter">
                  查看全部
                </el-button>
                <span>{{ nodeSectionCountText }}</span>
              </div>
            </div>
            <el-empty v-if="!displayedBatchNodes.length && !loading" :description="nodeEmptyText" />
            <div v-else class="stage-list">
              <section v-for="group in stageGroups" :key="group.key" class="stage-group">
                <div class="stage-heading">
                  <span class="stage-title">{{ group.title }}</span>
                  <span class="stage-count">{{ group.nodes.length }} 个</span>
                </div>
                <div class="node-card-list">
                  <article
                    v-for="node in group.nodes"
                    :key="node.id"
                    class="node-card"
                    role="button"
                    tabindex="0"
                    @click="openDetail(node)"
                    @keyup.enter="openDetail(node)"
                  >
                    <div class="node-card-header">
                      <div class="node-title-wrap">
                        <div class="node-title">{{ getNodeTitle(node) }}</div>
                        <div class="node-order">节点序号 {{ displayValue(node.displayNodeOrder) }}</div>
                      </div>
                      <div class="tag-stack">
                        <el-tag size="small" :type="getStatusTag(node.status)">
                          {{ node.status || '未完成' }}
                        </el-tag>
                        <el-tag size="small" :type="getWarningTag(node.warningLevel)">
                          {{ node.warningLevel || '正常' }}
                        </el-tag>
                      </div>
                    </div>
                    <div class="node-info-grid">
                      <div class="info-item">
                        <span class="info-label">责任人</span>
                        <span class="info-value">{{ node.executorName || '--' }}</span>
                      </div>
                      <div class="info-item">
                        <span class="info-label">审批人</span>
                        <span class="info-value">{{ node.approverName || '--' }}</span>
                      </div>
                      <div class="info-item">
                        <span class="info-label">计划结束时间</span>
                        <span class="info-value">{{ node.planEnd || '--' }}</span>
                      </div>
                      <div class="info-item">
                        <span class="info-label">完成时间</span>
                        <span class="info-value">{{ node.actualFinish || '--' }}</span>
                      </div>
                    </div>
                    <div class="node-card-actions" @click.stop @keyup.stop>
                      <el-button size="small" type="primary" plain :icon="ViewIcon" @click="openDetail(node)">
                        详情
                      </el-button>
                      <el-button
                        v-if="isProjectManager && node.mainStageLabel"
                        size="small"
                        type="primary"
                        :icon="PlusIcon"
                        @click="openCreateNodeDialog(node)"
                      >
                        新增
                      </el-button>
                      <el-button
                        v-if="canManageNode(node)"
                        size="small"
                        type="primary"
                        plain
                        :icon="ClockIcon"
                        @click="openDelayDialog(node)"
                      >
                        延期
                      </el-button>
                      <el-button
                        v-if="canManageNode(node)"
                        size="small"
                        type="primary"
                        plain
                        :icon="EditIcon"
                        @click="openEditDialog(node)"
                      >
                        编辑
                      </el-button>
                      <el-button
                        v-if="canManageNode(node)"
                        size="small"
                        type="danger"
                        plain
                        :icon="DeleteIcon"
                        @click="handleDeleteNode(node)"
                      >
                        删除
                      </el-button>
                    </div>
                  </article>
                </div>
              </section>
            </div>
          </section>
        </template>
      </main>

      <el-dialog
        v-model="detailDialogVisible"
        title="节点详情"
        width="100%"
        :fullscreen="true"
        class="progress-mobile-dialog"
      >
        <div v-if="detailNode" class="detail-content">
          <div class="detail-title-block">
            <div class="detail-title">{{ getNodeTitle(detailNode) }}</div>
            <div class="detail-subtitle">{{ detailNode.projectName || '--' }}</div>
          </div>
          <el-descriptions :column="1" border size="small" class="detail-descriptions">
            <el-descriptions-item label="项目名称">{{ detailNode.projectName || '--' }}</el-descriptions-item>
            <el-descriptions-item label="项目编号">{{ detailNode.projectCode || '--' }}</el-descriptions-item>
            <el-descriptions-item label="主阶段">{{ detailNode.mainStageLabel || '--' }}</el-descriptions-item>
            <el-descriptions-item label="节点名称">{{ getNodeTitle(detailNode) }}</el-descriptions-item>
            <el-descriptions-item label="批次编号">{{ detailNode.batchNo || '--' }}</el-descriptions-item>
            <el-descriptions-item label="批次名称">{{ detailNode.batchName || '--' }}</el-descriptions-item>
            <el-descriptions-item label="计划结束时间">{{ detailNode.planEnd || '--' }}</el-descriptions-item>
            <el-descriptions-item label="完成时间">{{ detailNode.actualFinish || '--' }}</el-descriptions-item>
            <el-descriptions-item label="当前状态">{{ detailNode.status || '未完成' }}</el-descriptions-item>
            <el-descriptions-item label="预警等级">{{ detailNode.warningLevel || '正常' }}</el-descriptions-item>
            <el-descriptions-item label="责任人">{{ detailNode.executorName || '--' }}</el-descriptions-item>
            <el-descriptions-item label="审批人">{{ detailNode.approverName || '--' }}</el-descriptions-item>
            <el-descriptions-item label="执行说明">{{ detailNode.executionNote || '--' }}</el-descriptions-item>
            <el-descriptions-item label="超期原因">{{ detailNode.overdueReason || '--' }}</el-descriptions-item>
          </el-descriptions>

          <section class="detail-attachments">
            <div class="attachment-heading">现场资料附件</div>
            <div v-if="!detailAttachments.length" class="empty-attachments">暂无附件</div>
            <div v-else class="attachment-list">
              <div
                v-for="(item, index) in detailAttachments"
                :key="`attachment-${index}`"
                class="attachment-item"
              >
                <span class="attachment-name" :title="item.name">{{ item.name }}</span>
                <div class="attachment-actions">
                  <el-button
                    v-if="item.isImage"
                    link
                    type="primary"
                    :icon="ViewIcon"
                    @click="previewAttachment(item)"
                  >
                    预览
                  </el-button>
                  <el-button
                    v-if="item.canDownload"
                    link
                    type="primary"
                    :icon="DownloadIcon"
                    :loading="downloadActionKey === getAttachmentActionKey(item, index)"
                    @click="downloadAttachment(item, index)"
                  >
                    下载
                  </el-button>
                </div>
              </div>
            </div>
          </section>
        </div>
        <template #footer>
          <el-button type="primary" @click="detailDialogVisible = false">关闭</el-button>
        </template>
      </el-dialog>

      <el-dialog
        v-model="batchAttachmentDialogVisible"
        :title="batchAttachmentDialogTitle"
        width="100%"
        :fullscreen="true"
        append-to-body
        class="progress-mobile-dialog"
      >
        <div class="batch-attachment-summary">{{ batchAttachmentSummaryText }}</div>
        <div v-if="batchAttachmentEntries.length" class="batch-attachment-list">
          <div
            v-for="item in batchAttachmentEntries"
            :key="item.pinId"
            class="batch-attachment-card"
            :class="{ 'is-pinned': item.isPinned }"
          >
            <div class="batch-attachment-title-row">
              <span class="batch-attachment-name" :title="item.name">{{ item.name }}</span>
              <el-tag v-if="item.isPinned" size="small" type="warning" effect="plain">已置顶</el-tag>
            </div>
            <div class="batch-attachment-meta">
              <span>主阶段：{{ item.mainStageLabel || '--' }}</span>
              <span>节点：{{ item.nodeLabel || '--' }}</span>
              <span>责任人：{{ item.executorName || '--' }}</span>
            </div>
            <div class="batch-attachment-actions">
              <el-button size="small" type="warning" plain @click="toggleBatchAttachmentPin(item)">
                {{ item.isPinned ? '取消置顶' : '置顶' }}
              </el-button>
              <el-button
                v-if="item.canView"
                size="small"
                type="primary"
                plain
                :icon="ViewIcon"
                @click="viewBatchAttachment(item)"
              >
                查看
              </el-button>
              <el-button
                v-if="item.canDownload"
                size="small"
                type="primary"
                plain
                :icon="DownloadIcon"
                :loading="downloadActionKey === getAttachmentActionKey(item)"
                @click="downloadAttachment(item)"
              >
                下载
              </el-button>
              <template v-if="isProjectManager">
                <el-button
                  size="small"
                  type="primary"
                  plain
                  :icon="EditIcon"
                  :disabled="Boolean(attachmentActionKey)"
                  :loading="attachmentActionKey === getAttachmentActionKey(item)"
                  @click="openEditBatchAttachmentDialog(item)"
                >
                  编辑
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  plain
                  :icon="DeleteIcon"
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
          <el-button type="primary" @click="batchAttachmentDialogVisible = false">关闭</el-button>
        </template>
      </el-dialog>

      <el-dialog
        v-model="createNodeDialogVisible"
        title="新增节点"
        width="100%"
        :fullscreen="true"
        append-to-body
        class="progress-mobile-dialog"
      >
        <el-form label-position="top" class="mobile-form">
          <el-form-item label="主阶段">
            <el-select v-model="createNodeForm.stageKey" placeholder="请选择主阶段" filterable>
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
              class="full-control"
            />
            <div class="dialog-hint">{{ createNodeScopeHint }}</div>
          </el-form-item>
          <el-form-item label="计划结束时间">
            <el-date-picker
              v-model="createNodeForm.planEnd"
              type="datetime"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              placeholder="请选择时间"
              class="full-control"
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
              :loading="memberLoading"
            >
              <el-option v-for="item in memberOptions" :key="item.id" :label="item.label" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="审批人">
            <el-select
              v-model="createNodeForm.approverId"
              filterable
              clearable
              placeholder="请选择成员"
              :loading="memberLoading"
            >
              <el-option v-for="item in memberOptions" :key="item.id" :label="item.label" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="同步所有批次">
            <div class="dialog-switch-wrap">
              <el-switch v-model="createNodeForm.syncAllBatches" />
              <span class="dialog-switch-label">开启后会在当前项目所有批次的同主阶段插入该节点</span>
            </div>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="createNodeDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="creatingNode" @click="handleCreateNode">确定新增</el-button>
        </template>
      </el-dialog>

      <el-dialog
        v-model="editDialogVisible"
        title="编辑节点"
        width="100%"
        :fullscreen="true"
        append-to-body
        class="progress-mobile-dialog"
      >
        <el-form label-position="top" class="mobile-form">
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
              class="full-control"
            />
            <div class="dialog-hint">{{ editNodeOrderHint }}</div>
          </el-form-item>
          <el-form-item label="计划结束时间">
            <el-date-picker
              v-model="editForm.planEnd"
              type="datetime"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              placeholder="请选择时间"
              class="full-control"
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
              :loading="memberLoading"
            >
              <el-option v-for="item in memberOptions" :key="item.id" :label="item.label" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="审批人">
            <el-select
              v-model="editForm.approverId"
              filterable
              clearable
              placeholder="请选择成员"
              :loading="memberLoading"
            >
              <el-option v-for="item in memberOptions" :key="item.id" :label="item.label" :value="item.id" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="savingEdit" @click="handleSaveEdit">保存</el-button>
        </template>
      </el-dialog>

      <el-dialog
        v-model="delayDialogVisible"
        title="一键延期"
        width="100%"
        :fullscreen="true"
        append-to-body
        class="progress-mobile-dialog"
      >
        <el-form label-position="top" class="mobile-form">
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
              class="full-control"
              placeholder="请输入延期天数"
            />
          </el-form-item>
        </el-form>
        <div class="delay-dialog-hint">{{ delayScopeHint }}</div>
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
          <el-button type="primary" :loading="delayingNodes" @click="handleApplyDelay">确认延期</el-button>
        </template>
      </el-dialog>

      <el-dialog
        v-model="createBatchDialogVisible"
        title="新增批次"
        width="100%"
        :fullscreen="true"
        append-to-body
        class="progress-mobile-dialog"
      >
        <el-form label-position="top" class="mobile-form">
          <el-form-item label="批次编号">
            <el-input-number
              v-model="createBatchForm.batchNo"
              :min="1"
              :step="1"
              :precision="0"
              controls-position="right"
              class="full-control"
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

      <el-dialog
        v-model="editBatchDialogVisible"
        title="编辑批次"
        width="100%"
        :fullscreen="true"
        append-to-body
        class="progress-mobile-dialog"
      >
        <el-form label-position="top" class="mobile-form">
          <el-form-item label="批次编号">
            <el-input-number
              v-model="editBatchForm.batchNo"
              :min="1"
              :step="1"
              :precision="0"
              controls-position="right"
              class="full-control"
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

      <el-dialog
        v-model="attachmentEditDialogVisible"
        title="编辑附件"
        width="100%"
        :fullscreen="true"
        append-to-body
        class="progress-mobile-dialog"
      >
        <el-form label-position="top" class="mobile-form">
          <el-form-item label="附件名称">
            <el-input
              v-model="attachmentEditForm.name"
              maxlength="120"
              show-word-limit
              placeholder="请输入附件名称"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="attachmentEditDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="Boolean(attachmentActionKey)" @click="handleSaveBatchAttachment">
            保存
          </el-button>
        </template>
      </el-dialog>

      <el-dialog
        v-model="imagePreviewVisible"
        :title="previewImageTitle"
        width="100%"
        :fullscreen="true"
        append-to-body
        class="progress-mobile-dialog"
      >
        <div class="image-preview-body">
          <el-image
            v-if="previewImageUrl"
            :src="previewImageUrl"
            fit="contain"
            class="preview-image"
          />
          <el-empty v-else description="暂无可预览图片" />
        </div>
        <template #footer>
          <el-button @click="imagePreviewVisible = false">关闭</el-button>
          <el-button
            v-if="previewImageItem?.canDownload"
            type="primary"
            :loading="downloadActionKey === getAttachmentActionKey(previewImageItem)"
            @click="downloadAttachment(previewImageItem)"
          >
            下载
          </el-button>
        </template>
      </el-dialog>
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage, ElMessageBox, ElConfigProvider } from 'element-plus';
import {
  CirclePlus as CirclePlusIcon,
  Clock as ClockIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
  Paperclip as PaperclipIcon,
  Plus as PlusIcon,
  View as ViewIcon
} from '@element-plus/icons-vue';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import api from '../api/client';
import { useProjectProgressPermissions } from '../composables/useProjectProgressPermissions';
import {
  addDaysToDate,
  buildBatchCardLabel,
  buildBatchCardSubLabel,
  buildBatchKey,
  buildStageOptionFromRecord,
  compareBatchGroup,
  compareOrderValue,
  compareStageNodePosition,
  formatAttachment,
  formatDate,
  formatDateTime,
  getExecutorIds,
  getMemberId,
  getProgressRecordId,
  getMainStageLabel,
  getMainStageOrder,
  hasProjectStageRecord,
  isDone,
  normalizeAttachmentList,
  normalizeAttachmentPayloadList,
  normalizeBatchNo,
  normalizeIdList,
  normalizeLabel,
  normalizeNode,
  parseBatchNoNumber,
  parsePositiveInt,
  shiftPlanTimeValue,
  stripAccountSuffix,
  updatePlanTimeValue
} from '../utils/projectProgress';

const PROJECT_PROGRESS_PAGE_SIZE = 300;
const MAX_FETCH_PAGES = 20;
const BATCH_ATTACHMENT_PIN_STORAGE_KEY = 'project-progress-batch-attachment-pins';
const NODE_FILTER_OVERDUE = 'overdue';

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

const route = useRoute();
const {
  isProjectManager,
  loadProjectManagers,
  syncCurrentUser,
  ensureProjectManagerAction,
  canManageNode
} = useProjectProgressPermissions(route);

const projectLoading = ref(false);
const loading = ref(false);
const projectOptions = ref([]);
const selectedProjectKey = ref('');
const progressRecords = ref([]);
const currentBatchKey = ref('');
const activeNodeFilter = ref('');
const detailDialogVisible = ref(false);
const detailNode = ref(null);
const imagePreviewVisible = ref(false);
const previewImageItem = ref(null);
const downloadActionKey = ref('');
const batchAttachmentDialogVisible = ref(false);
const batchAttachmentPinnedIds = ref([]);
const attachmentActionKey = ref('');
const attachmentEditDialogVisible = ref(false);
const attachmentEditItem = ref(null);
const attachmentEditForm = ref({ name: '' });
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
const originalExecutorIds = ref([]);
const originalApproverId = ref('');
const originalPlanRange = ref({
  planStart: '',
  planEnd: ''
});

const fetchAllPages = async (fetcher, params = {}) => {
  const records = [];
  for (let page = 0; page < MAX_FETCH_PAGES; page += 1) {
    const result = await fetcher({
      ...params,
      skip: page * PROJECT_PROGRESS_PAGE_SIZE,
      limit: PROJECT_PROGRESS_PAGE_SIZE
    });
    if (result?.code !== 200 || !Array.isArray(result.data)) {
      return {
        ok: false,
        data: records,
        msg: result?.msg || '加载数据失败'
      };
    }
    records.push(...result.data);
    if (result.data.length < PROJECT_PROGRESS_PAGE_SIZE) {
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

const getProjectCode = (project) =>
  normalizeLabel(project?.project_code || project?.projectCode || project?.['项目编号'] || project?._widget_1769064437789);

const getProjectName = (project) =>
  normalizeLabel(project?.project_name || project?.projectName || project?.name || project?.['项目名称']);

const getProjectType = (project) =>
  normalizeLabel(project?.project_type || project?.projectType || project?.type || project?.['项目类型']);

const getProjectOptionLabel = (project) =>
  normalizeLabel(
    project?.order_no ||
      project?.orderNo ||
      project?.contract_name ||
      project?.contractName ||
      project?.['订单号'] ||
      project?.['合同名称']
  ) || getProjectName(project) || '未命名项目';

const buildProjectOption = (project, index) => {
  const projectCode = getProjectCode(project);
  const projectName = getProjectName(project);
  const projectType = getProjectType(project);
  const label = getProjectOptionLabel(project);
  const subtitle = [projectName, projectCode].filter(Boolean).join(' / ') || label;
  return {
    key: `${projectCode}||${projectName}||${index}`,
    label,
    subtitle,
    projectCode,
    projectName,
    projectType,
    raw: project
  };
};

const selectedProject = computed(
  () => projectOptions.value.find((option) => option.key === selectedProjectKey.value) || null
);

const currentProject = computed(() => {
  const project = selectedProject.value || {};
  const firstRecord = progressRecords.value[0] || {};
  return {
    projectCode: project.projectCode || normalizeLabel(firstRecord.project_code),
    projectName: project.projectName || normalizeLabel(firstRecord.project_name),
    projectType: project.projectType || normalizeLabel(firstRecord.project_type),
    records: progressRecords.value
  };
});

const batchCards = computed(() => {
  const grouped = new Map();
  progressRecords.value.forEach((record) => {
    const batchNo = normalizeBatchNo(record?.batch_no);
    const batchName = normalizeLabel(record?.batch_name);
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

const currentBatchCard = computed(() => {
  if (!batchCards.value.length) return null;
  return batchCards.value.find((item) => item.key === currentBatchKey.value) || batchCards.value[0];
});

const currentBatchRecords = computed(() => currentBatchCard.value?.records || []);

const currentBatchDescriptor = computed(() => {
  if (!currentBatchCard.value) return null;
  return {
    key: currentBatchCard.value.key,
    batchNo: currentBatchCard.value.batchNo,
    batchName: currentBatchCard.value.batchName
  };
});

const currentBatchNodes = computed(() => {
  const nodes = currentBatchRecords.value
    .map((record, index) => normalizeNode(record, index))
    .sort(compareStageNodePosition);
  const stageCounters = new Map();
  return nodes.map((node) => {
    const stageKey = `${node.mainStageLabel || ''}||${node.mainStageOrder ?? ''}`;
    const position = (stageCounters.get(stageKey) || 0) + 1;
    stageCounters.set(stageKey, position);
    return {
      ...node,
      displayNodeOrder: node.projectStageOrder ?? position
    };
  });
});

const isOverdueNode = (node) => normalizeLabel(node?.status).startsWith('超期');

const displayedBatchNodes = computed(() => {
  if (activeNodeFilter.value === NODE_FILTER_OVERDUE) {
    return currentBatchNodes.value.filter(isOverdueNode);
  }
  return currentBatchNodes.value;
});

const stageGroups = computed(() => {
  const grouped = new Map();
  displayedBatchNodes.value.forEach((node) => {
    const key = `${node.mainStageLabel || '__empty__'}||${node.mainStageOrder ?? ''}`;
    if (!grouped.has(key)) {
      grouped.set(key, {
        key,
        title: node.mainStageLabel || '未分组阶段',
        nodes: []
      });
    }
    grouped.get(key).nodes.push(node);
  });
  return Array.from(grouped.values());
});

const progressSummary = computed(() => {
  const nodes = currentBatchNodes.value;
  const totalCount = nodes.length;
  const doneCount = nodes.filter((node) => isDone(node.status)).length;
  const overdueCount = nodes.filter(isOverdueNode).length;
  const warningCount = nodes.filter((node) => node.warningLevel && node.warningLevel !== '正常').length;
  return {
    totalCount,
    doneCount,
    overdueCount,
    warningCount,
    completionRate: totalCount ? Math.round((doneCount / totalCount) * 100) : 0
  };
});

const nodeSectionTitle = computed(() =>
  activeNodeFilter.value === NODE_FILTER_OVERDUE ? '超期节点明细' : '节点执行明细'
);

const nodeSectionCountText = computed(() => {
  if (activeNodeFilter.value === NODE_FILTER_OVERDUE) {
    return `${displayedBatchNodes.value.length} / ${currentBatchNodes.value.length} 个节点`;
  }
  return `${currentBatchNodes.value.length} 个节点`;
});

const nodeEmptyText = computed(() =>
  activeNodeFilter.value === NODE_FILTER_OVERDUE ? '当前批次暂无超期节点' : '当前批次暂无节点'
);

const clearNodeFilter = () => {
  activeNodeFilter.value = '';
};

const handleOverdueSummaryClick = () => {
  if (!progressSummary.value.overdueCount) {
    clearNodeFilter();
    ElMessage.info('当前批次暂无超期节点');
    return;
  }
  activeNodeFilter.value = NODE_FILTER_OVERDUE;
};

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
    return String(a.label || '').localeCompare(String(b.label || ''), 'zh');
  });
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

const delayAffectedNodes = computed(() => {
  if (!canManageNode(delayRow.value)) return [];
  const startIndex = currentBatchNodes.value.findIndex(
    (node) => node.recordId && node.recordId === delayRow.value.recordId
  );
  if (startIndex < 0) return [];
  return currentBatchNodes.value
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

const memberOptions = computed(() =>
  members.value.map((item) => ({
    id: item.user_id,
    label: stripAccountSuffix(item.name || '未命名')
  }))
);

const detailAttachments = computed(() => normalizeAttachmentList(detailNode.value?.siteUploadRaw));
const previewImageTitle = computed(() => previewImageItem.value?.name || '图片预览');
const previewImageUrl = computed(() => previewImageItem.value?.url || '');

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
  currentBatchNodes.value.forEach((node, nodeIndex) => {
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

const batchAttachmentSummaryText = computed(() => {
  const count = batchAttachmentEntries.value.length;
  return isProjectManager.value
    ? `当前批次共汇总 ${count} 个附件，支持置顶、查看、下载、编辑和删除。`
    : `当前批次共汇总 ${count} 个附件，支持置顶、查看和下载。`;
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
  originalApproverId.value = '';
  originalPlanRange.value = {
    planStart: '',
    planEnd: ''
  };
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

watch(delayDialogVisible, (visible) => {
  if (visible) return;
  delayRow.value = null;
  delayForm.value = buildEmptyDelayForm();
});

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

watch(attachmentEditDialogVisible, (visible) => {
  if (visible) return;
  attachmentEditItem.value = null;
  attachmentEditForm.value = { name: '' };
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
  }
);

const loadProjects = async () => {
  projectLoading.value = true;
  try {
    const result = await fetchAllPages(api.listProjectSummary);
    if (!result.ok) {
      projectOptions.value = [];
      ElMessage.error(result.msg || '加载项目失败');
      return;
    }
    projectOptions.value = result.data
      .map(buildProjectOption)
      .filter((option) => option.projectCode || option.projectName);
    if (!selectedProjectKey.value && projectOptions.value.length) {
      selectedProjectKey.value = projectOptions.value[0].key;
      await loadProjectNodes();
    }
  } catch (error) {
    console.error('加载项目失败：', error);
    projectOptions.value = [];
    ElMessage.error('加载项目失败');
  } finally {
    projectLoading.value = false;
  }
};

const loadProjectNodes = async (preferredBatchKey = currentBatchKey.value) => {
  const project = selectedProject.value;
  if (!project) {
    progressRecords.value = [];
    currentBatchKey.value = '';
    return;
  }

  loading.value = true;
  try {
    const result = await fetchAllPages(api.listProjectProgress, {
      projectCode: project.projectCode,
      projectName: project.projectName
    });
    if (result.ok) {
      progressRecords.value = result.data;
      if (preferredBatchKey) {
        currentBatchKey.value = preferredBatchKey;
      }
    } else {
      progressRecords.value = [];
      ElMessage.error(result.msg || '加载项目节点失败');
    }
  } catch (error) {
    console.error('加载项目节点失败：', error);
    progressRecords.value = [];
    ElMessage.error('加载项目节点失败');
  } finally {
    loading.value = false;
  }
};

const handleProjectChange = async (value) => {
  clearNodeFilter();
  detailDialogVisible.value = false;
  detailNode.value = null;
  imagePreviewVisible.value = false;
  previewImageItem.value = null;
  batchAttachmentDialogVisible.value = false;
  if (!value) {
    progressRecords.value = [];
    currentBatchKey.value = '';
    return;
  }
  await loadProjectNodes('');
};

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

const getNodeTitle = (node) => node?.nodeLabel || node?.name || '未命名节点';

const displayValue = (value) => {
  const text = normalizeLabel(value);
  return text || '--';
};

const getStatusTag = (status) => {
  if (status === '完成' || status === '超期完成') return 'success';
  if (status === '待审批' || status === '超期待审批') return 'warning';
  if (status === '超期') return 'danger';
  return 'info';
};

const getWarningTag = (level) => {
  if (level === '三级预警') return 'danger';
  if (level === '二级预警') return 'warning';
  if (level === '一级预警') return 'info';
  return 'success';
};

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

  const preferredStage = (row && buildStageOptionFromRecord(row)) || stageOptions.value[0] || null;
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
      ElMessage.success(`新增节点成功：成功新增 ${createdCount} 个批次节点，重排 ${reorderedCount} 条`);
    }

    createNodeDialogVisible.value = false;
    await loadProjectNodes(currentBatchKey.value);
  } catch (error) {
    console.error('新增节点失败：', error);
    ElMessage.error('新增节点失败');
  } finally {
    creatingNode.value = false;
  }
};

const openEditDialog = async (row) => {
  if (!canManageNode(row)) {
    ElMessage.warning('仅支持编辑具体节点');
    return;
  }
  editRow.value = row;
  const initialExecutorIds = getExecutorIds(row.executorRaw);
  const initialApproverId = getMemberId(row.approverRaw);
  const initialPlanStart = row.planStartRaw ? formatDate(row.planStartRaw) : row.planStart || '';
  const initialPlanEnd = row.planEndRaw ? formatDateTime(row.planEndRaw) : row.planEnd || '';
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
      await loadProjectNodes(currentBatchKey.value);
    } else if (summary.successCount > 0) {
      ElMessage.warning(`节点编辑已部分完成：成功 ${summary.successCount} 条，失败 ${summary.failedCount} 条`);
      editDialogVisible.value = false;
      await loadProjectNodes(currentBatchKey.value);
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

    await loadProjectNodes(currentBatchKey.value);
  } catch (error) {
    console.error('删除节点失败：', error);
    ElMessage.error('删除节点失败');
  }
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
  const shiftedPlanEnd = addDaysToDate(node.planEndRaw, days, true);

  if (JSON.stringify(shiftedPlanTime) !== JSON.stringify(node.rawPlanTime)) {
    payload.plan_time = shiftedPlanTime;
  }
  if (node.planEndRaw && shiftedPlanEnd && shiftedPlanEnd !== formatDateTime(node.planEndRaw)) {
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
        after_plan_end: addDaysToDate(node.planEndRaw, delayDays, true),
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
      const messageParts = [`延期完成：成功 ${updatedCount} 个节点`];
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
      ElMessage.warning(messageParts.join('，'));
    } else {
      ElMessage.success(`延期成功：已顺延 ${updatedCount} 个节点 ${delayDays} 天，并通知 ${notifiedUserCount} 位责任人`);
    }

    delayDialogVisible.value = false;
    await loadProjectNodes(currentBatchKey.value);
  } catch (error) {
    console.error('延期失败：', error);
    ElMessage.error('延期失败');
  } finally {
    delayingNodes.value = false;
  }
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
    await loadProjectNodes(batchKey);
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
  if (
    hasDuplicatedBatchName(batchName, sourceKey) ||
    batchCards.value.some((item) => item.key === nextBatchKey && item.key !== sourceKey)
  ) {
    ElMessage.warning('该批次名称已存在，请使用其他名称');
    return;
  }

  if (nextBatchKey === sourceKey) {
    ElMessage.warning('批次信息未变化');
    return;
  }

  const records = Array.isArray(sourceBatch.records) ? sourceBatch.records : [];
  const validRecords = records.filter((item) => item && getProgressRecordId(item));
  if (!validRecords.length) {
    ElMessage.error('该批次没有可更新的节点记录');
    return;
  }

  editingBatch.value = true;
  try {
    const updateTasks = validRecords.map((record) =>
      api.updateProjectProgress(getProgressRecordId(record), {
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
    await loadProjectNodes(nextBatchKey);
    currentBatchKey.value = nextBatchKey;
  } catch (error) {
    console.error('批次编辑失败：', error);
    ElMessage.error('批次编辑失败');
  } finally {
    editingBatch.value = false;
  }
};

const openDetail = (node) => {
  if (!node) return;
  previewImageItem.value = null;
  imagePreviewVisible.value = false;
  detailNode.value = node;
  detailDialogVisible.value = true;
};

const previewAttachment = (item) => {
  if (!item?.isImage || !item?.url) {
    ElMessage.warning('该附件暂无可预览图片地址');
    return;
  }
  previewImageItem.value = item;
  imagePreviewVisible.value = true;
};

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

const getAttachmentActionKey = (item, index = '') =>
  [
    item?.recordId || detailNode.value?.recordId || detailNode.value?.id || '',
    item?.attachmentIndex ?? index ?? '',
    item?.fileKey || item?.originalUrl || item?.downloadUrl || item?.url || '',
    item?.name || ''
  ].join('::');

const downloadAttachment = async (item, index = '') => {
  if (!item?.canDownload) {
    ElMessage.warning('该附件暂无可下载地址');
    return;
  }

  const actionKey = getAttachmentActionKey(item, index);
  downloadActionKey.value = actionKey;
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
    if (downloadActionKey.value === actionKey) {
      downloadActionKey.value = '';
    }
  }
};

const openBatchAttachmentDialog = () => {
  if (!currentBatchCard.value) {
    ElMessage.warning('请先选择批次');
    return;
  }
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
      await loadProjectNodes(currentBatchKey.value);
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

const openEditBatchAttachmentDialog = (item) => {
  if (!ensureProjectManagerAction('仅项目管理员可编辑附件')) return;
  attachmentEditItem.value = item;
  attachmentEditForm.value = {
    name: item?.name || ''
  };
  attachmentEditDialogVisible.value = true;
};

const handleSaveBatchAttachment = async () => {
  if (!ensureProjectManagerAction('仅项目管理员可编辑附件')) return;
  const item = attachmentEditItem.value;
  const nextName = normalizeLabel(attachmentEditForm.value.name);
  if (!item) {
    ElMessage.error('未找到要编辑的附件');
    return;
  }
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
  attachmentEditDialogVisible.value = false;
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
    previewAttachment(item);
    return;
  }
  const targetUrl = item.originalUrl || item.downloadUrl || item.url;
  if (!targetUrl) {
    ElMessage.warning('该附件暂无可查看地址');
    return;
  }
  window.open(targetUrl, '_blank', 'noopener,noreferrer');
};

onMounted(async () => {
  await loadProjectManagers();
  await syncCurrentUser();
  await loadProjects();
});
</script>

<style scoped>
.progress-mobile-page {
  min-height: 100vh;
  background: #f4f6f8;
  color: #1f2937;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

.progress-mobile-header {
  position: sticky;
  top: 0;
  z-index: 5;
  background: #fff;
  padding: 12px 12px 10px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.page-title {
  font-size: 18px;
  line-height: 24px;
  font-weight: 700;
  color: #111827;
}

.project-select {
  width: 100%;
}

.project-option {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
  line-height: 1.35;
}

.project-option-title,
.project-option-subtitle {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-option-title {
  color: #111827;
  font-size: 14px;
}

.project-option-subtitle {
  color: #909399;
  font-size: 12px;
}

.progress-mobile-body {
  width: 100%;
  max-width: 720px;
  margin: 0 auto;
  box-sizing: border-box;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-x: hidden;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #606266;
  font-size: 13px;
  line-height: 20px;
  margin-bottom: 8px;
}

.section-heading-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.batch-section,
.mobile-action-section,
.summary-section,
.node-section {
  width: 100%;
  min-width: 0;
}

.batch-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 2px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.batch-scroll::-webkit-scrollbar {
  display: none;
}

.batch-card {
  flex: 0 0 148px;
  min-height: 66px;
  border: 1px solid #d8e1ef;
  border-radius: 8px;
  background: #fff;
  padding: 10px;
  text-align: left;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  color: #303133;
}

.batch-card.active {
  border-color: #1677ff;
  background: #eef5ff;
}

.batch-title,
.batch-subtitle {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.batch-title {
  font-size: 14px;
  font-weight: 600;
}

.batch-subtitle {
  font-size: 12px;
  color: #6b7280;
}

.mobile-action-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.mobile-action-grid :deep(.el-button) {
  width: 100%;
  min-width: 0;
  margin-left: 0;
}

.mobile-action-grid :deep(.el-button > span) {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.summary-section {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.summary-card {
  min-width: 0;
  min-height: 74px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #fff;
  padding: 10px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
}

.summary-card-button {
  width: 100%;
  appearance: none;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.summary-card-button.active,
.summary-card-button:focus-visible {
  border-color: #f56c6c;
  box-shadow: 0 0 0 3px rgba(245, 108, 108, 0.14);
}

.summary-card-button.active {
  background: #fff5f5;
}

.completion-card {
  grid-column: 1 / -1;
}

.summary-label {
  font-size: 12px;
  color: #909399;
  line-height: 18px;
}

.summary-value {
  font-size: 22px;
  line-height: 28px;
  font-weight: 700;
  color: #111827;
}

.summary-value.danger {
  color: #f56c6c;
}

.summary-value.warning {
  color: #e6a23c;
}

.stage-list,
.node-card-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stage-group {
  min-width: 0;
}

.stage-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin: 6px 0 8px;
}

.stage-title {
  min-width: 0;
  font-size: 15px;
  line-height: 22px;
  font-weight: 700;
  color: #111827;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stage-count {
  flex-shrink: 0;
  font-size: 12px;
  color: #909399;
}

.node-card {
  min-width: 0;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  padding: 12px;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
  cursor: pointer;
  outline: none;
}

.node-card:focus-visible {
  border-color: #1677ff;
  box-shadow: 0 0 0 3px rgba(22, 119, 255, 0.16);
}

.node-card-header {
  min-width: 0;
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.node-title-wrap {
  min-width: 0;
  flex: 1;
}

.node-title {
  min-width: 0;
  font-size: 15px;
  line-height: 22px;
  font-weight: 700;
  color: #111827;
  overflow-wrap: anywhere;
}

.node-order {
  margin-top: 4px;
  font-size: 12px;
  line-height: 18px;
  color: #909399;
}

.tag-stack {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.node-info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px 10px;
}

.info-item {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font-size: 12px;
  line-height: 18px;
  color: #909399;
}

.info-value {
  min-width: 0;
  font-size: 13px;
  line-height: 20px;
  color: #303133;
  overflow-wrap: anywhere;
}

.node-card-actions {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid #eef2f7;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.node-card-actions :deep(.el-button) {
  min-width: 0;
  width: 100%;
  margin-left: 0;
  padding-left: 8px;
  padding-right: 8px;
}

.node-card-actions :deep(.el-button > span) {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-title-block {
  border-radius: 8px;
  background: #f5f7fa;
  padding: 12px;
}

.detail-title {
  font-size: 17px;
  line-height: 24px;
  font-weight: 700;
  color: #111827;
  overflow-wrap: anywhere;
}

.detail-subtitle {
  margin-top: 4px;
  font-size: 13px;
  line-height: 20px;
  color: #606266;
  overflow-wrap: anywhere;
}

.detail-descriptions :deep(.el-descriptions__label) {
  width: 104px;
  color: #6b7280;
}

.detail-descriptions :deep(.el-descriptions__content) {
  word-break: break-word;
}

.detail-attachments {
  border-radius: 8px;
  background: #f9fafb;
  padding: 12px;
}

.attachment-heading {
  font-size: 13px;
  line-height: 20px;
  color: #606266;
  margin-bottom: 8px;
}

.empty-attachments {
  min-height: 36px;
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  background: #fff;
  color: #909399;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  min-width: 0;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fff;
  padding: 8px 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.attachment-name {
  min-width: 0;
  flex: 1;
  font-size: 13px;
  line-height: 20px;
  color: #303133;
  overflow-wrap: anywhere;
}

.attachment-actions {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}

.attachment-text {
  font-size: 12px;
  color: #909399;
}

.batch-attachment-summary {
  border-radius: 8px;
  background: #f5f7fa;
  padding: 10px 12px;
  color: #606266;
  font-size: 13px;
  line-height: 20px;
  margin-bottom: 10px;
}

.batch-attachment-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.batch-attachment-card {
  min-width: 0;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  padding: 12px;
}

.batch-attachment-card.is-pinned {
  border-color: #f3c96b;
  background: #fffaf0;
}

.batch-attachment-title-row {
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.batch-attachment-name {
  min-width: 0;
  flex: 1;
  font-size: 14px;
  line-height: 22px;
  font-weight: 600;
  color: #111827;
  overflow-wrap: anywhere;
}

.batch-attachment-meta {
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
  line-height: 18px;
  color: #6b7280;
}

.batch-attachment-actions {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.batch-attachment-actions :deep(.el-button) {
  width: 100%;
  min-width: 0;
  margin-left: 0;
  padding-left: 8px;
  padding-right: 8px;
}

.batch-attachment-actions :deep(.el-button > span) {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mobile-form {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mobile-form :deep(.el-select),
.mobile-form :deep(.el-input),
.mobile-form :deep(.el-input-number),
.mobile-form :deep(.el-date-editor) {
  width: 100%;
}

.full-control {
  width: 100%;
}

.dialog-hint,
.delay-dialog-hint {
  margin-top: 6px;
  font-size: 12px;
  line-height: 18px;
  color: #909399;
}

.dialog-switch-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.dialog-switch-label {
  min-width: 0;
  font-size: 13px;
  line-height: 20px;
  color: #606266;
  overflow-wrap: anywhere;
}

.delay-preview-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.delay-preview-tag,
.delay-preview-more {
  max-width: 100%;
  border-radius: 999px;
  background: #eef5ff;
  color: #1677ff;
  font-size: 12px;
  line-height: 18px;
  padding: 4px 8px;
  overflow-wrap: anywhere;
}

.image-preview-body {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  width: 100%;
  max-height: 78vh;
}

.progress-mobile-dialog :deep(.el-dialog__body) {
  padding: 12px;
}

.progress-mobile-dialog :deep(.el-dialog__footer) {
  padding: 10px 12px 14px;
}

@media (max-width: 420px) {
  .progress-mobile-body {
    padding: 10px 8px 14px;
  }

  .node-card-header {
    flex-direction: column;
  }

  .tag-stack {
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .node-card-actions,
  .batch-attachment-actions {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .attachment-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .attachment-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
