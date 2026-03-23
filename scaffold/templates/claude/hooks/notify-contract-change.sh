#!/usr/bin/env bash
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
        echo '{"additionalContext": "⚠️ 契约文件已变更，请在任务汇报里标注需同步哪些角色（{{#has_hardware}}{{role_hardware}}/{{/has_hardware}}{{role_frontend}}/{{role_backend}}）"}'
        ;;
esac

exit 0
