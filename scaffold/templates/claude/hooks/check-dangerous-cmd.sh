#!/usr/bin/env bash
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
