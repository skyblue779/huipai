"""
项目 API 路由
"""
import logging
from flask import Blueprint, request, jsonify
from api.online_office import api_client
from field_mapping import PROJECT_FIELDS_EN

logger = logging.getLogger(__name__)

project_bp = Blueprint('project', __name__, url_prefix='/api/project')


@project_bp.route('/list', methods=['GET'])
def list_projects():
    """获取项目列表"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 20, type=int)
        search = request.args.get('search', '', type=str)
        
        filter_obj = None
        if search:
            # 按项目名称或编号搜索
            filter_obj = {
                'rel': 'or',
                'cond': [
                    {
                        'field': '项目名称',
                        'method': 'like',
                        'value': [search]
                    },
                    {
                        'field': '项目编号',
                        'method': 'like',
                        'value': [search]
                    }
                ]
            }
        
        projects = api_client.list_projects(skip=skip, limit=limit, filter_obj=filter_obj)
        
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': projects,
            'total': len(projects)
        })
    except Exception as e:
        logger.error(f"获取项目列表失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@project_bp.route('/list-summary', methods=['GET'])
def list_project_summary():
    """获取项目简要信息（英文字段）"""
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

        if search:
            filter_obj = {
                'rel': 'or',
                'cond': [
                    {
                        'field': PROJECT_FIELDS_EN['project_name'],
                        'method': 'like',
                        'value': [search]
                    },
                    {
                        'field': PROJECT_FIELDS_EN['project_code'],
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

        fields = [
            'project_code',
            'project_name',
            'project_type',
            'project_cost_type',
            'project_status',
            'plan_start',
            'plan_finish',
            'project_manager'
        ]
        projects = api_client.list_projects_en(
            skip=skip,
            limit=limit,
            filter_obj=filter_obj,
            fields=fields
        )
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': projects,
            'total': len(projects)
        })
    except Exception as e:
        logger.error(f"获取项目简要信息失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@project_bp.route('/get/<data_id>', methods=['GET'])
def get_project(data_id):
    """获取单个项目"""
    try:
        project = api_client.get_project(data_id)
        
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': project
        })
    except Exception as e:
        logger.error(f"获取项目失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@project_bp.route('/create', methods=['POST'])
def create_project():
    """创建项目"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请提供数据'
            }), 400
        
        result = api_client.create_project(data)
        
        return jsonify({
            'code': 200,
            'msg': '创建成功',
            'data': result
        })
    except Exception as e:
        logger.error(f"创建项目失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@project_bp.route('/update/<data_id>', methods=['PUT'])
def update_project(data_id):
    """更新项目"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请提供数据'
            }), 400
        
        result = api_client.update_project(data_id, data)
        
        return jsonify({
            'code': 200,
            'msg': '更新成功',
            'data': result
        })
    except Exception as e:
        logger.error(f"更新项目失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@project_bp.route('/delete/<data_id>', methods=['DELETE'])
def delete_project(data_id):
    """删除项目"""
    try:
        api_client.delete_project(data_id)
        
        return jsonify({
            'code': 200,
            'msg': '删除成功'
        })
    except Exception as e:
        logger.error(f"删除项目失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500
