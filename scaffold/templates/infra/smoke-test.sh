#!/bin/bash
# 联调冒烟测试 — 快速验证主链路
# 根据项目实际情况补充测试用例
set -e

echo "===== 联调冒烟测试 ====="

BASE_URL="${1:-http://localhost:8000}"

echo ""
echo "1. 后端 Health Check"
curl -sf "$BASE_URL/health" | python3 -m json.tool || { echo "❌ /health 失败"; exit 1; }
echo "✅ /health 正常"

echo ""
echo "2. 前端可访问"
curl -sf -o /dev/null http://localhost:3000 && echo "✅ 前端正常" || echo "❌ 前端不可访问"

echo ""
echo "3. 数据库连通（通过 /health 判断）"
DB_STATUS=$(curl -sf "$BASE_URL/health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('database','unknown'))" 2>/dev/null)
if [ "$DB_STATUS" = "ok" ]; then
    echo "✅ 数据库连通"
else
    echo "❌ 数据库状态: $DB_STATUS"
fi

echo ""
echo "===== 冒烟测试完成 ====="
