"""
阶段配置 API 路由
"""
import logging
from flask import Blueprint, request, jsonify
from api.online_office import api_client

logger = logging.getLogger(__name__)

stage_bp = Blueprint('stage', __name__, url_prefix='/api/stage')


@stage_bp.route('/list', methods=['GET'])
def list_stages():
    """获取阶段列表"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 20, type=int)

        project_type = request.args.get('project_type', None, type=str)

        filter_obj = None
        # Online-Office 筛选：按“项目类型”字段等于某值
        if project_type:
            filter_obj = {
                'rel': 'and',
                'cond': [
                    {
                        'field': '_widget_1769152663361',
                        'method': 'eq',
                        'value': [project_type]
                    }
                ]
            }
        
        stages = api_client.list_stages(skip=skip, limit=limit, filter_obj=filter_obj)
        
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': stages,
            'total': len(stages)
        })
    except Exception as e:
        logger.error(f"获取阶段列表失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@stage_bp.route('/get/<data_id>', methods=['GET'])
def get_stage(data_id):
    """获取单个阶段"""
    try:
        stage = api_client.get_stage(data_id)
        
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': stage
        })
    except Exception as e:
        logger.error(f"获取阶段失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@stage_bp.route('/create', methods=['POST'])
def create_stage():
    """创建阶段"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请提供数据'
            }), 400
        
        result = api_client.create_stage(data)
        
        return jsonify({
            'code': 200,
            'msg': '创建成功',
            'data': result
        })
    except Exception as e:
        logger.error(f"创建阶段失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@stage_bp.route('/update/<data_id>', methods=['PUT'])
def update_stage(data_id):
    """更新阶段"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请提供数据'
            }), 400
        
        result = api_client.update_stage(data_id, data)
        
        return jsonify({
            'code': 200,
            'msg': '更新成功',
            'data': result
        })
    except Exception as e:
        logger.error(f"更新阶段失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@stage_bp.route('/delete/<data_id>', methods=['DELETE'])
def delete_stage(data_id):
    """删除阶段"""
    try:
        api_client.delete_stage(data_id)
        
        return jsonify({
            'code': 200,
            'msg': '删除成功'
        })
    except Exception as e:
        logger.error(f"删除阶段失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500
