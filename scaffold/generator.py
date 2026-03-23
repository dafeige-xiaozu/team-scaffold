"""scaffold generator -- 模板引擎 + 文件生成。

模板系统：
- {{variable}} -- 变量替换
- {{#condition}}...{{/condition}} -- 条件块（条件为真时保留）
- {{^condition}}...{{/condition}} -- 反向条件块（条件为假时保留）

JSON 文件由 Python dict 生成（manifest 中标记 "generator"），不走模板。
"""

import json
import re
from importlib import resources
from pathlib import Path

from scaffold import DEFAULT_ROLES, DEFAULT_TEAM_NAME


def _load_manifest() -> dict:
    """加载 manifest.json。"""
    tpl_dir = resources.files("scaffold") / "templates"
    manifest_path = tpl_dir / "manifest.json"
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _load_template(name: str) -> str:
    """从 scaffold/templates/ 加载模板文件。"""
    tpl_dir = resources.files("scaffold") / "templates"
    tpl_path = tpl_dir / name
    return tpl_path.read_text(encoding="utf-8")


def render_template(template: str, variables: dict) -> str:
    """渲染模板：变量替换 + 条件块。

    处理顺序：
    1. 条件块 {{#cond}}...{{/cond}} 和 {{^cond}}...{{/cond}}
    2. 变量替换 {{variable}}
    """
    text = template

    # 条件块（支持嵌套，从内到外处理）
    # {{#condition}}content{{/condition}} -- 条件为真时保留 content
    max_iterations = 20
    for _ in range(max_iterations):
        match = re.search(
            r"\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}",
            text,
            re.DOTALL,
        )
        if not match:
            # 也检查反向条件
            match_inv = re.search(
                r"\{\{\^(\w+)\}\}(.*?)\{\{/\1\}\}",
                text,
                re.DOTALL,
            )
            if not match_inv:
                break
            cond_name = match_inv.group(1)
            inner = match_inv.group(2)
            cond_val = variables.get(cond_name, False)
            if cond_val:
                text = text[: match_inv.start()] + text[match_inv.end() :]
            else:
                text = text[: match_inv.start()] + inner + text[match_inv.end() :]
            continue

        cond_name = match.group(1)
        inner = match.group(2)
        cond_val = variables.get(cond_name, False)
        if cond_val:
            text = text[: match.start()] + inner + text[match.end() :]
        else:
            text = text[: match.start()] + text[match.end() :]

    # 变量替换
    def _replace_var(m):
        key = m.group(1)
        return str(variables.get(key, m.group(0)))

    text = re.sub(r"\{\{(\w+)\}\}", _replace_var, text)

    return text


# ─── JSON 生成器 ───────────────────────────────────────────────────────────────

def _gen_settings_json(info: dict) -> str:
    """生成 .claude/settings.json。"""
    settings = {
        "permissions": {
            "allow": [
                "Bash(python scripts/state_cli.py *)",
                "Bash(pip freeze *)",
                "Bash(pytest *)",
                "Bash(bash scripts/bootstrap_check.sh)",
                "Bash(bash infra/scripts/smoke-test.sh *)",
                "Bash(git log *)",
                "Bash(git status *)",
                "Bash(git diff *)",
                "Bash(git show *)",
                "Bash(cd *)",
                "Bash(ls *)",
                "Bash(cat *)",
                "Bash(docker compose *)",
                "Bash(docker build *)",
                "Bash(alembic *)",
                "Bash(npm run *)",
                "Bash(npm install *)",
                "Bash(uvicorn *)",
                "Bash(curl *)",
                "Bash(python3 *)",
                "Bash(pip install *)",
                "Bash(git add *)",
                "Bash(git commit *)",
                "Bash(git push origin main)",
            ],
            "deny": [
                "Edit(./.state/**)",
                "Write(./.state/**)",
                "Bash(rm -rf /)",
                "Bash(rm -rf .)",
                "Bash(rm -rf ~)",
                "Bash(git push --force *)",
                "Bash(git commit * --no-verify *)",
                "Bash(git commit --no-verify *)",
                "Bash(git push * --no-verify *)",
                "Bash(git reset --hard *)",
                "Bash(git checkout -- .)",
                "Bash(git clean -f *)",
                "Bash(git branch -D *)",
                "Bash(rm -rf backend/)",
                "Bash(rm -rf frontend/)",
                "Bash(rm -rf infra/)",
                "Bash(rm -rf hardware/)",
                "Bash(rm -rf node_modules/)",
                "Bash(docker system prune *)",
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
            ],
        },
    }

    if info["has_hardware"]:
        settings["hooks"]["PostToolUse"].append({
            "matcher": "Write|Edit",
            "hooks": [{"type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/remind-iot-security-review.sh"}],
        })

    return json.dumps(settings, indent=2, ensure_ascii=False) + "\n"


def _gen_package_json(info: dict) -> str:
    """生成 frontend/package.json。"""
    d = info["dir_name"]
    data = {
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
    }
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _gen_tsconfig_json(info: dict) -> str:
    """生成 frontend/tsconfig.json。"""
    data = {
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
    }
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _gen_eslintrc_json(info: dict) -> str:
    """生成 frontend/.eslintrc.json。"""
    return json.dumps({"extends": ["next/core-web-vitals"]}, indent=2, ensure_ascii=False) + "\n"


def _gen_decisions_json(info: dict) -> str:
    """生成 .state/decisions.json。"""
    from datetime import datetime, timezone
    roles = info.get("roles", DEFAULT_ROLES)
    now = datetime.now(timezone.utc).isoformat()
    data = [
        {
            "id": "DEC-001",
            "title": "时间统一 UTC ISO 8601（Z 结尾），前端转本地时间",
            "status": "locked",
            "proposed_by": roles["architect"],
            "proposed_at": now,
            "locked_at": now,
        },
        {
            "id": "DEC-002",
            "title": "pip/npm 统一国内镜像源（清华/淘宝）",
            "status": "locked",
            "proposed_by": roles["architect"],
            "proposed_at": now,
            "locked_at": now,
        },
    ]
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


# Generator registry
_GENERATORS = {
    "settings_json": _gen_settings_json,
    "package_json": _gen_package_json,
    "tsconfig_json": _gen_tsconfig_json,
    "eslintrc_json": _gen_eslintrc_json,
    "decisions_json": _gen_decisions_json,
}


# ─── 主生成逻辑 ───────────────────────────────────────────────────────────────

def generate_files(info: dict) -> dict:
    """根据 info 生成所有文件。

    返回 {relative_path: (content, executable)}。
    """
    manifest = _load_manifest()
    files = {}

    # 构建模板变量
    variables = _build_variables(info)

    for entry in manifest["files"]:
        output_path = entry["output"]

        # 条件过滤
        condition = entry.get("condition")
        if condition:
            negate = condition.startswith("!")
            cond_key = condition.lstrip("!")
            cond_val = bool(variables.get(cond_key, False))
            if negate:
                cond_val = not cond_val
            if not cond_val:
                continue

        executable = entry.get("executable", False)

        # 渲染输出路径中的变量（虽然当前没有，但保留扩展性）
        output_path = render_template(output_path, variables)

        generator = entry.get("generator")
        if generator:
            # 使用 Python 生成器
            gen_func = _GENERATORS[generator]
            content = gen_func(info)
        else:
            # 使用模板文件
            template_name = entry["template"]
            template = _load_template(template_name)
            content = render_template(template, variables)

        files[output_path] = (content, executable)

    return files


def _build_role_mapping_json(roles: dict, has_hardware: bool) -> str:
    """构建角色名→状态目录的 JSON 字符串，用于 shell 模板中安全传递给 Python。"""
    mapping = {
        roles["architect"]: "architect",
        roles["backend"]: "backend",
        roles["frontend"]: "frontend",
        roles["devops"]: "infra",
        roles["security"]: "security",
    }
    if has_hardware:
        mapping[roles["hardware"]] = "hardware"
        mapping[roles["iot_security"]] = "iot-security"
    return json.dumps(mapping, ensure_ascii=False)


def _build_variables(info: dict) -> dict:
    """从 info 构建模板变量字典。"""
    ip = info["server_ip"]
    d = info["dir_name"]
    roles = info.get("roles", DEFAULT_ROLES)
    team_name = info.get("team_name", DEFAULT_TEAM_NAME)

    deploy_rule = (
        "所有部署走 infra/deploy/deploy.sh"
        if ip
        else "部署方案待服务器确定后配置"
    )
    deploy_path = f"/opt/{d}/" if ip else ""

    red_line_1 = (
        "禁止直接改服务器文件，所有部署走 `infra/deploy/deploy.sh`"
        if ip
        else "禁止直接改服务器文件，部署脚本待服务器确定后生成（`scaffold init --server <IP> --force`）"
    )

    r = roles  # shorthand

    hw_roles_assign = (
        f"| {r['hardware']} | 设备固件 hardware/ |\n| {r['devops']} | 部署联调 infra/ |\n| {r['security']} | 平台安全审查 |\n| {r['iot_security']} | 嵌入式安全审查 |"
        if info["has_hardware"]
        else f"| {r['devops']} | 部署联调 infra/ |\n| {r['security']} | 平台安全审查 |"
    )

    eng_pattern = (
        f"{r['backend']}|{r['frontend']}|{r['devops']}|{r['hardware']}"
        if info["has_hardware"]
        else f"{r['backend']}|{r['frontend']}|{r['devops']}"
    )
    review_pattern = (
        f"{r['architect']}|{r['security']}|{r['iot_security']}"
        if info["has_hardware"]
        else f"{r['architect']}|{r['security']}"
    )
    all_roles = (
        f"{r['backend']} {r['frontend']} {r['devops']} {r['hardware']} {r['architect']} {r['security']} {r['iot_security']}"
        if info["has_hardware"]
        else f"{r['backend']} {r['frontend']} {r['devops']} {r['architect']} {r['security']}"
    )

    return {
        "project_name": info["project_name"],
        "project_desc": info["project_desc"],
        "frontend_stack": info["frontend_stack"],
        "backend_stack": info["backend_stack"],
        "database": info["database"],
        "server_ip": ip,
        "dir_name": d,
        "date": info["date"],
        "deploy_path": deploy_path,
        "deploy_rule": deploy_rule,
        "red_line_1": red_line_1,
        "has_hardware": info["has_hardware"],
        "has_server": bool(ip),
        "hw_roles_assign": hw_roles_assign,
        "eng_pattern": eng_pattern,
        "review_pattern": review_pattern,
        "all_roles": all_roles,
        "team_name": team_name,
        # 角色名模板变量
        "role_owner": r["owner"],
        "role_architect": r["architect"],
        "role_frontend": r["frontend"],
        "role_backend": r["backend"],
        "role_devops": r["devops"],
        "role_hardware": r["hardware"],
        "role_security": r["security"],
        "role_iot_security": r["iot_security"],
        # JSON 序列化的角色映射，避免在 shell 模板中拼 Python 字符串导致注入
        "role_mapping_json": _build_role_mapping_json(roles, info["has_hardware"]),
    }
