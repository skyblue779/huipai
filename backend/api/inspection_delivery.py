"""
样品检测交付现场管理 API 路由
"""
import logging
from flask import Blueprint, request, jsonify
from api.online_office import api_client
from config import DINGDING_CORP_ID
from field_mapping import INSPECTION_DELIVERY_FIELDS_EN, DELIVERY_FIELDS_EN, PROJECT_FIELDS_EN

logger = logging.getLogger(__name__)

inspection_delivery_bp = Blueprint('inspection_delivery', __name__, url_prefix='/api/inspection-delivery')


def _normalize_token(value):
    if value is None:
        return ''
    return str(value).strip().lower()


def _extract_manager_token(manager_value):
    if not manager_value:
        return ''
    if isinstance(manager_value, list):
        if not manager_value:
            return ''
        return _extract_manager_token(manager_value[0])
    if isinstance(manager_value, dict):
        return manager_value.get('name') or manager_value.get('user_id') or manager_value.get('_id') or manager_value.get('id') or ''
    return str(manager_value)


def _match_user_id(users, token):
    normalized = _normalize_token(token)
    if not normalized:
        return ''
    for user in users or []:
        if not isinstance(user, dict):
            continue
        for key in ('user_id', '_id', 'id', 'account', 'name', 'nickname', 'realname', 'uniqueid'):
            if _normalize_token(user.get(key)) == normalized:
                return user.get('user_id') or user.get('_id') or user.get('id') or ''
    return ''


def _find_project_manager(project_name):
    if not project_name:
        return '', ''
    filter_obj = {
        'rel': 'and',
        'cond': [
            {
                'field': PROJECT_FIELDS_EN['project_name'],
                'method': 'eq',
                'value': [project_name]
            }
        ]
    }
    projects = api_client.list_projects_en(
        skip=0,
        limit=1,
        filter_obj=filter_obj,
        fields=['project_name', 'project_code', 'project_manager']
    )
    if not projects:
        filter_obj['cond'][0]['method'] = 'like'
        projects = api_client.list_projects_en(
            skip=0,
            limit=1,
            filter_obj=filter_obj,
            fields=['project_name', 'project_code', 'project_manager']
        )
    if not projects:
        return '', ''
    project = projects[0]
    manager_token = _extract_manager_token(project.get('project_manager'))
    project_code = project.get('project_code') or ''
    return manager_token, project_code


@inspection_delivery_bp.route('/list', methods=['GET'])
def list_inspection_deliveries():
    """获取样品检测交付记录列表"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 300, type=int)
        search = request.args.get('search', '', type=str)
        delivery_no = request.args.get('delivery_no', '', type=str)
        project_name = request.args.get('project_name', '', type=str)
        handover_status = request.args.get('handover_status', '', type=str)

        filter_obj = None
        cond = []

        if delivery_no:
            cond.append({
                'field': INSPECTION_DELIVERY_FIELDS_EN['delivery_no'],
                'method': 'like',
                'value': [delivery_no]
            })
        if project_name:
            cond.append({
                'field': INSPECTION_DELIVERY_FIELDS_EN['project_name'],
                'method': 'like',
                'value': [project_name]
            })
        if handover_status:
            cond.append({
                'field': INSPECTION_DELIVERY_FIELDS_EN['handover_status'],
                'method': 'eq',
                'value': [handover_status]
            })

        if search:
            filter_obj = {
                'rel': 'or',
                'cond': [
                    {
                        'field': INSPECTION_DELIVERY_FIELDS_EN['handover_no'],
                        'method': 'like',
                        'value': [search]
                    },
                    {
                        'field': INSPECTION_DELIVERY_FIELDS_EN['delivery_no'],
                        'method': 'like',
                        'value': [search]
                    },
                    {
                        'field': INSPECTION_DELIVERY_FIELDS_EN['project_name'],
                        'method': 'like',
                        'value': [search]
                    }
                ]
            }
        elif cond:
            filter_obj = {
                'rel': 'and',
                'cond': cond
            }

        items = api_client.list_inspection_deliveries(skip=skip, limit=limit, filter_obj=filter_obj)
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': items,
            'total': len(items)
        })
    except Exception as exc:
        logger.error("获取样品检测交付记录失败: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500


@inspection_delivery_bp.route('/get/<data_id>', methods=['GET'])
def get_inspection_delivery(data_id):
    """获取单条记录"""
    try:
        item = api_client.get_inspection_delivery(data_id)
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': item
        })
    except Exception as exc:
        logger.error("获取样品检测交付详情失败: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500


@inspection_delivery_bp.route('/create', methods=['POST'])
def create_inspection_delivery():
    """创建记录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请提供数据'
            }), 400
        result = api_client.create_inspection_delivery(data)
        return jsonify({
            'code': 200,
            'msg': '创建成功',
            'data': result
        })
    except Exception as exc:
        logger.error("创建样品检测交付失败: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500


@inspection_delivery_bp.route('/update/<data_id>', methods=['PUT'])
def update_inspection_delivery(data_id):
    """更新记录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请提供数据'
            }), 400
        result = api_client.update_inspection_delivery(data_id, data)
        if data.get('handover_status') == '异常':
            record = result if isinstance(result, dict) and result else {}
            delivery_no = record.get('delivery_no') if isinstance(record, dict) else None
            project_name = record.get('project_name') if isinstance(record, dict) else ''
            if not delivery_no or not project_name:
                record = api_client.get_inspection_delivery(data_id)
                delivery_no = delivery_no or (record.get('delivery_no') if isinstance(record, dict) else None)
                project_name = project_name or (record.get('project_name') if isinstance(record, dict) else '')

            # 回填发货异常状态
            try:
                if delivery_no:
                    deliveries = api_client.list_deliveries(
                        skip=0,
                        limit=1,
                        filter_obj={
                            'rel': 'and',
                            'cond': [
                                {
                                    'field': DELIVERY_FIELDS_EN['delivery_no'],
                                    'method': 'eq',
                                    'value': [delivery_no]
                                }
                            ]
                        }
                    )
                    if deliveries:
                        delivery_id = deliveries[0].get('_id')
                        if delivery_id:
                            api_client.update_delivery(delivery_id, {'status': '异常'})
            except Exception as exc:
                logger.error("回填发货异常状态失败: %s", exc)

            # 发送钉钉通知
            try:
                if record:
                    project_name = project_name or ''
                    manager_token, project_code = _find_project_manager(project_name)
                    if not manager_token:
                        logger.warning("未找到项目经理信息，无法发送钉钉消息")
                    elif not DINGDING_CORP_ID:
                        logger.warning("未配置钉钉corp_id，无法发送消息")
                    else:
                        users = api_client.list_users()
                        user_id = _match_user_id(users, manager_token)
                        if not user_id:
                            logger.warning("未匹配到项目经理成员ID，无法发送钉钉消息")
                        else:
                            title = '样品检测交付异常提醒'
                            abnormal_reason = record.get('abnormal_reason') or '未填写'
                            handover_no = record.get('handover_no') or ''
                            content = (
                                f"项目名称：{project_name}\n"
                                f"项目编号：{project_code}\n"
                                f"发货单号：{delivery_no}\n"
                                f"交付单号：{handover_no}\n"
                                f"异常原因：{abnormal_reason}"
                            )
                            logger.info(f"DEBUG - 发送钉钉使用的CorpID: {repr(DINGDING_CORP_ID)}")
                            api_client.send_dingding_message(
                                corp_id=DINGDING_CORP_ID,
                                users=[user_id],
                                title=title,
                                content=content
                            )                         
            except Exception as exc:
                logger.error("发送钉钉消息失败: %s", exc)
        return jsonify({
            'code': 200,
            'msg': '更新成功',
            'data': result
        })
    except Exception as exc:
        logger.error("更新样品检测交付失败: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500


@inspection_delivery_bp.route('/delete/<data_id>', methods=['DELETE'])
def delete_inspection_delivery(data_id):
    """删除记录"""
    try:
        api_client.delete_inspection_delivery(data_id)
        return jsonify({
            'code': 200,
            'msg': '删除成功'
        })
    except Exception as exc:
        logger.error("删除样品检测交付失败: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500


@inspection_delivery_bp.route('/upload', methods=['POST'])
def upload_inspection_delivery_files():
    """上传附件"""
    try:
        files = request.get_json()
        if not isinstance(files, list):
            return jsonify({
                'code': 400,
                'msg': '请提供文件URL列表'
            }), 400
        result = api_client.upload_inspection_delivery_files(files)
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': result
        })
    except Exception as exc:
        logger.error("上传样品检测交付附件失败: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500
