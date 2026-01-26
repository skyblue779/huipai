# 徽派家私数字管理平台 - 完整项目文档

## 📋 项目概述

这是一个前端 Vue 3 + Element Plus + Vite、后端 Python 的全栈项目，用于管理徽派家私的项目信息和阶段配置。后端通过 Online-Office API 进行数据操作，使用字段别名映射来实现与数据库的通信。

## 🏗️ 项目结构

```
huipai/
├── frontend/
│   ├── index.html                         # Vite 入口
│   ├── package.json                       # 前端依赖与脚本
│   ├── vite.config.js                     # Vite 配置
│   ├── src/
│   │   ├── App.vue                        # 根组件
│   │   ├── main.js                        # 应用入口
│   │   ├── api/
│   │   │   └── client.js                  # API 客户端
│   │   ├── pages/
│   │   │   └── StageConfig.vue            # 项目阶段配置页面
│   │   └── styles/
│   │       └── main.css                   # 全局样式
│   └── dist/                              # 构建输出 (npm run build)
│
└── backend/
    ├── app.py                             # Flask主应用
    ├── config.py                          # 配置文件
    ├── field_mapping.py                   # 字段别名映射
    ├── requirements.txt                   # Python依赖
    ├── .env                               # 环境变量
    ├── run.bat / run.sh                   # 启动脚本
    ├── api/
    │   ├── __init__.py
    │   ├── online_office.py                # Online-Office API客户端
    │   ├── stage_config.py                # 阶段配置路由
    │   └── project.py                     # 项目路由
```

## 🚀 快速开始

### 前置要求
- Python 3.8+
- Node.js (用于前端构建与开发服务器)
- 现代浏览器

### 后端启动步骤

#### Windows:
```bash
cd backend
run.bat
```

#### Linux/Mac:
```bash
cd backend
chmod +x run.sh
./run.sh
```

#### 手动启动:
```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py
```

服务将在 `http://172.16.0.66:9989` 上运行

### 前端访问

```bash
cd frontend
npm install
npm run dev
```

访问：`http://localhost:9988`

默认后端地址为 `http://172.16.0.66:9989`。如需切换，请在 `frontend` 目录创建 `.env.local`：

```
VITE_API_BASE_URL=http://your-api-host:9989
```

## 📡 API 文档

### 基础信息
- **基础URL**: `http://172.16.0.66:9989`
- **Content-Type**: `application/json`

### 健康检查
```http
GET /health

Response:
{
  "code": 200,
  "msg": "服务正常",
  "status": "healthy"
}
```

### 阶段配置 API

#### 1. 获取阶段列表
```http
GET /api/stage/list?skip=0&limit=20

Response:
{
  "code": 200,
  "msg": "成功",
  "data": [
    {
      "阶段节点id": "xxx",
      "名称": "售前阶段",
      "父节点": null,
      "排序": 1,
      ...
    }
  ],
  "total": 5
}
```

#### 2. 获取单个阶段
```http
GET /api/stage/get/{data_id}

Response:
{
  "code": 200,
  "msg": "成功",
  "data": { ... }
}
```

#### 3. 创建阶段
```http
POST /api/stage/create

Body:
{
  "名称": "新阶段",
  "编号": "S03",
  "描述": "阶段描述",
  "排序": 3
}

Response:
{
  "code": 200,
  "msg": "创建成功",
  "data": { ... }
}
```

#### 4. 更新阶段
```http
PUT /api/stage/update/{data_id}

Body:
{
  "名称": "更新后的名称",
  "描述": "更新描述"
}

Response:
{
  "code": 200,
  "msg": "更新成功",
  "data": { ... }
}
```

#### 5. 删除阶段
```http
DELETE /api/stage/delete/{data_id}

Response:
{
  "code": 200,
  "msg": "删除成功"
}
```

### 项目 API

#### 1. 获取项目列表
```http
GET /api/project/list?skip=0&limit=20&search=项目名称

Response:
{
  "code": 200,
  "msg": "成功",
  "data": [
    {
      "项目编号": "HP-2025-001",
      "项目名称": "希尔顿酒店项目",
      "项目类型": "订单类",
      "项目状态": "进行中",
      ...
    }
  ],
  "total": 10
}
```

#### 2. 获取单个项目
```http
GET /api/project/get/{data_id}

Response:
{
  "code": 200,
  "msg": "成功",
  "data": { ... }
}
```

#### 3. 创建项目
```http
POST /api/project/create

Body:
{
  "项目编号": "HP-2025-002",
  "项目名称": "新项目",
  "项目类型": "订单类",
  "建设地点": "杭州",
  "项目状态": "进行中",
  "项目经理": "张三",
  "责任部门": "工程部"
}

Response:
{
  "code": 200,
  "msg": "创建成功",
  "data": { ... }
}
```

#### 4. 更新项目
```http
PUT /api/project/update/{data_id}

Body:
{
  "项目名称": "更新后的名称",
  "项目状态": "已完成"
}

Response:
{
  "code": 200,
  "msg": "更新成功",
  "data": { ... }
}
```

#### 5. 删除项目
```http
DELETE /api/project/delete/{data_id}

Response:
{
  "code": 200,
  "msg": "删除成功"
}
```

## 🔧 字段别名映射

### 阶段配置表字段映射
| 中文名称 | 字段别名 |
|---------|--------|
| 阶段节点id | _widget_1769130163477 |
| 名称 | _widget_1769130163517 |
| 父节点 | _widget_1769130163557 |
| 排序 | _widget_1769130163598 |

### 项目表字段映射
| 中文名称 | 字段别名 |
|---------|--------|
| 项目编号 | _widget_1769064437789 |
| 项目名称 | _widget_1769064437770 |
| 合同名称 | _widget_1769064437829 |
| 项目类型 | _widget_1769064636768 |
| 建设地点 | _widget_1769064637832 |
| 项目状态 | _widget_1769064637023 |
| 计划开工 | _widget_1769064637850 |
| 计划完工 | _widget_1769064637874 |
| 项目经理 | _widget_1769064637963 |
| 责任部门 | _widget_1769066077660 |
| 参与人员 | _widget_1769066077800 |
| 子表单 | _widget_1769131834894 |
| 项目阶段 | _widget_1769131834919 |
| 执行人 | _widget_1769131834982 |
| 计划时间 | _widget_1769131835032 |
| 实际完成 | _widget_1769131835092 |
| 状态 | _widget_1769131835157 |

## 📝 前端集成示例

### 在Vue中使用
```javascript
import api from './api/client';

// 获取阶段列表
async function loadStages() {
  try {
    const response = await api.listStages({ skip: 0, limit: 20 });
    stages.value = response.data;
  } catch (error) {
    console.error('获取数据失败:', error);
  }
}

// 创建阶段
async function handleSave() {
  try {
    await api.createStage({
      name: currentStage.value.name,
      sort_order: 1,
      project_type: selectedProjectType.value
    });
    ElMessage.success('保存成功');
  } catch (error) {
    ElMessage.error('保存失败');
  }
}
```

## 🔐 安全建议

1. **生产环境配置**:
   - 修改 `.env` 文件中的 `SECRET_KEY`
   - 设置 `DEBUG=False`
   - 配置正确的 CORS 源

2. **API认证** (可选):
   - 实现JWT或Token认证
   - 在请求头中添加认证令牌

3. **数据验证**:
   - 后端已包含基本的字段映射验证
   - 建议添加更详细的输入验证

## 🐛 故障排除

### 跨域问题
如果前端无法访问后端API，请检查：
1. 后端是否正在运行
2. 前端中的 API URL 是否正确
3. 后端的 CORS 配置是否包含前端域名

### Online-Office API 连接问题
1. 检查网络连接
2. 验证 API 密钥和应用ID
3. 检查字段别名是否正确

### 虚拟环境问题
```bash
# 重建虚拟环境
rm -rf venv  # Windows: rmdir /s venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 📚 相关文档

- [Flask 文档](https://flask.palletsprojects.com/)
- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Online-Office OpenAPI 文档](https://ahyg.online-office.net/openapi)

## 💡 开发建议

1. **后端开发**:
   - 在 `api/` 目录中添加新的路由
   - 在 `field_mapping.py` 中维护字段映射
   - 使用 `api_client` 实例进行 Online-Office API 调用

2. **前端开发**:
   - 更新 `src/api/client.js` 中的 API 方法
   - 在 Vue 组件中使用 `api` 进行数据操作
   - 实现错误处理和加载状态

3. **测试**:
   - 使用 Postman 或 curl 测试 API
   - 验证字段映射的正确性
   - 测试错误情况

## 📞 支持

如有问题，请检查：
1. 项目结构是否完整
2. 依赖是否正确安装
3. 配置文件是否正确设置
4. 网络连接是否正常

## 📄 许可证

项目所有权：徽派家私

---

**最后更新**: 2026年1月23日
**版本**: 1.0.0
