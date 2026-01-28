"""
Online-Office API 对接模块
"""
import requests
import logging
from typing import Dict, List, Optional, Any
from config import (
    ONLINE_OFFICE_BASE_URL,
    APP_ID,
    API_KEY,
    STAGE_CONFIG_ENTRY_ID,
    PROJECT_ENTRY_ID,
    PROJECT_TYPE_ENTRY_ID,
    PROJECT_PROGRESS_ENTRY_ID,
    REQUEST_TIMEOUT
)
from field_mapping import (
    FieldMapper,
    PROJECT_FIELDS,
    STAGE_CONFIG_FIELDS_EN,
    STAGE_CONFIG_REVERSE_EN,
    PROJECT_TYPE_REVERSE_EN,
    PROJECT_PROGRESS_FIELDS_EN,
    PROJECT_PROGRESS_REVERSE_EN,
)

logger = logging.getLogger(__name__)


class OnlineOfficeAPI:
    """Online-Office API 客户端"""
    
    def __init__(self, app_id: str = APP_ID):
        self.app_id = app_id
        self.base_url = ONLINE_OFFICE_BASE_URL
        self.session = requests.Session()
        # 添加认证头
        self.session.headers.update({
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        })
    
    def _build_url(self, entry_id: str, endpoint: str) -> str:
        """构建API URL"""
        return f"{self.base_url}/app/{self.app_id}/entry/{entry_id}/{endpoint}"
    
    def _request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        try:
            logger.info(f"API 请求: {method} {url}")
            response = self.session.request(
                method, 
                url, 
                timeout=REQUEST_TIMEOUT,
                **kwargs
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"API 响应: {result}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"响应内容: {e.response.text}")
            raise
    
    # ==================== 阶段配置表操作 ====================
    
    def create_stage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建阶段节点"""
        # 转换字段别名
        mapped_data = FieldMapper.map_to_alias(data, STAGE_CONFIG_FIELDS_EN)
        
        url = self._build_url(STAGE_CONFIG_ENTRY_ID, 'data_create')
        result = self._request('POST', url, json={'data': mapped_data})
        return FieldMapper.map_from_alias(result.get('data', {}), STAGE_CONFIG_REVERSE_EN)
    
    def get_stage(self, data_id: str) -> Dict[str, Any]:
        """获取单个阶段节点"""
        url = self._build_url(STAGE_CONFIG_ENTRY_ID, 'data_retrieve')
        result = self._request('POST', url, json={'data_id': data_id})
        
        # 转换为英文字段名
        data = result.get('data', {})
        return FieldMapper.map_from_alias(data, STAGE_CONFIG_REVERSE_EN)
    
    def list_stages(self, skip: int = 0, limit: int = 300, filter_obj: Optional[Dict] = None) -> List[Dict]:
        """查询阶段节点列表"""
        url = self._build_url(STAGE_CONFIG_ENTRY_ID, 'data')
        
        payload = {
            'skip': skip,
            'limit': limit
        }
        if filter_obj:
            payload['filter'] = filter_obj
        
        result = self._request('POST', url, json=payload)
        
        # 转换为英文字段名
        return [FieldMapper.map_from_alias(item, STAGE_CONFIG_REVERSE_EN) for item in result.get('data', [])]

    def list_project_types(self, skip: int = 0, limit: int = 300, filter_obj: Optional[Dict] = None) -> List[Dict]:
        """查询项目类型列表"""
        url = self._build_url(PROJECT_TYPE_ENTRY_ID, 'data')

        payload = {
            'skip': skip,
            'limit': limit
        }
        if filter_obj:
            payload['filter'] = filter_obj

        result = self._request('POST', url, json=payload)
        return [FieldMapper.map_from_alias(item, PROJECT_TYPE_REVERSE_EN) for item in result.get('data', [])]
    
    def update_stage(self, data_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新阶段节点"""
        # 只映射支持的字段，过滤掉其他字段
        supported_fields = {k: v for k, v in STAGE_CONFIG_FIELDS_EN.items() if k in data}
        mapped_data = FieldMapper.map_to_alias(data, supported_fields)
        
        url = self._build_url(STAGE_CONFIG_ENTRY_ID, 'data_update')
        result = self._request('POST', url, json={
            'data_id': data_id,
            'data': mapped_data
        })
        return FieldMapper.map_from_alias(result.get('data', {}), STAGE_CONFIG_REVERSE_EN)
    
    def delete_stage(self, data_id: str) -> bool:
        """删除阶段节点"""
        url = self._build_url(STAGE_CONFIG_ENTRY_ID, 'data_delete')
        self._request('POST', url, json={
            'data_id': data_id,
            'is_start_event': False,
            'operator': ''
        })
        return True
    
    # ==================== 项目表操作 ====================
    
    def create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建项目"""
        mapped_data = FieldMapper.map_to_alias(data, PROJECT_FIELDS)
        
        url = self._build_url(PROJECT_ENTRY_ID, 'data_create')
        result = self._request('POST', url, json={'data': mapped_data})
        return result.get('data', {})
    
    def get_project(self, data_id: str) -> Dict[str, Any]:
        """获取单个项目"""
        url = self._build_url(PROJECT_ENTRY_ID, 'data_retrieve')
        result = self._request('POST', url, json={'data_id': data_id})
        
        data = result.get('data', {})
        return FieldMapper.map_from_alias(data, {v: k for k, v in PROJECT_FIELDS.items()})
    
    def list_projects(self, skip: int = 0, limit: int = 300, filter_obj: Optional[Dict] = None) -> List[Dict]:
        """查询项目列表"""
        url = self._build_url(PROJECT_ENTRY_ID, 'data')
        
        payload = {
            'skip': skip,
            'limit': limit
        }
        if filter_obj:
            payload['filter'] = filter_obj
        
        result = self._request('POST', url, json=payload)
        
        reverse_map = {v: k for k, v in PROJECT_FIELDS.items()}
        return [FieldMapper.map_from_alias(item, reverse_map) for item in result.get('data', [])]
    
    def update_project(self, data_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新项目"""
        mapped_data = FieldMapper.map_to_alias(data, PROJECT_FIELDS)
        
        url = self._build_url(PROJECT_ENTRY_ID, 'data_update')
        result = self._request('POST', url, json={
            'data_id': data_id,
            'data': mapped_data
        })
        return result.get('data', {})
    
    def delete_project(self, data_id: str) -> bool:
        """删除项目"""
        url = self._build_url(PROJECT_ENTRY_ID, 'data_delete')
        self._request('POST', url, json={
            'data_id': data_id,
            'is_start_event': False,
            'operator': ''
        })
        return True

    # ==================== Project progress operations ====================

    def create_project_progress(self, data: Dict[str, Any]) -> Dict[str, Any]:
        mapped_data = FieldMapper.map_to_alias(data, PROJECT_PROGRESS_FIELDS_EN)
        url = self._build_url(PROJECT_PROGRESS_ENTRY_ID, 'data_create')
        result = self._request('POST', url, json={'data': mapped_data})
        return FieldMapper.map_from_alias(result.get('data', {}), PROJECT_PROGRESS_REVERSE_EN)

    def get_project_progress(self, data_id: str) -> Dict[str, Any]:
        url = self._build_url(PROJECT_PROGRESS_ENTRY_ID, 'data_retrieve')
        result = self._request('POST', url, json={'data_id': data_id})
        data = result.get('data', {})
        return FieldMapper.map_from_alias(data, PROJECT_PROGRESS_REVERSE_EN)

    def list_project_progress(
        self,
        skip: int = 0,
        limit: int = 300,
        filter_obj: Optional[Dict] = None
    ) -> List[Dict]:
        url = self._build_url(PROJECT_PROGRESS_ENTRY_ID, 'data')
        payload = {
            'skip': skip,
            'limit': limit
        }
        if filter_obj:
            payload['filter'] = filter_obj
        result = self._request('POST', url, json=payload)
        return [
            FieldMapper.map_from_alias(item, PROJECT_PROGRESS_REVERSE_EN)
            for item in result.get('data', [])
        ]

    def update_project_progress(self, data_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        supported_fields = {k: v for k, v in PROJECT_PROGRESS_FIELDS_EN.items() if k in data}
        mapped_data = FieldMapper.map_to_alias(data, supported_fields)
        url = self._build_url(PROJECT_PROGRESS_ENTRY_ID, 'data_update')
        result = self._request('POST', url, json={
            'data_id': data_id,
            'data': mapped_data
        })
        return FieldMapper.map_from_alias(result.get('data', {}), PROJECT_PROGRESS_REVERSE_EN)

    def delete_project_progress(self, data_id: str) -> bool:
        url = self._build_url(PROJECT_PROGRESS_ENTRY_ID, 'data_delete')
        self._request('POST', url, json={
            'data_id': data_id,
            'is_start_event': False,
            'operator': ''
        })
        return True

    def upload_project_progress_files(self, files: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        url = self._build_url(PROJECT_PROGRESS_ENTRY_ID, 'upload_file')
        result = self._request('POST', url, json=files)
        return result.get('data', [])

# 全局API实例
api_client = OnlineOfficeAPI()
