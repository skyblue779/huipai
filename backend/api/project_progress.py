"""
Project progress API routes.
"""
import logging
import json
import os
import re
import uuid
import threading
from collections import deque
from datetime import datetime, timedelta
from urllib.parse import quote, unquote, urlparse
import requests
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app, send_from_directory, Response, stream_with_context
from api.online_office import api_client
from field_mapping import PROJECT_FIELDS_EN, PROJECT_PROGRESS_FIELDS_EN
from config import REQUEST_TIMEOUT, DINGDING_CORP_ID, DELAY_REQUESTS_FILE, DELAY_REQUEST_CC_ROLE_ID

logger = logging.getLogger(__name__)

progress_bp = Blueprint('progress', __name__, url_prefix='/api/progress')

STATUS_PENDING = '\u672a\u5b8c\u6210'
STATUS_OVERDUE = '\u8d85\u671f'
STATUS_DONE = '\u5b8c\u6210'
STATUS_OVERDUE_DONE = '\u8d85\u671f\u5b8c\u6210'
STATUS_PENDING_APPROVAL = '\u5f85\u5ba1\u6279'
STATUS_OVERDUE_PENDING_APPROVAL = '\u8d85\u671f\u5f85\u5ba1\u6279'

DONE_STATUSES = {STATUS_DONE, STATUS_OVERDUE_DONE}
WAITING_APPROVAL_STATUSES = {STATUS_PENDING_APPROVAL, STATUS_OVERDUE_PENDING_APPROVAL}
DELAY_REQUEST_STATUS_PENDING = 'pending'
DELAY_REQUEST_STATUS_APPROVED = 'approved'
DELAY_REQUEST_STATUS_REJECTED = 'rejected'

PROJECT_ADMIN_KEYWORDS = ('管理员', 'admin')
DATE_PATTERN = re.compile(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?')
delay_request_lock = threading.Lock()


def _normalize_executor(value):
    if value is None:
        return value
    if isinstance(value, list):
        normalized = []
        for item in value:
            if isinstance(item, dict):
                user_id = item.get('user_id') or item.get('_id') or item.get('id')
                if user_id:
                    normalized.append(str(user_id))
            elif item:
                normalized.append(str(item))
        return normalized
    if isinstance(value, dict):
        user_id = value.get('user_id') or value.get('_id') or value.get('id')
        return [str(user_id)] if user_id else []
    return [str(value)]


def _normalize_single_member(value):
    if value is None:
        return value
    if isinstance(value, list):
        for item in value:
            normalized = _normalize_single_member(item)
            if normalized:
                return normalized
        return ''
    if isinstance(value, dict):
        user_id = value.get('user_id') or value.get('_id') or value.get('id')
        return str(user_id).strip() if user_id else ''
    return str(value).strip()


def _normalize_delay_request_status(value):
    text = str(value or '').strip().lower()
    if text in {
        DELAY_REQUEST_STATUS_PENDING,
        DELAY_REQUEST_STATUS_APPROVED,
        DELAY_REQUEST_STATUS_REJECTED
    }:
        return text
    return DELAY_REQUEST_STATUS_PENDING


def _now_text():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def _ensure_delay_request_store():
    directory = os.path.dirname(DELAY_REQUESTS_FILE)
    if directory:
        os.makedirs(directory, exist_ok=True)
    if not os.path.isfile(DELAY_REQUESTS_FILE):
        with open(DELAY_REQUESTS_FILE, 'w', encoding='utf-8') as file_obj:
            json.dump([], file_obj, ensure_ascii=False, indent=2)


def _load_delay_requests():
    with delay_request_lock:
        _ensure_delay_request_store()
        try:
            with open(DELAY_REQUESTS_FILE, 'r', encoding='utf-8') as file_obj:
                data = json.load(file_obj)
                return data if isinstance(data, list) else []
        except Exception as exc:
            logger.error('Load delay requests failed: %s', exc)
            return []


def _save_delay_requests(records):
    with delay_request_lock:
        _ensure_delay_request_store()
        with open(DELAY_REQUESTS_FILE, 'w', encoding='utf-8') as file_obj:
            json.dump(records, file_obj, ensure_ascii=False, indent=2)


def _is_project_admin_candidate(value):
    if not value:
        return False
    if isinstance(value, list):
        return any(_is_project_admin_candidate(item) for item in value)
    if isinstance(value, dict):
        tokens = [
            value.get('name'),
            value.get('user_name'),
            value.get('account'),
            value.get('nickname'),
            value.get('realname')
        ]
    else:
        tokens = [value]
    for token in tokens:
        text = str(token or '').strip().lower()
        if not text:
            continue
        if any(keyword.lower() in text for keyword in PROJECT_ADMIN_KEYWORDS):
            return True
    return False


def _extract_delay_request_users(value):
    if not value:
        return []
    if isinstance(value, list):
        users = []
        for item in value:
            users.extend(_extract_delay_request_users(item))
        return users
    if isinstance(value, dict):
        return [value]
    return [{'user_id': str(value).strip()}]


def _resolve_delay_request_reviewer_ids(candidates, users):
    reviewer_ids = []
    for item in candidates or []:
        if not _is_project_admin_candidate(item):
            continue
        for user in _extract_delay_request_users(item):
            matched = _resolve_dingding_user_ids(user, users)
            for user_id in matched:
                if user_id and user_id not in reviewer_ids:
                    reviewer_ids.append(user_id)

    if reviewer_ids:
        return reviewer_ids

    for user in users or []:
        if not _is_project_admin_candidate(user):
            continue
        user_id = str(user.get('user_id') or user.get('_id') or user.get('id') or '').strip()
        if user_id and user_id not in reviewer_ids:
            reviewer_ids.append(user_id)
    return reviewer_ids


def _add_unique_user_id(target, user_id):
    normalized = str(user_id or '').strip()
    if normalized and normalized not in target:
        target.append(normalized)


def _resolve_delay_request_user_ids(value, users):
    user_ids = []
    if isinstance(value, list):
        for item in value:
            for user_id in _resolve_delay_request_user_ids(item, users):
                _add_unique_user_id(user_ids, user_id)
        return user_ids

    if isinstance(value, dict):
        tokens = [
            value.get('user_id'),
            value.get('userid'),
            value.get('userId'),
            value.get('_id'),
            value.get('id'),
            value.get('account'),
            value.get('name'),
            value.get('username'),
            value.get('user_name'),
            value.get('userName'),
            value.get('nickname'),
            value.get('realname'),
            value.get('uniqueid'),
            value.get('mobile'),
            value.get('email')
        ]
    else:
        tokens = [value]

    for token in tokens:
        if not token:
            continue
        matched = _match_user_id(users, token)
        candidate = matched
        if not candidate and (not users or _looks_like_user_id(token)):
            candidate = str(token).strip()
        _add_unique_user_id(user_ids, candidate)
    return user_ids


def _resolve_role_member_user_ids(role_id, users):
    normalized_role_id = str(role_id or '').strip()
    if not normalized_role_id:
        return []
    try:
        members = api_client.list_role_members(normalized_role_id)
    except Exception as exc:
        logger.error('List role members failed for delay request cc role %s: %s', normalized_role_id, exc)
        return []

    member_ids = []
    for member in members or []:
        for user_id in _resolve_delay_request_user_ids(member, users):
            _add_unique_user_id(member_ids, user_id)
    return member_ids


def _build_project_filter(project_code, project_name):
    cond = []
    if project_code:
        cond.append({
            'field': PROJECT_FIELDS_EN['project_code'],
            'method': 'like',
            'value': [project_code]
        })
    if project_name:
        cond.append({
            'field': PROJECT_FIELDS_EN['project_name'],
            'method': 'like',
            'value': [project_name]
        })
    if not cond:
        return None
    return {
        'rel': 'and',
        'cond': cond
    }


def _resolve_project_business_owner(project_code, project_name):
    filter_obj = _build_project_filter(project_code, project_name)
    if not filter_obj:
        return None

    try:
        projects = api_client.list_projects_en(
            skip=0,
            limit=20,
            filter_obj=filter_obj,
            fields=['project_code', 'project_name', 'business_owner']
        )
    except Exception as exc:
        logger.error('Resolve project business owner failed: %s', exc)
        return None

    if not projects:
        return None

    normalized_code = _normalize_token(project_code)
    normalized_name = _normalize_token(project_name)
    for project in projects:
        code_matches = not normalized_code or _normalize_token(project.get('project_code')) == normalized_code
        name_matches = not normalized_name or _normalize_token(project.get('project_name')) == normalized_name
        if code_matches and name_matches and project.get('business_owner'):
            return project.get('business_owner')

    for project in projects:
        if project.get('business_owner'):
            return project.get('business_owner')
    return None


def _resolve_project_codes_by_order_or_code(search):
    text = str(search or '').strip()
    if not text:
        return []
    filter_obj = {
        'rel': 'or',
        'cond': [
            {
                'field': PROJECT_FIELDS_EN['order_no'],
                'method': 'like',
                'value': [text]
            },
            {
                'field': PROJECT_FIELDS_EN['project_code'],
                'method': 'like',
                'value': [text]
            }
        ]
    }
    try:
        projects = api_client.list_projects_en(
            skip=0,
            limit=300,
            filter_obj=filter_obj,
            fields=['project_code', 'order_no']
        )
    except Exception as exc:
        logger.error('Resolve project codes by order or code failed: %s', exc)
        return []

    codes = []
    for project in projects or []:
        code = str(project.get('project_code') or '').strip()
        if code and code not in codes:
            codes.append(code)
    return codes


def _is_delay_request_business_owner_reviewer(reviewer, business_owner):
    if not business_owner:
        return True
    if not reviewer:
        return False
    try:
        users = api_client.list_users()
    except Exception as exc:
        logger.error('List users failed before checking delay request reviewer: %s', exc)
        users = []

    owner_ids = _resolve_delay_request_user_ids(business_owner, users)
    reviewer_ids = _resolve_delay_request_user_ids(reviewer, users)
    if owner_ids and reviewer_ids:
        return any(user_id in owner_ids for user_id in reviewer_ids)

    return _normalize_token(_format_member_display(reviewer)) == _normalize_token(_format_member_display(business_owner))


def _parse_datetime_value(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    formats = (
        '%Y-%m-%d %H:%M:%S',
        '%Y/%m/%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y/%m/%d %H:%M',
        '%Y-%m-%d',
        '%Y/%m/%d'
    )
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _shift_datetime_match(text, days):
    original = str(text or '')
    parsed = _parse_datetime_value(original)
    if parsed is None:
        return original
    shifted = parsed + timedelta(days=days)
    if ':' in original:
        if len(original.split(':')) >= 3:
            fmt = '%Y-%m-%d %H:%M:%S'
        else:
            fmt = '%Y-%m-%d %H:%M'
    else:
        fmt = '%Y-%m-%d'
    return shifted.strftime(fmt)


def _shift_date_like_value(value, days):
    if value is None:
        return value
    if isinstance(value, list):
        return [_shift_date_like_value(item, days) for item in value]
    if isinstance(value, dict):
        return {key: _shift_date_like_value(item, days) for key, item in value.items()}
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return value
        return DATE_PATTERN.sub(lambda match: _shift_datetime_match(match.group(0), days), value)

    parsed = _parse_datetime_value(value)
    if parsed is None:
        return value
    return (parsed + timedelta(days=days)).strftime('%Y-%m-%d')


def _normalize_token(value):
    if value is None:
        return ''
    return str(value).strip().lower()


def _looks_like_user_id(value):
    text = str(value or '').strip()
    if len(text) < 8 or ' ' in text:
        return False
    normalized = text.replace('-', '').replace('_', '')
    return normalized.isalnum()


def _match_user_id(users, token):
    normalized = _normalize_token(token)
    if not normalized:
        return ''
    for user in users or []:
        if not isinstance(user, dict):
            continue
        for key in (
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
        ):
            if _normalize_token(user.get(key)) == normalized:
                return str(user.get('user_id') or user.get('_id') or user.get('id') or '').strip()
    return ''


def _resolve_dingding_user_ids(value, users):
    resolved = []
    for token in _normalize_executor(value) or []:
        matched = _match_user_id(users, token)
        candidate = matched
        if not candidate and (not users or _looks_like_user_id(token)):
            candidate = str(token).strip()
        if candidate and candidate not in resolved:
            resolved.append(candidate)
    return resolved


def _build_batch_label(batch_no='', batch_name=''):
    no_text = str(batch_no or '').strip()
    name_text = str(batch_name or '').strip()
    if no_text and name_text:
        return f'{name_text}（批次 {no_text}）'
    if name_text:
        return name_text
    if no_text:
        return f'批次 {no_text}'
    return '未分批'


def _build_delay_node_label(main_stage_label='', node_label=''):
    main_label = str(main_stage_label or '').strip()
    stage_label = str(node_label or '').strip()
    if main_label and stage_label and main_label != stage_label:
        return f'{main_label} / {stage_label}'
    return stage_label or main_label or '未命名节点'


def _build_delay_node_schedule_text(node):
    before_date = str(node.get('before_plan_end') or node.get('before_plan_start') or '').strip()
    after_date = str(node.get('after_plan_end') or node.get('after_plan_start') or '').strip()
    if before_date and after_date:
        return f'{before_date} -> {after_date}'
    if after_date:
        return f'延期后：{after_date}'
    if before_date:
        return f'原计划：{before_date}'
    return '计划日期未设置'


def _build_delay_message_content(project_name, project_code, batch_no, batch_name, delay_days, nodes):
    lines = [
        f"项目名称：{str(project_name or '').strip() or '--'}",
        f"项目编号：{str(project_code or '').strip() or '--'}",
        f"批次：{_build_batch_label(batch_no, batch_name)}",
        f"延期天数：{delay_days} 天",
        "延期节点："
    ]
    for index, node in enumerate(nodes, start=1):
        lines.append(
            f"{index}. {_build_delay_node_label(node.get('main_stage_label'), node.get('node_label'))}，"
            f"{_build_delay_node_schedule_text(node)}"
        )
    return '\n'.join(lines)


def _extract_account_corp_id(account_info):
    if not isinstance(account_info, dict):
        return ''

    last_selected = str(account_info.get('last_sel_corp_id') or '').strip()
    if last_selected:
        return last_selected

    corp_id = str(account_info.get('corp_id') or '').strip()
    if corp_id:
        return corp_id

    corp_list = account_info.get('corp')
    if isinstance(corp_list, list):
        preferred = ''
        for item in corp_list:
            if not isinstance(item, dict):
                continue
            item_corp_id = str(item.get('corp_id') or '').strip()
            if not item_corp_id:
                continue
            if item.get('owner') is False:
                return item_corp_id
            if not preferred:
                preferred = item_corp_id
        if preferred:
            return preferred

    return ''


def _extract_notify_error_message(error):
    response = getattr(error, 'response', None)
    response_text = ''
    if response is not None:
        try:
            payload = response.json()
            code = str(payload.get('code') or '').strip()
            msg = str(payload.get('msg') or '').strip()
            if code == '13003':
                return '钉钉团队号配置错误，请检查 DINGDING_CORP_ID'
            if code == '12003':
                return '当前责任人不是该钉钉团队内的合法接收成员'
            if msg:
                return msg
        except Exception:
            response_text = str(getattr(response, 'text', '') or '').strip()
    raw_text = response_text or str(error or '').strip()
    if 'Incorrect team information' in raw_text:
        return '钉钉团队号配置错误，请检查 DINGDING_CORP_ID'
    if 'No legal message recipient was matched' in raw_text:
        return '当前责任人不是该钉钉团队内的合法接收成员'
    return raw_text or '钉钉通知发送失败'


def _send_delay_notifications(project_name, project_code, batch_no, batch_name, delay_days, nodes):
    summary = {
        'notified_user_count': 0,
        'notify_failed_count': 0,
        'notified_node_count': 0,
        'notification_disabled': False,
        'notify_error_summary': ''
    }

    if not nodes:
        return summary

    if not DINGDING_CORP_ID:
        logger.warning('DINGDING_CORP_ID is empty, skip project progress delay notification')
        summary['notification_disabled'] = True
        return summary

    try:
        users = api_client.list_users()
    except Exception as exc:
        logger.error('List users failed before sending project progress delay notification: %s', exc)
        users = []

    grouped = {}
    notified_record_ids = set()
    for node in nodes:
        user_ids = _resolve_dingding_user_ids(
            node.get('executor_raw') or node.get('executor_ids'),
            users
        )
        if not user_ids:
            continue
        record_id = str(node.get('record_id') or '').strip()
        if record_id:
            notified_record_ids.add(record_id)
        for user_id in user_ids:
            grouped.setdefault(user_id, []).append(node)

    summary['notified_node_count'] = len(notified_record_ids)
    if not grouped:
        return summary

    title = '项目节点延期通知'
    error_messages = []
    account_info_cache = {}
    for user_id, user_nodes in grouped.items():
        try:
            if user_id not in account_info_cache:
                try:
                    account_info_cache[user_id] = api_client.get_account_info(user_id=user_id)
                except Exception as account_error:
                    logger.warning(
                        'Get account info failed for user %s before sending delay notification: %s',
                        user_id,
                        account_error
                    )
                    account_info_cache[user_id] = {}

            corp_id = _extract_account_corp_id(account_info_cache.get(user_id)) or DINGDING_CORP_ID
            if not corp_id:
                readable_error = '未找到可用的钉钉团队号'
                if readable_error not in error_messages:
                    error_messages.append(readable_error)
                summary['notify_failed_count'] += 1
                continue

            api_client.send_dingding_message(
                corp_id=corp_id,
                users=[user_id],
                title=title,
                content=_build_delay_message_content(
                    project_name,
                    project_code,
                    batch_no,
                    batch_name,
                    delay_days,
                    user_nodes
                )
            )
            summary['notified_user_count'] += 1
        except Exception as exc:
            summary['notify_failed_count'] += 1
            readable_error = _extract_notify_error_message(exc)
            if readable_error and readable_error not in error_messages:
                error_messages.append(readable_error)
            logger.error(
                'Send project progress delay notification failed for user %s: %s',
                user_id,
                readable_error
            )
            if readable_error == '钉钉团队号配置错误，请检查 DINGDING_CORP_ID':
                break

    if error_messages:
        summary['notify_error_summary'] = '；'.join(error_messages)

    return summary


def _format_member_display(value):
    if not value:
        return '--'
    if isinstance(value, list):
        names = [_format_member_display(item) for item in value]
        names = [item for item in names if item and item != '--']
        return ' / '.join(names) if names else '--'
    if isinstance(value, dict):
        return str(
            value.get('name')
            or value.get('username')
            or value.get('user_name')
            or value.get('userName')
            or value.get('nickname')
            or value.get('realname')
            or value.get('account')
            or value.get('user_id')
            or value.get('_id')
            or value.get('id')
            or '--'
        ).strip() or '--'
    return str(value).strip() or '--'


def _build_approval_message_content(record):
    project_name = str(record.get('project_name') or '').strip() or '--'
    project_code = str(record.get('project_code') or '').strip() or '--'
    batch_no = record.get('batch_no', '')
    batch_name = record.get('batch_name', '')
    main_stage = str(record.get('main_stage') or '').strip()
    node_name = str(record.get('project_stage') or '').strip()
    if main_stage and node_name and main_stage != node_name:
        stage_label = f'{main_stage} / {node_name}'
    else:
        stage_label = node_name or main_stage or '--'

    lines = [
        f"\u9879\u76ee\u540d\u79f0\uff1a{project_name}",
        f"\u9879\u76ee\u7f16\u53f7\uff1a{project_code}",
        f"\u6279\u6b21\uff1a{_build_batch_label(batch_no, batch_name)}",
        f"\u8282\u70b9\uff1a{stage_label}",
        f"\u8d23\u4efb\u4eba\uff1a{_format_member_display(record.get('executor'))}",
        f"\u8ba1\u5212\u5b8c\u6210\uff1a{str(record.get('plan_finishtime') or '').strip() or '--'}",
        f"\u5b9e\u9645\u5b8c\u6210\uff1a{str(record.get('actual_finish') or '').strip() or '--'}",
        f"\u6267\u884c\u8bf4\u660e\uff1a{str(record.get('execution_note') or '').strip() or '--'}",
    ]

    overdue_reason = str(record.get('overdue_reason') or '').strip()
    if overdue_reason:
        lines.append(f"\u8d85\u671f\u539f\u56e0\uff1a{overdue_reason}")

    lines.append('\u8bf7\u53ca\u65f6\u8fdb\u5165\u7cfb\u7edf\u5b8c\u6210\u8282\u70b9\u5ba1\u6279\u3002')
    return '\n'.join(lines)


def _send_approval_notifications(record):
    summary = {
        'notified_user_count': 0,
        'notify_failed_count': 0,
        'notification_disabled': False,
        'notify_error_summary': ''
    }

    approver_value = record.get('approver')
    if not approver_value:
        return summary

    try:
        users = api_client.list_users()
    except Exception as exc:
        logger.error('List users failed before sending project progress approval notification: %s', exc)
        users = []

    approver_ids = _resolve_dingding_user_ids(approver_value, users)
    if not approver_ids:
        return summary

    title = '\u9879\u76ee\u8282\u70b9\u5ba1\u6279\u63d0\u9192'
    error_messages = []
    account_info_cache = {}

    for user_id in approver_ids:
        try:
            if user_id not in account_info_cache:
                try:
                    account_info_cache[user_id] = api_client.get_account_info(user_id=user_id)
                except Exception as account_error:
                    logger.warning(
                        'Get account info failed for user %s before sending approval notification: %s',
                        user_id,
                        account_error
                    )
                    account_info_cache[user_id] = {}

            corp_id = _extract_account_corp_id(account_info_cache.get(user_id)) or DINGDING_CORP_ID
            if not corp_id:
                readable_error = '\u672a\u627e\u5230\u53ef\u7528\u7684\u9489\u9489\u56e2\u961f\u53f7'
                if readable_error not in error_messages:
                    error_messages.append(readable_error)
                summary['notify_failed_count'] += 1
                continue

            api_client.send_dingding_message(
                corp_id=corp_id,
                users=[user_id],
                title=title,
                content=_build_approval_message_content(record)
            )
            summary['notified_user_count'] += 1
        except Exception as exc:
            summary['notify_failed_count'] += 1
            readable_error = _extract_notify_error_message(exc)
            if readable_error and readable_error not in error_messages:
                error_messages.append(readable_error)
            logger.error(
                'Send project progress approval notification failed for user %s: %s',
                user_id,
                readable_error
            )
            if readable_error == '钉钉团队号配置错误，请检查 DINGDING_CORP_ID':
                break

    if error_messages:
        summary['notify_error_summary'] = '；'.join(error_messages)

    return summary


def _build_delay_request_message_content(request_record):
    nodes = request_record.get('nodes') or []
    lines = [
        f"项目名称：{str(request_record.get('project_name') or '').strip() or '--'}",
        f"项目编号：{str(request_record.get('project_code') or '').strip() or '--'}",
        f"批次：{_build_batch_label(request_record.get('batch_no'), request_record.get('batch_name'))}",
        f"申请人：{_format_member_display(request_record.get('applicant'))}",
        f"审核人：{_format_member_display(request_record.get('business_owner'))}",
        f"延期天数：{request_record.get('delay_days') or 0} 天"
    ]

    reason = str(request_record.get('reason') or '').strip()
    if reason:
        lines.append(f"申请原因：{reason}")

    lines.append('申请节点：')
    for index, node in enumerate(nodes, start=1):
        lines.append(
            f"{index}. {_build_delay_node_label(node.get('main_stage_label'), node.get('node_label'))}"
        )
    lines.append('请在项目进度管理中审核延期申请。')
    return '\n'.join(lines)


def _send_delay_request_notifications(request_record):
    summary = {
        'notified_user_count': 0,
        'cc_notified_user_count': 0,
        'notify_failed_count': 0,
        'notification_disabled': False,
        'reviewer_missing': False,
        'notify_error_summary': ''
    }

    try:
        users = api_client.list_users()
    except Exception as exc:
        logger.error('List users failed before sending project delay request notification: %s', exc)
        users = []

    reviewer_ids = _resolve_delay_request_user_ids(request_record.get('business_owner'), users)
    cc_ids = _resolve_role_member_user_ids(request_record.get('cc_role_id') or DELAY_REQUEST_CC_ROLE_ID, users)
    recipient_ids = []
    for user_id in reviewer_ids:
        _add_unique_user_id(recipient_ids, user_id)
    for user_id in cc_ids:
        _add_unique_user_id(recipient_ids, user_id)

    if not reviewer_ids:
        summary['reviewer_missing'] = True

    if not recipient_ids:
        summary['notification_disabled'] = True
        return summary

    title = '项目节点延期申请'
    error_messages = []
    account_info_cache = {}

    for user_id in recipient_ids:
        try:
            if user_id not in account_info_cache:
                try:
                    account_info_cache[user_id] = api_client.get_account_info(user_id=user_id)
                except Exception as account_error:
                    logger.warning(
                        'Get account info failed for user %s before sending delay request notification: %s',
                        user_id,
                        account_error
                    )
                    account_info_cache[user_id] = {}

            corp_id = _extract_account_corp_id(account_info_cache.get(user_id)) or DINGDING_CORP_ID
            if not corp_id:
                readable_error = '未找到可用的钉钉团队号'
                if readable_error not in error_messages:
                    error_messages.append(readable_error)
                summary['notify_failed_count'] += 1
                continue

            api_client.send_dingding_message(
                corp_id=corp_id,
                users=[user_id],
                title=title,
                content=_build_delay_request_message_content(request_record)
            )
            if user_id in reviewer_ids:
                summary['notified_user_count'] += 1
            else:
                summary['cc_notified_user_count'] += 1
        except Exception as exc:
            summary['notify_failed_count'] += 1
            readable_error = _extract_notify_error_message(exc)
            if readable_error and readable_error not in error_messages:
                error_messages.append(readable_error)
            logger.error(
                'Send project delay request notification failed for user %s: %s',
                user_id,
                readable_error
            )
            if readable_error == '钉钉团队号配置错误，请检查 DINGDING_CORP_ID':
                break

    if error_messages:
        summary['notify_error_summary'] = '；'.join(error_messages)
    return summary


def _build_delay_payload_from_record(record, delay_days):
    payload = {}
    plan_time = record.get('plan_time')
    shifted_plan_time = _shift_date_like_value(plan_time, delay_days)
    if shifted_plan_time != plan_time:
        payload['plan_time'] = shifted_plan_time

    plan_finish = record.get('plan_finishtime')
    shifted_plan_finish = _shift_date_like_value(plan_finish, delay_days)
    if shifted_plan_finish != plan_finish:
        payload['plan_finishtime'] = shifted_plan_finish
    return payload


def _prepare_delay_nodes_for_apply(nodes, delay_days):
    prepared_nodes = []
    skipped_count = 0

    for node in nodes or []:
        if not isinstance(node, dict):
            skipped_count += 1
            continue

        record_id = str(node.get('record_id') or node.get('data_id') or '').strip()
        if not record_id:
            skipped_count += 1
            continue

        current_record = {}
        try:
            current_record = api_client.get_project_progress(record_id)
        except Exception as exc:
            logger.error('Get project progress failed before applying delay for %s: %s', record_id, exc)

        payload = node.get('payload')
        if not isinstance(payload, dict) or not payload:
            payload = _build_delay_payload_from_record(current_record, delay_days)
        if not payload:
            skipped_count += 1
            continue

        prepared_nodes.append({
            'record_id': record_id,
            'main_stage_label': str(node.get('main_stage_label') or current_record.get('main_stage') or '').strip(),
            'node_label': str(node.get('node_label') or current_record.get('project_stage') or '').strip(),
            'before_plan_start': str(node.get('before_plan_start') or current_record.get('plan_time') or '').strip(),
            'after_plan_start': str(node.get('after_plan_start') or payload.get('plan_time') or '').strip(),
            'before_plan_end': str(node.get('before_plan_end') or current_record.get('plan_finishtime') or '').strip(),
            'after_plan_end': str(node.get('after_plan_end') or payload.get('plan_finishtime') or '').strip(),
            'executor_ids': node.get('executor_ids') or _normalize_executor(current_record.get('executor')) or [],
            'executor_raw': node.get('executor_raw') or current_record.get('executor'),
            'payload': payload
        })

    return prepared_nodes, skipped_count


def _apply_delay_nodes(project_name, project_code, batch_no, batch_name, delay_days, nodes):
    prepared_nodes, skipped_count = _prepare_delay_nodes_for_apply(nodes, delay_days)
    summary = {
        'total': len(nodes or []),
        'updated_count': 0,
        'failed_count': 0,
        'skipped_count': skipped_count
    }
    updated_nodes = []

    for node in prepared_nodes:
        record_id = str(node.get('record_id') or '').strip()
        update_payload = node.get('payload')
        if not record_id or not isinstance(update_payload, dict) or not update_payload:
            summary['skipped_count'] += 1
            continue

        try:
            if 'executor' in update_payload:
                update_payload['executor'] = _normalize_executor(update_payload.get('executor'))
            api_client.update_project_progress(record_id, update_payload)
            summary['updated_count'] += 1
            updated_nodes.append({
                'record_id': record_id,
                'main_stage_label': str(node.get('main_stage_label') or '').strip(),
                'node_label': str(node.get('node_label') or '').strip(),
                'before_plan_start': str(node.get('before_plan_start') or '').strip(),
                'after_plan_start': str(node.get('after_plan_start') or '').strip(),
                'before_plan_end': str(node.get('before_plan_end') or '').strip(),
                'after_plan_end': str(node.get('after_plan_end') or '').strip(),
                'executor_ids': node.get('executor_ids') or [],
                'executor_raw': node.get('executor_raw')
            })
        except Exception as exc:
            summary['failed_count'] += 1
            logger.error('Delay update failed for project progress record %s: %s', record_id, exc)

    summary.update(
        _send_delay_notifications(
            project_name=project_name,
            project_code=project_code,
            batch_no=batch_no,
            batch_name=batch_name,
            delay_days=delay_days,
            nodes=updated_nodes
        )
    )
    return summary


def _serialize_delay_request(item):
    if not isinstance(item, dict):
        return {}
    data = dict(item)
    data['status'] = _normalize_delay_request_status(data.get('status'))
    data['node_count'] = len(data.get('nodes') or [])
    return data


def _extract_uploaded_filename(file_url):
    if not file_url:
        return ''

    raw_value = str(file_url).strip()
    if not raw_value:
        return ''

    parsed = urlparse(raw_value)
    path = parsed.path if (parsed.scheme or parsed.netloc) else raw_value
    normalized_path = unquote(str(path or '').strip())
    if not (
        normalized_path.startswith('/uploads/')
        or normalized_path.startswith(f'{progress_bp.url_prefix}/file/')
    ):
        return ''

    filename = os.path.basename(normalized_path)
    safe_name = os.path.basename(filename)
    if not safe_name or safe_name in {'.', '..'}:
        return ''
    return safe_name


def _extract_remote_file_key(file_url):
    if not file_url:
        return ''

    parsed = urlparse(str(file_url).strip())
    path = unquote(parsed.path or '').strip()
    safe_name = os.path.basename(path)
    if not safe_name or safe_name in {'.', '..', 'uploads'}:
        return ''
    return safe_name


def _is_allowed_remote_download_url(file_url):
    if not file_url:
        return False

    parsed = urlparse(str(file_url).strip())
    if parsed.scheme not in {'http', 'https'}:
        return False

    hostname = (parsed.hostname or '').lower()
    if not hostname:
        return False

    return hostname == 'online-office.net' or hostname.endswith('.online-office.net')


def _build_attachment_disposition(filename):
    normalized = str(filename or '').strip() or 'attachment'
    ascii_name = secure_filename(normalized)
    _, ext = os.path.splitext(normalized)
    safe_ext = secure_filename(ext).lstrip('.')
    if (
        not ascii_name
        or not os.path.splitext(ascii_name)[0]
        or (safe_ext and ascii_name.lower() == safe_ext.lower())
    ):
        ascii_name = f"attachment.{safe_ext}" if safe_ext else 'attachment'
    quoted_name = quote(normalized)
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{quoted_name}"


def _guess_download_name(file_url, display_name=''):
    if display_name:
        return str(display_name).strip()

    parsed = urlparse(str(file_url).strip())
    raw_name = os.path.basename(unquote(parsed.path or ''))
    return raw_name or 'attachment'


def _append_query_param(url, key, value):
    if not url or not value:
        return url
    separator = '&' if '?' in url else '?'
    return f"{url}{separator}{key}={quote(str(value).strip())}"


def _normalize_base_url(value):
    normalized = str(value or '').strip().rstrip('/')
    if normalized.endswith('/api'):
        normalized = normalized[:-4]
    return normalized


def _resolve_public_file_base_url():
    configured_base = _normalize_base_url(current_app.config.get('FILE_PUBLIC_BASE_URL'))
    if configured_base:
        return configured_base

    forwarded_host = str(request.headers.get('X-Forwarded-Host', '')).split(',', 1)[0].strip()
    forwarded_proto = str(request.headers.get('X-Forwarded-Proto', '')).split(',', 1)[0].strip()
    if forwarded_host:
        return f"{forwarded_proto or request.scheme or 'http'}://{forwarded_host}"

    return _normalize_base_url(request.host_url)


def _build_progress_public_file_url(stored_filename):
    return f"{_resolve_public_file_base_url()}{progress_bp.url_prefix}/file/{quote(stored_filename)}"


def _normalize_upload_display_name(filename):
    normalized = str(filename or '').replace('\\', '/').split('/')[-1].replace('\x00', '').strip()
    return normalized or 'attachment'


def _build_upload_storage_name(display_name):
    _, ext = os.path.splitext(str(display_name or '').strip())
    safe_ext = secure_filename(ext).strip().lower().lstrip('.')
    return f"{uuid.uuid4().hex}.{safe_ext}" if safe_ext else uuid.uuid4().hex


def _build_remote_download_candidates(file_url='', original_url='', download_url='', file_key='', display_name=''):
    candidates = []
    seen = set()

    def add_candidate(url):
        normalized = str(url or '').strip()
        if not normalized or normalized in seen:
            return
        if not _is_allowed_remote_download_url(normalized):
            return
        seen.add(normalized)
        candidates.append(normalized)

    public_base = (current_app.config.get('PUBLIC_BASE_URL') or '').rstrip('/')
    resolved_key = str(file_key or '').strip() or _extract_remote_file_key(download_url) or _extract_remote_file_key(original_url) or _extract_remote_file_key(file_url)
    resolved_name = str(display_name or '').strip()

    add_candidate(download_url)
    add_candidate(original_url)
    add_candidate(file_url)

    if resolved_name:
        add_candidate(_append_query_param(original_url, 'attname', resolved_name))
        add_candidate(_append_query_param(file_url, 'attname', resolved_name))

    if public_base and resolved_key:
        base_download = f"{public_base}/file/get/{quote(resolved_key)}"
        if resolved_name:
            add_candidate(_append_query_param(base_download, 'filename', resolved_name))
        add_candidate(base_download)

    if resolved_key and public_base:
        image_host_candidate = f"{public_base}/{quote(resolved_key)}"
        if resolved_name:
            add_candidate(_append_query_param(image_host_candidate, 'attname', resolved_name))
        add_candidate(image_host_candidate)

    return candidates


def _looks_like_preview_html(response, first_chunk, download_name):
    content_type = str(response.headers.get('Content-Type', '')).lower()
    if 'text/html' not in content_type:
        return False

    filename = str(download_name or '').strip().lower()
    if filename.endswith(('.html', '.htm')):
        return False

    preview = (first_chunk or b'').lstrip()[:128].lower()
    return preview.startswith(b'<!doctype html') or preview.startswith(b'<html')


def _stream_remote_response(remote_response, download_name):
    chunk_iter = remote_response.iter_content(chunk_size=8192)
    first_chunk = b''
    for chunk in chunk_iter:
        if chunk:
            first_chunk = chunk
            break

    if _looks_like_preview_html(remote_response, first_chunk, download_name):
        remote_response.close()
        return None

    if remote_response.headers.get('Content-Length') == '0' and not first_chunk:
        remote_response.close()
        return None

    def generate():
        try:
            if first_chunk:
                yield first_chunk
            for chunk in chunk_iter:
                if chunk:
                    yield chunk
        finally:
            remote_response.close()

    response = Response(
        stream_with_context(generate()),
        content_type='application/octet-stream'
    )
    content_length = remote_response.headers.get('Content-Length')
    if content_length and content_length != '0':
        response.headers['Content-Length'] = content_length
    response.headers['Content-Disposition'] = _build_attachment_disposition(download_name)
    return response


@progress_bp.route('/list', methods=['GET'])
def list_project_progress():
    """List project progress records."""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 300, type=int)
        search = request.args.get('search', '', type=str)
        project_code = request.args.get('project_code', '', type=str)
        project_name = request.args.get('project_name', '', type=str)

        filter_obj = None
        cond = []

        if project_code:
            cond.append({
                'field': PROJECT_PROGRESS_FIELDS_EN['project_code'],
                'method': 'like',
                'value': [project_code]
            })

        if project_name:
            cond.append({
                'field': PROJECT_PROGRESS_FIELDS_EN['project_name'],
                'method': 'like',
                'value': [project_name]
            })

        if search:
            search_project_codes = _resolve_project_codes_by_order_or_code(search)
            search_cond = [
                {
                    'field': PROJECT_PROGRESS_FIELDS_EN['project_code'],
                    'method': 'like',
                    'value': [search]
                }
            ]
            for code in search_project_codes:
                if code == search:
                    continue
                search_cond.append({
                    'field': PROJECT_PROGRESS_FIELDS_EN['project_code'],
                    'method': 'like',
                    'value': [code]
                })
            filter_obj = {
                'rel': 'or',
                'cond': search_cond
            }
        elif cond:
            filter_obj = {
                'rel': 'and',
                'cond': cond
            }

        items = api_client.list_project_progress(skip=skip, limit=limit, filter_obj=filter_obj)
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': items,
            'total': len(items)
        })
    except Exception as e:
        logger.error(f"获取项目进度列表失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@progress_bp.route('/get/<data_id>', methods=['GET'])
def get_project_progress(data_id):
    """Get a single progress record."""
    try:
        item = api_client.get_project_progress(data_id)
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': item
        })
    except Exception as e:
        logger.error(f"获取项目进度失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@progress_bp.route('/file/<path:filename>', methods=['GET'])
def get_project_progress_public_file(filename):
    """Serve locally uploaded files for Online Office remote ingestion."""
    safe_name = os.path.basename(unquote(str(filename or '').strip()))
    if not safe_name or safe_name in {'.', '..'}:
        return jsonify({
            'code': 400,
            'msg': 'Invalid file name'
        }), 400

    upload_dir = current_app.config.get('UPLOAD_DIR') or os.path.join(os.getcwd(), 'uploads')
    file_path = os.path.join(upload_dir, safe_name)
    if not os.path.isfile(file_path):
        return jsonify({
            'code': 404,
            'msg': 'File not found'
        }), 404

    return send_from_directory(upload_dir, safe_name, as_attachment=False)


@progress_bp.route('/download', methods=['GET'])
def download_project_progress_file():
    """Download a locally uploaded progress attachment."""
    try:
        file_url = request.args.get('url', '', type=str)
        original_url = request.args.get('original_url', '', type=str)
        download_url = request.args.get('download_url', '', type=str)
        file_key = request.args.get('file_key', '', type=str)
        display_name = request.args.get('name', '', type=str).strip()

        if not any([file_url, original_url, download_url, file_key]):
            return jsonify({
                'code': 400,
                'msg': '请提供附件地址'
            }), 400

        stored_filename = _extract_uploaded_filename(file_url)
        if not stored_filename:
            candidates = _build_remote_download_candidates(
                file_url=file_url,
                original_url=original_url,
                download_url=download_url,
                file_key=file_key,
                display_name=display_name
            )
            if not candidates:
                return jsonify({
                    'code': 400,
                    'msg': '当前附件不支持代理下载'
                }), 400

            download_name = _guess_download_name(display_name or original_url or download_url or file_url, display_name)
            errors = deque(maxlen=3)
            for candidate_url in candidates:
                try:
                    remote_response = requests.get(candidate_url, stream=True, timeout=REQUEST_TIMEOUT)
                    remote_response.raise_for_status()
                    streamed_response = _stream_remote_response(remote_response, download_name)
                    if streamed_response is not None:
                        return streamed_response
                    errors.append(f'{candidate_url}: preview_html_or_empty')
                except requests.exceptions.RequestException as request_error:
                    errors.append(f'{candidate_url}: {request_error}')
                    continue

            logger.error("Project progress attachment proxy download failed for all candidates: %s", list(errors))
            if errors and all('preview_html_or_empty' in error for error in errors):
                return jsonify({
                    'code': 422,
                    'msg': '该附件在上传入库时已被保存为 HTML 页面，不是原始文件，需要重新上传该附件'
                }), 422
            return jsonify({
                'code': 502,
                'msg': '未获取到有效附件文件'
            }), 502

        upload_dir = current_app.config.get('UPLOAD_DIR') or os.path.join(os.getcwd(), 'uploads')
        file_path = os.path.join(upload_dir, stored_filename)
        if not os.path.isfile(file_path):
            return jsonify({
                'code': 404,
                'msg': '附件不存在或已被删除'
            }), 404

        download_name = display_name or stored_filename.split('_', 1)[-1] or stored_filename
        response = send_from_directory(
            upload_dir,
            stored_filename,
            as_attachment=True,
            download_name=download_name
        )
        response.headers['Content-Disposition'] = _build_attachment_disposition(download_name)
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"代理下载项目进度附件失败: {e}")
        return jsonify({
            'code': 502,
            'msg': '获取远程附件失败'
        }), 502
    except Exception as e:
        logger.error(f"下载项目进度附件失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@progress_bp.route('/create', methods=['POST'])
def create_project_progress():
    """Create a progress record."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请提供数据'
            }), 400
        if 'executor' in data:
            data['executor'] = _normalize_executor(data.get('executor'))
        if 'approver' in data:
            data['approver'] = _normalize_single_member(data.get('approver'))
        result = api_client.create_project_progress(data)
        return jsonify({
            'code': 200,
            'msg': '创建成功',
            'data': result
        })
    except Exception as e:
        logger.error(f"创建项目进度失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@progress_bp.route('/update/<data_id>', methods=['PUT'])
def update_project_progress(data_id):
    """Update a progress record."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请提供数据'
            }), 400
        submit_for_approval = bool(data.pop('submit_for_approval', False))
        approval_action = str(data.pop('approval_action', '') or '').strip().lower()
        if 'executor' in data:
            data['executor'] = _normalize_executor(data.get('executor'))
        if 'approver' in data:
            data['approver'] = _normalize_single_member(data.get('approver'))

        current_record = {}
        should_load_current = submit_for_approval or bool(approval_action) or 'status' in data
        if should_load_current:
            current_record = api_client.get_project_progress(data_id)

        current_status = str(current_record.get('status') or '').strip()
        approver_value = (
            _normalize_single_member(data.get('approver'))
            if 'approver' in data
            else _normalize_single_member(current_record.get('approver'))
        )

        approval_requested = False
        if approval_action:
            if current_status not in WAITING_APPROVAL_STATUSES:
                return jsonify({
                    'code': 400,
                    'msg': '当前节点不在待审批状态'
                }), 400
            if approval_action == 'approve':
                data['status'] = (
                    STATUS_OVERDUE_DONE
                    if current_status == STATUS_OVERDUE_PENDING_APPROVAL
                    else STATUS_DONE
                )
            elif approval_action == 'reject':
                data['status'] = (
                    STATUS_OVERDUE
                    if current_status == STATUS_OVERDUE_PENDING_APPROVAL
                    else STATUS_PENDING
                )
            else:
                return jsonify({
                    'code': 400,
                    'msg': '无效的审批操作'
                }), 400
        elif submit_for_approval:
            target_status = str(data.get('status') or '').strip()
            if approver_value and target_status in DONE_STATUSES:
                data['status'] = (
                    STATUS_OVERDUE_PENDING_APPROVAL
                    if target_status == STATUS_OVERDUE_DONE
                    else STATUS_PENDING_APPROVAL
                )
                approval_requested = True

        result = api_client.update_project_progress(data_id, data)
        response_data = dict(result or {})
        notify_summary = {}

        if approval_requested:
            merged_record = {**current_record, **response_data}
            merged_record['approver'] = current_record.get('approver') or data.get('approver') or approver_value
            notify_summary = _send_approval_notifications(merged_record)
            response_data.update({
                'approval_requested': True,
                'notification_disabled': notify_summary.get('notification_disabled', False),
                'notify_failed_count': notify_summary.get('notify_failed_count', 0),
                'notify_error_summary': notify_summary.get('notify_error_summary', '')
            })

        response_msg = '更新成功'
        if approval_requested:
            if notify_summary.get('notify_failed_count'):
                error_text = notify_summary.get('notify_error_summary') or '审批通知发送失败'
                response_msg = f'提交成功，已转审批；{error_text}'
            else:
                response_msg = '提交成功，已通知审批人'
        elif approval_action == 'approve':
            response_msg = '审批通过'
        elif approval_action == 'reject':
            response_msg = '已驳回'
        return jsonify({
            'code': 200,
            'msg': response_msg,
            'data': response_data
        })
    except Exception as e:
        logger.error(f"更新项目进度失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@progress_bp.route('/delay-request/list', methods=['GET'])
def list_delay_requests():
    try:
        project_code = str(request.args.get('project_code') or '').strip()
        project_name = str(request.args.get('project_name') or '').strip()
        status = _normalize_delay_request_status(request.args.get('status') or DELAY_REQUEST_STATUS_PENDING)

        records = _load_delay_requests()
        filtered = []
        for item in records:
            normalized = _serialize_delay_request(item)
            if status and normalized.get('status') != status:
                continue
            if project_code and str(normalized.get('project_code') or '').strip() != project_code:
                continue
            if project_name and str(normalized.get('project_name') or '').strip() != project_name:
                continue
            filtered.append(normalized)

        filtered.sort(
            key=lambda item: (
                str(item.get('created_at') or ''),
                str(item.get('request_id') or '')
            ),
            reverse=True
        )
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': filtered,
            'total': len(filtered)
        })
    except Exception as e:
        logger.error(f"List project delay requests failed: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@progress_bp.route('/delay-request/create', methods=['POST'])
def create_delay_request():
    try:
        payload = request.get_json() or {}
        nodes = payload.get('nodes')
        delay_days = payload.get('delay_days', 0)
        try:
            delay_days = int(delay_days)
        except (TypeError, ValueError):
            delay_days = 0

        if delay_days <= 0:
            return jsonify({
                'code': 400,
                'msg': '请输入大于 0 的延期天数'
            }), 400

        if not isinstance(nodes, list) or not nodes:
            return jsonify({
                'code': 400,
                'msg': '请提供要申请延期的节点'
            }), 400

        anchor_record_id = str(payload.get('anchor_record_id') or nodes[0].get('record_id') or '').strip()
        if not anchor_record_id:
            return jsonify({
                'code': 400,
                'msg': '缺少起始节点记录ID'
            }), 400

        records = _load_delay_requests()
        for item in records:
            normalized = _serialize_delay_request(item)
            if normalized.get('status') != DELAY_REQUEST_STATUS_PENDING:
                continue
            if str(normalized.get('anchor_record_id') or '').strip() == anchor_record_id:
                return jsonify({
                    'code': 400,
                    'msg': '该节点已有待审核的延期申请'
                }), 400

        project_name = str(payload.get('project_name') or '').strip()
        project_code = str(payload.get('project_code') or '').strip()
        business_owner = (
            payload.get('business_owner')
            or payload.get('project_business_owner')
            or _resolve_project_business_owner(project_code, project_name)
        )

        request_record = {
            'request_id': uuid.uuid4().hex,
            'status': DELAY_REQUEST_STATUS_PENDING,
            'project_name': project_name,
            'project_code': project_code,
            'batch_no': payload.get('batch_no', ''),
            'batch_name': payload.get('batch_name', ''),
            'delay_days': delay_days,
            'reason': str(payload.get('reason') or '').strip(),
            'anchor_record_id': anchor_record_id,
            'nodes': nodes,
            'applicant': payload.get('applicant') or {},
            'business_owner': business_owner,
            'cc_role_id': DELAY_REQUEST_CC_ROLE_ID,
            'reviewer_candidates': payload.get('reviewer_candidates') or [],
            'created_at': _now_text(),
            'updated_at': _now_text()
        }
        records.append(request_record)
        _save_delay_requests(records)

        notify_summary = _send_delay_request_notifications(request_record)
        response_data = _serialize_delay_request(request_record)
        response_data.update({
            'notified_user_count': notify_summary.get('notified_user_count', 0),
            'cc_notified_user_count': notify_summary.get('cc_notified_user_count', 0),
            'notify_failed_count': notify_summary.get('notify_failed_count', 0),
            'notification_disabled': notify_summary.get('notification_disabled', False),
            'reviewer_missing': notify_summary.get('reviewer_missing', False),
            'notify_error_summary': notify_summary.get('notify_error_summary', '')
        })

        return jsonify({
            'code': 200,
            'msg': '延期申请已提交',
            'data': response_data
        })
    except Exception as e:
        logger.error(f"Create project delay request failed: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@progress_bp.route('/delay-request/<request_id>/approve', methods=['POST'])
def approve_delay_request(request_id):
    try:
        payload = request.get_json() or {}
        records = _load_delay_requests()
        target = None
        for item in records:
            if str(item.get('request_id') or '').strip() == str(request_id).strip():
                target = item
                break

        if not target:
            return jsonify({
                'code': 404,
                'msg': '延期申请不存在'
            }), 404

        if _normalize_delay_request_status(target.get('status')) != DELAY_REQUEST_STATUS_PENDING:
            return jsonify({
                'code': 400,
                'msg': '该延期申请已处理'
            }), 400

        reviewer = payload.get('reviewer') or {}
        if not _is_delay_request_business_owner_reviewer(reviewer, target.get('business_owner')):
            return jsonify({
                'code': 403,
                'msg': '仅该项目商务负责人可审核延期申请'
            }), 403

        summary = _apply_delay_nodes(
            project_name=str(target.get('project_name') or '').strip(),
            project_code=str(target.get('project_code') or '').strip(),
            batch_no=target.get('batch_no', ''),
            batch_name=target.get('batch_name', ''),
            delay_days=int(target.get('delay_days') or 0),
            nodes=target.get('nodes') or []
        )
        if int(summary.get('updated_count') or 0) <= 0:
            return jsonify({
                'code': 400,
                'msg': '延期申请执行失败，未更新任何节点'
            }), 400

        target['status'] = DELAY_REQUEST_STATUS_APPROVED
        target['updated_at'] = _now_text()
        target['reviewer'] = reviewer
        target['review_result'] = 'approved'
        target['apply_summary'] = summary
        _save_delay_requests(records)

        return jsonify({
            'code': 200,
            'msg': '延期申请已通过',
            'data': {
                'request': _serialize_delay_request(target),
                'summary': summary
            }
        })
    except Exception as e:
        logger.error(f"Approve project delay request failed: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@progress_bp.route('/delay-request/<request_id>/reject', methods=['POST'])
def reject_delay_request(request_id):
    try:
        payload = request.get_json() or {}
        records = _load_delay_requests()
        target = None
        for item in records:
            if str(item.get('request_id') or '').strip() == str(request_id).strip():
                target = item
                break

        if not target:
            return jsonify({
                'code': 404,
                'msg': '延期申请不存在'
            }), 404

        if _normalize_delay_request_status(target.get('status')) != DELAY_REQUEST_STATUS_PENDING:
            return jsonify({
                'code': 400,
                'msg': '该延期申请已处理'
            }), 400

        reviewer = payload.get('reviewer') or {}
        if not _is_delay_request_business_owner_reviewer(reviewer, target.get('business_owner')):
            return jsonify({
                'code': 403,
                'msg': '仅该项目商务负责人可审核延期申请'
            }), 403

        target['status'] = DELAY_REQUEST_STATUS_REJECTED
        target['updated_at'] = _now_text()
        target['reviewer'] = reviewer
        target['review_result'] = 'rejected'
        target['review_note'] = str(payload.get('review_note') or '').strip()
        _save_delay_requests(records)

        return jsonify({
            'code': 200,
            'msg': '延期申请已驳回',
            'data': _serialize_delay_request(target)
        })
    except Exception as e:
        logger.error(f"Reject project delay request failed: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@progress_bp.route('/delay', methods=['POST'])
def delay_project_progress():
    """Batch delay progress nodes and notify responsible users via DingTalk."""
    try:
        payload = request.get_json() or {}
        nodes = payload.get('nodes')
        delay_days = payload.get('delay_days', 0)
        try:
            delay_days = int(delay_days)
        except (TypeError, ValueError):
            delay_days = 0

        if delay_days <= 0:
            return jsonify({
                'code': 400,
                'msg': '璇疯緭鍏ュぇ浜 0 鐨勫欢鏈熷ぉ鏁?'
            }), 400

        if not isinstance(nodes, list) or not nodes:
            return jsonify({
                'code': 400,
                'msg': '璇锋彁渚涢渶瑕佸欢鏈熺殑鑺傜偣鍒楄〃'
            }), 400

        project_name = str(payload.get('project_name') or '').strip()
        project_code = str(payload.get('project_code') or '').strip()
        batch_no = payload.get('batch_no', '')
        batch_name = payload.get('batch_name', '')
        summary = _apply_delay_nodes(
            project_name=project_name,
            project_code=project_code,
            batch_no=batch_no,
            batch_name=batch_name,
            delay_days=delay_days,
            nodes=nodes
        )

        return jsonify({
            'code': 200,
            'msg': '寤舵湡澶勭悊瀹屾垚',
            'data': summary
        })
    except Exception as e:
        logger.error(f"寤舵湡椤圭洰杩涘害澶辫触: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@progress_bp.route('/delete/<data_id>', methods=['DELETE'])
def delete_project_progress(data_id):
    """Delete a progress record."""
    try:
        api_client.delete_project_progress(data_id)
        return jsonify({
            'code': 200,
            'msg': '删除成功'
        })
    except Exception as e:
        logger.error(f"删除项目进度失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@progress_bp.route('/upload', methods=['POST'])
def upload_project_progress_files():
    """Upload file metadata for progress attachments."""
    try:
        if request.files:
            files = request.files.getlist('files') or list(request.files.values())
            if not files:
                return jsonify({
                    'code': 400,
                    'msg': 'Please upload files'
                }), 400
            upload_dir = current_app.config.get('UPLOAD_DIR') or os.path.join(os.getcwd(), 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            payload = []
            for file in files:
                if not file or not file.filename:
                    continue
                filename = _normalize_upload_display_name(file.filename)
                unique_name = _build_upload_storage_name(filename)
                file_path = os.path.join(upload_dir, unique_name)
                file.save(file_path)
                file_url = _build_progress_public_file_url(unique_name)
                payload.append({'name': filename, 'url': file_url})
            if not payload:
                return jsonify({
                    'code': 400,
                    'msg': 'No valid files'
                }), 400
            result = api_client.upload_project_progress_files(payload)
            normalized_result = []
            for index, item in enumerate(result if isinstance(result, list) else []):
                expected_name = payload[index].get('name') if index < len(payload) else ''
                if isinstance(item, dict):
                    normalized_item = dict(item)
                else:
                    normalized_item = {'url': '', 'size': 0, 'mime': '', 'name': ''}
                if expected_name:
                    normalized_item['name'] = expected_name
                    normalized_item.setdefault('file_name', expected_name)
                    normalized_item.setdefault('fileName', expected_name)
                normalized_result.append(normalized_item)
            return jsonify({
                'code': 200,
                'msg': 'success',
                'data': normalized_result
            })
        files = request.get_json()
        if not isinstance(files, list):
            return jsonify({
                'code': 400,
                'msg': 'Please provide file URL list'
            }), 400
        result = api_client.upload_project_progress_files(files)
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': result
        })
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500
