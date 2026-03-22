---
description: "前端开发规范"
globs: "frontend/**"
---

# 前端开发规范

- 改完确认 npm run build 通过
- API 调用统一封装在 lib/api.ts，禁止裸 fetch
- 所有数据访问 data?.field ?? 默认值
- 页面必须有 loading/error/empty 三个状态
- 禁止 TypeScript ! 非空断言
- 新会话先读 frontend/STATUS.md
- 后端需求拒绝：「这是后端任务，请发给乔峰」

## 适用角色
本规则适用于黄蓉（前端工程师）。
张三丰（联调负责人）为联调目的修改 frontend/ 文件时，遵循张三丰 agent 定义中的跨目录修改权限，不受本规则的"拒绝"条款约束。
