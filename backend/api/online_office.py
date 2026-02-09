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
    COST_STAGE_ENTRY_ID,
    PROJECT_ENTRY_ID,
    PROJECT_TYPE_ENTRY_ID,
    COST_TYPE_ENTRY_ID,
    PROJECT_PROGRESS_ENTRY_ID,
    PROJECT_BUDGET_ENTRY_ID,
    DELIVERY_ENTRY_ID,
    INSPECTION_ENTRY_ID,
    REQUEST_TIMEOUT
)
from field_mapping import (
    FieldMapper,
    PROJECT_FIELDS,
    PROJECT_FIELDS_EN,
    STAGE_CONFIG_FIELDS_EN,
    STAGE_CONFIG_REVERSE_EN,
    COST_STAGE_FIELDS_EN,
    COST_STAGE_REVERSE_EN,
    PROJECT_TYPE_REVERSE_EN,
    COST_TYPE_REVERSE_EN,
    PROJECT_REVERSE_EN,
    PROJECT_PROGRESS_FIELDS_EN,
    PROJECT_PROGRESS_REVERSE_EN,
    PROJECT_BUDGET_FIELDS_EN,
    PROJECT_BUDGET_DETAIL_FIELDS_EN,
    PROJECT_BUDGET_REVERSE_EN,
    PROJECT_BUDGET_DETAIL_REVERSE_EN,
    DELIVERY_FIELDS_EN,
    DELIVERY_ITEM_FIELDS_EN,
    DELIVERY_REVERSE_EN,
    DELIVERY_ITEM_REVERSE_EN,
    INSPECTION_FIELDS_EN,
    INSPECTION_REVERSE_EN,
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

    def list_cost_types(self, skip: int = 0, limit: int = 300, filter_obj: Optional[Dict] = None) -> List[Dict]:
        """List cost types."""
        url = self._build_url(COST_TYPE_ENTRY_ID, 'data')

        payload = {
            'skip': skip,
            'limit': limit
        }
        if filter_obj:
            payload['filter'] = filter_obj

        result = self._request('POST', url, json=payload)
        return [FieldMapper.map_from_alias(item, COST_TYPE_REVERSE_EN) for item in result.get('data', [])]
    
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
    
    

    # ==================== Cost stage operations ====================

    def create_cost_stage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create cost stage."""
        mapped_data = FieldMapper.map_to_alias(data, COST_STAGE_FIELDS_EN)
        url = self._build_url(COST_STAGE_ENTRY_ID, 'data_create')
        result = self._request('POST', url, json={'data': mapped_data})
        return FieldMapper.map_from_alias(result.get('data', {}), COST_STAGE_REVERSE_EN)

    def get_cost_stage(self, data_id: str) -> Dict[str, Any]:
        """Get cost stage."""
        url = self._build_url(COST_STAGE_ENTRY_ID, 'data_retrieve')
        result = self._request('POST', url, json={'data_id': data_id})
        data = result.get('data', {})
        return FieldMapper.map_from_alias(data, COST_STAGE_REVERSE_EN)

    def list_cost_stages(self, skip: int = 0, limit: int = 300, filter_obj: Optional[Dict] = None) -> List[Dict]:
        """List cost stages."""
        url = self._build_url(COST_STAGE_ENTRY_ID, 'data')
        payload = {
            'skip': skip,
            'limit': limit
        }
        if filter_obj:
            payload['filter'] = filter_obj
        result = self._request('POST', url, json=payload)
        return [FieldMapper.map_from_alias(item, COST_STAGE_REVERSE_EN) for item in result.get('data', [])]

    def update_cost_stage(self, data_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update cost stage."""
        supported_fields = {k: v for k, v in COST_STAGE_FIELDS_EN.items() if k in data}
        mapped_data = FieldMapper.map_to_alias(data, supported_fields)
        url = self._build_url(COST_STAGE_ENTRY_ID, 'data_update')
        result = self._request('POST', url, json={
            'data_id': data_id,
            'data': mapped_data
        })
        return FieldMapper.map_from_alias(result.get('data', {}), COST_STAGE_REVERSE_EN)

    def delete_cost_stage(self, data_id: str) -> bool:
        """Delete cost stage."""
        url = self._build_url(COST_STAGE_ENTRY_ID, 'data_delete')
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

    def list_projects_en(
        self,
        skip: int = 0,
        limit: int = 300,
        filter_obj: Optional[Dict] = None,
        fields: Optional[List[str]] = None
    ) -> List[Dict]:
        """查询项目列表（英文字段）"""
        url = self._build_url(PROJECT_ENTRY_ID, 'data')

        payload = {
            'skip': skip,
            'limit': limit
        }
        if filter_obj:
            payload['filter'] = filter_obj
        if fields:
            payload['fields'] = [PROJECT_FIELDS_EN.get(name, name) for name in fields]

        result = self._request('POST', url, json=payload)
        return [FieldMapper.map_from_alias(item, PROJECT_REVERSE_EN) for item in result.get('data', [])]
    
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

    # ==================== Project budget operations ====================

    @staticmethod
    def _map_budget_details_to_alias(details: Any) -> List[Dict[str, Any]]:
        if not isinstance(details, list):
            return []
        mapped = []
        for item in details:
            if not isinstance(item, dict):
                continue
            mapped.append(FieldMapper.map_to_alias(item, PROJECT_BUDGET_DETAIL_FIELDS_EN))
        return mapped

    @staticmethod
    def _map_budget_details_from_alias(details: Any) -> Any:
        if not isinstance(details, list):
            return details
        mapped = []
        for item in details:
            if not isinstance(item, dict):
                continue
            mapped.append(FieldMapper.map_from_alias(item, PROJECT_BUDGET_DETAIL_REVERSE_EN))
        return mapped

    def _map_project_budget_from_alias(self, data: Dict[str, Any]) -> Dict[str, Any]:
        mapped = FieldMapper.map_from_alias(data, PROJECT_BUDGET_REVERSE_EN)
        details_key = PROJECT_BUDGET_REVERSE_EN.get(PROJECT_BUDGET_FIELDS_EN['cost_details'])
        if details_key and details_key in mapped:
            mapped[details_key] = self._map_budget_details_from_alias(mapped.get(details_key))
        return mapped

    def create_project_budget(self, data: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(data or {})
        details = payload.pop('cost_details', None)
        mapped_data = FieldMapper.map_to_alias(payload, PROJECT_BUDGET_FIELDS_EN)
        if details is not None:
            mapped_data[PROJECT_BUDGET_FIELDS_EN['cost_details']] = self._map_budget_details_to_alias(details)
        url = self._build_url(PROJECT_BUDGET_ENTRY_ID, 'data_create')
        result = self._request('POST', url, json={'data': mapped_data})
        return self._map_project_budget_from_alias(result.get('data', {}))

    def get_project_budget(self, data_id: str) -> Dict[str, Any]:
        url = self._build_url(PROJECT_BUDGET_ENTRY_ID, 'data_retrieve')
        result = self._request('POST', url, json={'data_id': data_id})
        data = result.get('data', {})
        return self._map_project_budget_from_alias(data)

    def list_project_budgets(
        self,
        skip: int = 0,
        limit: int = 300,
        filter_obj: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        url = self._build_url(PROJECT_BUDGET_ENTRY_ID, 'data')
        payload = {
            'skip': skip,
            'limit': limit
        }
        if filter_obj:
            payload['filter'] = filter_obj
        result = self._request('POST', url, json=payload)
        return [
            self._map_project_budget_from_alias(item)
            for item in result.get('data', [])
        ]

    def update_project_budget(self, data_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data:
            return {}
        payload = dict(data)
        details = None
        if 'cost_details' in payload:
            details = payload.pop('cost_details')
        supported_fields = {k: v for k, v in PROJECT_BUDGET_FIELDS_EN.items() if k in payload}
        mapped_data = FieldMapper.map_to_alias(payload, supported_fields)
        if details is not None:
            mapped_data[PROJECT_BUDGET_FIELDS_EN['cost_details']] = self._map_budget_details_to_alias(details)
        url = self._build_url(PROJECT_BUDGET_ENTRY_ID, 'data_update')
        result = self._request('POST', url, json={
            'data_id': data_id,
            'data': mapped_data
        })
        return self._map_project_budget_from_alias(result.get('data', {}))

    def delete_project_budget(self, data_id: str) -> bool:
        url = self._build_url(PROJECT_BUDGET_ENTRY_ID, 'data_delete')
        self._request('POST', url, json={
            'data_id': data_id,
            'is_start_event': False,
            'operator': ''
        })
        return True

    def upload_project_budget_files(self, files: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        url = self._build_url(PROJECT_BUDGET_ENTRY_ID, 'upload_file')
        result = self._request('POST', url, json=files)
        return result.get('data', [])

    # ==================== Delivery operations ====================

    @staticmethod
    def _map_delivery_items_to_alias(details: Any) -> List[Dict[str, Any]]:
        if not isinstance(details, list):
            return []
        mapped = []
        for item in details:
            if isinstance(item, dict):
                mapped.append(FieldMapper.map_to_alias(item, DELIVERY_ITEM_FIELDS_EN))
        return mapped

    @staticmethod
    def _map_delivery_items_from_alias(details: Any) -> List[Dict[str, Any]]:
        if not isinstance(details, list):
            return []
        mapped = []
        for item in details:
            if isinstance(item, dict):
                mapped.append(FieldMapper.map_from_alias(item, DELIVERY_ITEM_REVERSE_EN))
        return mapped

    @staticmethod
    def _normalize_delivery_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        value = payload.get('inspection_items')
        if value is None:
            return payload
        if isinstance(value, list):
            return payload
        if isinstance(value, str):
            trimmed = value.strip()
            payload['inspection_items'] = [trimmed] if trimmed else []
            return payload
        payload['inspection_items'] = [value]
        return payload

    def _map_delivery_from_alias(self, data: Dict[str, Any]) -> Dict[str, Any]:
        mapped = FieldMapper.map_from_alias(data, DELIVERY_REVERSE_EN)
        items_key = DELIVERY_REVERSE_EN.get(DELIVERY_FIELDS_EN['cargo_items'])
        if items_key and items_key in mapped:
            mapped[items_key] = self._map_delivery_items_from_alias(mapped.get(items_key))
        return mapped

    def list_deliveries(
        self,
        skip: int = 0,
        limit: int = 300,
        filter_obj: Optional[Dict] = None
    ) -> List[Dict]:
        url = self._build_url(DELIVERY_ENTRY_ID, 'data')
        payload = {
            'skip': skip,
            'limit': limit
        }
        if filter_obj:
            payload['filter'] = filter_obj
        result = self._request('POST', url, json=payload)
        return [
            self._map_delivery_from_alias(item)
            for item in result.get('data', [])
        ]

    def get_delivery(self, data_id: str) -> Dict[str, Any]:
        url = self._build_url(DELIVERY_ENTRY_ID, 'data_retrieve')
        result = self._request('POST', url, json={'data_id': data_id})
        data = result.get('data', {})
        return self._map_delivery_from_alias(data)

    def create_delivery(self, data: Dict[str, Any]) -> Dict[str, Any]:
        payload = self._normalize_delivery_payload(dict(data))
        details = payload.pop('cargo_items', None)
        mapped_data = FieldMapper.map_to_alias(payload, DELIVERY_FIELDS_EN)
        if details is not None:
            mapped_data[DELIVERY_FIELDS_EN['cargo_items']] = self._map_delivery_items_to_alias(details)
        url = self._build_url(DELIVERY_ENTRY_ID, 'data_create')
        result = self._request('POST', url, json={'data': mapped_data})
        return self._map_delivery_from_alias(result.get('data', {}))

    def update_delivery(self, data_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        payload = self._normalize_delivery_payload(dict(data))
        details = payload.pop('cargo_items', None)
        supported_fields = {k: v for k, v in DELIVERY_FIELDS_EN.items() if k in payload}
        mapped_data = FieldMapper.map_to_alias(payload, supported_fields)
        if details is not None:
            mapped_data[DELIVERY_FIELDS_EN['cargo_items']] = self._map_delivery_items_to_alias(details)
        url = self._build_url(DELIVERY_ENTRY_ID, 'data_update')
        result = self._request('POST', url, json={
            'data_id': data_id,
            'data': mapped_data
        })
        return self._map_delivery_from_alias(result.get('data', {}))

    def delete_delivery(self, data_id: str) -> bool:
        url = self._build_url(DELIVERY_ENTRY_ID, 'data_delete')
        self._request('POST', url, json={
            'data_id': data_id,
            'is_start_event': False,
            'operator': ''
        })
        return True

    def upload_delivery_files(self, files: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        url = self._build_url(DELIVERY_ENTRY_ID, 'upload_file')
        result = self._request('POST', url, json=files)
        return result.get('data', [])

    # ==================== Inspection operations ====================

    def list_inspections(
        self,
        skip: int = 0,
        limit: int = 300,
        filter_obj: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        url = self._build_url(INSPECTION_ENTRY_ID, 'data')
        payload = {
            'skip': skip,
            'limit': limit
        }
        if filter_obj:
            payload['filter'] = filter_obj
        result = self._request('POST', url, json=payload)
        return [
            FieldMapper.map_from_alias(item, INSPECTION_REVERSE_EN)
            for item in result.get('data', [])
        ]

    # ==================== User directory operations ====================

    def list_users(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/user/user_list"
        result = self._request('POST', url, json={})
        return result.get('users', [])

    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/user/user_info"
        result = self._request('POST', url, json={'user_id': user_id})
        return result.get('user', {})

# 全局API实例
api_client = OnlineOfficeAPI()
