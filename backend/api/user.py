"""
User directory API routes.
"""
import logging
from flask import Blueprint, jsonify
from api.online_office import api_client
from config import PROJECT_MANAGER_ROLE_ID, DELAY_REQUEST_REVIEW_ADMIN_ROLE_ID

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
        if _normalize_token(user.get('username')) == token:
            return user
        if _normalize_token(user.get('user_name')) == token:
            return user
        if _normalize_token(user.get('userName')) == token:
            return user
        if _normalize_token(user.get('uniqueid')) == token:
            return user
    return None


def _normalize_account_user(user):
    if not isinstance(user, dict):
        return {}
    normalized = dict(user)
    if not normalized.get('name'):
        normalized['name'] = normalized.get('username', '')
    if not normalized.get('user_name'):
        normalized['user_name'] = normalized.get('username', normalized.get('name', ''))
    return normalized


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
        logger.warning(f"get_user_info failed: {e} - fallback to account_info/list")

    try:
        account_user = _normalize_account_user(api_client.get_account_info(user_id=user_id))
        if account_user:
            return jsonify({
                'code': 200,
                'msg': 'success',
                'data': account_user
            })
    except Exception as e:
        logger.warning(f"get_account_info fallback failed: {e}")

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


@user_bp.route('/role-members/<role_id>', methods=['GET'])
def list_role_members(role_id):
    """List members for a specific role."""
    try:
        users = api_client.list_role_members(role_id)
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': users,
            'total': len(users)
        })
    except Exception as e:
        logger.error(f"list_role_members failed: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@user_bp.route('/project-managers', methods=['GET'])
def list_project_managers():
    """List configured project manager role members."""
    try:
        users = api_client.list_role_members(PROJECT_MANAGER_ROLE_ID)
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': users,
            'total': len(users),
            'role_id': PROJECT_MANAGER_ROLE_ID
        })
    except Exception as e:
        logger.error(f"list_project_managers failed: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500


@user_bp.route('/delay-request-review-admins', methods=['GET'])
def list_delay_request_review_admins():
    """List members who may review project delay requests as administrators."""
    try:
        users = api_client.list_role_members(DELAY_REQUEST_REVIEW_ADMIN_ROLE_ID)
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': users,
            'total': len(users),
            'role_id': DELAY_REQUEST_REVIEW_ADMIN_ROLE_ID
        })
    except Exception as e:
        logger.error(f"list_delay_request_review_admins failed: {e}")
        return jsonify({
            'code': 500,
            'msg': str(e)
        }), 500
