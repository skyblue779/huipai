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
    '项目成本类型': '_widget_1770203938133',
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
    'plan_finishtime': '_widget_1770709742059',
    'actual_finish': '_widget_1769239633664',
    'status': '_widget_1769239633688',
    'site_upload': '_widget_1769411917447',
    'execution_note': '_widget_1769411917532',
    'overdue_reason': '_widget_1769411917651',
    'warning_level': '_widget_1769570424734',
}

PROJECT_PROGRESS_REVERSE_EN = {v: k for k, v in PROJECT_PROGRESS_FIELDS_EN.items()}

PROJECT_REVERSE = {v: k for k, v in PROJECT_FIELDS.items()}

# 项目表英文字段映射（前端使用）
PROJECT_FIELDS_EN = {
    'project_code': '_widget_1769064437789',
    'project_name': '_widget_1769064437770',
    'contract_name': '_widget_1769064437829',
    'project_type': '_widget_1769064636768',
    'location': '_widget_1769064637832',
    'project_cost_type': '_widget_1770203938133',
    'project_status': '_widget_1769064637023',
    'plan_start': '_widget_1769064637850',
    'plan_finish': '_widget_1769064637874',
    'project_manager': '_widget_1769064637963',
    'owner_department': '_widget_1769066077660',
    'participants': '_widget_1769066077800',
}
PROJECT_REVERSE_EN = {v: k for k, v in PROJECT_FIELDS_EN.items()}

# 项目预算管理表字段映射 (entry: 7235499ba8fd3f91362c04ce)
PROJECT_BUDGET_FIELDS_EN = {
    'project_code': '_widget_1770184687558',
    'project_name': '_widget_1770184687577',
    'project_type': '_widget_1770184687725',
    'cost_center': '_widget_1770184687688',
    'cost_item': '_widget_1770184687651',
    'cost_type': '_widget_1770714371641',
    'main_stage_order': '_widget_1770184687596',
    'project_stage_order': '_widget_1770184687871',
    'status': '_widget_1770184688070',
    'budget_standard': '_widget_1770184688128',
    'actual_total': '_widget_1770184688149',
    'cost_details': '_widget_1770184688372',
    'variance_root_cause': '_widget_1770362492081',
}

PROJECT_BUDGET_DETAIL_FIELDS_EN = {
    'detail_date': '_widget_1770184688515',
    'detail_item': '_widget_1770184688732',
    'detail_amount': '_widget_1770184688945',
    'detail_remark': '_widget_1770184688999',
}

PROJECT_BUDGET_REVERSE_EN = {v: k for k, v in PROJECT_BUDGET_FIELDS_EN.items()}
PROJECT_BUDGET_DETAIL_REVERSE_EN = {v: k for k, v in PROJECT_BUDGET_DETAIL_FIELDS_EN.items()}

# 发货管理表字段映射 (entry: 7f214b928a8811cfd38e6d2c)
DELIVERY_FIELDS_EN = {
    'delivery_no': '_widget_1770458498302',
    'project_name': '_widget_1770458498418',
    'delivery_date': '_widget_1770458498335',
    'order_no': '_widget_1770458498316',
    'delivery_address': '_widget_1770458498468',
    'inspection_items': '_widget_1770599794961',
    'status': '_widget_1770458499012',
    'cargo_items': '_widget_1770458498505',
    'logistics_company': '_widget_1770458498887',
    'logistics_no': '_widget_1770458498924',
    'remark': '_widget_1770458498943',
}

DELIVERY_ITEM_FIELDS_EN = {
    'product_name': '_widget_1770458498530',
    'spec_model': '_widget_1770458498597',
    'quantity': '_widget_1770458498729',
    'unit': '_widget_1770458498665',
}

DELIVERY_REVERSE_EN = {v: k for k, v in DELIVERY_FIELDS_EN.items()}
DELIVERY_ITEM_REVERSE_EN = {v: k for k, v in DELIVERY_ITEM_FIELDS_EN.items()}

# 检测项目表字段映射 (entry: 37f8492484812d6cd8781fc8)
INSPECTION_FIELDS_EN = {
    'inspection_no': '_widget_1770600279891',
    'inspection_project': '_widget_1770600279908',
}

INSPECTION_REVERSE_EN = {v: k for k, v in INSPECTION_FIELDS_EN.items()}

# 样品检测交付现场管理表字段映射 (entry: afe94bb78534c3db2ca05e97)
INSPECTION_DELIVERY_FIELDS_EN = {
    'handover_no': '_widget_1770602533864',
    'delivery_no': '_widget_1770599102686',
    'project_name': '_widget_1770602533948',
    'delivery_date': '_widget_1770602534095',
    'delivery_address': '_widget_1770602534003',
    'order_no': '_widget_1770602534022',
    'cargo_items': '_widget_1770602534119',
    'inspection_info': '_widget_1770602534585',
    'receiver_customer': '_widget_1770602535438',
    'handover_date': '_widget_1770602536184',
    'handover_status': '_widget_1770602535781',
    'abnormal_reason': '_widget_1770605979585',
    'remark': '_widget_1770602536376',
    'handover_person': '_widget_1770602535478',
}

INSPECTION_DELIVERY_CARGO_FIELDS_EN = {
    'product_name': '_widget_1770602534167',
    'spec_model': '_widget_1770602534222',
    'quantity': '_widget_1770602534279',
    'unit': '_widget_1770602534330',
}

INSPECTION_DELIVERY_INSPECTION_FIELDS_EN = {
    'inspection_project': '_widget_1770602534633',
    'inspector': '_widget_1770602534862',
    'inspection_status': '_widget_1770602534786',
    'description': '_widget_1770602535346',
}

INSPECTION_DELIVERY_REVERSE_EN = {v: k for k, v in INSPECTION_DELIVERY_FIELDS_EN.items()}
INSPECTION_DELIVERY_CARGO_REVERSE_EN = {v: k for k, v in INSPECTION_DELIVERY_CARGO_FIELDS_EN.items()}
INSPECTION_DELIVERY_INSPECTION_REVERSE_EN = {v: k for k, v in INSPECTION_DELIVERY_INSPECTION_FIELDS_EN.items()}


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
