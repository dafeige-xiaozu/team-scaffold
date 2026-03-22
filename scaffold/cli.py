"""scaffold CLI -- 参数解析 + 交互收集。"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from scaffold import __version__


def ask(prompt: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    val = input(f"  {prompt}{hint}: ").strip()
    return val or default


def collect_info(args) -> dict:
    """收集项目信息，支持交互和非交互两种模式。"""
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
    print(f"  大飞哥无敌战队 — 项目协作框架初始化 v{__version__}")
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


def main():
    parser = argparse.ArgumentParser(
        prog="scaffold",
        description="大飞哥无敌战队 — 项目协作框架初始化",
    )
    sub = parser.add_subparsers(dest="command")

    # scaffold init
    init_p = sub.add_parser("init", help="初始化项目框架")
    init_p.add_argument("--dry-run", action="store_true", help="只预览不写入")
    init_p.add_argument("--project-name", help="项目名称（跳过交互）")
    init_p.add_argument("--desc", help="项目描述（跳过交互）")
    init_p.add_argument("--server", help="服务器 IP")
    init_p.add_argument("--hardware", action="store_true", help="包含硬件端")
    init_p.add_argument("--force", action="store_true", help="覆盖已存在的文件")
    init_p.add_argument(
        "--output-dir",
        help="输出目录（默认当前目录）",
        default=None,
    )

    # scaffold version
    sub.add_parser("version", help="显示版本号")

    args = parser.parse_args()

    if args.command == "version":
        print(f"scaffold v{__version__}")
        return

    if args.command == "init":
        _run_init(args)
        return

    parser.print_help()


def _run_init(args):
    """执行 init 子命令。"""
    import stat

    from scaffold.generator import generate_files

    output_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
    output_dir = output_dir.resolve()

    info = collect_info(args)

    # 临时切到 output_dir 以保持 dir_name 兼容
    if args.output_dir:
        info["dir_name"] = output_dir.name

    files = generate_files(info)

    # Preview
    print()
    print("=" * 60)
    print(f"  项目：{info['project_name']}")
    print(f"  目录：{output_dir}")
    print(f"  文件：{len(files)} 个")
    print("=" * 60)
    print()

    exists = []
    for path in sorted(files.keys()):
        full = output_dir / path
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
    elif args.project_name and args.desc:
        pass  # non-interactive, skip confirmation
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
        full = output_dir / path
        if full.exists() and not args.force:
            continue
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        if executable:
            full.chmod(full.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"  + {path}")
        written += 1

    d = info["dir_name"]
    hw = info["has_hardware"]
    print(f"\n  ✅ 完成！生成了 {written} 个文件。")
    print(f"""
  下一步：
    1. cp .env.example .env && vi .env  # 修改密码等敏感配置
    2. bash scripts/bootstrap_check.sh    # 检查环境是否就绪
    3. git init && git add -A && git commit -m "init: 项目协作框架"
    4. git config core.hooksPath .githooks    # 启用 pre-commit / pre-push 自动检查

  启动各角色（工程师自动模式，架构师/审查员正常模式）：
    ./start.sh 王重阳     # 架构师
    ./start.sh 乔峰       # 后端
    ./start.sh 黄蓉       # 前端
    ./start.sh 张三丰     # 联调
    {'./start.sh 杨过       # 硬件' if hw else ''}
    ./start.sh 一灯大师   # 安全审查
    {'./start.sh 郭靖       # 嵌入式安全' if hw else ''}

    查看所有角色：claude agents

  环境说明：
    默认使用 PostgreSQL（docker compose up postgres redis -d 即可）
    超轻量演示：修改 .env 中 DATABASE_URL 为 sqlite:///./dev.db
""")
