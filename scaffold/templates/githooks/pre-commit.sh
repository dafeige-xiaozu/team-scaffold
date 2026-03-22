#!/bin/bash
# Git pre-commit hook — 自动模式下的关键防线
# 安装方式：git config core.hooksPath .githooks
set -e

echo "===== Pre-commit 检查 ====="

FAILED=0

# ── 1. 后端测试 ──
if git diff --cached --name-only | grep -q "^backend/"; then
    echo "[后端] 检测到 backend/ 变更，运行 pytest..."
    if [ -f backend/requirements.txt ]; then
        cd backend
        if command -v python3 >/dev/null 2>&1; then
            python3 -m pytest tests/ -q --tb=short 2>&1 || {
                echo "❌ pytest 失败，阻止提交" >&2
                FAILED=1
            }
        else
            echo "⚠️ python3 不可用，跳过后端测试"
        fi
        cd ..
    fi
fi

# ── 2. 前端构建检查 ──
if git diff --cached --name-only | grep -q "^frontend/"; then
    echo "[前端] 检测到 frontend/ 变更，运行 lint..."
    if [ -f frontend/package.json ] && [ -d frontend/node_modules ]; then
        cd frontend
        npm run lint --silent 2>&1 || {
            echo "❌ lint 失败，阻止提交" >&2
            FAILED=1
        }
        cd ..
    else
        echo "⚠️ 前端依赖未安装，跳过 lint"
    fi
fi

# ── 3. 后端 py_compile 检查 ──
if git diff --cached --name-only | grep -q "^backend/.*\.py$"; then
    echo "[后端] Python 语法检查..."
    while read f; do
        if [ -f "$f" ]; then
            python3 -m py_compile "$f" 2>&1 || {
                echo "❌ $f 语法错误，阻止提交" >&2
                FAILED=1
            }
        fi
    done < <(git diff --cached --name-only | grep "^backend/.*\.py$")
fi

{{#has_hardware}}# ── 4. hardware py_compile 检查 ──
if git diff --cached --name-only | grep -q "^hardware/.*\.py$"; then
    echo "[硬件] Python 语法检查..."
    while read f; do
        if [ -f "$f" ]; then
            python3 -m py_compile "$f" 2>&1 || {
                echo "❌ $f 语法错误，阻止提交" >&2
                FAILED=1
            }
        fi
    done < <(git diff --cached --name-only | grep "^hardware/.*\.py$")
fi

{{/has_hardware}}# ── 5. 契约同步检查 ──
if git diff --cached --name-only | grep -qE "^backend/(main\.py|routers/|api/|endpoints/)"; then
    if ! git diff --cached --name-only | grep -q "^contracts/"; then
        echo "⚠️ 警告：修改了后端接口层文件但未更新 contracts/CONTRACTS.md"
        echo "   如果本次改动涉及接口变更，请先更新契约文档"
    fi
fi

# ── 6. 敏感文件检查 ──
if git diff --cached --name-only | grep -qE "\.env$|\.env\.local$|credentials|secret|\.pem$|\.key$"; then
    echo "❌ 检测到敏感文件被提交，阻止提交" >&2
    echo "   匹配的文件："
    git diff --cached --name-only | grep -E "\.env$|\.env\.local$|credentials|secret|\.pem$|\.key$"
    FAILED=1
fi

# ── 7. 大文件检查 ──
while read f; do
    if [ -f "$f" ]; then
        SIZE=$(wc -c < "$f" 2>/dev/null || echo 0)
        if [ "$SIZE" -gt 10485760 ]; then  # 10MB
            echo "❌ $f 超过 10MB（${SIZE} bytes），阻止提交" >&2
            FAILED=1
        fi
    fi
done < <(git diff --cached --name-only)

if [ "$FAILED" -ne 0 ]; then
    echo ""
    echo "===== Pre-commit 检查未通过 ====="
    exit 1
fi

echo "===== Pre-commit 检查通过 ====="
exit 0
