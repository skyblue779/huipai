# 徽派家私项目测试与 AI 结合落地包

生成日期：2026-03-27

本套内容基于当前仓库实际模块生成，覆盖前端页面、后端 API、手工测试、回归测试、测试报告和 AI 提示词。

## 文档清单

- [landing-plan.md](./landing-plan.md)：项目级测试与 AI 结合落地方案
- [test-cases.md](./test-cases.md)：按模块拆分的测试用例集
- [test-report-template.md](./test-report-template.md)：测试报告模板和项目示例
- [ai-prompts.md](./ai-prompts.md)：适配本项目的 AI 提示词模板

## 当前项目范围

| 领域 | 页面/路由 | 关键接口 | 首批测试重点 |
| --- | --- | --- | --- |
| 工作台 | `/workbench` | 聚合预算、交付、进度数据 | 汇总卡片准确性、预警消息、角色切换 |
| 阶段配置 | `/stage-config` | `/api/stage/*`、`/api/project-type/list` | 树节点增删改、层级限制、长名称展示 |
| 成本阶段配置 | `/project-cost-config` | `/api/cost-stage/*`、`/api/cost-type/list` | 预算标准、树节点操作、删除限制 |
| 项目预算管理 | `/project-budget-management` | `/api/project-budget/*` | 成本项增删改、排序重排、金额显示、预算执行率 |
| 项目进度管理 | `/project-progress` | `/api/progress/*`、`/api/project/list-summary` | 节点新增/编辑/删除、批次同步、执行人数据 |
| 项目执行 | `/project-execution` | `/api/progress/*`、`/api/user/*` | 当前用户执行阶段过滤、超期处理 |
| 发货管理 | `/delivery-management` | `/api/delivery/*` | 发货单创建、附件、状态流转 |
| 检测交付管理 | `/inspection-delivery-management`、`/inspection-delivery-mobile` | `/api/inspection-delivery/*`、`/api/inspection/list` | 交付状态更新、异常回填、移动端填报 |
| 看板分析 | `/overall-budget-dashboard`、`/project-control-dashboard` | `/api/project-budget/list`、`/api/progress/list` | 指标聚合、图表数据一致性、超支识别 |

## 这套内容怎么用

1. 需求评审时先看 [landing-plan.md](./landing-plan.md)，确定当前版本要测哪些模块。
2. 提测前从 [test-cases.md](./test-cases.md) 里勾选对应模块用例，补充版本特有场景。
3. 执行测试时保留接口返回、截图、控制台日志，交给 [ai-prompts.md](./ai-prompts.md) 里的提示词做归因和汇总。
4. 版本结束后按 [test-report-template.md](./test-report-template.md) 出日报、周报或版本报告。

## 建议的首批落地顺序

1. 先从项目预算管理开始，因为该模块计算、汇总、排序、金额展示最复杂，最容易出线上口径问题。
2. 第二批落到项目进度管理和项目执行，因为这两个模块有节点重排、用户过滤和批次同步。
3. 第三批落到发货与检测交付，因为它涉及跨模块状态回填和移动端填报。
4. 最后把工作台和各类看板纳入回归最小集，作为全链路验收出口。

## 推荐的测试资产目录

建议后续在仓库中补齐以下目录：

```text
docs/qa-ai/                  # 测试方法、模板、提示词
tests/manual/                # 手工测试用例和执行记录
tests/reports/               # 日报、周报、版本报告
tests/fixtures/              # 导入文件、截图、接口样例
tests/regression/            # 回归范围清单
```

## 当前项目最值得先让 AI 介入的点

- 根据 `frontend/src/pages/*.vue` 和 `backend/api/*.py` 变更自动生成回归范围。
- 根据预算、进度、交付模块的失败日志自动生成缺陷草稿。
- 根据测试结果自动汇总版本报告和风险清单。
- 根据最近修复过的问题，自动补回归用例并沉淀进知识库。
