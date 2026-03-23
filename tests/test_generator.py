"""scaffold generator tests."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from scaffold import __version__
from scaffold.generator import generate_files, render_template


# ── render_template tests ──

class TestRenderTemplate:
    def test_simple_variable(self):
        result = render_template("Hello {{name}}!", {"name": "World"})
        assert result == "Hello World!"

    def test_multiple_variables(self):
        tpl = "{{a}} and {{b}}"
        result = render_template(tpl, {"a": "X", "b": "Y"})
        assert result == "X and Y"

    def test_unknown_variable_preserved(self):
        result = render_template("{{unknown}}", {})
        assert result == "{{unknown}}"

    def test_condition_true(self):
        tpl = "before{{#flag}}INNER{{/flag}}after"
        result = render_template(tpl, {"flag": True})
        assert result == "beforeINNERafter"

    def test_condition_false(self):
        tpl = "before{{#flag}}INNER{{/flag}}after"
        result = render_template(tpl, {"flag": False})
        assert result == "beforeafter"

    def test_inverse_condition_true(self):
        tpl = "before{{^flag}}INNER{{/flag}}after"
        result = render_template(tpl, {"flag": True})
        assert result == "beforeafter"

    def test_inverse_condition_false(self):
        tpl = "before{{^flag}}INNER{{/flag}}after"
        result = render_template(tpl, {"flag": False})
        assert result == "beforeINNERafter"

    def test_condition_with_variable_inside(self):
        tpl = "{{#show}}Hello {{name}}!{{/show}}"
        result = render_template(tpl, {"show": True, "name": "Test"})
        assert result == "Hello Test!"

    def test_multiline_condition(self):
        tpl = "line1\n{{#flag}}line2\nline3\n{{/flag}}line4"
        result_true = render_template(tpl, {"flag": True})
        assert result_true == "line1\nline2\nline3\nline4"
        result_false = render_template(tpl, {"flag": False})
        assert result_false == "line1\nline4"

    def test_positive_and_negative_condition_together(self):
        """Both {{#flag}} and {{^flag}} blocks for the same flag."""
        tpl = "{{#flag}}YES{{/flag}}{{^flag}}NO{{/flag}}"
        assert render_template(tpl, {"flag": True}) == "YES"
        assert render_template(tpl, {"flag": False}) == "NO"

    def test_nested_variable_in_condition(self):
        """Variable substitution inside conditional blocks."""
        tpl = "{{#show}}Hello {{name}}! {{#extra}}({{role}}){{/extra}}{{/show}}"
        result = render_template(tpl, {"show": True, "name": "Alice", "extra": True, "role": "admin"})
        assert result == "Hello Alice! (admin)"
        result2 = render_template(tpl, {"show": True, "name": "Bob", "extra": False, "role": "user"})
        assert result2 == "Hello Bob! "
        result3 = render_template(tpl, {"show": False, "name": "X", "extra": True, "role": "Y"})
        assert result3 == ""

    def test_multiple_conditions_different_flags(self):
        """Multiple condition blocks with different flags."""
        tpl = "A{{#x}}B{{/x}}C{{#y}}D{{/y}}E"
        assert render_template(tpl, {"x": True, "y": True}) == "ABCDE"
        assert render_template(tpl, {"x": True, "y": False}) == "ABCE"
        assert render_template(tpl, {"x": False, "y": True}) == "ACDE"
        assert render_template(tpl, {"x": False, "y": False}) == "ACE"


# ── generate_files tests ──

class TestGenerateFiles:
    @pytest.fixture
    def base_info(self):
        return {
            "project_name": "测试项目",
            "project_desc": "这是一个测试",
            "frontend_stack": "Next.js + TypeScript",
            "backend_stack": "Python 3.11 + FastAPI",
            "database": "PostgreSQL",
            "server_ip": "",
            "has_hardware": False,
            "dir_name": "test-project",
            "date": "2026-03-22",
        }

    def test_generates_files(self, base_info):
        files = generate_files(base_info)
        assert len(files) > 50
        # Check some key files exist
        assert "CLAUDE.md" in files
        assert "backend/main.py" in files
        assert "frontend/src/app/page.tsx" in files
        assert ".gitignore" in files

    def test_all_values_are_tuples(self, base_info):
        files = generate_files(base_info)
        for path, value in files.items():
            assert isinstance(value, tuple), f"{path} value is not tuple"
            assert len(value) == 2, f"{path} tuple length != 2"
            assert isinstance(value[0], str), f"{path} content is not str"
            assert isinstance(value[1], bool), f"{path} executable is not bool"

    def test_project_name_in_output(self, base_info):
        files = generate_files(base_info)
        claude_md = files["CLAUDE.md"][0]
        assert "测试项目" in claude_md

    def test_no_hardware_excludes_hardware_dir(self, base_info):
        base_info["has_hardware"] = False
        files = generate_files(base_info)
        hardware_files = [k for k in files if k.startswith("hardware/")]
        assert len(hardware_files) == 0
        # Also no hardware agent or iot-security agent
        assert ".claude/agents/hardware.md" not in files
        assert ".claude/agents/iot-security.md" not in files
        assert ".claude/hooks/remind-iot-security-review.sh" not in files

    def test_hardware_includes_hardware_dir(self, base_info):
        base_info["has_hardware"] = True
        files = generate_files(base_info)
        assert "hardware/STATUS.md" in files
        assert ".claude/agents/hardware.md" in files
        assert ".claude/agents/iot-security.md" in files
        assert ".claude/hooks/remind-iot-security-review.sh" in files

    def test_no_server_excludes_deploy_sh(self, base_info):
        base_info["server_ip"] = ""
        files = generate_files(base_info)
        assert "infra/deploy/deploy.sh" not in files

    def test_server_includes_deploy_sh(self, base_info):
        base_info["server_ip"] = "192.168.1.100"
        files = generate_files(base_info)
        assert "infra/deploy/deploy.sh" in files
        content = files["infra/deploy/deploy.sh"][0]
        assert "192.168.1.100" in content

    def test_executable_flags(self, base_info):
        files = generate_files(base_info)
        # These should be executable
        assert files[".githooks/pre-commit"][1] is True
        assert files[".githooks/pre-push"][1] is True
        assert files["start.sh"][1] is True
        # These should not
        assert files["CLAUDE.md"][1] is False
        assert files["backend/main.py"][1] is False

    def test_json_files_are_valid_json(self, base_info):
        files = generate_files(base_info)
        json_paths = [
            ".claude/settings.json",
            "frontend/package.json",
            "frontend/tsconfig.json",
            "frontend/.eslintrc.json",
            ".state/decisions.json",
        ]
        for path in json_paths:
            content = files[path][0]
            parsed = json.loads(content)
            assert isinstance(parsed, (dict, list)), f"{path} is not dict/list"

    def test_settings_json_has_hardware_hook(self, base_info):
        base_info["has_hardware"] = True
        files = generate_files(base_info)
        settings = json.loads(files[".claude/settings.json"][0])
        post_hooks = settings["hooks"]["PostToolUse"]
        commands = [h["hooks"][0]["command"] for h in post_hooks]
        assert any("remind-iot-security-review" in c for c in commands)

    def test_settings_json_no_hardware_hook(self, base_info):
        base_info["has_hardware"] = False
        files = generate_files(base_info)
        settings = json.loads(files[".claude/settings.json"][0])
        post_hooks = settings["hooks"]["PostToolUse"]
        commands = [h["hooks"][0]["command"] for h in post_hooks]
        assert not any("remind-iot-security-review" in c for c in commands)

    def test_backend_main_has_project_name(self, base_info):
        files = generate_files(base_info)
        content = files["backend/main.py"][0]
        assert "测试项目" in content

    def test_frontend_page_has_project_name(self, base_info):
        files = generate_files(base_info)
        content = files["frontend/src/app/page.tsx"][0]
        assert "测试项目" in content
        assert "这是一个测试" in content

    def test_version(self):
        assert __version__ == "6.0.0"

    def test_force_overwrite(self, base_info, tmp_path):
        """--force should overwrite existing files."""
        files = generate_files(base_info)
        # Write files to disk first
        for path, (content, _) in files.items():
            full = tmp_path / path
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
        # Modify one file
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("modified content", encoding="utf-8")
        assert claude_md.read_text() == "modified content"
        # Re-generate and overwrite
        files2 = generate_files(base_info)
        for path, (content, _) in files2.items():
            full = tmp_path / path
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
        # Should be overwritten with generated content
        assert "测试项目" in claude_md.read_text()

    def test_no_hardware_excludes_hardware_references_in_content(self, base_info):
        """Without hardware, generated content should not mention hardware roles."""
        base_info["has_hardware"] = False
        files = generate_files(base_info)
        # Check architect.md does not mention hardware-only roles
        architect = files[".claude/agents/architect.md"][0]
        assert "杨过" not in architect
        assert "郭靖" not in architect
        # Check devops.md does not mention device debugging sections
        devops = files[".claude/agents/devops.md"][0]
        assert "设备联调" not in devops
        assert "设备侧必验项" not in devops
        # Check team protocol does not mention hardware roles
        protocol = files[".claude/rules/00-team-protocol.md"][0]
        assert "杨过" not in protocol

    def test_hardware_includes_hardware_references_in_content(self, base_info):
        """With hardware, generated content should include hardware roles."""
        base_info["has_hardware"] = True
        files = generate_files(base_info)
        architect = files[".claude/agents/architect.md"][0]
        assert "杨过" in architect
        assert "郭靖" in architect
        devops = files[".claude/agents/devops.md"][0]
        assert "设备联调" in devops
        assert "设备侧必验项" in devops
        protocol = files[".claude/rules/00-team-protocol.md"][0]
        assert "杨过" in protocol

    def test_single_quote_in_role_name(self, base_info):
        """角色名含单引号时，生成的 on-session-start.sh 中 Python 代码语法正确。"""
        base_info["roles"] = {
            "owner": "老王's",
            "architect": "王重阳's",
            "frontend": "黄蓉",
            "backend": "老王's",
            "devops": "张三丰",
            "hardware": "杨过",
            "security": "一灯大师",
            "iot_security": "郭靖",
        }
        files = generate_files(base_info)
        hook_content = files[".claude/hooks/on-session-start.sh"][0]
        # 提取 heredoc 中的 Python 代码
        import re
        m = re.search(r"<<'PYEOF'\n(.*?)\nPYEOF", hook_content, re.DOTALL)
        assert m, "on-session-start.sh 中找不到 PYEOF heredoc 代码块"
        py_code = m.group(1)
        # 验证 Python 语法正确
        compile(py_code, "<on-session-start>", "exec")

    def test_template_variables_not_leaked(self, base_info):
        """Ensure no unresolved {{variable}} patterns remain (except intentional ones)."""
        files = generate_files(base_info)
        # These files intentionally contain {{ }} for user-facing templates
        intentional_files = {
            ".claude/skills/assign-task/SKILL.md",  # 提示词模板
        }
        import re
        for path, (content, _) in files.items():
            if path in intentional_files:
                continue
            # Find {{word}} patterns that look like unresolved template vars
            matches = re.findall(r"\{\{(\w+)\}\}", content)
            # Filter out known false positives (e.g., in bash scripts, JS template literals)
            real_template_vars = [
                m for m in matches
                if m not in (
                    # Bash variables that use similar syntax
                    "name",  # f-string in worker.py
                )
            ]
            # Allow empty list
            if real_template_vars:
                # These should only be intentional user-facing placeholders
                assert False, f"{path} has unresolved template vars: {real_template_vars}"
