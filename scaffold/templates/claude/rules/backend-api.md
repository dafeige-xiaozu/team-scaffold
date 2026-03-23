---
description: "后端开发规范"
globs: "backend/**"
---

# 后端开发规范

- 改完确认 pytest 无新增失败
- 改接口必须先更新 contracts/CONTRACTS.md
- 新会话先读 backend/STATUS.md
- 前端需求拒绝：「这是前端任务，请发给{{role_frontend}}」

## 数据库迁移规范

- 新增模型字段时，必须同时写 migration 脚本（ALTER TABLE ADD COLUMN）
- 不能只靠 ORM 的 create_all，它只创建新表不加新列
- migration 脚本必须是幂等的（重复执行不报错）：
  ```sql
  -- 先检查列是否存在再添加
  DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='xxx' AND column_name='new_field')
    THEN ALTER TABLE xxx ADD COLUMN new_field TEXT;
    END IF;
  END $$;
  ```

## 接口字段命名一致性

- 同一概念在所有接口中必须用同一个字段名
- 确定后写入 contracts/CONTRACTS.md，前后端共同遵守
- 常见踩坑：device_count vs total_devices、line_name vs name、alert_type vs type

## 适用角色
本规则适用于{{role_backend}}（后端工程师）。
{{role_devops}}（联调负责人）为联调目的修改 backend/ 文件时，遵循{{role_devops}} agent 定义中的跨目录修改权限，不受本规则的"拒绝"条款约束。
