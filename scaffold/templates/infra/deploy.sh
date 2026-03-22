#!/bin/bash
# 一键部署脚本
# 注意：需要在服务器上配置 deploy 用户，并设置好 SSH 免密登录
#   useradd -m deploy && usermod -aG docker deploy
#   在本地：ssh-copy-id deploy@{{server_ip}}
set -e

DEPLOY_START=$(date +%s)
TARGET=${1:-all}
SERVER=deploy@{{server_ip}}
DEPLOY_PATH="{{deploy_path}}"

echo "===== 部署 ====="
echo "目标: $TARGET"

# 定位项目根目录（deploy.sh 在 infra/deploy/ 下）
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_DIR"

# md5 兼容检测（macOS 没有 md5sum）
if command -v md5sum >/dev/null 2>&1; then
    MD5_CMD="md5sum"
elif command -v md5 >/dev/null 2>&1; then
    MD5_CMD="md5 -r"
else
    echo "WARNING: 无 md5 校验工具，跳过校验"
    MD5_CMD="echo SKIP"
fi

# ── 打包 + 本地 md5 ──
if [ "$TARGET" = "frontend" ] || [ "$TARGET" = "all" ]; then
    echo "打包前端..."
    tar czf /tmp/frontend-update.tar.gz --exclude='node_modules' --exclude='.next' --exclude='.git' -C frontend .
    LOCAL_FE_MD5=$($MD5_CMD /tmp/frontend-update.tar.gz | awk '{print $1}')
    echo "前端包 md5: $LOCAL_FE_MD5"
fi
if [ "$TARGET" = "backend" ] || [ "$TARGET" = "all" ]; then
    echo "打包后端..."
    tar czf /tmp/backend-update.tar.gz --exclude='__pycache__' --exclude='data' --exclude='*.db' --exclude='*.pt' --exclude='*.onnx' --exclude='.git' -C backend .
    LOCAL_BE_MD5=$($MD5_CMD /tmp/backend-update.tar.gz | awk '{print $1}')
    echo "后端包 md5: $LOCAL_BE_MD5"
fi

# ── 上传 ──
echo "上传..."
if [ "$TARGET" = "frontend" ]; then
    scp /tmp/frontend-update.tar.gz $SERVER:/tmp/
elif [ "$TARGET" = "backend" ]; then
    scp /tmp/backend-update.tar.gz $SERVER:/tmp/
else
    scp /tmp/frontend-update.tar.gz /tmp/backend-update.tar.gz $SERVER:/tmp/
fi

scp infra/docker/docker-compose.yml $SERVER:${DEPLOY_PATH}docker-compose.yml
scp .env $SERVER:${DEPLOY_PATH}.env 2>/dev/null || echo "(本地无 .env，跳过)"

# ── 服务器端部署 ──
echo "服务器部署..."
ssh $SERVER "TARGET=$TARGET DEPLOY_PATH=$DEPLOY_PATH LOCAL_FE_MD5=${LOCAL_FE_MD5:-} LOCAL_BE_MD5=${LOCAL_BE_MD5:-} bash -s" << 'EOF'
set -e

# md5 校验（踩坑清单第 7 条）
if [ -n "$LOCAL_FE_MD5" ]; then
    REMOTE_FE_MD5=$(md5sum /tmp/frontend-update.tar.gz | awk '{print $1}')
    if [ "$LOCAL_FE_MD5" != "$REMOTE_FE_MD5" ]; then
        echo "ERROR: 前端包 md5 不匹配！本地=$LOCAL_FE_MD5 远程=$REMOTE_FE_MD5" >&2
        exit 1
    fi
    echo "前端包 md5 校验通过"
fi
if [ -n "$LOCAL_BE_MD5" ]; then
    REMOTE_BE_MD5=$(md5sum /tmp/backend-update.tar.gz | awk '{print $1}')
    if [ "$LOCAL_BE_MD5" != "$REMOTE_BE_MD5" ]; then
        echo "ERROR: 后端包 md5 不匹配！本地=$LOCAL_BE_MD5 远程=$REMOTE_BE_MD5" >&2
        exit 1
    fi
    echo "后端包 md5 校验通过"
fi

# 备份旧目录（失败时可手动回滚：mv backend.bak.xxx backend）
TIMESTAMP=$(date +%s)
if [ "$TARGET" = "frontend" ] || [ "$TARGET" = "all" ]; then
    if [ -d "${DEPLOY_PATH}frontend" ]; then
        cp -r "${DEPLOY_PATH}frontend" "${DEPLOY_PATH}frontend.bak.$TIMESTAMP"
    fi
    cd ${DEPLOY_PATH}frontend && tar xzf /tmp/frontend-update.tar.gz
fi
if [ "$TARGET" = "backend" ] || [ "$TARGET" = "all" ]; then
    if [ -d "${DEPLOY_PATH}backend" ]; then
        cp -r "${DEPLOY_PATH}backend" "${DEPLOY_PATH}backend.bak.$TIMESTAMP"
    fi
    cd ${DEPLOY_PATH}backend && tar xzf /tmp/backend-update.tar.gz
fi

cd $DEPLOY_PATH
if [ "$TARGET" = "frontend" ]; then
    docker compose build frontend && docker compose up -d frontend
elif [ "$TARGET" = "backend" ]; then
    docker compose build backend celery-worker && docker compose up -d backend celery-worker
else
    docker compose build && docker compose up -d
fi

# 循环探测 health（最多等 60s，每 5s 探测一次）
echo "等待服务就绪..."
for i in $(seq 1 12); do
    if curl -s --max-time 5 http://localhost:8000/health > /dev/null 2>&1; then
        echo "health 检查通过"
        break
    fi
    if [ "$i" -eq 12 ]; then
        echo "WARNING: 60s 内 health 未就绪，请手动检查"
    else
        sleep 5
    fi
done

docker compose ps --format table

# 清理超过 3 天的旧备份
find $DEPLOY_PATH -maxdepth 1 -name "*.bak.*" -mtime +3 -exec rm -rf {} \;
EOF

DEPLOY_END=$(date +%s)
echo ""
echo "部署完成！耗时 $(((DEPLOY_END - DEPLOY_START) / 60))分$(((DEPLOY_END - DEPLOY_START) % 60))秒"
