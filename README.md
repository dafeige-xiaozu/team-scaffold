# team-scaffold

大飞哥无敌战队 -- 项目协作框架生成器 v5.0.0

一键生成多角色协作项目的完整骨架：CLAUDE.md、agents、hooks、rules、skills、前后端代码、基础设施配置、契约文档、状态管理等。

## 安装

```bash
pip install -e .
```

## 用法

```bash
# 交互模式
cd ~/Projects/新项目目录
scaffold init

# 非交互模式
scaffold init --project-name "我的项目" --desc "一句话描述"

# 预览不写入
scaffold init --dry-run --project-name "我的项目" --desc "一句话描述"

# 覆盖已有文件
scaffold init --force --project-name "我的项目" --desc "一句话描述"

# 包含硬件端 + 指定服务器
scaffold init --project-name "我的项目" --desc "一句话描述" --hardware --server 10.0.1.100

# 指定输出目录
scaffold init --project-name "我的项目" --desc "一句话描述" --output-dir /tmp/my-project

# 查看版本
scaffold version
```

## 生成的项目结构

```
项目根目录/
  CLAUDE.md              # 团队协作主文件
  ARCHITECT.md           # 架构师状态
  DECISIONS.md           # 决策记录说明
  start.sh               # 启动角色的快捷脚本
  .claude/
    settings.json        # 权限和 hooks 配置
    agents/              # 角色定义（架构师、前端、后端、运维等）
    hooks/               # 会话启动、危险命令检查、文件保护等
    rules/               # 团队规范、踩坑记录、角色规则
    skills/              # 技能：任务分配、决策管理、状态查看等
  backend/               # 后端骨架（FastAPI + SQLAlchemy + Celery）
  frontend/              # 前端骨架（Next.js + TypeScript + Tailwind）
  infra/                 # 基础设施（Docker Compose + Nginx + 部署脚本）
  hardware/              # 硬件端骨架（可选，--hardware 启用）
  contracts/             # 接口契约文档
  scripts/               # 工具脚本（状态管理 CLI 等）
  .state/                # 状态存储（决策记录等）
  .githooks/             # Git hooks（pre-commit、pre-push、commit-msg）
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--project-name` | 项目名称（中文），跳过交互 |
| `--desc` | 项目描述（一句话），跳过交互 |
| `--server` | 服务器 IP，生成部署脚本 |
| `--hardware` | 包含硬件端目录和相关 agent |
| `--dry-run` | 只预览不写入文件 |
| `--force` | 覆盖已存在的文件 |
| `--output-dir` | 指定输出目录（默认当前目录） |

## 角色体系

| 角色 | 代号 | 职责 |
|------|------|------|
| 产品负责人 | 大飞哥 | 提需求、做决策 |
| 架构师 | 王重阳 | 技术拆解、任务编排 |
| 前端工程师 | 黄蓉 | frontend/ 开发 |
| 后端工程师 | 乔峰 | backend/ 开发 |
| 联调负责人 | 张三丰 | infra/ + 全链路联调 |
| 硬件工程师 | 杨过 | hardware/ 开发（可选） |
| 平台安全审查员 | 一灯大师 | 安全审查 |
| 嵌入式安全审查员 | 郭靖 | 设备安全审查（可选） |

## 开发

```bash
pip install -e .
pytest tests/
```

## 许可证

MIT
