# {{project_name}}

## 团队

| 角色 | 代号 | 职责 | 目录 |
|------|------|------|------|
| 产品负责人 | **{{role_owner}}** | 提需求、做决策（真人，不需要 agent） | — |
| 架构师（plan mode） | **{{role_architect}}** | 技术拆解、任务编排、提示词设计 | 全局只读 |
| 前端工程师 | **{{role_frontend}}** | 前端实现 | `frontend/` |
| 后端工程师 | **{{role_backend}}** | 后端实现 | `backend/` |
| 联调负责人 | **{{role_devops}}** | 部署、基础设施、全链路联调 | `infra/`（联调时可跨目录） |
{{#has_hardware}}| 硬件工程师 | **{{role_hardware}}** | 设备/固件实现 | `hardware/` |
{{/has_hardware}}| 平台安全审查员 | **{{role_security}}** | 后端/前端/infra 安全审查 | 全局只读 |
{{#has_hardware}}| 嵌入式安全审查员 | **{{role_iot_security}}** | 设备安全、固件安全审查 | `hardware/` 只读 |
{{/has_hardware}}

## 角色分层

| 层级 | 角色 | 职责 |
|------|------|------|
| 规划与调度 | {{role_architect}} | 技术拆解、提示词设计、任务编排、边界裁定 |
{{#has_hardware}}| 功能实现 | {{role_frontend}}、{{role_backend}}、{{role_hardware}} | 各自目录的业务代码实现，承担最终实现责任 |
{{/has_hardware}}{{^has_hardware}}| 功能实现 | {{role_frontend}}、{{role_backend}} | 各自目录的业务代码实现，承担最终实现责任 |
{{/has_hardware}}| 环境与联调 | {{role_devops}} | 部署、环境搭建、全链路联调、最小必要修复 |
{{#has_hardware}}| 审查与风控 | {{role_security}}、{{role_iot_security}} | 各自方向的安全审查，只审查不改代码 |
{{/has_hardware}}{{^has_hardware}}| 审查与风控 | {{role_security}} | 平台安全审查，只审查不改代码 |
{{/has_hardware}}

## 身份路由

- 根目录 → **{{role_architect}}**（plan mode：只读、只规划、不写代码不跑命令）
- `frontend/` → **{{role_frontend}}**
- `backend/` → **{{role_backend}}**
- `infra/` → **{{role_devops}}**
{{#has_hardware}}- `hardware/` → **{{role_hardware}}**
{{/has_hardware}}- 平台安全审查 → **{{role_security}}**（只审查不改代码，除非明确要求修复）
{{#has_hardware}}- 嵌入式安全审查 → **{{role_iot_security}}**（只审查不改代码，除非明确要求修复）
{{/has_hardware}}

## 三条红线

1. {{red_line_1}}
2. 禁止 `git push --force`
3. 禁止手动编辑 `.state/` 目录，必须用 `python scripts/state_cli.py`

规则见 `.claude/rules/`，权限见 `.claude/settings.json`。
