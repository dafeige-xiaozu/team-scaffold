#!/bin/bash
# 项目环境自检
set -u

PASS=0
FAIL=0

check() {
    if eval "$2" > /dev/null 2>&1; then
        echo "  ✅ $1"
        PASS=$((PASS + 1))
    else
        echo "  ❌ $1 — $3"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo "===== 环境自检 ====="
echo ""

check ".env 文件存在" "[ -f .env ]" "运行: cp .env.example .env && vi .env"
check "Python >= 3.11" "python3 -c 'import sys; assert sys.version_info >= (3,11)'" "安装 Python 3.11+"
check "Node >= 18" "node -e 'process.exit(parseInt(process.version.slice(1)) < 18 ? 1 : 0)'" "安装 Node 18+"
check "Docker 可用" "docker info" "安装并启动 Docker"
check "docker compose 可用" "docker compose version" "升级 Docker 或安装 compose 插件"
check "PostgreSQL 容器可连接" "docker compose -f infra/docker/docker-compose.yml exec -T postgres pg_isready -U app" "运行: docker compose -f infra/docker/docker-compose.yml up postgres -d"
check "Redis 容器可连接" "docker compose -f infra/docker/docker-compose.yml exec -T redis redis-cli ping" "运行: docker compose -f infra/docker/docker-compose.yml up redis -d"

echo ""
echo "===== 结果：${PASS} 通过，${FAIL} 失败 ====="
echo ""
