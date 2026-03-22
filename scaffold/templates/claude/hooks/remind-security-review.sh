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
    backend/main.py|backend/routers/*|backend/api/*|backend/endpoints/*|backend/auth*|backend/upload*)
        echo '{"additionalContext": "⚠️ 你正在修改后端接口层文件，涉及认证/权限/上传等敏感逻辑时，完成后请通知一灯大师进行安全审查（/security-review）"}'
        ;;
    infra/*|*/docker-compose*|*/nginx*|*/Dockerfile*)
        echo '{"additionalContext": "⚠️ 你正在修改基础设施配置，完成后请通知一灯大师进行安全审查，重点关注默认密码、开放端口、debug 模式"}'
        ;;
    .env.example|.env*)
        echo '{"additionalContext": "⚠️ 环境变量配置已变更，请确认无敏感信息硬编码，完成后通知一灯大师审查"}'
        ;;
    contracts/*|./contracts/*)
        echo '{"additionalContext": "⚠️ 契约变更可能影响联调安全（认证方式、字段校验规则等），完成后请通知一灯大师审查兼容性风险"}'
        ;;
esac

exit 0
