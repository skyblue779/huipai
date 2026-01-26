"""
项目类型 API 路由
"""
import logging
from flask import Blueprint, request, jsonify
from api.online_office import api_client

logger = logging.getLogger(__name__)

project_type_bp = Blueprint('project_type', __name__, url_prefix='/api/project-type')


@project_type_bp.route('/list', methods=['GET'])
def list_project_types():
    """获取项目类型列表"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 300, type=int)

        types_ = api_client.list_project_types(skip=skip, limit=limit)
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': types_,
            'total': len(types_)
        })
    except Exception as e:
        logger.error(f"获取项目类型列表失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


