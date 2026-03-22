#!/usr/bin/env python3
"""
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
        f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        fcntl.flock(f, fcntl.LOCK_UN)


def cmd_team_status(args):
    """Print team status — 读取各目录 STATUS.md 的摘要。"""
    print("\n===== 团队状态 =====\n")
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
            lines = content.split("\n")
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
    print("\n===== 决策列表 =====\n")
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
