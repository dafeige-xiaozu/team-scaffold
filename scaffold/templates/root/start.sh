#!/bin/bash
# 启动角色
# 用法：./start.sh 乔峰
#       ./start.sh 王重阳
set -e

AGENT="${1:?用法: ./start.sh <角色名>}"

# 工程师角色：全自动模式
# 架构师/审查员：正常模式（需要人工监督）
case "$AGENT" in
    {{eng_pattern}})
        echo "以自动模式启动 $AGENT ..."
        exec claude --agent "$AGENT" --dangerously-skip-permissions
        ;;
    {{review_pattern}})
        echo "以正常模式启动 $AGENT ..."
        exec claude --agent "$AGENT"
        ;;
    *)
        echo "未知角色: $AGENT"
        echo "可用角色: {{all_roles}}"
        exit 1
        ;;
esac
