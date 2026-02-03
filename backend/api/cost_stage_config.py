"""
Cost stage configuration API routes.
"""
import logging
from flask import Blueprint, request, jsonify
from api.online_office import api_client

logger = logging.getLogger(__name__)

cost_stage_bp = Blueprint('cost_stage', __name__, url_prefix='/api/cost-stage')


@cost_stage_bp.route('/list', methods=['GET'])
def list_cost_stages():
    """List cost stages."""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 20, type=int)
        project_type = request.args.get('project_type', None, type=str)

        filter_obj = None
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

        stages = api_client.list_cost_stages(skip=skip, limit=limit, filter_obj=filter_obj)
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': stages,
            'total': len(stages)
        })
    except Exception as exc:
        logger.error("Failed to list cost stages: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500


@cost_stage_bp.route('/get/<data_id>', methods=['GET'])
def get_cost_stage(data_id):
    """Get a cost stage."""
    try:
        stage = api_client.get_cost_stage(data_id)
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': stage
        })
    except Exception as exc:
        logger.error("Failed to get cost stage: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500


@cost_stage_bp.route('/create', methods=['POST'])
def create_cost_stage():
    """Create a cost stage."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'msg': 'missing data'
            }), 400

        result = api_client.create_cost_stage(data)
        return jsonify({
            'code': 200,
            'msg': 'created',
            'data': result
        })
    except Exception as exc:
        logger.error("Failed to create cost stage: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500


@cost_stage_bp.route('/update/<data_id>', methods=['PUT'])
def update_cost_stage(data_id):
    """Update a cost stage."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'msg': 'missing data'
            }), 400

        result = api_client.update_cost_stage(data_id, data)
        return jsonify({
            'code': 200,
            'msg': 'updated',
            'data': result
        })
    except Exception as exc:
        logger.error("Failed to update cost stage: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500


@cost_stage_bp.route('/delete/<data_id>', methods=['DELETE'])
def delete_cost_stage(data_id):
    """Delete a cost stage."""
    try:
        api_client.delete_cost_stage(data_id)
        return jsonify({
            'code': 200,
            'msg': 'deleted'
        })
    except Exception as exc:
        logger.error("Failed to delete cost stage: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500
