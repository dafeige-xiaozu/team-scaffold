#!/usr/bin/env python3
"""
大飞哥无敌战队 — 项目协作框架初始化脚本 v4.1

生成完整的 Claude Code 项目协作框架：
  agents / hooks / rules / skills / state / contracts / deploy
  + 后端骨架（FastAPI）+ 前端骨架（Next.js）

纯 Python 标准库，无额外依赖。

用法：
    cd ~/Projects/新项目目录
    python ~/Projects/team-tools/setup_project.py
    python ~/Projects/team-tools/setup_project.py --dry-run
    python ~/Projects/team-tools/setup_project.py --project-name "我的项目" --desc "一句话描述"
    python ~/Projects/team-tools/setup_project.py --force  # 覆盖已有文件
"""
import argparse
import json
import os
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# 交互收集
# ═══════════════════════════════════════════════════════════════════════════════

def ask(prompt: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    val = input(f"  {prompt}{hint}: ").strip()
    return val or default


def collect_info(args) -> dict:
    info = {
        "project_name": args.project_name or "",
        "project_desc": args.desc or "",
        "frontend_stack": "Next.js + TypeScript + Tailwind CSS + shadcn/ui",
        "backend_stack": "Python 3.11 + FastAPI + SQLAlchemy + Celery + Redis",
        "database": "PostgreSQL",
        "server_ip": "",
        "has_hardware": False,
        "dir_name": Path.cwd().name,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }

    if args.project_name and args.desc:
        # Non-interactive mode
        info["server_ip"] = args.server or ""
        info["has_hardware"] = args.hardware
        return info

    print()
    print("=" * 60)
    print("  大飞哥无敌战队 — 项目协作框架初始化 v4.1")
    print("=" * 60)
    print()

    info["project_name"] = ask("项目名称（中文）", info["project_name"])
    while not info["project_name"]:
        print("  ⚠️  不能为空")
        info["project_name"] = ask("项目名称（中文）")

    info["project_desc"] = ask("项目简述（一句话）", info["project_desc"])
    while not info["project_desc"]:
        print("  ⚠️  不能为空")
        info["project_desc"] = ask("项目简述（一句话）")

    print("\n  ── 技术栈（回车用默认）──")
    info["frontend_stack"] = ask("前端", info["frontend_stack"])
    info["backend_stack"] = ask("后端", info["backend_stack"])
    info["database"] = ask("数据库", info["database"])

    print("\n  ── 基础设施 ──")
    info["server_ip"] = ask("服务器 IP（可跳过）")
    hw = ask("是否有独立硬件端仓库", "N")
    info["has_hardware"] = hw.lower() in ("y", "yes")

    return info


# ═══════════════════════════════════════════════════════════════════════════════
# 文件生成器（按目录分组）
# ═══════════════════════════════════════════════════════════════════════════════

def _build_root_docs(f, info):
    """CLAUDE.md、RULES.md、DECISIONS.md 等根目录文档。"""
    _add = lambda p, c, x=False: f.__setitem__(p, (c.strip() + "\n", x))

    n = info["project_name"]

    _add("CLAUDE.md", f"""# {n}

## 团队

| 角色 | 代号 | 职责 | 目录 |
|------|------|------|------|
| 产品负责人 | **大飞哥** | 提需求、做决策 | — |
| 架构师 | **王重阳** | 统筹调度、出提示词 | 根目录 |
| 前端 | **黄蓉** | 前端开发 | `frontend/` |
| 后端 | **乔峰** | 后端开发 | `backend/` |
| 运维 | **张三丰** | 部署、Docker、联调 | `infra/` |
| 硬件 | **杨过** | 边缘设备 | `firmware/` |

## 身份路由

- 根目录 → **王重阳**（只讨论方案出提示词，不写代码不跑命令）
- `frontend/` → **黄蓉**
- `backend/` → **乔峰**
- `infra/` → **张三丰**
- `firmware/` → **杨过**

## 三条红线

1. 禁止直接改服务器文件，所有部署走 `infra/deploy/deploy.sh`
2. 禁止 `git push --force`
3. 禁止手动编辑 `.state/` 目录，必须用 `python scripts/state_cli.py`

详细规则见 `.claude/rules/`，权限见 `.claude/settings.json`。
""")

    _add("RULES.md", """# 全员工作规则

> 所有工程师必须遵守。

## 自主执行
- 收到任务后完全自主完成，严禁中途停下来问大飞哥
- 遇到不确定选最保守方案，完成后在汇报里说明
- 唯一允许提问：任务描述有矛盾或缺少关键信息

## 汇报格式（缺一不可）
1. 改了哪些文件
2. commit message
3. 是否已 git push origin main
4. push 是否成功

## Git
- 每次 commit 后自动 git push origin main
- 修改完确认 build/test 通过再 commit

## 状态传承
- 每次任务完成后更新 STATUS.md
- 新会话第一件事：读 CLAUDE.md + STATUS.md

## 安全
- 所有沟通用中文
- 部署走 deploy.sh，禁止直接改服务器文件
- 删文件必须先移到 ~/.Trash/，汇报里列出路径
""")

    _add("DECISIONS.md", """# 已决策事项

> 已确认不再重复讨论。如需变更请明确说明。
> 使用 /decision 记录新决策。

（决策记录在 .state/decisions.json，此文件仅做人类快速参考）
""")

    _add("ARCHITECT.md", """# ARCHITECT.md — 王重阳运行状态

> 新会话说：「读 CLAUDE.md 和 ARCHITECT.md，继续开发」

## 踩过的坑
（格式：坑 → 解决方案）

## 当前进度
### 已完成
（待填写）

### 待做
| 优先级 | 事项 |
|--------|------|
| 🔴 高 | |
| 🟡 中 | |
| ⚪ 低 | |
""")

    _add("SESSION.md", """# 会话任务单

> 新会话说：「读 SESSION.md，继续开发」

## 本次目标
（每次开始前填写）

## 上次遗留
（从 ARCHITECT.md 搬过来）

## 本次不做
（防止跑偏）
""")

    _add(".scaffold-version", f"v4.1\ngenerated: {info['date']}\n")


def _build_claude_config(f, info):
    """.claude/ 下的 settings、agents、hooks、rules、skills。"""
    _add = lambda p, c, x=False: f.__setitem__(p, (c.strip() + "\n", x))

    n = info["project_name"]

    # ── .claude/settings.json ──
    settings = {
        "permissions": {
            "allow": [
                "Bash(python scripts/state_cli.py *)",
                "Bash(pip freeze *)",
                "Bash(npm run lint)",
                "Bash(npm run test *)",
                "Bash(pytest *)",
            ],
            "deny": [
                "Edit(./.state/**)",
                "Write(./.state/**)",
                "Bash(rm -rf /)",
                "Bash(rm -rf .)",
                "Bash(rm -rf ~)",
                "Bash(git push --force *)",
            ],
        },
        "hooks": {
            "SessionStart": [
                {
                    "matcher": "startup|resume|compact|clear",
                    "hooks": [{"type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/on-session-start.sh"}],
                }
            ],
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [{"type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-dangerous-cmd.sh"}],
                },
                {
                    "matcher": "Edit|Write",
                    "hooks": [{"type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/guard-protected-files.sh"}],
                },
            ],
            "PostToolUse": [
                {
                    "matcher": "Write|Edit",
                    "hooks": [{"type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/notify-contract-change.sh"}],
                }
            ],
        },
    }
    _add(".claude/settings.json", json.dumps(settings, indent=2, ensure_ascii=False))

    # ── .claude/agents/ ──
    _add(".claude/agents/boss.md", f"""---
name: "大飞哥"
description: "产品负责人 — 提需求、做决策、分发任务"
---

# 大飞哥（产品负责人）

你是 {n} 的产品负责人，团队叫你「大飞哥」。

## 职责
- 提需求、做决策、验收成果
- 给各工程师分发任务（复制提示词到对应窗口）
- 管理项目优先级

## 常用命令
- `/team-status` — 查看全员状态
- `/decision` — 记录新决策
""")

    _add(".claude/agents/architect.md", f"""---
name: "王重阳"
description: "架构师 — 统筹调度、出提示词，不写代码不跑命令"
---

# 王重阳（架构师）

你是 {n} 的架构师。**不写任何业务代码，不执行任何命令**。

## 工作方式
讨论方案 → 拆解任务 → 输出提示词 → 大飞哥分发。

## 提示词输出规范
每条提示词包含：
1. 任务需要读的文件
2. 任务描述和步骤
3. 验证标准
4. 末尾加：「注意：全程自主完成，不要中途停下来问我。」

## 严禁
- 不 spawn 子 Agent
- 不执行 Bash 命令
- 不读业务代码文件
- 不跑 build/test/deploy

## 进度跟踪
用 ARCHITECT.md 记录。上下文过长时提示大飞哥开新会话。
""")

    _add(".claude/agents/backend.md", f"""---
name: "乔峰"
description: "后端工程师 — 负责 backend/ 目录"
---

# 乔峰（后端工程师）

你是 {n} 的后端工程师。豪迈直率、干脆利落。

## 技术栈
{info['backend_stack']} + {info['database']}

## 职责
- backend/ 目录下所有代码
- API 开发、数据库、异步任务

## 边界
- 前端需求拒绝：「这是前端任务，请发给黄蓉」
- 运维需求拒绝：「这是运维任务，请发给张三丰」

## 特有规则
- 修改完确认 pytest 无新增失败
- 改接口必须先更新 contracts/CONTRACTS.md
""")

    _add(".claude/agents/frontend.md", f"""---
name: "黄蓉"
description: "前端工程师 — 负责 frontend/ 目录"
---

# 黄蓉（前端工程师）

你是 {n} 的前端工程师。冰雪聪明、古灵精怪。

## 技术栈
{info['frontend_stack']}

## 职责
- frontend/ 目录下所有代码
- 页面、组件、交互

## 边界
- 后端需求拒绝：「这是后端任务，请发给乔峰」

## 特有规则
- 修改完确认 npm run build 通过
- API 调用统一封装，禁止裸 fetch
- 所有数据访问 data?.field ?? 默认值
""")

    _add(".claude/agents/hardware.md", f"""---
name: "杨过"
description: "硬件工程师 — 负责 firmware/ 目录"
---

# 杨过（硬件工程师）

你是 {n} 的硬件工程师。亦正亦邪、做事果断。

## 职责
- firmware/ 目录下所有代码
- 边缘设备、嵌入式推理

## 边界
- 平台前后端需求拒绝：「这是平台任务，发错对象了」

## 特有规则
- 修改完确认 python -m py_compile 通过
- 接口契约以 contracts/CONTRACTS.md 为准
""")

    _add(".claude/agents/devops.md", f"""---
name: "张三丰"
description: "运维工程师 — 负责 infra/ 目录"
---

# 张三丰（运维工程师）

你是 {n} 的运维工程师。沉稳老练。

## 技术栈
Docker Compose + Nginx + Bash

## 职责
- infra/ 目录下所有配置
- 部署脚本、Docker、Nginx
- 部署后联调验证

## 边界
- 不改 frontend/ 或 backend/ 业务代码
- 发现业务 bug 汇报给对应工程师

## 特有规则
- 部署前确认 docker compose build 成功
- 所有部署走 deploy.sh
""")

    # ── .claude/hooks/ ──
    _add(".claude/hooks/on-session-start.sh", r"""#!/usr/bin/env bash
set -euo pipefail

# P2-8: python3 fallback — 没有 python3 不阻塞会话
command -v python3 >/dev/null 2>&1 || { echo "python3 not found, skipping hook"; exit 0; }

# Read agent_type from stdin JSON
AGENT_TYPE=$(python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('agent_type', 'unknown'))
except: print('unknown')
")

STATUS_FILE=".state/status/${AGENT_TYPE}.json"

echo "=== 会话启动 ==="
echo "角色: ${AGENT_TYPE}"

if [ -f "$STATUS_FILE" ]; then
    python3 -c "
import json
with open('${STATUS_FILE}') as f:
    s = json.load(f)
print(f\"上次任务: {s.get('task', '无')}\")
print(f\"进度: {s.get('progress', '未知')}\")
print(f\"更新时间: {s.get('updated_at', '未知')}\")
"
else
    echo "首次启动，无历史状态"
fi

echo "=================="
""", True)

    _add(".claude/hooks/check-dangerous-cmd.sh", r"""#!/usr/bin/env bash
set -euo pipefail

# P2-8: python3 fallback
command -v python3 >/dev/null 2>&1 || { echo "python3 not found, skipping hook"; exit 0; }

# Read command from stdin JSON
CMD=$(python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('input', {}).get('command', ''))
except: print('')
")

# Dangerous patterns (block)
case "$CMD" in
    *"rm -rf /"*|*"rm -rf ."*|*"rm -rf ~"*)
        echo "BLOCKED: 危险的 rm -rf 命令" >&2
        exit 2
        ;;
    *"DROP DATABASE"*|*"drop database"*|*"DROP TABLE"*|*"drop table"*|*"TRUNCATE"*|*"truncate"*)
        echo "BLOCKED: 危险的数据库操作" >&2
        exit 2
        ;;
esac

# Safe cleanup patterns (allow)
# rm -rf node_modules, __pycache__, .next, dist, build, /tmp/ — all OK
exit 0
""", True)

    # P0-3 fix: 去掉 */requirements.txt 通配
    # P2-11: 彻底去掉 requirements.txt 拦截规则（根目录空文件已删除）
    _add(".claude/hooks/guard-protected-files.sh", r"""#!/usr/bin/env bash
set -euo pipefail

# P2-8: python3 fallback
command -v python3 >/dev/null 2>&1 || { echo "python3 not found, skipping hook"; exit 0; }

# Read file_path from stdin JSON
FILE_PATH=$(python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('input', {}).get('file_path', ''))
except: print('')
")

case "$FILE_PATH" in
    .state/*|./.state/*)
        echo "BLOCKED: .state/ 目录禁止直接编辑。请用：python scripts/state_cli.py status-set <role> --task '...' --progress '...'" >&2
        exit 2
        ;;
esac

exit 0
""", True)

    _add(".claude/hooks/notify-contract-change.sh", r"""#!/usr/bin/env bash
set -euo pipefail

# P2-8: python3 fallback
command -v python3 >/dev/null 2>&1 || { echo "python3 not found, skipping hook"; exit 0; }

FILE_PATH=$(python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('input', {}).get('file_path', ''))
except: print('')
")

case "$FILE_PATH" in
    contracts/*|./contracts/*)
        echo '{"additionalContext": "⚠️ 契约文件已变更，请在任务汇报里标注需同步哪些角色（杨过/黄蓉/乔峰）"}'
        ;;
esac

exit 0
""", True)

    # ── .claude/rules/ ──
    _add(".claude/rules/00-team-protocol.md", """---
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

## 汇报格式（缺一不可）
1. 改了哪些文件
2. commit message
3. 是否已 git push origin main
4. push 是否成功

## Git
- 每次 commit 后自动 git push origin main
- 修改完确认 build/test 通过再 commit

## 部署
- 所有部署走 infra/deploy/deploy.sh
- 所有配置通过代码仓库管理

## 状态传承
- 每次任务完成后更新 STATUS.md
- 新会话第一件事：读 CLAUDE.md + STATUS.md
""")

    _add(".claude/rules/07-pitfall-registry.md", """---
description: "踩坑 Top 10 — 全局常驻加载，避免重复踩坑"
globs: "**"
---

# 踩坑 Top 10

1. **deploy.sh 禁止 --no-cache** — 3 分钟变 22 分钟
2. **requirements.txt 禁止手动编辑** — 用 pip freeze 生成
3. **presigned URL 有效期至少 6 小时** — 大文件+排队会超时
4. **Celery soft_time_limit 至少 7200s** — 大文件处理需要时间
5. **docker-compose 必须 stop_grace_period** — 防止强杀丢任务
6. **API 时间一律 UTC+Z** — 前端转本地时间
7. **部署后必须 md5 校验** — 确认文件同步一致
8. **pip/npm 配国内镜像** — pip.conf + .npmrc
9. **.env 必须有 .env.example** — 新人能快速配置
10. **改接口必须先更新契约文档** — contracts/CONTRACTS.md
""")

    _add(".claude/rules/backend-api.md", """---
description: "后端开发规范"
globs: "backend/**"
---

# 后端开发规范

- 改完确认 pytest 无新增失败
- 改接口必须先更新 contracts/CONTRACTS.md
- 新会话先读 backend/STATUS.md
- 前端需求拒绝：「这是前端任务，请发给黄蓉」
""")

    _add(".claude/rules/frontend-ui.md", """---
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
""")

    _add(".claude/rules/hardware-protocol.md", """---
description: "硬件端开发规范"
globs: "firmware/**"
---

# 硬件端开发规范

- 改完确认 python -m py_compile 通过
- 接口契约以 contracts/CONTRACTS.md 为准
- 新会话先读 firmware/STATUS.md
""")

    _add(".claude/rules/infra-deploy.md", """---
description: "运维部署规范"
globs: "infra/**"
---

# 运维部署规范

- 部署前确认 docker compose build 成功
- 所有部署走 infra/deploy/deploy.sh
- 不修改 frontend/ 或 backend/ 业务代码
- 发现业务 bug 汇报给对应工程师
- 新会话先读 infra/STATUS.md
""")

    _add(".claude/rules/api-contracts.md", """---
description: "接口契约变更规范"
globs: "contracts/**"
---

# 接口契约规范

- contracts/ 是所有仓库的唯一接口标准
- 任何接口变更必须先更新此处，再改代码
- 变更后在汇报里标注需同步哪些角色
""")

    # ── .claude/skills/ ──
    _add(".claude/skills/team-status/SKILL.md", """---
name: "team-status"
description: "查看全员工作状态"
disable-model-invocation: true
---

# /team-status

查看全员当前工作状态。

## 执行
```bash
python scripts/state_cli.py team-status
```
""")

    _add(".claude/skills/decision/SKILL.md", """---
name: "decision"
description: "记录新决策"
disable-model-invocation: true
---

# /decision

记录一条新的架构/技术决策。

## 执行
用户提供标题和提议人后执行：
```bash
python scripts/state_cli.py decision-propose --title "决策标题" --proposed-by "角色名"
```
""")

    _add(".claude/skills/resume-role/SKILL.md", """---
name: "resume-role"
description: "恢复角色上下文"
disable-model-invocation: true
---

# /resume-role

读取当前角色的状态文件恢复上下文。

## 执行
```bash
python scripts/state_cli.py team-status
```
然后读取对应目录的 STATUS.md。
""")


def _build_state(f, info):
    """.state/ 目录。"""
    _add = lambda p, c, x=False: f.__setitem__(p, (c.strip() + "\n", x))

    now = datetime.now(timezone.utc).isoformat()
    decisions_data = [
        {
            "id": "DEC-001",
            "title": "时间统一 UTC ISO 8601（Z 结尾），前端转本地时间",
            "status": "locked",
            "proposed_by": "王重阳",
            "proposed_at": now,
            "locked_at": now,
        },
        {
            "id": "DEC-002",
            "title": "pip/npm 统一国内镜像源（清华/淘宝）",
            "status": "locked",
            "proposed_by": "王重阳",
            "proposed_at": now,
            "locked_at": now,
        },
    ]
    _add(".state/decisions.json", json.dumps(decisions_data, indent=2, ensure_ascii=False))
    _add(".state/changelog.md", f"# Changelog\n\n## {info['date']}\n- 项目初始化\n")
    _add(".state/status/.gitkeep", "")


def _build_contracts(f, info):
    """contracts/ 目录。"""
    _add = lambda p, c, x=False: f.__setitem__(p, (c.strip() + "\n", x))

    n = info["project_name"]

    _add("contracts/CONTRACTS.md", f"""# {n} — API 接口契约

> 任何接口变更必须先更新此文件。

## 通用规范
- 用户端认证：`Authorization: Bearer {{jwt_token}}`
- 设备端认证：`X-Device-Token: {{device_token}}`（不带 Bearer）
- 响应格式：成功直接返回数据，错误 `{{"detail": "中文错误信息"}}`
- 时间字段：UTC ISO 8601（带 Z）

## 接口列表
（开发过程中逐步填充）
""")

    _add("contracts/data-models.yaml", f"""# {n} — 数据模型定义
# 开发过程中逐步填充

# models: []
""")

    _add("contracts/error-codes.yaml", f"""# {n} — 错误码定义
# 开发过程中逐步填充

# errors: []
""")


def _build_backend(f, info):
    """backend/ 骨架。"""
    _add = lambda p, c, x=False: f.__setitem__(p, (c.strip() + "\n", x))

    n = info["project_name"]

    # P1-9: backend/__init__.py
    _add("backend/__init__.py", "")

    _add("backend/main.py", f"""\"\"\"
{n} — FastAPI 入口
\"\"\"
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="{n}", version="0.1.0")

# CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {{"status": "ok"}}
""")

    # P0-2: worker.py — Celery 骨架
    _add("backend/worker.py", """import os
from celery import Celery

broker = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app = Celery("worker", broker=broker)
app.config_from_object({
    "task_soft_time_limit": 7200,  # 踩坑清单第 4 条
    "task_time_limit": 7500,
})


@app.task
def example_task(name: str):
    return f"Hello {name}"
""")

    # P1-8: models.py — SQLAlchemy 骨架
    _add("backend/models.py", """from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# 示例模型（按需修改）
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     name = Column(String(100), nullable=False)
#     created_at = Column(DateTime, server_default=func.now())
""")

    _add("backend/requirements.txt", """fastapi>=0.110,<1.0
uvicorn[standard]>=0.27,<1.0
sqlalchemy>=2.0,<3.0
alembic>=1.13,<2.0
celery[redis]>=5.3,<6.0
redis>=5.0,<6.0
psycopg2-binary>=2.9,<3.0
python-dotenv>=1.0,<2.0
pytest>=8.0,<9.0
httpx>=0.27,<1.0
""")

    # P0-1 fix: Dockerfile 使用方案 B — context 为项目根目录，COPY 路径明确指向 backend/
    _add("backend/Dockerfile", """FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

# 拷贝国内镜像配置
COPY pip.conf /etc/pip.conf

# 只拷贝 backend 的依赖文件
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 只拷贝 backend 代码（不会包含 frontend/、.git/ 等）
COPY backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""")

    _add("backend/alembic.ini", """[alembic]
script_location = alembic
sqlalchemy.url = sqlite:///./dev.db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
""")

    # P1-8 fix: alembic env.py 引入 models.Base
    _add("backend/alembic/env.py", """import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 从环境变量覆盖 sqlalchemy.url
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

from models import Base
target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
""")

    _add("backend/alembic/versions/.gitkeep", "")

    _add("backend/alembic/script.py.mako", """\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
\"\"\"
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
""")

    _add("backend/pyproject.toml", """[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
asyncio_mode = "auto"
""")

    _add("backend/conftest.py", """import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    \"\"\"FastAPI 测试客户端。\"\"\"
    with TestClient(app) as c:
        yield c
""")

    # P1-10: backend/tests/__init__.py
    _add("backend/tests/__init__.py", "")

    _add("backend/tests/test_health.py", """def test_health(client):
    resp = client.get(\"/health\")
    assert resp.status_code == 200
    assert resp.json()[\"status\"] == \"ok\"
""")


def _build_frontend(f, info):
    """frontend/ 骨架。"""
    _add = lambda p, c, x=False: f.__setitem__(p, (c.strip() + "\n", x))

    n = info["project_name"]
    d = info["dir_name"]

    _add("frontend/package.json", json.dumps({
        "name": d,
        "version": "0.1.0",
        "private": True,
        "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
            "lint": "next lint",
            "test": "echo \"no tests yet\" && exit 0",
        },
        "dependencies": {
            "next": "^14",
            "react": "^18",
            "react-dom": "^18",
        },
        "devDependencies": {
            "@types/node": "^20",
            "@types/react": "^18",
            "@types/react-dom": "^18",
            "typescript": "^5",
            "tailwindcss": "^3",
            "postcss": "^8",
            "autoprefixer": "^10",
        },
    }, indent=2, ensure_ascii=False))

    _add("frontend/tsconfig.json", json.dumps({
        "compilerOptions": {
            "target": "es5",
            "lib": ["dom", "dom.iterable", "esnext"],
            "allowJs": True,
            "skipLibCheck": True,
            "strict": True,
            "noEmit": True,
            "esModuleInterop": True,
            "module": "esnext",
            "moduleResolution": "bundler",
            "resolveJsonModule": True,
            "isolatedModules": True,
            "jsx": "preserve",
            "incremental": True,
            "plugins": [{"name": "next"}],
            "paths": {"@/*": ["./src/*"]},
        },
        "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
        "exclude": ["node_modules"],
    }, indent=2, ensure_ascii=False))

    _add("frontend/next.config.js", """/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
};

module.exports = nextConfig;
""")

    _add("frontend/Dockerfile", """FROM node:20-alpine AS base

# --- deps ---
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci || npm install

# --- build ---
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# --- run ---
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
""")

    _add("frontend/src/lib/api.ts", f"""/**
 * {n} — API 统一封装
 *
 * 所有后端请求都从这里发出，禁止在组件里裸 fetch。
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

interface RequestOptions extends Omit<RequestInit, "body"> {{
  body?: unknown;
}}

async function request<T>(path: string, options: RequestOptions = {{}}): Promise<T> {{
  const {{ body, headers: customHeaders, ...rest }} = options;

  const headers: HeadersInit = {{
    "Content-Type": "application/json",
    ...customHeaders,
  }};

  const res = await fetch(`${{API_BASE}}${{path}}`, {{
    headers,
    body: body ? JSON.stringify(body) : undefined,
    ...rest,
  }});

  if (!res.ok) {{
    const err = await res.json().catch(() => ({{ detail: "请求失败" }}));
    throw new Error(err.detail ?? `HTTP ${{res.status}}`);
  }}

  return res.json() as Promise<T>;
}}

export const api = {{
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) => request<T>(path, {{ method: "POST", body }}),
  put: <T>(path: string, body: unknown) => request<T>(path, {{ method: "PUT", body }}),
  del: <T>(path: string) => request<T>(path, {{ method: "DELETE" }}),
}};
""")

    # P1-7: 修复 ReactNode import + P1-5: 加 globals.css import
    _add("frontend/src/app/layout.tsx", f"""import type {{ ReactNode }} from "react";
import "./globals.css";

export const metadata = {{
  title: "{n}",
  description: "{info['project_desc']}",
}};

export default function RootLayout({{
  children,
}}: {{
  children: ReactNode;
}}) {{
  return (
    <html lang="zh-CN">
      <body>{{children}}</body>
    </html>
  );
}}
""")

    _add("frontend/src/app/page.tsx", f"""export default function Home() {{
  return (
    <main style={{{{ padding: "2rem" }}}}>
      <h1>{n}</h1>
      <p>{info['project_desc']}</p>
    </main>
  );
}}
""")

    # P1-5: globals.css + Tailwind 配置
    _add("frontend/src/app/globals.css", """@tailwind base;
@tailwind components;
@tailwind utilities;
""")

    _add("frontend/tailwind.config.js", """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
};
""")

    _add("frontend/postcss.config.js", """module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
""")


def _build_infra(f, info):
    """infra/ + 配置文件。"""
    _add = lambda p, c, x=False: f.__setitem__(p, (c.strip() + "\n", x))

    n = info["project_name"]
    d = info["dir_name"]
    ip = info["server_ip"]
    deploy_path = f"/opt/{d}/" if ip else ""

    if ip:
        _add("infra/deploy/deploy.sh", f"""#!/bin/bash
# 一键部署脚本
# 注意：需要在服务器上配置 deploy 用户，并设置好 SSH 免密登录
#   useradd -m deploy && usermod -aG docker deploy
#   在本地：ssh-copy-id deploy@{ip}
set -e

DEPLOY_START=$(date +%s)
TARGET=${{1:-all}}
SERVER=deploy@{ip}
DEPLOY_PATH="{deploy_path}"

echo "===== 部署 ====="
echo "目标: $TARGET"

cd ~/Projects/{d}

# ── 打包 + 本地 md5 ──
if [ "$TARGET" = "frontend" ] || [ "$TARGET" = "all" ]; then
    echo "打包前端..."
    tar czf /tmp/frontend-update.tar.gz --exclude='node_modules' --exclude='.next' --exclude='.git' -C frontend .
    LOCAL_FE_MD5=$(md5sum /tmp/frontend-update.tar.gz | awk '{{print $1}}')
    echo "前端包 md5: $LOCAL_FE_MD5"
fi
if [ "$TARGET" = "backend" ] || [ "$TARGET" = "all" ]; then
    echo "打包后端..."
    tar czf /tmp/backend-update.tar.gz --exclude='__pycache__' --exclude='data' --exclude='*.db' --exclude='*.pt' --exclude='*.onnx' --exclude='.git' -C backend .
    LOCAL_BE_MD5=$(md5sum /tmp/backend-update.tar.gz | awk '{{print $1}}')
    echo "后端包 md5: $LOCAL_BE_MD5"
fi

# ── 上传 ──
echo "上传..."
if [ "$TARGET" = "frontend" ]; then
    scp /tmp/frontend-update.tar.gz $SERVER:/tmp/
elif [ "$TARGET" = "backend" ]; then
    scp /tmp/backend-update.tar.gz $SERVER:/tmp/
else
    scp /tmp/frontend-update.tar.gz /tmp/backend-update.tar.gz $SERVER:/tmp/
fi

scp infra/docker/docker-compose.yml $SERVER:${{DEPLOY_PATH}}docker-compose.yml
scp .env $SERVER:${{DEPLOY_PATH}}.env 2>/dev/null || echo "(本地无 .env，跳过)"

# ── 服务器端部署 ──
echo "服务器部署..."
ssh $SERVER "TARGET=$TARGET DEPLOY_PATH=$DEPLOY_PATH LOCAL_FE_MD5=${{LOCAL_FE_MD5:-}} LOCAL_BE_MD5=${{LOCAL_BE_MD5:-}} bash -s" << 'EOF'
set -e

# md5 校验（踩坑清单第 7 条）
if [ -n "$LOCAL_FE_MD5" ]; then
    REMOTE_FE_MD5=$(md5sum /tmp/frontend-update.tar.gz | awk '{{print $1}}')
    if [ "$LOCAL_FE_MD5" != "$REMOTE_FE_MD5" ]; then
        echo "ERROR: 前端包 md5 不匹配！本地=$LOCAL_FE_MD5 远程=$REMOTE_FE_MD5" >&2
        exit 1
    fi
    echo "前端包 md5 校验通过"
fi
if [ -n "$LOCAL_BE_MD5" ]; then
    REMOTE_BE_MD5=$(md5sum /tmp/backend-update.tar.gz | awk '{{print $1}}')
    if [ "$LOCAL_BE_MD5" != "$REMOTE_BE_MD5" ]; then
        echo "ERROR: 后端包 md5 不匹配！本地=$LOCAL_BE_MD5 远程=$REMOTE_BE_MD5" >&2
        exit 1
    fi
    echo "后端包 md5 校验通过"
fi

# 备份旧目录（失败时可手动回滚：mv backend.bak.xxx backend）
TIMESTAMP=$(date +%s)
if [ "$TARGET" = "frontend" ] || [ "$TARGET" = "all" ]; then
    if [ -d "${{DEPLOY_PATH}}frontend" ]; then
        cp -r "${{DEPLOY_PATH}}frontend" "${{DEPLOY_PATH}}frontend.bak.$TIMESTAMP"
    fi
    cd ${{DEPLOY_PATH}}frontend && tar xzf /tmp/frontend-update.tar.gz
fi
if [ "$TARGET" = "backend" ] || [ "$TARGET" = "all" ]; then
    if [ -d "${{DEPLOY_PATH}}backend" ]; then
        cp -r "${{DEPLOY_PATH}}backend" "${{DEPLOY_PATH}}backend.bak.$TIMESTAMP"
    fi
    cd ${{DEPLOY_PATH}}backend && tar xzf /tmp/backend-update.tar.gz
fi

cd $DEPLOY_PATH
if [ "$TARGET" = "frontend" ]; then
    docker compose build frontend && docker compose up -d frontend
elif [ "$TARGET" = "backend" ]; then
    docker compose build backend celery-worker && docker compose up -d backend celery-worker
else
    docker compose build && docker compose up -d
fi

# 循环探测 health（最多等 60s，每 5s 探测一次）
echo "等待服务就绪..."
for i in $(seq 1 12); do
    if curl -s --max-time 5 http://localhost:8000/health > /dev/null 2>&1; then
        echo "health 检查通过"
        break
    fi
    if [ "$i" -eq 12 ]; then
        echo "WARNING: 60s 内 health 未就绪，请手动检查"
    else
        sleep 5
    fi
done

docker compose ps --format table

# 清理超过 3 天的旧备份
find $DEPLOY_PATH -maxdepth 1 -name "*.bak.*" -mtime +3 -exec rm -rf {{}} \\;
EOF

DEPLOY_END=$(date +%s)
echo ""
echo "部署完成！耗时 $(((DEPLOY_END - DEPLOY_START) / 60))分$(((DEPLOY_END - DEPLOY_START) % 60))秒"
""", True)

    # P0-1 fix (方案B): context 保持 ../../，Dockerfile 里 COPY 路径改成 backend/ 前缀
    # P2-12: postgres 去掉 env_file，只保留 environment 块
    # P1-6: 加 nginx 服务（注释掉）
    _add("infra/docker/docker-compose.yml", f"""services:
  backend:
    build:
      context: ../../
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    env_file: ../../.env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    stop_grace_period: 30s
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  celery-worker:
    build:
      context: ../../
      dockerfile: backend/Dockerfile
    command: ["celery", "-A", "worker", "worker", "--loglevel=info", "--concurrency=2"]
    env_file: ../../.env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    stop_grace_period: 120s

  frontend:
    build:
      context: ../../frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${{POSTGRES_USER:-app}}
      POSTGRES_PASSWORD: ${{POSTGRES_PASSWORD:-change-me-in-production}}
      POSTGRES_DB: ${{POSTGRES_DB:-app_db}}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${{POSTGRES_USER:-app}}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ── Nginx 反向代理（生产环境取消注释）──
  # nginx:
  #   image: nginx:alpine
  #   ports:
  #     - "80:80"
  #   volumes:
  #     - ../nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
  #   depends_on:
  #     - backend
  #     - frontend

volumes:
  pgdata:
""")

    # P1-6: Nginx 基础配置模板
    _add("infra/nginx/default.conf", """upstream backend {
    server backend:8000;
}
upstream frontend {
    server frontend:3000;
}

server {
    listen 80;

    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
""")


def _build_config_files(f, info):
    """.env.example、.gitignore、.dockerignore、pip.conf 等。"""
    _add = lambda p, c, x=False: f.__setitem__(p, (c.strip() + "\n", x))

    ip = info["server_ip"]

    _add("pip.conf", "[global]\nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple\ntrusted-host = pypi.tuna.tsinghua.edu.cn\n")
    _add(".npmrc", "registry=https://registry.npmmirror.com\n")

    # P2-11: 去掉根目录空 requirements.txt（容易和 backend/requirements.txt 混淆）

    env_lines = [
        "ENV=development", "SECRET_KEY=change-me", "",
        "DATABASE_URL=sqlite:///./dev.db",
        "# DATABASE_URL=postgresql://user:pass@localhost:5432/dbname", "",
        "REDIS_URL=redis://localhost:6379/0",
        "CORS_ORIGINS=http://localhost:3000", "",
        "# PostgreSQL (docker-compose 使用)",
        "POSTGRES_USER=app",
        "POSTGRES_PASSWORD=change-me-in-production",
        "POSTGRES_DB=app_db",
    ]
    if ip:
        env_lines.append(f"PLATFORM_BASE_URL=http://{ip}:8000")
    _add(".env.example", "\n".join(env_lines) + "\n")

    _add(".gitignore", """# Python
__pycache__/
*.pyc
*.egg-info/
.venv/
venv/
*.db

# Node
node_modules/
.next/
out/

# IDE
.vscode/
.idea/

# OS
.DS_Store

# Env
.env
*.env.local

# Data
data/
*.pt
*.onnx
dump.rdb
""")

    # P1-4: .dockerignore
    _add(".dockerignore", """.git
.state
node_modules
.next
out
__pycache__
*.pyc
*.db
*.pt
*.onnx
.env
.env.*
data/
dump.rdb
*.tar.gz
""")


def _build_scripts(f, info):
    """scripts/ 目录。"""
    _add = lambda p, c, x=False: f.__setitem__(p, (c.strip() + "\n", x))

    _add("scripts/state_cli.py", r"""#!/usr/bin/env python3
"""
    + '''"""
状态管理 CLI — 管理团队状态、决策、changelog。

用法：
    python scripts/state_cli.py team-status
    python scripts/state_cli.py status-set backend --task "修复 bug" --progress "50%"
    python scripts/state_cli.py decisions
    python scripts/state_cli.py decision-propose --title "用 Redis 做缓存" --proposed-by "乔峰"
    python scripts/state_cli.py decision-lock DEC-003
    python scripts/state_cli.py changelog-add backend "修复数据集上传超时"
"""
import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# P2-9: fcntl 跨平台兜底
try:
    import fcntl
except ImportError:
    # Windows 或其他不支持 fcntl 的平台 — 用空操作替代
    class _FcntlStub:
        LOCK_SH = 0
        LOCK_EX = 0
        LOCK_UN = 0
        @staticmethod
        def flock(f, op):
            pass
    fcntl = _FcntlStub()

STATE_DIR = Path(__file__).resolve().parent.parent / ".state"
STATUS_DIR = STATE_DIR / "status"
DECISIONS_FILE = STATE_DIR / "decisions.json"
CHANGELOG_FILE = STATE_DIR / "changelog.md"

ROLES = ["backend", "frontend", "firmware", "infra", "architect"]


def _atomic_write(path: Path, content: str):
    """Write via temp file + rename for atomicity."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    closed = False
    try:
        os.write(fd, content.encode("utf-8"))
        os.close(fd)
        closed = True
        os.rename(tmp, str(path))
    except Exception:
        if not closed:
            os.close(fd)
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _load_decisions() -> list:
    if not DECISIONS_FILE.exists():
        return []
    with open(DECISIONS_FILE, "r") as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f, fcntl.LOCK_UN)
    return data


def _save_decisions(data: list):
    DECISIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DECISIONS_FILE, "a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        f.truncate()
        f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\\n")
        fcntl.flock(f, fcntl.LOCK_UN)


def cmd_team_status(args):
    """Print team status table."""
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    print("\\n===== 团队状态 =====\\n")
    print(f"{'角色':<12} {'任务':<30} {'进度':<10} {'更新时间'}")
    print("-" * 75)
    for role in ROLES:
        status_file = STATUS_DIR / f"{role}.json"
        if status_file.exists():
            s = json.loads(status_file.read_text())
            task = s.get("task", "—")[:28]
            progress = s.get("progress", "—")
            updated = s.get("updated_at", "—")[:19]
        else:
            task, progress, updated = "—", "—", "—"
        print(f"{role:<12} {task:<30} {progress:<10} {updated}")
    print()


def cmd_status_set(args):
    """Update role status."""
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    data = {
        "role": args.role,
        "task": args.task,
        "progress": args.progress,
        "updated_at": now,
    }
    _atomic_write(STATUS_DIR / f"{args.role}.json", json.dumps(data, indent=2, ensure_ascii=False))
    print(f"✅ {args.role} 状态已更新")


def cmd_decisions(args):
    """List all decisions."""
    decs = _load_decisions()
    if not decs:
        print("暂无决策记录")
        return
    print("\\n===== 决策列表 =====\\n")
    for d in decs:
        icon = "🔒" if d.get("status") == "locked" else "📝"
        print(f"  {icon} {d['id']}: {d['title']} (by {d.get('proposed_by', '?')})")
    print()


def cmd_decision_propose(args):
    """Propose a new decision."""
    decs = _load_decisions()
    max_id = 0
    for d in decs:
        try:
            num = int(d["id"].split("-")[1])
            if num > max_id:
                max_id = num
        except (IndexError, ValueError):
            pass
    new_id = f"DEC-{max_id + 1:03d}"
    now = datetime.now(timezone.utc).isoformat()
    decs.append({
        "id": new_id,
        "title": args.title,
        "status": "proposed",
        "proposed_by": args.proposed_by,
        "proposed_at": now,
    })
    _save_decisions(decs)
    print(f"✅ 决策已记录: {new_id} — {args.title}")


def cmd_decision_lock(args):
    """Lock a decision."""
    decs = _load_decisions()
    for d in decs:
        if d["id"] == args.decision_id:
            d["status"] = "locked"
            d["locked_at"] = datetime.now(timezone.utc).isoformat()
            _save_decisions(decs)
            print(f"🔒 {args.decision_id} 已锁定")
            return
    print(f"❌ 未找到 {args.decision_id}")


def cmd_changelog_add(args):
    """Append to changelog (P0-2: 同一天不重复写日期 header)."""
    CHANGELOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_header = f"## {today}"
    line = f"- [{args.role}] {args.message}\\n"

    # 检查文件末尾是否已有当天日期 header
    has_today = False
    if CHANGELOG_FILE.exists():
        content = CHANGELOG_FILE.read_text(encoding="utf-8")
        # 逐行检查是否有当天 header
        for existing_line in content.splitlines():
            if existing_line.strip() == today_header:
                has_today = True
                break

    with open(CHANGELOG_FILE, "a") as f:
        if has_today:
            f.write(line)
        else:
            f.write(f"\\n{today_header}\\n{line}")
    print(f"✅ changelog 已追加")


def main():
    parser = argparse.ArgumentParser(description="项目状态管理 CLI")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("team-status", help="查看全员状态")

    p = sub.add_parser("status-set", help="更新角色状态")
    p.add_argument("role", choices=ROLES)
    p.add_argument("--task", required=True)
    p.add_argument("--progress", default="进行中")

    sub.add_parser("decisions", help="列出所有决策")

    p = sub.add_parser("decision-propose", help="提议新决策")
    p.add_argument("--title", required=True)
    p.add_argument("--proposed-by", required=True)

    p = sub.add_parser("decision-lock", help="锁定决策")
    p.add_argument("decision_id")

    p = sub.add_parser("changelog-add", help="追加 changelog")
    p.add_argument("role", choices=ROLES)
    p.add_argument("message")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    {
        "team-status": cmd_team_status,
        "status-set": cmd_status_set,
        "decisions": cmd_decisions,
        "decision-propose": cmd_decision_propose,
        "decision-lock": cmd_decision_lock,
        "changelog-add": cmd_changelog_add,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
''')


def build_files(info: dict) -> dict:
    """Return {relative_path: (content, executable)}.

    v4.1: 拆分为多个子函数，主函数只负责调用和 firmware 过滤。
    """
    f = {}

    _build_root_docs(f, info)
    _build_claude_config(f, info)
    _build_state(f, info)
    _build_contracts(f, info)
    _build_scripts(f, info)
    _build_backend(f, info)
    _build_frontend(f, info)
    _build_infra(f, info)
    _build_config_files(f, info)

    # Sub-directory CLAUDE.md + STATUS.md
    n = info["project_name"]
    _add = lambda p, c, x=False: f.__setitem__(p, (c.strip() + "\n", x))

    for role, name, stack, directory in [
        ("backend", "乔峰", info["backend_stack"], "backend"),
        ("frontend", "黄蓉", info["frontend_stack"], "frontend"),
        ("firmware", "杨过", "Python + ONNX Runtime + GPIO", "firmware"),
        ("infra", "张三丰", "Docker Compose + Nginx + Bash", "infra"),
    ]:
        _add(f"{directory}/CLAUDE.md", f"""# {n} — {name}

## 身份
你叫**{name}**，负责 `{directory}/` 目录。团队全貌见根目录 CLAUDE.md。

## 技术栈
{stack}

## 规则
参见根目录 RULES.md。详细规范见 .claude/rules/。
新会话先读 STATUS.md；任务完成后更新 STATUS.md。
""")

        _add(f"{directory}/STATUS.md", f"""# STATUS.md — {name}工作状态

> 每次任务完成后必须更新。新会话先读此文件。

## 上次完成
（每次任务后填写）

## 进行中
（当前未完成的任务）

## 已知坑
（踩过的坑）

## 待验证
（改了但还没部署验证的）
""")

    # Remove firmware if no hardware
    if not info["has_hardware"]:
        f = {k: v for k, v in f.items() if not k.startswith("firmware/")}

    return f


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="大飞哥无敌战队 — 项目协作框架初始化")
    parser.add_argument("--dry-run", action="store_true", help="只预览不写入")
    parser.add_argument("--project-name", help="项目名称（跳过交互）")
    parser.add_argument("--desc", help="项目描述（跳过交互）")
    parser.add_argument("--server", help="服务器 IP")
    parser.add_argument("--hardware", action="store_true", help="包含硬件端")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的文件")
    args = parser.parse_args()

    info = collect_info(args)
    files = build_files(info)

    # Preview
    print()
    print("=" * 60)
    print(f"  项目：{info['project_name']}")
    print(f"  目录：{Path.cwd()}")
    print(f"  文件：{len(files)} 个")
    print("=" * 60)
    print()

    exists = []
    for path in sorted(files.keys()):
        full = Path.cwd() / path
        if full.exists():
            if args.force:
                exists.append(path)
                print(f"    overwrite  {path}")
            else:
                exists.append(path)
                print(f"    skip  {path}")
        else:
            print(f"    +     {path}")

    if args.force:
        new_count = len(files)
        overwrite_count = len(exists)
        print(f"\n  新增 {new_count - overwrite_count} 个文件，覆盖 {overwrite_count} 个已存在")
    else:
        new_count = len(files) - len(exists)
        print(f"\n  新增 {new_count} 个文件，跳过 {len(exists)} 个已存在")

    if args.dry_run:
        print("\n  [dry-run] 未写入任何文件。")
        return

    if not args.force and new_count == 0:
        print("\n  所有文件都已存在。")
        return

    # 非交互模式（project_name + desc 都传了）且 force 时直接写入
    if args.force and args.project_name and args.desc:
        pass  # skip confirmation
    else:
        if args.force:
            confirm = input(f"\n  将覆盖 {len(exists)} 个已有文件，确认？[Y/n]: ").strip().lower()
        else:
            confirm = input(f"\n  确认生成？[Y/n]: ").strip().lower()
        if confirm and confirm != "y":
            print("  已取消。")
            return

    print()
    written = 0
    for path, (content, executable) in sorted(files.items()):
        full = Path.cwd() / path
        if full.exists() and not args.force:
            continue
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        if executable:
            full.chmod(full.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"  + {path}")
        written += 1

    d = info["dir_name"]
    print(f"\n  ✅ 完成！生成了 {written} 个文件。")
    print(f"""
  下一步：
    1. cp .env.example .env && vi .env  # 修改配置（开发环境用 sqlite，生产环境改 postgresql）
    2. git init && git add -A && git commit -m "init: 项目协作框架"

  启动各角色：
    大飞哥：cd ~/Projects/{d} && claude --agent 大飞哥
    架构师：cd ~/Projects/{d} && claude --agent 王重阳
    后端：  cd ~/Projects/{d} && claude --agent 乔峰
    前端：  cd ~/Projects/{d} && claude --agent 黄蓉
    运维：  cd ~/Projects/{d} && claude --agent 张三丰
    硬件：  cd ~/Projects/{d} && claude --agent 杨过

    查看所有角色：claude agents

  环境说明：
    开发环境：DATABASE_URL=sqlite:///./dev.db（默认，开箱即用）
    生产环境：修改 .env 中 DATABASE_URL 为 PostgreSQL 连接串
""")


if __name__ == "__main__":
    main()
