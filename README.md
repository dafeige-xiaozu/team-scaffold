# team-scaffold

项目协作框架生成器 v6.0.0

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

# 自定义团队名和角色名
scaffold init --project-name "我的项目" --desc "一句话描述" \
  --team-name "星辰战队" \
  --role owner=老王 \
  --role architect=诸葛亮 \
  --role frontend=貂蝉 \
  --role backend=关羽 \
  --role devops=赵云 \
  --role security=司马懿

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
| `--team-name` | 团队名称（默认：大飞哥无敌战队） |
| `--role KEY=NAME` | 自定义角色代号，可多次使用 |
| `--server` | 服务器 IP，生成部署脚本 |
| `--hardware` | 包含硬件端目录和相关 agent |
| `--dry-run` | 只预览不写入文件 |
| `--force` | 覆盖已存在的文件 |
| `--output-dir` | 指定输出目录（默认当前目录） |

## 可自定义的角色

| 角色 key | 默认代号 | 职责 |
|----------|----------|------|
| `owner` | 大飞哥 | 产品负责人 |
| `architect` | 王重阳 | 架构师 |
| `frontend` | 黄蓉 | 前端工程师 |
| `backend` | 乔峰 | 后端工程师 |
| `devops` | 张三丰 | 联调负责人 |
| `hardware` | 杨过 | 硬件工程师（可选） |
| `security` | 一灯大师 | 平台安全审查员 |
| `iot_security` | 郭靖 | 嵌入式安全审查员（可选） |

交互模式下会询问是否自定义角色代号；非交互模式通过 `--role` 参数指定。

## 开发

```bash
pip install -e .
pytest tests/
```

## 许可证

MIT
