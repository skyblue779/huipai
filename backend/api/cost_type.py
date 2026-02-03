"""
Cost type API routes.
"""
import logging
from flask import Blueprint, request, jsonify
from api.online_office import api_client

logger = logging.getLogger(__name__)

cost_type_bp = Blueprint('cost_type', __name__, url_prefix='/api/cost-type')


@cost_type_bp.route('/list', methods=['GET'])
def list_cost_types():
    """List cost types."""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 300, type=int)

        types_ = api_client.list_cost_types(skip=skip, limit=limit)
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': types_,
            'total': len(types_)
        })
    except Exception as exc:
        logger.error("Failed to list cost types: %s", exc)
        return jsonify({
            'code': 500,
            'msg': str(exc)
        }), 500
