# {{project_name}} — API 接口契约

> 任何接口变更必须先更新此文件。

## 通用规范
- 用户端认证：`Authorization: Bearer {jwt_token}`
- 设备端认证：`X-Device-Token: {device_token}`（不带 Bearer）
- 响应格式：成功直接返回数据，错误 `{"detail": "中文错误信息"}`
- 时间字段：UTC ISO 8601（带 Z）

## 接口列表
（开发过程中逐步填充）
