"""
Delivery management API routes.
"""
import logging
import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app
from api.online_office import api_client
from field_mapping import DELIVERY_FIELDS_EN

logger = logging.getLogger(__name__)

delivery_bp = Blueprint('delivery', __name__, url_prefix='/api/delivery')

def _normalize_inspection_items(data):
    if not isinstance(data, dict):
        return data
    value = data.get('inspection_items')
    if value is None:
        return data
    if isinstance(value, list):
        return data
    if isinstance(value, str):
        trimmed = value.strip()
        data['inspection_items'] = [trimmed] if trimmed else []
        return data
    data['inspection_items'] = [value]
    return data


@delivery_bp.route('/list', methods=['GET'])
def list_deliveries():
    """List delivery records."""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 300, type=int)
        search = request.args.get('search', '', type=str)
        delivery_no = request.args.get('delivery_no', '', type=str)
        project_name = request.args.get('project_name', '', type=str)
        order_no = request.args.get('order_no', '', type=str)
        status = request.args.get('status', '', type=str)

        filter_obj = None
        cond = []

        if delivery_no:
            cond.append({
                'field': DELIVERY_FIELDS_EN['delivery_no'],
                'method': 'like',
                'value': [delivery_no]
            })
        if project_name:
            cond.append({
                'field': DELIVERY_FIELDS_EN['project_name'],
                'method': 'like',
                'value': [project_name]
            })
        if order_no:
            cond.append({
                'field': DELIVERY_FIELDS_EN['order_no'],
                'method': 'like',
                'value': [order_no]
            })
        if status:
            cond.append({
                'field': DELIVERY_FIELDS_EN['status'],
                'method': 'eq',
                'value': [status]
            })

        if search:
            filter_obj = {
                'rel': 'or',
                'cond': [
                    {
                        'field': DELIVERY_FIELDS_EN['delivery_no'],
                        'method': 'like',
                        'value': [search]
                    },
                    {
                        'field': DELIVERY_FIELDS_EN['project_name'],
                        'method': 'like',
                        'value': [search]
                    },
                    {
                        'field': DELIVERY_FIELDS_EN['order_no'],
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

        items = api_client.list_deliveries(skip=skip, limit=limit, filter_obj=filter_obj)
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': items,
            'total': len(items)
        })
    except Exception as exc:
        logger.error("获取发货列表失败: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500


@delivery_bp.route('/get/<data_id>', methods=['GET'])
def get_delivery(data_id):
    """Get a single delivery record."""
    try:
        item = api_client.get_delivery(data_id)
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': item
        })
    except Exception as exc:
        logger.error("获取发货详情失败: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500


@delivery_bp.route('/create', methods=['POST'])
def create_delivery():
    """Create a delivery record."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请提供数据'
            }), 400
        data = _normalize_inspection_items(data)
        result = api_client.create_delivery(data)
        return jsonify({
            'code': 200,
            'msg': '创建成功',
            'data': result
        })
    except Exception as exc:
        logger.error("创建发货失败: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500


@delivery_bp.route('/update/<data_id>', methods=['PUT'])
def update_delivery(data_id):
    """Update a delivery record."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请提供数据'
            }), 400
        data = _normalize_inspection_items(data)
        result = api_client.update_delivery(data_id, data)
        return jsonify({
            'code': 200,
            'msg': '更新成功',
            'data': result
        })
    except Exception as exc:
        logger.error("更新发货失败: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500


@delivery_bp.route('/delete/<data_id>', methods=['DELETE'])
def delete_delivery(data_id):
    """Delete a delivery record."""
    try:
        api_client.delete_delivery(data_id)
        return jsonify({
            'code': 200,
            'msg': '删除成功'
        })
    except Exception as exc:
        logger.error("删除发货失败: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500


@delivery_bp.route('/upload', methods=['POST'])
def upload_delivery_files():
    """Upload files and return Online-Office file metadata."""
    try:
        if request.files:
            files = request.files.getlist('files') or list(request.files.values())
            if not files:
                return jsonify({
                    'code': 400,
                    'msg': '请上传文件'
                }), 400
            upload_dir = current_app.config.get('UPLOAD_DIR') or os.path.join(os.getcwd(), 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            public_base = current_app.config.get('PUBLIC_BASE_URL') or request.host_url.rstrip('/')
            payload = []
            for file in files:
                if not file or not file.filename:
                    continue
                filename = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(upload_dir, unique_name)
                file.save(file_path)
                file_url = f"{public_base}/uploads/{unique_name}"
                payload.append({'name': filename, 'url': file_url})
            if not payload:
                return jsonify({
                    'code': 400,
                    'msg': '无有效文件'
                }), 400
            result = api_client.upload_delivery_files(payload)
            return jsonify({
                'code': 200,
                'msg': 'success',
                'data': result
            })

        files = request.get_json()
        if not isinstance(files, list):
            return jsonify({
                'code': 400,
                'msg': '请提供文件URL列表'
            }), 400
        result = api_client.upload_delivery_files(files)
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': result
        })
    except Exception as exc:
        logger.error("上传发货附件失败: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500
