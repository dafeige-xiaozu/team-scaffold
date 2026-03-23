#!/usr/bin/env bash
set -euo pipefail

command -v python3 >/dev/null 2>&1 || { echo "python3 not found, skipping hook"; exit 0; }

FILE_PATH=$(python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('input', {}).get('file_path', ''))
except: print('')
")

case "$FILE_PATH" in
    hardware/*|./hardware/*)
        echo '{"additionalContext": "⚠️ 你正在修改 hardware/ 下的代码。涉及鉴权、通信、OTA、密钥、外设控制等敏感逻辑时，完成后请通知{{role_iot_security}}进行嵌入式安全审查（/iot-security-review）"}'
        ;;
esac

exit 0
