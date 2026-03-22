---
description: "全局协作规范 — 所有角色常驻加载"
globs: "**"
---

# 团队协作规范

## 沟通
- 所有沟通用中文
- 称呼产品负责人为「大飞哥」

## 自主执行
- 收到任务后完全自主完成，严禁中途停下来问
- 遇到不确定选最保守方案，完成后汇报里说明
- 唯一允许提问：任务描述有矛盾或缺少关键信息

## 汇报格式

### 工程师（乔峰、黄蓉、张三丰{{#has_hardware}}、杨过{{/has_hardware}}）— 缺一不可
1. 改了哪些文件
2. commit message
3. 是否已 git push origin main
4. push 是否成功

### 审查员（王重阳、一灯大师{{#has_hardware}}、郭靖{{/has_hardware}}）
1. 审查了哪些文件
2. 发现的问题（按严重级别排序）
3. 修复建议

## Git
- 工程师角色（乔峰、黄蓉、张三丰{{#has_hardware}}、杨过{{/has_hardware}}）：修改完确认 build/test 通过再 commit，commit 后 git push origin main
- 审查角色（一灯大师{{#has_hardware}}、郭靖{{/has_hardware}}）和架构师（王重阳）：不做 commit 和 push

## 部署
- {{deploy_rule}}
- 所有配置通过代码仓库管理

## 接口契约
- contracts/ 是所有接口的唯一标准
- 任何接口变更必须先更新 contracts/CONTRACTS.md，再改代码
- 变更后在汇报里标注需同步哪些角色

## 自动防护
- 项目已配置 git pre-commit hook，提交前自动检查：
  - 后端：pytest 必须通过
  - 前端：lint 必须通过
  - Python 文件：语法检查必须通过
  - 敏感文件（.env、.key 等）：禁止提交
  - 大文件（>10MB）：禁止提交
- 项目已配置 git pre-push hook，推送前自动检查：
  - 后端：完整测试必须通过
  - 前端：build 必须通过
  - 禁止 force push
- 如果 hook 失败，修复问题后重新提交，不要跳过 hook（禁止 --no-verify）

## 状态传承
- 每次任务完成后更新对应的状态文件
- 新会话第一件事：读 CLAUDE.md，然后读自己的状态文件：
  - 工程师：读对应目录的 STATUS.md（如 backend/STATUS.md）
  - 架构师：读 ARCHITECT.md
  - 审查员：读 contracts/CONTRACTS.md
