"""
检测项目 API 路由
"""
import logging
from flask import Blueprint, request, jsonify
from api.online_office import api_client
from field_mapping import INSPECTION_FIELDS_EN

logger = logging.getLogger(__name__)

inspection_bp = Blueprint('inspection', __name__, url_prefix='/api/inspection')


@inspection_bp.route('/list', methods=['GET'])
def list_inspections():
    """获取检测项目列表"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 300, type=int)
        search = request.args.get('search', '', type=str)
        inspection_project = request.args.get('inspection_project', '', type=str)

        filter_obj = None
        cond = []

        if inspection_project:
            cond.append({
                'field': INSPECTION_FIELDS_EN['inspection_project'],
                'method': 'like',
                'value': [inspection_project]
            })

        if search:
            filter_obj = {
                'rel': 'or',
                'cond': [
                    {
                        'field': INSPECTION_FIELDS_EN['inspection_no'],
                        'method': 'like',
                        'value': [search]
                    },
                    {
                        'field': INSPECTION_FIELDS_EN['inspection_project'],
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

        items = api_client.list_inspections(skip=skip, limit=limit, filter_obj=filter_obj)
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': items,
            'total': len(items)
        })
    except Exception as exc:
        logger.error("获取检测项目列表失败: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500

