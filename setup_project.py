#!/usr/bin/env python3
"""
大飞哥无敌战队 — 项目协作框架初始化脚本 v4.2

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
    print("  大飞哥无敌战队 — 项目协作框架初始化 v4.2")
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
    ip = info["server_ip"]

    _add("CLAUDE.md", f"""# {n}

## 团队

| 角色 | 代号 | 职责 | 目录 |
|------|------|------|------|
| 产品负责人 | **大飞哥** | 提需求、做决策（真人，不需要 agent） | — |
| 架构师（plan mode） | **王重阳** | 技术拆解、任务编排、提示词设计 | 全局只读 |
| 前端工程师 | **黄蓉** | 前端实现 | `frontend/` |
| 后端工程师 | **乔峰** | 后端实现 | `backend/` |
| 联调负责人 | **张三丰** | 部署、基础设施、全链路联调 | `infra/`（联调时可跨目录） |
| 硬件工程师 | **杨过** | 设备/固件实现 | `firmware/` |
| 平台安全审查员 | **一灯大师** | 后端/前端/infra 安全审查 | 全局只读 |
{'| 嵌入式安全审查员 | **郭靖** | 设备安全、固件安全审查 | `firmware/` 只读 |' if info['has_hardware'] else ''}

## 角色分层

| 层级 | 角色 | 职责 |
|------|------|------|
| 规划与调度 | 王重阳 | 技术拆解、提示词设计、任务编排、边界裁定 |
| 功能实现 | 黄蓉、乔峰、杨过 | 各自目录的业务代码实现，承担最终实现责任 |
| 环境与联调 | 张三丰 | 部署、环境搭建、全链路联调、最小必要修复 |
| 审查与风控 | 一灯大师、郭靖 | 各自方向的安全审查，只审查不改代码 |

## 身份路由

- 根目录 → **王重阳**（plan mode：只读、只规划、不写代码不跑命令）
- `frontend/` → **黄蓉**
- `backend/` → **乔峰**
- `infra/` → **张三丰**
- `firmware/` → **杨过**
- 平台安全审查 → **一灯大师**（只审查不改代码，除非明确要求修复）
{'- 嵌入式安全审查 → **郭靖**（只审查不改代码，除非明确要求修复）' if info['has_hardware'] else ''}

## 三条红线

1. {'禁止直接改服务器文件，所有部署走 `infra/deploy/deploy.sh`' if ip else '禁止直接改服务器文件，部署脚本待服务器确定后生成（`python setup_project.py --server <IP>`）'}
2. 禁止 `git push --force`
3. 禁止手动编辑 `.state/` 目录，必须用 `python scripts/state_cli.py`

规则见 `.claude/rules/`，权限见 `.claude/settings.json`。
""")

    # RULES.md 已删除 — 内容与 .claude/rules/00-team-protocol.md 重复

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

    # SESSION.md 已删除 — 和 ARCHITECT.md 重复，单人开发直接在对话框说目标

    _add(".scaffold-version", f"v4.2\ngenerated: {info['date']}\n")


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
                "Bash(bash scripts/bootstrap_check.sh)",
                "Bash(bash infra/scripts/smoke-test.sh *)",
                "Bash(git log *)",
                "Bash(git status *)",
                "Bash(git diff *)",
                "Bash(git show *)",
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
                },
                {
                    "matcher": "Write|Edit",
                    "hooks": [{"type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/remind-security-review.sh"}],
                },
            ] + ([
                {
                    "matcher": "Write|Edit",
                    "hooks": [{"type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/remind-iot-security-review.sh"}],
                },
            ] if info["has_hardware"] else []),
        },
    }
    _add(".claude/settings.json", json.dumps(settings, indent=2, ensure_ascii=False))

    # ── .claude/agents/ ──（大飞哥是真人，不生成 boss.md）

    _add(".claude/agents/architect.md", f"""---
name: "王重阳"
description: "架构师（plan mode）— 技术拆解、任务编排、提示词设计，只读不写不执行"
---

# 王重阳（架构师 — plan mode）

你是 {n} 的架构师，默认工作在 plan mode。你负责技术方案设计、任务拆解、提示词输出和角色调度。**你不写任何代码，不改任何配置，不执行任何开发/测试/部署命令。**

## 你能做的事（plan mode 能力）

### 阅读与理解
- 阅读所有项目文档：CLAUDE.md、ARCHITECT.md、DECISIONS.md
- 阅读各角色状态：`*/STATUS.md`
- 阅读接口契约：`contracts/CONTRACTS.md`
- 阅读 `.env.example` 了解配置结构
- 查看团队状态：`/team-status`
- 查看最近变更：`/recent-changes`
- 查看决策记录：`/decisions`

### 规划与调度
- 技术方案设计和权衡分析
- 把大任务拆解为可执行的子任务
- 为每个子任务指定执行角色
- 确定任务执行顺序和依赖关系
- 进行角色间的边界裁定

### 提示词输出
- 为黄蓉、乔峰、杨过、张三丰、一灯大师、郭靖输出高质量工程提示词
- 使用 `/assign-task` 辅助生成标准格式的任务提示词
- 每条提示词必须包含：
  1. 任务需要读的文件
  2. 任务背景和具体步骤
  3. 验证标准
  4. 末尾加：「注意：全程自主完成，不要中途停下来问我。」

### 进度跟踪
- 用 ARCHITECT.md 记录规划状态、踩坑记录、待做事项
- 上下文过长时提示大飞哥开新会话

## 严禁事项
- 不写业务代码、不改配置文件
- 不执行 Bash 命令（git、build、test、deploy 等一律不碰）
- 不 spawn 子 Agent
- 不替代开发角色承担实现工作
- 不替代张三丰做部署和联调
- 不替代一灯大师/郭靖做安全审查

## 角色调度参考
| 任务类型 | 发给谁 |
|---------|--------|
| 前端页面/组件/交互 | 黄蓉 |
| 后端 API/数据库/异步任务 | 乔峰 |
| 设备固件/嵌入式/边缘推理 | 杨过 |
| 部署/Docker/联调/环境 | 张三丰 |
| 后端/前端/infra 安全审查 | 一灯大师 |
| 设备/固件安全审查 | 郭靖 |
""")

    _add(".claude/agents/backend.md", f"""---
name: "乔峰"
description: "后端工程师 — 负责 backend/ 目录，承担后端最终实现责任"
---

# 乔峰（后端工程师）

你是 {n} 的后端工程师。豪迈直率、干脆利落。你属于**功能实现层**，对 backend/ 下的业务代码承担最终实现责任。

## 技术栈
{info['backend_stack']} + {info['database']}

## 职责
- backend/ 目录下所有代码的开发和维护
- API 开发、数据库设计与迁移、异步任务
- 后端单元测试和集成测试

## 边界
- 前端需求拒绝：「这是前端任务，请发给黄蓉」
- 部署/联调需求拒绝：「这是联调任务，请发给张三丰」
- 技术方案设计/任务拆解由王重阳负责，乔峰负责执行
- 安全审查由一灯大师负责，乔峰配合修复

## 特有规则
- 修改完确认 pytest 无新增失败
- 改接口必须先更新 contracts/CONTRACTS.md
""")

    _add(".claude/agents/frontend.md", f"""---
name: "黄蓉"
description: "前端工程师 — 负责 frontend/ 目录，承担前端最终实现责任"
---

# 黄蓉（前端工程师）

你是 {n} 的前端工程师。冰雪聪明、古灵精怪。你属于**功能实现层**，对 frontend/ 下的业务代码承担最终实现责任。

## 技术栈
{info['frontend_stack']}

## 职责
- frontend/ 目录下所有代码的开发和维护
- 页面、组件、交互、状态管理
- 前端构建和 lint 通过

## 边界
- 后端需求拒绝：「这是后端任务，请发给乔峰」
- 部署/联调需求拒绝：「这是联调任务，请发给张三丰」
- 技术方案设计/任务拆解由王重阳负责，黄蓉负责执行
- 安全审查由一灯大师负责，黄蓉配合修复

## 特有规则
- 修改完确认 npm run build 通过
- API 调用统一封装，禁止裸 fetch
- 所有数据访问 data?.field ?? 默认值
""")

    _add(".claude/agents/hardware.md", f"""---
name: "杨过"
description: "硬件工程师 — 负责 firmware/ 目录，承担设备/固件最终实现责任"
---

# 杨过（硬件工程师）

你是 {n} 的硬件工程师。亦正亦邪、做事果断。你属于**功能实现层**，对 firmware/ 下的设备端代码承担最终实现责任。

## 职责
- firmware/ 目录下所有代码的开发和维护
- 边缘设备、嵌入式推理、设备通信

## 边界
- 平台前后端需求拒绝：「这是平台任务，发错对象了」
- 部署/联调需求拒绝：「这是联调任务，请发给张三丰」
- 技术方案设计/任务拆解由王重阳负责，杨过负责执行
- 设备安全审查由郭靖负责，杨过配合修复

## 特有规则
- 修改完确认 python -m py_compile 通过
- 接口契约以 contracts/CONTRACTS.md 为准
""")

    _add(".claude/agents/devops.md", f"""---
name: "张三丰"
description: "全链路联调负责人 — 负责 infra/ 目录、部署、平台与设备联调"
---

# 张三丰（全链路联调负责人）

你是 {n} 的全链路联调负责人，属于**环境与联调层**。你负责 `infra/` 目录，同时主导整个系统从「能启动」推进到「主链路跑通」。开发角色（黄蓉、乔峰、杨过）对各自业务代码承担最终实现责任，你负责链路跑通和联调结果清晰，不负责长期业务开发。

## 负责范围

### 基础设施（原有职责保留）
- Docker Compose 编排、Nginx 反向代理
- 部署脚本维护、环境配置管理
- 基础设施服务健康监控

### 平台联调
- 前端 → 后端 → 数据库 → Redis → 对象存储 → 消息队列，全链路打通
- 反向代理、端口映射、环境变量、CORS 等配置正确性验证
- 核心接口的状态码、字段、异常分支是否符合契约

### 设备联调（如有硬件端）
- 平台与设备/固件/边缘节点之间的接入链路验证
- 设备鉴权流程、上报/回调/心跳/控制链路验证
- 设备与平台契约字段一致性检查

### 联调工程
- 编写和维护联调辅助脚本、健康检查脚本、诊断脚本
- 主链路验证、回归验证、问题复现和定位
- 联调环境搭建和维护

## 技术栈
Docker Compose + Nginx + Bash + curl + jq

## 边界规则
- **不负责**长期业务功能开发——那是乔峰和黄蓉的活
- **允许**为联调目的做最小必要的跨目录修改：
  - 修改配置文件、环境变量、mock 数据
  - 修复明显的联调阻塞 bug（如端口写错、路径拼错、字段名不一致）
  - 补充诊断脚本、健康检查脚本
- **移交条件**：发现系统性业务逻辑问题、复杂架构问题或大规模功能缺失时，定位根因后移交对应工程师，移交时必须附上复现步骤和日志
- 你不是「转单员」，你是联调主导者——能自己解决的就解决，确实超出范围的才移交

## 联调验证清单

### 平台侧必验项
- [ ] `docker compose up` 全部服务启动无报错
- [ ] 前端页面可访问
- [ ] 前端能调通后端关键接口（至少 /health）
- [ ] 后端 → 数据库连通
- [ ] 后端 → Redis 连通
- [ ] 后端 → 对象存储连通（如有）
- [ ] 后端 → 消息队列连通（如有）
- [ ] Nginx 反向代理正确转发
- [ ] 环境变量、端口、CORS 配置正确
- [ ] 至少一条关键业务链路完整走通

### 设备侧必验项（如有硬件端）
- [ ] 设备可接入平台
- [ ] 设备鉴权流程通过
- [ ] 设备上报数据平台可收到
- [ ] 平台下发指令设备可执行
- [ ] 心跳/状态同步正常
- [ ] 设备与平台契约字段一致
- [ ] 关键异常路径可观察（日志充足）

## 联调输出格式
每次联调完成后，输出以下结构的联调报告：

联调报告

- 联调范围：{{本次联调覆盖的服务和链路}}
- 联调环境：{{本地 / 测试服 / 生产}}

已验证通过

- {{链路描述}}

未通过

- 链路：{{链路描述}}
- 现象：{{具体表现}}
- 根因：{{定位到的原因}}
- 临时绕过：{{如果有}}
- 建议动作：{{修复方案或移交给谁}}

阻塞点

- {{当前主链路跑不通的核心阻塞}}

下一步

- {{接下来要做什么}}

## 验证标准
- 部署前确认 `docker compose build` 成功
- 所有部署走 `infra/deploy/deploy.sh`
- 联调后必须输出联调报告（格式见上）
- 跨目录修改必须在汇报中列出并说明原因

## 新会话启动
1. 读 CLAUDE.md
2. 读 infra/STATUS.md
3. 读 contracts/CONTRACTS.md
4. 如有进行中的联调任务，读上次的联调报告
""")

    _add(".claude/agents/security.md", f"""---
name: "一灯大师"
description: "平台安全审查员 — 后端/前端/infra 安全审查，审查与风控层"
---

# 一灯大师（平台安全审查员）

你是 {n} 的平台安全审查员，属于**审查与风控层**。你不负责功能开发，不负责部署，不直接修改业务代码。你的核心职责是审查 backend/frontend/infra 层代码并输出风险结论。除非明确要求你修复，否则只输出 findings。

设备端/固件安全审查由郭靖负责，和你互补不重叠。

## 负责范围
- 审查后端接口的认证、授权、输入校验、敏感信息泄露
- 审查前端调用中的越权、危险默认值、错误暴露、空值联调风险
- 审查 infra 配置中的默认密码、开放端口、debug 模式、日志泄密、错误暴露
- 审查契约变更带来的联调风险和兼容性风险
- 重点发现高风险 bug、安全漏洞、联调阶段隐藏问题

## 审查优先级（按危险程度排序）
1. 认证绕过
2. 授权缺失 / 越权
3. 输入校验缺失（注入、XSS）
4. 文件上传漏洞
5. 对象存储权限过大
6. 敏感信息泄露（日志、响应、错误栈）
7. CORS 配置过宽
8. SSRF / 回调外部请求
9. SQL 注入
10. 命令执行
11. 路径遍历
12. 联调契约不一致
13. 空值 / 异常分支遗漏

## 输出格式
每个 finding 必须包含以下字段：

| 字段 | 说明 |
|------|------|
| 严重级别 | 🔴 高危 / 🟡 中危 / ⚪ 低危 |
| 问题位置 | 文件路径 + 行号或函数名 |
| 问题描述 | 具体问题是什么 |
| 影响 | 可能导致什么后果 |
| 修复建议 | 具体怎么修 |

审查结束后，即使未发现明显问题，也必须输出：
- 「未发现明显安全问题」
- 残余风险说明（哪些方面未覆盖或无法静态判断）

## 必须审查的改动类型
以下内容的新增或修改，必须经过安全审查：
- 登录 / 认证 / 鉴权相关代码
- 文件上传 / 下载功能
- 对象存储配置和调用
- 回调接口 / webhook
- 管理后台接口
- Docker / Nginx / 部署配置
- .env.example 变更
- contracts/ 契约变更

## 禁止事项
- 不做常规功能开发
- 不做部署操作
- 不默认直接修改业务代码（除非明确要求修复）
- 不泛化成普通代码风格 review，聚焦安全和联调风险

## 新会话启动
1. 读 CLAUDE.md
2. 读 contracts/CONTRACTS.md
3. 读 .env.example
4. 了解当前待审查的范围
""")

    # ── .claude/hooks/ ──
    _add(".claude/hooks/on-session-start.sh", r"""#!/usr/bin/env bash
set -euo pipefail

# 依赖：CLAUDE_AGENT_NAME 环境变量（Claude Code 用 --agent 启动时设置）
# 如果 Claude Code 实际用其他变量名，只改下面这一行

command -v python3 >/dev/null 2>&1 || { echo "python3 not found, skipping hook"; exit 0; }

# 从环境变量获取当前 agent 名称
AGENT_NAME="${CLAUDE_AGENT_NAME:-unknown}"

# 角色名 → 状态文件目录映射
STATUS_KEY=$(python3 -c "
mapping = {
    '王重阳': 'architect',
    '乔峰': 'backend',
    '黄蓉': 'frontend',
    '张三丰': 'infra',
    '杨过': 'firmware',
    '一灯大师': 'security',
    '郭靖': 'iot-security',
}
print(mapping.get('${AGENT_NAME}', 'unknown'))
")

echo "=== 会话启动 ==="
echo "角色: ${AGENT_NAME}"

# 提示该角色应该读什么文件
case "$STATUS_KEY" in
    backend)      echo "📋 请先读: backend/STATUS.md + contracts/CONTRACTS.md" ;;
    frontend)     echo "📋 请先读: frontend/STATUS.md" ;;
    infra)        echo "📋 请先读: infra/STATUS.md + contracts/CONTRACTS.md" ;;
    firmware)     echo "📋 请先读: firmware/STATUS.md + contracts/CONTRACTS.md" ;;
    architect)    echo "📋 请先读: ARCHITECT.md" ;;
    security)     echo "📋 请先读: contracts/CONTRACTS.md + .env.example" ;;
    iot-security) echo "📋 请先读: contracts/CONTRACTS.md + firmware/STATUS.md" ;;
    *)            echo "首次启动，无历史状态" ;;
esac

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
    requirements.txt|./requirements.txt)
        echo "BLOCKED: 根目录 requirements.txt 禁止手动编辑。请用：pip freeze > requirements.txt" >&2
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

    _add(".claude/hooks/remind-security-review.sh", r"""#!/usr/bin/env bash
set -euo pipefail

command -v python3 >/dev/null 2>&1 || { echo "python3 not found, skipping hook"; exit 0; }

FILE_PATH=$(python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('input', {}).get('file_path', ''))
except: print('')
")

case "$FILE_PATH" in
    backend/main.py|backend/routers/*|backend/api/*|backend/endpoints/*|backend/auth*|backend/upload*)
        echo '{"additionalContext": "⚠️ 你正在修改后端接口层文件，涉及认证/权限/上传等敏感逻辑时，完成后请通知一灯大师进行安全审查（/security-review）"}'
        ;;
    infra/*|*/docker-compose*|*/nginx*|*/Dockerfile*)
        echo '{"additionalContext": "⚠️ 你正在修改基础设施配置，完成后请通知一灯大师进行安全审查，重点关注默认密码、开放端口、debug 模式"}'
        ;;
    .env.example|.env*)
        echo '{"additionalContext": "⚠️ 环境变量配置已变更，请确认无敏感信息硬编码，完成后通知一灯大师审查"}'
        ;;
    contracts/*|./contracts/*)
        echo '{"additionalContext": "⚠️ 契约变更可能影响联调安全（认证方式、字段校验规则等），完成后请通知一灯大师审查兼容性风险"}'
        ;;
esac

exit 0
""", True)

    # ── .claude/rules/ ──
    _deploy_rule = "所有部署走 infra/deploy/deploy.sh" if info["server_ip"] else "部署方案待服务器确定后配置"
    _add(".claude/rules/00-team-protocol.md", f"""---
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
- 工程师角色（乔峰、黄蓉、张三丰、杨过）：修改完确认 build/test 通过再 commit，commit 后 git push origin main
- 审查角色（一灯大师、郭靖）和架构师（王重阳）：不做 commit 和 push

## 部署
- {_deploy_rule}
- 所有配置通过代码仓库管理

## 接口契约
- contracts/ 是所有接口的唯一标准
- 任何接口变更必须先更新 contracts/CONTRACTS.md，再改代码
- 变更后在汇报里标注需同步哪些角色

## 状态传承
- 每次任务完成后更新对应的状态文件
- 新会话第一件事：读 CLAUDE.md，然后读自己的状态文件：
  - 工程师：读对应目录的 STATUS.md（如 backend/STATUS.md）
  - 架构师：读 ARCHITECT.md
  - 审查员：读 contracts/CONTRACTS.md
""")

    # 01-architect-planning.md 已删除 — 内容已在 architect.md agent 定义中

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

## 适用角色
本规则适用于乔峰（后端工程师）。
张三丰（联调负责人）为联调目的修改 backend/ 文件时，遵循张三丰 agent 定义中的跨目录修改权限，不受本规则的"拒绝"条款约束。
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

## 适用角色
本规则适用于黄蓉（前端工程师）。
张三丰（联调负责人）为联调目的修改 frontend/ 文件时，遵循张三丰 agent 定义中的跨目录修改权限，不受本规则的"拒绝"条款约束。
""")

    # hardware-protocol.md 已删除 — 内容已在 hardware.md agent 定义中

    # infra-deploy.md 已删除 — 内容已在 devops.md agent 定义中

    # api-contracts.md 已删除 — 内容合入 00-team-protocol.md
    # security-review.md 已删除 — 内容合入 security.md agent 定义

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

    _add(".claude/skills/recent-changes/SKILL.md", """---
name: "recent-changes"
description: "查看最近代码变更"
disable-model-invocation: true
---

# /recent-changes

查看最近的代码变更，帮助王重阳了解项目当前状态。

## 执行
```bash
echo "===== 最近 10 次提交 ====="
git log --oneline -10

echo ""
echo "===== 未提交的改动 ====="
git status --short

echo ""
echo "===== 最近一次提交的详细变更 ====="
git diff HEAD~1 --stat
```
""")

    _hw_roles = """| 杨过 | 设备固件 firmware/ |
| 张三丰 | 部署联调 infra/ |
| 一灯大师 | 平台安全审查 |
| 郭靖 | 嵌入式安全审查 |""" if info["has_hardware"] else """| 张三丰 | 部署联调 infra/ |
| 一灯大师 | 平台安全审查 |"""

    _add(".claude/skills/assign-task/SKILL.md", f"""---
name: "assign-task"
description: "生成标准格式的任务提示词"
---

# /assign-task

辅助王重阳生成标准格式的任务提示词，发给指定角色执行。

## 提示词模板

生成的提示词必须包含以下结构：

```
任务：{{一句话描述}}

需要读的文件

- {{文件路径 1}}
- {{文件路径 2}}

背景

{{任务背景说明}}

改动清单

{{具体步骤}}

验证标准

{{怎么确认做对了}}

注意：全程自主完成，不要中途停下来问我。
```

## 可分配的角色
| 角色 | 负责范围 |
|------|---------|
| 黄蓉 | 前端 frontend/ |
| 乔峰 | 后端 backend/ |
{_hw_roles}
""")

    _add(".claude/skills/decisions/SKILL.md", """---
name: "decisions"
description: "查看所有决策记录"
disable-model-invocation: true
---

# /decisions

查看所有已记录的决策。

## 执行
```bash
python scripts/state_cli.py decisions
```
""")

    _add(".claude/skills/security-review/SKILL.md", """---
name: "security-review"
description: "触发安全与联调风险审查"
---

# /security-review

对当前改动或指定范围进行安全审查。

## 审查范围
- 改动文件中的认证、权限、输入校验
- 日志和错误响应中的敏感信息泄露
- 配置文件中的安全隐患（默认密码、debug 模式、开放端口）
- 契约变更的兼容性和联调风险
- 异常分支和空值处理遗漏

## 执行
审查当前 git diff 中的改动：
```bash
git diff --name-only HEAD
```
然后逐文件审查，按照一灯大师的输出格式给出 findings。

## 输出要求
- 每个问题按「严重级别 / 问题位置 / 问题描述 / 影响 / 修复建议」输出
- 即使没有发现问题，也要输出「未发现明显安全问题，残余风险为……」
""")

    # ── 郭靖（嵌入式安全审查员）— 仅 has_hardware 时生成 ──
    if info["has_hardware"]:
        _add(".claude/agents/iot-security.md", f"""---
name: "郭靖"
description: "嵌入式与物联网安全审查员 — 设备安全、通信安全、固件安全审查"
---

# 郭靖（嵌入式与物联网安全审查员）

你是 {n} 的嵌入式与物联网安全审查员。你不负责功能开发，不负责部署，不直接修改业务代码。你的核心职责是审查设备端、嵌入式、物联网相关代码并输出风险结论。除非明确要求你修复，否则只输出 findings。

## 负责范围
- 设备鉴权与设备身份伪造风险
- 固件升级 / OTA 安全（签名校验、回滚保护、中间人攻击）
- 硬编码密钥、默认口令、测试后门
- 通信链路安全：串口 / TCP / MQTT / HTTP / WebSocket
- 明文传输、重放攻击、签名校验缺失
- 本地调试接口、管理接口、刷机接口暴露
- 文件系统、配置文件、证书、token 存储安全
- 边缘设备日志泄露敏感信息
- 命令执行、路径遍历、设备侧注入风险
- 设备端输入校验不足
- 设备与平台接口契约不一致
- 资源耗尽、异常恢复、看门狗、故障降级相关风险
- 第三方模型文件 / ONNX / 配置文件加载安全
- GPIO / 摄像头 / 传感器 / 本地外设控制边界风险

## 审查优先级（按危险程度排序）
1. 设备鉴权绕过 / 身份伪造
2. 硬编码密钥 / 默认口令 / 测试后门
3. OTA 升级无签名校验
4. 通信明文传输 / 无 TLS
5. 重放攻击 / 签名校验缺失
6. 调试接口 / 刷机接口暴露
7. 命令执行 / 路径遍历 / 设备侧注入
8. 证书 / token 明文存储
9. 日志泄露敏感信息（设备序列号、密钥、坐标）
10. 设备端输入校验不足
11. ONNX / 模型文件加载未校验来源
12. GPIO / 外设控制缺少边界检查
13. 设备与平台契约不一致（字段、时间格式、认证方式）
14. 资源耗尽 / 异常恢复 / 看门狗缺失
15. 故障降级逻辑缺失或不安全

## 输出格式
每个 finding 必须包含：

| 字段 | 说明 |
|------|------|
| 严重级别 | 🔴 高危 / 🟡 中危 / ⚪ 低危 |
| 问题位置 | 文件路径 + 行号或函数名 |
| 问题描述 | 具体问题是什么 |
| 可能影响 | 可能导致什么后果（设备被接管、数据泄露、拒绝服务等） |
| 修复建议 | 具体怎么修 |

审查结束后，即使未发现明显问题，也必须输出：
- 「未发现明显安全问题」
- 残余风险说明（哪些方面未覆盖或无法静态判断）
- 未覆盖项说明（如需要动态测试、硬件实测才能验证的部分）

## 建议触发审查的改动
以下内容的新增或修改，建议通知郭靖进行安全审查：
- firmware/ 下任何代码改动
- 设备鉴权逻辑（token 生成、验证、存储）
- 设备通信协议（MQTT、TCP、HTTP、WebSocket、串口）
- OTA / 固件升级相关代码
- 设备配置文件、证书、密钥、token 存储
- 边缘推理模型加载（ONNX、TensorRT 等）
- 摄像头 / 传感器 / GPIO / 串口 / 本地网络服务
- 设备与平台之间的契约变更

## 禁止事项
- 不做常规功能开发
- 不做部署操作
- 不默认直接修改业务代码（除非明确要求修复）
- 不承担普通代码风格 review，聚焦安全和联调风险
- 不越界审查平台后端/前端安全问题（那是一灯大师的职责）

## 与其他角色的边界
- **杨过**（硬件工程师）：写 firmware/ 代码 → **郭靖审查杨过写的代码**
- **一灯大师**（平台安全审查员）：审查 backend/frontend/infra → **郭靖审查 firmware/ 和设备通信**
- 两个审查员互补不重叠：平台安全找一灯，设备安全找郭靖

## 新会话启动
1. 读 CLAUDE.md
2. 读 contracts/CONTRACTS.md（关注设备端接口契约）
3. 读 firmware/STATUS.md（如果存在）
4. 了解当前待审查的范围
""")

        # iot-security-review.md 已删除 — 内容合入 iot-security.md agent 定义

        _add(".claude/skills/iot-security-review/SKILL.md", """---
name: "iot-security-review"
description: "触发嵌入式与物联网安全审查"
---

# /iot-security-review

对设备端 / 嵌入式 / 物联网相关改动进行安全审查。

## 审查范围
- 设备鉴权、身份认证、token 管理
- 通信链路安全（加密、签名、防重放）
- OTA / 固件升级安全
- 硬编码密钥、默认口令、测试后门
- 配置文件、证书、token 存储安全
- 调试接口、管理接口暴露
- 模型文件加载安全
- GPIO / 外设控制边界
- 设备与平台契约一致性
- 资源管理、异常恢复、故障降级

## 执行
审查 firmware/ 目录下的改动：
```bash
git diff --name-only HEAD -- firmware/
```
然后逐文件审查，按照郭靖的输出格式给出 findings。

## 输出要求
- 每个问题按「严重级别 / 问题位置 / 问题描述 / 可能影响 / 修复建议」输出
- 即使没有发现问题，也要输出「未发现明显安全问题，残余风险为……」
- 需要硬件实测才能确认的风险，标注「需实测验证」
""")

        _add(".claude/hooks/remind-iot-security-review.sh", r"""#!/usr/bin/env bash
set -euo pipefail

command -v python3 >/dev/null 2>&1 || { echo "python3 not found, skipping hook"; exit 0; }

FILE_PATH=$(python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('input', {}).get('file_path', ''))
except: print('')
")

case "$FILE_PATH" in
    firmware/*|./firmware/*)
        echo '{"additionalContext": "⚠️ 你正在修改 firmware/ 下的代码。涉及鉴权、通信、OTA、密钥、外设控制等敏感逻辑时，完成后请通知郭靖进行嵌入式安全审查（/iot-security-review）"}'
        ;;
esac

exit 0
""", True)


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
    # .state/changelog.md 已删除 — git log 天然记录变更
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
    result = {{"status": "ok"}}
    try:
        from database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        result["database"] = "ok"
    except Exception as e:
        result["database"] = str(e)
        result["status"] = "degraded"
    return result
""")

    _add("backend/worker.py", f"""\"\"\"
{n} — Celery Worker
\"\"\"
import os

from celery import Celery

broker_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery("worker", broker=broker_url, backend=broker_url)

app.conf.update(
    task_soft_time_limit=7200,   # 踩坑清单第 4 条
    task_time_limit=7500,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@app.task
def example_task(name: str) -> str:
    \"\"\"示例任务 — 实际开发时替换为真正的异步任务。\"\"\"
    return f"Hello {{name}}"
""")

    # v4.2: database.py — DB 连接 + session
    _add("backend/database.py", """import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://app:changeme@localhost:5432/app_db",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    \"\"\"FastAPI Depends 用的数据库会话生成器。\"\"\"
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""")

    # v4.2: models.py — 真实可用的示例模型
    _add("backend/models.py", """from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
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
sqlalchemy.url = postgresql://app:changeme@localhost:5432/app_db

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
    data = resp.json()
    assert \"status\" in data
    # status 可能是 \"ok\" 或 \"degraded\"（取决于数据库是否可用）
    assert data[\"status\"] in (\"ok\", \"degraded\")
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
            "eslint": "^8",
            "eslint-config-next": "^14",
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

    # v4.2: ESLint 配置，让 npm run lint 直接跑不交互
    _add("frontend/.eslintrc.json", json.dumps({
        "extends": ["next/core-web-vitals"],
    }, indent=2, ensure_ascii=False))

    # 前端 public 目录（Dockerfile COPY 需要）
    _add("frontend/public/.gitkeep", "")


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
    _add("infra/docker/docker-compose.yml", f"""# 开发时只起数据库：docker compose up postgres redis -d

services:
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
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
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
      POSTGRES_PASSWORD: ${{POSTGRES_PASSWORD:-changeme}}
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
    # ── 联调辅助文件 ──
    _add("infra/checklist.md", """# 联调检查清单

> 每次联调前过一遍，打勾确认。

## 环境准备
- [ ] .env 文件已配置
- [ ] Docker 服务已启动
- [ ] 数据库已初始化（alembic upgrade head）

## 平台联调
- [ ] docker compose up 全部服务正常
- [ ] 前端页面可访问
- [ ] /health 接口返回 ok
- [ ] 数据库连通
- [ ] Redis 连通
- [ ] Nginx 代理正常
- [ ] 核心业务链路走通

## 设备联调（如有）
- [ ] 设备可接入
- [ ] 鉴权通过
- [ ] 数据上报成功
- [ ] 指令下发成功
- [ ] 心跳正常
- [ ] 契约字段一致

## 结论
- 联调结果：PASS / FAIL
- 阻塞点：
- 下一步：
""")

    _add("infra/report-template.md", """# 联调报告

- 日期：
- 联调范围：
- 联调环境：

## 已验证通过
-

## 未通过
- 链路：
- 现象：
- 根因：
- 临时绕过：
- 建议动作：

## 阻塞点
-

## 下一步
-
""")

    _add("infra/scripts/smoke-test.sh", """#!/bin/bash
# 联调冒烟测试 — 快速验证主链路
# 根据项目实际情况补充测试用例
set -e

echo "===== 联调冒烟测试 ====="

BASE_URL="${1:-http://localhost:8000}"

echo ""
echo "1. 后端 Health Check"
curl -sf "$BASE_URL/health" | python3 -m json.tool || { echo "❌ /health 失败"; exit 1; }
echo "✅ /health 正常"

echo ""
echo "2. 前端可访问"
curl -sf -o /dev/null http://localhost:3000 && echo "✅ 前端正常" || echo "❌ 前端不可访问"

echo ""
echo "3. 数据库连通（通过 /health 判断）"
DB_STATUS=$(curl -sf "$BASE_URL/health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('database','unknown'))" 2>/dev/null)
if [ "$DB_STATUS" = "ok" ]; then
    echo "✅ 数据库连通"
else
    echo "❌ 数据库状态: $DB_STATUS"
fi

echo ""
echo "===== 冒烟测试完成 ====="
""", True)

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
        "DATABASE_URL=postgresql://app:changeme@localhost:5432/app_db",
        "# 超轻量演示模式（不推荐正式开发）：",
        "# DATABASE_URL=sqlite:///./dev.db", "",
        "REDIS_URL=redis://localhost:6379/0",
        "CORS_ORIGINS=http://localhost:3000", "",
        "# PostgreSQL (docker-compose 使用)",
        "POSTGRES_USER=app",
        "POSTGRES_PASSWORD=changeme",
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

    # v4.2: 环境自检脚本
    _add("scripts/bootstrap_check.sh", """#!/bin/bash
# 项目环境自检
set -u

PASS=0
FAIL=0

check() {
    if eval "$2" > /dev/null 2>&1; then
        echo "  ✅ $1"
        PASS=$((PASS + 1))
    else
        echo "  ❌ $1 — $3"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo "===== 环境自检 ====="
echo ""

check ".env 文件存在" "[ -f .env ]" "运行: cp .env.example .env && vi .env"
check "Python >= 3.11" "python3 -c 'import sys; assert sys.version_info >= (3,11)'" "安装 Python 3.11+"
check "Node >= 18" "node -e 'process.exit(parseInt(process.version.slice(1)) < 18 ? 1 : 0)'" "安装 Node 18+"
check "Docker 可用" "docker info" "安装并启动 Docker"
check "docker compose 可用" "docker compose version" "升级 Docker 或安装 compose 插件"
check "PostgreSQL 容器可连接" "docker compose -f infra/docker/docker-compose.yml exec -T postgres pg_isready -U app" "运行: docker compose -f infra/docker/docker-compose.yml up postgres -d"
check "Redis 容器可连接" "docker compose -f infra/docker/docker-compose.yml exec -T redis redis-cli ping" "运行: docker compose -f infra/docker/docker-compose.yml up redis -d"

echo ""
echo "===== 结果：${PASS} 通过，${FAIL} 失败 ====="
echo ""
""", True)

    _add("scripts/state_cli.py", r"""#!/usr/bin/env python3
"""
    + '''"""
状态管理 CLI — 管理团队状态和决策。

用法：
    python scripts/state_cli.py team-status
    python scripts/state_cli.py decisions
    python scripts/state_cli.py decision-propose --title "用 Redis 做缓存" --proposed-by "乔峰"
    python scripts/state_cli.py decision-lock DEC-003
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
    """Print team status — 读取各目录 STATUS.md 的摘要。"""
    print("\\n===== 团队状态 =====\\n")
    status_files = {
        "backend": "backend/STATUS.md",
        "frontend": "frontend/STATUS.md",
        "infra": "infra/STATUS.md",
        "firmware": "firmware/STATUS.md",
        "architect": "ARCHITECT.md",
    }
    for role, path in status_files.items():
        full_path = Path(__file__).resolve().parent.parent / path
        if full_path.exists():
            content = full_path.read_text(encoding="utf-8")
            # 提取「进行中」section 的第一行作为摘要
            lines = content.split("\\n")
            summary = "—"
            in_section = False
            for line in lines:
                if "进行中" in line:
                    in_section = True
                    continue
                if in_section and line.strip() and not line.startswith("#"):
                    summary = line.strip()[:50]
                    break
            print(f"  {role:<12} {summary}")
        else:
            print(f"  {role:<12} （STATUS.md 不存在）")
    print()


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


def main():
    parser = argparse.ArgumentParser(description="项目状态管理 CLI")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("team-status", help="查看全员状态")

    sub.add_parser("decisions", help="列出所有决策")

    p = sub.add_parser("decision-propose", help="提议新决策")
    p.add_argument("--title", required=True)
    p.add_argument("--proposed-by", required=True)

    p = sub.add_parser("decision-lock", help="锁定决策")
    p.add_argument("decision_id")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    {
        "team-status": cmd_team_status,
        "decisions": cmd_decisions,
        "decision-propose": cmd_decision_propose,
        "decision-lock": cmd_decision_lock,
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

    # Sub-directory STATUS.md（不再生成子目录 CLAUDE.md — 信息已在 agent 定义中）
    n = info["project_name"]
    _add = lambda p, c, x=False: f.__setitem__(p, (c.strip() + "\n", x))

    for name, directory in [
        ("乔峰", "backend"),
        ("黄蓉", "frontend"),
        ("杨过", "firmware"),
        ("张三丰", "infra"),
    ]:
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
    1. cp .env.example .env && vi .env  # 修改密码等敏感配置
    2. bash scripts/bootstrap_check.sh    # 检查环境是否就绪
    3. git init && git add -A && git commit -m "init: 项目协作框架"

  启动各角色：
    架构师：cd ~/Projects/{d} && claude --agent 王重阳
    后端：  cd ~/Projects/{d} && claude --agent 乔峰
    前端：  cd ~/Projects/{d} && claude --agent 黄蓉
    运维：  cd ~/Projects/{d} && claude --agent 张三丰
    硬件：  cd ~/Projects/{d} && claude --agent 杨过
    安全审查：cd ~/Projects/{d} && claude --agent 一灯大师
    {'嵌入式安全：cd ~/Projects/' + d + ' && claude --agent 郭靖' if info['has_hardware'] else ''}

    查看所有角色：claude agents

  环境说明：
    默认使用 PostgreSQL（docker compose up postgres redis -d 即可）
    超轻量演示：修改 .env 中 DATABASE_URL 为 sqlite:///./dev.db
""")


if __name__ == "__main__":
    main()
