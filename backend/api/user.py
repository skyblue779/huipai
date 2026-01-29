"""
User directory API routes.
"""
import logging
from flask import Blueprint, jsonify
from api.online_office import api_client

logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

def _normalize_token(value):
    if value is None:
        return ''
    return str(value).strip().lower()


def _match_user_by_token(users, token):
    if not token:
        return None
    for user in users:
        if not isinstance(user, dict):
            continue
        if _normalize_token(user.get('user_id')) == token:
            return user
        if _normalize_token(user.get('_id')) == token:
            return user
        if _normalize_token(user.get('id')) == token:
            return user
        if _normalize_token(user.get('account')) == token:
            return user
        if _normalize_token(user.get('name')) == token:
            return user
        if _normalize_token(user.get('uniqueid')) == token:
            return user
    return None


@user_bp.route('/list', methods=['GET'])
def list_users():
    """List team members."""
    try:
        users = api_client.list_users()
        return jsonify({
            'code': 200,
            'msg': '成功',
            'data': users,
            'total': len(users)
        })
    except Exception as e:
        logger.error(f"获取成员列表失败: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@user_bp.route('/info/<user_id>', methods=['GET'])
def get_user_info(user_id):
    """Get member detail info."""
    try:
        user = api_client.get_user_info(user_id)
        if user:
            return jsonify({
                'code': 200,
                'msg': 'success',
                'data': user
            })
    except Exception as e:
        logger.warning(f"get_user_info failed: {e} - fallback to list")

    try:
        users = api_client.list_users()
        token = _normalize_token(user_id)
        matched = _match_user_by_token(users, token)
        if matched:
            matched_id = matched.get('user_id') or matched.get('_id') or matched.get('id')
            if matched_id and matched_id != user_id:
                try:
                    detail = api_client.get_user_info(matched_id)
                    if detail:
                        return jsonify({
                            'code': 200,
                            'msg': 'success',
                            'data': detail
                        })
                except Exception as e:
                    logger.warning(f"get_user_info fallback failed: {e}")
            return jsonify({
                'code': 200,
                'msg': 'success',
                'data': matched
            })
        return jsonify({
            'code': 404,
            'msg': 'user not found'
        }), 404
    except Exception as e:
        logger.error(f"get_user_info failed: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500
