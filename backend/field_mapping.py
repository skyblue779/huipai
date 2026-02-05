"""
字段别名映射配置
根据Online-Office的字段别名对应表
"""

# 阶段配置表的字段映射 (entry: 47c64f56ba43e2a6b8654029)
STAGE_CONFIG_FIELDS = {
    '阶段节点id': '_widget_1769130163477',
    '名称': '_widget_1769130163517',
    '父节点': '_widget_1769130163557',
    '排序': '_widget_1769130163598',
    '说明': '_widget_1769150079419',
    '项目类型': '_widget_1769152663361',
}

# 阶段配置表的英文字段映射（前端使用）
STAGE_CONFIG_FIELDS_EN = {
    'id': '_widget_1769130163477',
    'name': '_widget_1769130163517',
    'parent_id': '_widget_1769130163557',
    'sort_order': '_widget_1769130163598',
    'description': '_widget_1769150079419',
    'project_type': '_widget_1769152663361',
}

# 椤圭洰鎴愭湰闃舵閰嶇疆琛ㄧ殑鑻辨枃瀛楁鏄犲皠 (entry: 2ae1401fbd78bcccaba24a6b)
COST_STAGE_FIELDS_EN = {
    'id': '_widget_1769130163477',
    'name': '_widget_1769130163517',
    'parent_id': '_widget_1769130163557',
    'sort_order': '_widget_1769130163598',
    'description': '_widget_1769150079419',
    'project_type': '_widget_1769152663361',
    'budget_standard': '_widget_1770193455058',
}

# 项目类型表字段映射 (entry: 6e32422ead05c1ce9790f812)
PROJECT_TYPE_FIELDS_EN = {
    'id': '_widget_1769152903399',       # sn
    'name': '_widget_1769152903413',     # text
}
PROJECT_TYPE_REVERSE_EN = {v: k for k, v in PROJECT_TYPE_FIELDS_EN.items()}

# 椤圭洰鎴愭湰绫诲瀷琛ㄥ瓧娈垫槧灏? (entry: 30e046f98508908b9ae064ae)
COST_TYPE_FIELDS_EN = {
    'id': '_widget_1769152903399',       # sn
    'name': '_widget_1769152903413',     # text
}
COST_TYPE_REVERSE_EN = {v: k for k, v in COST_TYPE_FIELDS_EN.items()}

# 项目表的字段映射 (entry: e8894672999be041d2d1c4f1)
PROJECT_FIELDS = {
    '项目编号': '_widget_1769064437789',
    '项目名称': '_widget_1769064437770',
    '合同名称': '_widget_1769064437829',
    '项目类型': '_widget_1769064636768',
    '建设地点': '_widget_1769064637832',
    '项目状态': '_widget_1769064637023',
    '计划开工': '_widget_1769064637850',
    '计划完工': '_widget_1769064637874',
    '项目经理': '_widget_1769064637963',
    '责任部门': '_widget_1769066077660',
    '参与人员': '_widget_1769066077800',
    '子表单': '_widget_1769131834894',
    '项目阶段': '_widget_1769131834919',
    '执行人': '_widget_1769131834982',
    '计划时间': '_widget_1769131835032',
    '实际完成': '_widget_1769131835092',
    '状态': '_widget_1769131835157',
}

# 反向映射：从字段别名到中文名称
STAGE_CONFIG_REVERSE = {v: k for k, v in STAGE_CONFIG_FIELDS.items()}
STAGE_CONFIG_REVERSE_EN = {v: k for k, v in STAGE_CONFIG_FIELDS_EN.items()}
COST_STAGE_REVERSE_EN = {v: k for k, v in COST_STAGE_FIELDS_EN.items()}
PROJECT_PROGRESS_FIELDS_EN = {
    'project_code': '_widget_1769239633492',
    'project_name': '_widget_1769239633511',
    'project_type': '_widget_1769239633530',
    'main_stage': '_widget_1769239633707',
    'main_stage_order': '_widget_1769580025032',
    'project_stage': '_widget_1769239633603',
    'project_stage_order': '_widget_1769580025051',
    'executor': '_widget_1769239633622',
    'plan_time': '_widget_1769239633640',
    'actual_finish': '_widget_1769239633664',
    'status': '_widget_1769239633688',
    'site_upload': '_widget_1769411917447',
    'execution_note': '_widget_1769411917532',
    'overdue_reason': '_widget_1769411917651',
    'warning_level': '_widget_1769570424734',
}

PROJECT_PROGRESS_REVERSE_EN = {v: k for k, v in PROJECT_PROGRESS_FIELDS_EN.items()}

PROJECT_REVERSE = {v: k for k, v in PROJECT_FIELDS.items()}

# 项目预算管理表字段映射 (entry: 7235499ba8fd3f91362c04ce)
PROJECT_BUDGET_FIELDS_EN = {
    'project_code': '_widget_1770184687558',
    'project_name': '_widget_1770184687577',
    'project_type': '_widget_1770184687725',
    'cost_center': '_widget_1770184687688',
    'cost_item': '_widget_1770184687651',
    'main_stage_order': '_widget_1770184687596',
    'project_stage_order': '_widget_1770184687871',
    'status': '_widget_1770184688070',
    'budget_standard': '_widget_1770184688128',
    'actual_total': '_widget_1770184688149',
    'cost_details': '_widget_1770184688372',
}

PROJECT_BUDGET_DETAIL_FIELDS_EN = {
    'detail_date': '_widget_1770184688515',
    'detail_item': '_widget_1770184688732',
    'detail_amount': '_widget_1770184688945',
    'detail_remark': '_widget_1770184688999',
}

PROJECT_BUDGET_REVERSE_EN = {v: k for k, v in PROJECT_BUDGET_FIELDS_EN.items()}
PROJECT_BUDGET_DETAIL_REVERSE_EN = {v: k for k, v in PROJECT_BUDGET_DETAIL_FIELDS_EN.items()}


class FieldMapper:
    """字段映射工具类"""
    
    @staticmethod
    def map_to_alias(data, fields_dict):
        """
        将中文字段名转换为别名
        
        Args:
            data: 包含中文字段名的字典
            fields_dict: 字段映射字典
            
        Returns:
            包含别名的字典
        """
        result = {}
        for cn_name, value in data.items():
            alias = fields_dict.get(cn_name)
            if alias:
                result[alias] = value
            else:
                result[cn_name] = value
        return result
    
    @staticmethod
    def map_from_alias(data, reverse_fields_dict):
        """
        将别名转换为中文字段名
        
        Args:
            data: 包含别名的字典
            reverse_fields_dict: 反向映射字典
            
        Returns:
            包含中文字段名的字典
        """
        result = {}
        for alias, value in data.items():
            cn_name = reverse_fields_dict.get(alias, alias)
            result[cn_name] = value
        return result
