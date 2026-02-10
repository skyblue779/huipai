"""
样品检测交付现场管理 API 路由
"""
import logging
from flask import Blueprint, request, jsonify
from api.online_office import api_client
from field_mapping import INSPECTION_DELIVERY_FIELDS_EN

logger = logging.getLogger(__name__)

inspection_delivery_bp = Blueprint('inspection_delivery', __name__, url_prefix='/api/inspection-delivery')


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

