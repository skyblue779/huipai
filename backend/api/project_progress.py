"""
Project progress API routes.
"""
import logging
import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app
from api.online_office import api_client
from field_mapping import PROJECT_PROGRESS_FIELDS_EN

logger = logging.getLogger(__name__)

progress_bp = Blueprint('progress', __name__, url_prefix='/api/progress')


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
            filter_obj = {
                'rel': 'or',
                'cond': [
                    {
                        'field': PROJECT_PROGRESS_FIELDS_EN['project_name'],
                        'method': 'like',
                        'value': [search]
                    },
                    {
                        'field': PROJECT_PROGRESS_FIELDS_EN['project_code'],
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
        if 'executor' in data:
            data['executor'] = _normalize_executor(data.get('executor'))
        result = api_client.update_project_progress(data_id, data)
        return jsonify({
            'code': 200,
            'msg': '更新成功',
            'data': result
        })
    except Exception as e:
        logger.error(f"更新项目进度失败: {e}")
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
                    'msg': 'No valid files'
                }), 400
            result = api_client.upload_project_progress_files(payload)
            return jsonify({
                'code': 200,
                'msg': 'success',
                'data': result
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
