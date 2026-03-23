#!/bin/bash
# Git pre-push hook — 推送前最后防线
set -e

echo "===== Pre-push 检查 ====="

# 1. 检测 force push（通过比较新旧 ref）
while read local_ref local_sha remote_ref remote_sha; do
    if [ "$remote_sha" != "0000000000000000000000000000000000000000" ] && \
       [ "$local_sha" != "0000000000000000000000000000000000000000" ]; then
        # 检查本地提交是否包含远程 HEAD，不包含说明是 force push
        if ! git merge-base --is-ancestor "$remote_sha" "$local_sha" 2>/dev/null; then
            echo "❌ 检测到 non-fast-forward push（疑似 force push），阻止推送" >&2
            echo "   如果确实需要，请联系{{role_owner}}确认" >&2
            exit 1
        fi
    fi
done

# 2. 后端全量测试（push 前跑完整测试，不只是增量）
if [ -f backend/requirements.txt ] && [ -d backend/tests ]; then
    echo "[后端] 运行完整测试..."
    cd backend
    python3 -m pytest tests/ -q --tb=short 2>&1 || {
        echo "❌ 后端测试失败，阻止推送" >&2
        exit 1
    }
    cd ..
fi

# 3. 前端完整构建（push 前确认能 build）
if [ -f frontend/package.json ] && [ -d frontend/node_modules ]; then
    echo "[前端] 运行构建检查..."
    cd frontend
    npm run build --silent 2>&1 || {
        echo "❌ 前端构建失败，阻止推送" >&2
        exit 1
    }
    cd ..
fi

echo "===== Pre-push 检查通过 ====="
exit 0
