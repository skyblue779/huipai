"""
Project budget management API routes.
"""
import logging
import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app
from api.online_office import api_client
from field_mapping import PROJECT_BUDGET_FIELDS_EN

logger = logging.getLogger(__name__)

project_budget_bp = Blueprint('project_budget', __name__, url_prefix='/api/project-budget')


def _to_number(value):
    if value is None or value == '':
        return None
    try:
        if isinstance(value, str):
            value = value.replace(',', '').strip()
        return float(value)
    except (TypeError, ValueError):
        return None


def _apply_budget_status(data):
    if not isinstance(data, dict):
        return data
    budget_standard = _to_number(data.get('budget_standard'))
    actual_total = _to_number(data.get('actual_total'))
    if budget_standard is None or actual_total is None:
        return data
    data['status'] = '超支' if actual_total > budget_standard else '正常'
    return data


@project_budget_bp.route('/list', methods=['GET'])
def list_project_budgets():
    """List project budget records."""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 300, type=int)
        search = request.args.get('search', '', type=str)
        project_code = request.args.get('project_code', '', type=str)
        project_name = request.args.get('project_name', '', type=str)
        project_type = request.args.get('project_type', '', type=str)
        cost_center = request.args.get('cost_center', '', type=str)
        cost_item = request.args.get('cost_item', '', type=str)
        status = request.args.get('status', '', type=str)
        main_stage_order = request.args.get('main_stage_order', '', type=str)
        project_stage_order = request.args.get('project_stage_order', '', type=str)

        filter_obj = None
        cond = []

        if project_code:
            cond.append({
                'field': PROJECT_BUDGET_FIELDS_EN['project_code'],
                'method': 'like',
                'value': [project_code]
            })
        if project_name:
            cond.append({
                'field': PROJECT_BUDGET_FIELDS_EN['project_name'],
                'method': 'like',
                'value': [project_name]
            })
        if project_type:
            cond.append({
                'field': PROJECT_BUDGET_FIELDS_EN['project_type'],
                'method': 'eq',
                'value': [project_type]
            })
        if cost_center:
            cond.append({
                'field': PROJECT_BUDGET_FIELDS_EN['cost_center'],
                'method': 'eq',
                'value': [cost_center]
            })
        if cost_item:
            cond.append({
                'field': PROJECT_BUDGET_FIELDS_EN['cost_item'],
                'method': 'like',
                'value': [cost_item]
            })
        if status:
            cond.append({
                'field': PROJECT_BUDGET_FIELDS_EN['status'],
                'method': 'eq',
                'value': [status]
            })
        if main_stage_order:
            cond.append({
                'field': PROJECT_BUDGET_FIELDS_EN['main_stage_order'],
                'method': 'eq',
                'value': [str(main_stage_order)]
            })
        if project_stage_order:
            cond.append({
                'field': PROJECT_BUDGET_FIELDS_EN['project_stage_order'],
                'method': 'eq',
                'value': [str(project_stage_order)]
            })

        if search:
            filter_obj = {
                'rel': 'or',
                'cond': [
                    {
                        'field': PROJECT_BUDGET_FIELDS_EN['project_name'],
                        'method': 'like',
                        'value': [search]
                    },
                    {
                        'field': PROJECT_BUDGET_FIELDS_EN['project_code'],
                        'method': 'like',
                        'value': [search]
                    },
                    {
                        'field': PROJECT_BUDGET_FIELDS_EN['cost_item'],
                        'method': 'like',
                        'value': [search]
                    },
                    {
                        'field': PROJECT_BUDGET_FIELDS_EN['cost_center'],
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

        items = api_client.list_project_budgets(skip=skip, limit=limit, filter_obj=filter_obj)
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': items,
            'total': len(items)
        })
    except Exception as e:
        logger.error(f"获取项目预算列表失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@project_budget_bp.route('/get/<data_id>', methods=['GET'])
def get_project_budget(data_id):
    """Get a single project budget record."""
    try:
        item = api_client.get_project_budget(data_id)
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': item
        })
    except Exception as e:
        logger.error(f"获取项目预算失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@project_budget_bp.route('/create', methods=['POST'])
def create_project_budget():
    """Create a project budget record."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请提供数据'
            }), 400
        data = _apply_budget_status(data)
        result = api_client.create_project_budget(data)
        return jsonify({
            'code': 200,
            'msg': '创建成功',
            'data': result
        })
    except Exception as e:
        logger.error(f"创建项目预算失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@project_budget_bp.route('/update/<data_id>', methods=['PUT'])
def update_project_budget(data_id):
    """Update a project budget record."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请提供数据'
            }), 400
        data = _apply_budget_status(data)
        result = api_client.update_project_budget(data_id, data)
        return jsonify({
            'code': 200,
            'msg': '更新成功',
            'data': result
        })
    except Exception as e:
        logger.error(f"更新项目预算失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@project_budget_bp.route('/delete/<data_id>', methods=['DELETE'])
def delete_project_budget(data_id):
    """Delete a project budget record."""
    try:
        api_client.delete_project_budget(data_id)
        return jsonify({
            'code': 200,
            'msg': '删除成功'
        })
    except Exception as e:
        logger.error(f"删除项目预算失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@project_budget_bp.route('/upload', methods=['POST'])
def upload_project_budget_files():
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
            result = api_client.upload_project_budget_files(payload)
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
        result = api_client.upload_project_budget_files(files)
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': result
        })
    except Exception as e:
        logger.error(f"上传预算附件失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500
