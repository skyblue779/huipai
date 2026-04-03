# 徽派家私项目 AI 提示词模板

以下提示词都按当前项目模块设计，可直接复制给 AI 使用。

## 1. 变更转回归范围

```text
你现在是该项目的测试分析助手。请基于以下变更文件，输出：
1. 受影响模块
2. 必测功能点
3. 发布前最小回归集
4. 潜在跨模块影响

项目背景：
- 前端为 Vue 3 + Element Plus
- 后端为 Flask
- 核心模块包括阶段配置、成本阶段配置、项目预算管理、项目进度管理、项目执行、发货管理、检测交付管理、工作台和看板

请重点关注以下文件：
- frontend/src/pages/StageConfig.vue
- frontend/src/pages/ProjectCostConfig.vue
- frontend/src/pages/ProjectBudgetManagement.vue
- frontend/src/pages/ProjectProgressManagement.vue
- backend/api/project_budget.py
- backend/api/project_progress.py
- backend/api/inspection_delivery.py

变更文件：
{{git diff 或文件列表}}
```

## 2. 需求转测试点

```text
请基于以下需求，为徽派家私项目生成测试点。

输出要求：
- 按模块分组
- 每条测试点包含：场景、前置条件、关键步骤、预期结果、优先级
- 重点补充边界值、异常流、权限流、排序重排、金额展示和跨模块联动

项目模块：
- 阶段配置 /stage-config
- 成本阶段配置 /project-cost-config
- 项目预算管理 /project-budget-management
- 项目进度管理 /project-progress
- 项目执行 /project-execution
- 发货管理 /delivery-management
- 检测交付管理 /inspection-delivery-management
- 检测交付移动端 /inspection-delivery-mobile
- 工作台 /workbench
- 整体预算看板 /overall-budget-dashboard
- 项目管控看板 /project-control-dashboard

需求内容：
{{需求描述}}
```

## 3. 失败日志转缺陷草稿

```text
请根据以下测试失败证据，为该项目生成一份缺陷单草稿。

输出格式：
- 缺陷标题
- 模块
- 严重级别
- 复现步骤
- 实际结果
- 预期结果
- 疑似根因
- 影响范围
- 建议回归范围

项目背景：
- 预算管理存在金额汇总和排序重排逻辑
- 进度管理存在批次和节点序号逻辑
- 检测交付存在交付异常回填发货状态的联动逻辑

失败证据：
- 页面：
{{页面名称}}
- 操作步骤：
{{步骤}}
- 接口返回：
{{接口响应}}
- 控制台日志：
{{日志}}
- 截图说明：
{{截图描述}}
```

## 4. 测试报告生成

```text
请根据以下执行结果，为徽派家私项目生成测试报告。

输出结构：
1. 基本信息
2. 本次变更范围
3. 执行范围统计
4. 缺陷明细
5. 风险与遗留问题
6. 测试结论

要求：
- 结论简洁，不写空话
- 风险项聚焦预算口径、节点排序、交付状态联动、移动端同步
- 如果存在跨模块影响，要明确指出受影响页面和接口

执行结果：
{{测试结果}}
```

## 5. 用例去重和补缺

```text
下面是当前项目的测试用例列表。请执行两件事：
1. 找出重复或描述重叠的用例
2. 找出缺失的关键测试点

输出格式：
- 重复用例
- 建议合并后的标准用例
- 缺失测试点
- 建议新增用例编号

重点检查：
- 阶段树层级限制
- 长文本操作区可点击性
- 预算金额两位小数显示
- 成本项编辑默认值回填
- 成本项/节点删除后的重排
- 检测交付异常后的发货状态回填

现有用例：
{{用例列表}}
```

## 6. 发布前冒烟检查

```text
请基于该项目当前版本，生成一份发布前 30 分钟内可执行完的冒烟检查清单。

要求：
- 只保留最高风险场景
- 按模块分组
- 每条都给出预期结果
- 优先覆盖预算管理、阶段配置、进度管理、检测交付、工作台

当前版本变更：
{{变更说明}}
```

## 7. 代码变更辅助测试分析

```text
请阅读以下代码 diff，判断：
1. 这是 UI 变更、业务规则变更、接口变更，还是格式化变更
2. 哪些已有测试用例必须重跑
3. 是否需要新增回归用例
4. 最可能引发线上问题的点

项目特征：
- 树节点操作集中在 StageConfig 和 ProjectCostConfig
- 金额计算和汇总集中在 ProjectBudgetManagement
- 节点批次和执行人逻辑集中在 ProjectProgressManagement 和 ProjectExecution
- 交付异常联动集中在 inspection_delivery.py

代码 diff：
{{git diff}}
```
