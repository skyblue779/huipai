export const normalizeLabel = (value) => {
  if (value === null || value === undefined) return '';
  if (typeof value === 'string') return value.trim();
  return String(value);
};

export const parseDateValue = (value) => {
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

export const parseDateRange = (value) => {
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

export const formatDate = (value) => {
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

const formatDateTimeParts = (value) => {
  const date = value instanceof Date ? value : parseDateValue(value);
  if (!date || Number.isNaN(date.getTime())) return null;
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hour = String(date.getHours()).padStart(2, '0');
  const minute = String(date.getMinutes()).padStart(2, '0');
  const second = String(date.getSeconds()).padStart(2, '0');
  return { date, text: `${year}-${month}-${day} ${hour}:${minute}:${second}` };
};

export const formatDateTime = (value) => {
  if (!value) return '--';
  const parts = formatDateTimeParts(value);
  return parts ? parts.text : String(value);
};

const hasExplicitTime = (value) => typeof value === 'string' && /\d{1,2}:\d{2}/.test(value);

const hasNonZeroTime = (date) =>
  date instanceof Date &&
  !Number.isNaN(date.getTime()) &&
  (date.getHours() !== 0 || date.getMinutes() !== 0 || date.getSeconds() !== 0);

const formatShiftedDate = (date, sourceValue, forceTime) => {
  if (forceTime || hasExplicitTime(sourceValue) || hasNonZeroTime(date)) {
    return formatDateTime(date);
  }
  return formatDate(date);
};

export const addDaysToDate = (value, days, forceTime = false) => {
  const parsed = parseDateValue(value);
  if (!parsed) return '';
  const next = new Date(parsed.getTime());
  next.setDate(next.getDate() + days);
  return formatShiftedDate(next, value, forceTime);
};

export const formatDateCell = (value) => {
  if (!value) return '';
  return formatDate(value);
};

export const formatDateTimeCell = (value) => {
  if (!value) return '';
  return formatDateTime(value);
};

export const stripAccountSuffix = (value) => {
  if (value === null || value === undefined) return '';
  return String(value)
    .replace(/\s*[\(（][^()（）]*[\)）]\s*$/g, '')
    .trim();
};

export const formatUser = (value) => {
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

export const getExecutorIds = (value) => {
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

export const getMemberId = (value) => {
  const ids = getExecutorIds(value);
  return ids.length ? ids[0] : '';
};

export const normalizeIdList = (ids) =>
  (Array.isArray(ids) ? ids : [])
    .map((id) => String(id).trim())
    .filter(Boolean)
    .sort();

export const normalizeBatchNo = (value) => {
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

export const parseBatchNoNumber = (value) => {
  const normalized = normalizeBatchNo(value);
  if (!normalized) return null;
  const numeric = Number(normalized);
  if (!Number.isFinite(numeric)) return null;
  const asInt = Math.trunc(numeric);
  return asInt > 0 ? asInt : null;
};

export const buildBatchKey = (batchNo, batchName) => {
  const normalizedNo = normalizeBatchNo(batchNo);
  const normalizedName = normalizeLabel(batchName);
  if (!normalizedNo && !normalizedName) return '__default_batch__';
  return `${normalizedNo}||${normalizedName}`;
};

export const buildBatchCardLabel = (batchNo, batchName) => {
  const normalizedNo = normalizeBatchNo(batchNo);
  const normalizedName = normalizeLabel(batchName);
  if (normalizedNo && normalizedName) return `${normalizedName}（批次 ${normalizedNo}）`;
  if (normalizedName) return normalizedName;
  if (normalizedNo) return `批次 ${normalizedNo}`;
  return '未分批';
};

export const buildBatchCardSubLabel = (batchNo, batchName) => {
  const normalizedNo = normalizeBatchNo(batchNo);
  const normalizedName = normalizeLabel(batchName);
  if (!normalizedNo && !normalizedName) return '历史节点';
  if (normalizedNo && normalizedName) return `编号 ${normalizedNo}`;
  if (normalizedNo) return `编号 ${normalizedNo}`;
  return '未设置编号';
};

export const normalizeOrderValue = (value) => {
  if (value === null || value === undefined) return null;
  const trimmed = String(value).trim();
  if (!trimmed) return null;
  const numeric = Number(trimmed);
  if (Number.isFinite(numeric)) return numeric;
  return trimmed;
};

export const compareOrderValue = (a, b) => {
  if (a === null || a === undefined) return b === null || b === undefined ? 0 : 1;
  if (b === null || b === undefined) return -1;
  const aIsNumber = typeof a === 'number' && Number.isFinite(a);
  const bIsNumber = typeof b === 'number' && Number.isFinite(b);
  if (aIsNumber && bIsNumber) return a - b;
  return String(a).localeCompare(String(b), 'zh');
};

const compareTextValue = (a, b) => String(a || '').localeCompare(String(b || ''), 'zh');

export const parsePositiveInt = (value) => {
  if (value === null || value === undefined || value === '') return null;
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return null;
  const normalizedNumber = Math.trunc(numeric);
  return normalizedNumber > 0 ? normalizedNumber : null;
};

export const buildStageKey = (mainStage, mainStageOrder) =>
  `${normalizeLabel(mainStage)}||${normalizeLabel(mainStageOrder)}`;

export const getProgressRecordId = (record) =>
  record?._id || record?.id || record?.record_id || record?.recordId || '';

export const getMainStageLabel = (record) =>
  normalizeLabel(record?.main_stage || record?.mainStage || record?.mainStageLabel);

export const getMainStageOrder = (record) =>
  normalizeOrderValue(record?.main_stage_order ?? record?.mainStageOrder);

export const getProjectStageLabel = (record) =>
  normalizeLabel(record?.project_stage || record?.projectStage || record?.stage || record?.nodeLabel);

export const getProjectStageOrder = (record) =>
  normalizeOrderValue(record?.project_stage_order ?? record?.projectStageOrder);

export const hasProjectStageRecord = (record) => Boolean(getProjectStageLabel(record));

export const buildStageOptionFromRecord = (record) => {
  const label = getMainStageLabel(record);
  if (!label) return null;
  const order = getMainStageOrder(record);
  return {
    key: buildStageKey(label, order),
    label,
    order
  };
};

export const compareStageNodePosition = (a, b) => {
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

export const compareBatchGroup = (a, b) => {
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

export const isDone = (status) => status === '完成' || status === '超期完成';

export const normalizeNode = (record, index) => {
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
  const recordId = record._id || record.id || record.record_id || record.recordId || '';

  return {
    id: recordId || `${index}`,
    recordId,
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
    planEnd: formatDateTimeCell(planEndDate),
    actualFinishRaw: actualFinishDate,
    actualFinish: formatDateTimeCell(actualFinishDate),
    planStartSort: planStartDate ? planStartDate.getTime() : null,
    originalIndex: index,
    isMilestone: isDone(record.status || '未完成')
  };
};

export const shiftPlanTimeValue = (rawValue, days) => {
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

export const updatePlanTimeValue = (rawValue, newStart, fallbackEnd) => {
  if (!newStart) return rawValue;
  const formatEnd = (value) => {
    if (!value) return null;
    if (typeof value === 'string') return value.replace(/\//g, '-');
    if (value instanceof Date) return formatDateTime(value);
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

const IMAGE_EXT_RE = /\.(png|jpe?g|gif|bmp|webp|svg|heic|heif)(?:$|[?#])/i;

const isImageByText = (value) => {
  if (!value) return false;
  return IMAGE_EXT_RE.test(String(value).trim());
};

export const isImageAttachment = (name, url, mimeType) => {
  const normalizedMime = String(mimeType || '').trim().toLowerCase();
  if (normalizedMime.startsWith('image/')) return true;
  return isImageByText(name) || isImageByText(url);
};

const isDirectAttachmentUrl = (value) => /^https?:\/\//i.test(value) || String(value || '').startsWith('/');

export const formatAttachment = (item) => {
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

export const normalizeAttachmentList = (value) => {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value.map(formatAttachment).filter(Boolean);
  }
  const single = formatAttachment(value);
  return single ? [single] : [];
};

export const normalizeAttachmentPayloadList = (value) => {
  if (!value) return [];
  return Array.isArray(value) ? [...value] : [value];
};
