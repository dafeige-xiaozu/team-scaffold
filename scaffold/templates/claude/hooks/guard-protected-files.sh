#!/usr/bin/env bash
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
