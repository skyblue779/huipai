"""
配置文件
"""
import os

# Flask配置
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
DEBUG = os.getenv('DEBUG', True)

# Online-Office API配置
ONLINE_OFFICE_BASE_URL = 'https://ahyg.online-office.net/openapi/v1'
APP_ID = '59e10c88146584ed89e2896b'
API_KEY = os.getenv('API_KEY', 'mSg84nwyHNdcyye7kx2PB6GCNwdea4pp')

# 阶段配置表
STAGE_CONFIG_ENTRY_ID = '47c64f56ba43e2a6b8654029'

# 项目表
PROJECT_ENTRY_ID = 'e8894672999be041d2d1c4f1'

# 项目类型表
PROJECT_TYPE_ENTRY_ID = '6e32422ead05c1ce9790f812'

# CORS配置
CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:8080', 'http://127.0.0.1:5000']

# 请求超时
REQUEST_TIMEOUT = 30

