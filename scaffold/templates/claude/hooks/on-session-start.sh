#!/usr/bin/env bash
set -euo pipefail

# 依赖：CLAUDE_AGENT_NAME 环境变量（Claude Code 用 --agent 启动时设置）
# 如果 Claude Code 实际用其他变量名，只改下面这一行

command -v python3 >/dev/null 2>&1 || { echo "python3 not found, skipping hook"; exit 0; }

# 从环境变量获取当前 agent 名称
AGENT_NAME="${CLAUDE_AGENT_NAME:-unknown}"

# 角色名 → 状态文件目录映射
STATUS_KEY=$(python3 - "${AGENT_NAME}" <<'PYEOF'
import json, sys
mapping = json.loads("""{{role_mapping_json}}""")
print(mapping.get(sys.argv[1], 'unknown'))
PYEOF
)

echo "=== 会话启动 ==="
echo "角色: ${AGENT_NAME}"

# 提示该角色应该读什么文件
case "$STATUS_KEY" in
    backend)      echo "📋 请先读: backend/STATUS.md + contracts/CONTRACTS.md" ;;
    frontend)     echo "📋 请先读: frontend/STATUS.md" ;;
    infra)        echo "📋 请先读: infra/STATUS.md + contracts/CONTRACTS.md" ;;
{{#has_hardware}}    hardware)     echo "📋 请先读: hardware/STATUS.md + contracts/CONTRACTS.md" ;;
{{/has_hardware}}    architect)    echo "📋 请先读: ARCHITECT.md" ;;
    security)     echo "📋 请先读: contracts/CONTRACTS.md + .env.example" ;;
{{#has_hardware}}    iot-security) echo "📋 请先读: contracts/CONTRACTS.md + hardware/STATUS.md" ;;
{{/has_hardware}}
    *)            echo "首次启动，无历史状态" ;;
esac

echo "=================="
