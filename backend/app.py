"""
主应用入口
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import logging
from config import DEBUG, CORS_ORIGINS, SECRET_KEY, UPLOAD_DIR, PUBLIC_BASE_URL
from api.stage_config import stage_bp
from api.project import project_bp
from api.project_type import project_type_bp
from api.cost_stage_config import cost_stage_bp
from api.cost_type import cost_type_bp
from api.project_progress import progress_bp
from api.user import user_bp
from api.project_budget import project_budget_bp
from api.delivery import delivery_bp
from api.inspection import inspection_bp
from api.inspection_delivery import inspection_delivery_bp

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)
    
    # 加载配置
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = DEBUG
    app.config['UPLOAD_DIR'] = UPLOAD_DIR
    app.config['PUBLIC_BASE_URL'] = PUBLIC_BASE_URL
    
    # 启用CORS（开发模式下允许所有来源，避免前端跨域阻塞）
    # 生产环境请根据 CORS_ORIGINS 进行严格配置
    try:
        if app.config.get('DEBUG'):
            CORS(app, resources={r"/api/*": {"origins": "*"}})
        else:
            CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})
    except Exception:
        # 回退到宽松策略，确保开发阶段前端能访问
        CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册蓝图
    app.register_blueprint(stage_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(project_type_bp)
    app.register_blueprint(cost_stage_bp)
    app.register_blueprint(cost_type_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(project_budget_bp)
    app.register_blueprint(delivery_bp)
    app.register_blueprint(inspection_bp)
    app.register_blueprint(inspection_delivery_bp)
    
    # 健康检查端点
    @app.route('/uploads/<path:filename>', methods=['GET'])
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_DIR'], filename)

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'code': 200,
            'msg': '服务正常',
            'status': 'healthy'
        })
    
    # 根路由
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'code': 200,
            'msg': '欢迎使用徽派家私数字管理平台 API',
            'version': '1.0.0',
            'endpoints': {
                '阶段配置': {
                    '获取列表': 'GET /api/stage/list',
                    '获取详情': 'GET /api/stage/get/<id>',
                    '创建': 'POST /api/stage/create',
                    '更新': 'PUT /api/stage/update/<id>',
                    '删除': 'DELETE /api/stage/delete/<id>'
                },
                '项目管理': {
                    '获取列表': 'GET /api/project/list',
                    '获取详情': 'GET /api/project/get/<id>',
                    '创建': 'POST /api/project/create',
                    '更新': 'PUT /api/project/update/<id>',
                    '删除': 'DELETE /api/project/delete/<id>'
                }
            }
        })
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'code': 404,
            'msg': '资源不存在'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'code': 500,
            'msg': '服务器内部错误'
        }), 500
    
    logger.info("Flask 应用创建完成")
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='172.16.0.66', port=9989, debug=DEBUG)
