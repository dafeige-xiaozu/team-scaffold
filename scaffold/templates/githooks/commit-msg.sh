#!/bin/bash
# 确保 commit message 不为空且有最低质量
MSG=$(cat "$1")

if [ ${#MSG} -lt 10 ]; then
    echo "❌ commit message 太短（至少 10 个字符）" >&2
    exit 1
fi

# 禁止无意义的 commit message
case "$MSG" in
    fix|update|change|test|tmp|wip|"fix bug"|"update code")
        echo "❌ commit message 太笼统：'$MSG'，请描述具体改了什么" >&2
        exit 1
        ;;
esac

exit 0
