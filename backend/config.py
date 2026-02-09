"""
配置文件
"""
import os

# Base dir
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Flask配置
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
DEBUG = os.getenv('DEBUG', True)

# Online-Office API配置
ONLINE_OFFICE_BASE_URL = 'https://ahyg.online-office.net/openapi/v1'
APP_ID = '59e10c88146584ed89e2896b'
API_KEY = os.getenv('API_KEY', 'mSg84nwyHNdcyye7kx2PB6GCNwdea4pp')

# 阶段配置表
STAGE_CONFIG_ENTRY_ID = '47c64f56ba43e2a6b8654029'
COST_STAGE_ENTRY_ID = '2ae1401fbd78bcccaba24a6b'

# 项目表
PROJECT_ENTRY_ID = 'e8894672999be041d2d1c4f1'

# 项目类型表
PROJECT_TYPE_ENTRY_ID = '6e32422ead05c1ce9790f812'
COST_TYPE_ENTRY_ID = '30e046f98508908b9ae064ae'

PROJECT_PROGRESS_ENTRY_ID = '11714a488b65fc5074a981cd'

# 项目预算/成本管理表
PROJECT_BUDGET_ENTRY_ID = '7235499ba8fd3f91362c04ce'

# 发货管理表
DELIVERY_ENTRY_ID = '7f214b928a8811cfd38e6d2c'

# 检测项目表
INSPECTION_ENTRY_ID = '37f8492484812d6cd8781fc8'

# CORS配置
CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:8080', 'http://127.0.0.1:5000']

# 请求超时
REQUEST_TIMEOUT = 30


# Uploads
UPLOAD_DIR = os.getenv('UPLOAD_DIR', os.path.join(BASE_DIR, 'uploads'))
PUBLIC_BASE_URL = os.getenv('PUBLIC_BASE_URL', '')
