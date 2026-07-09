#!/usr/bin/env bash
# 打包 Ubuntu 24.04 部署包（在仓库根目录 YuXiaoTuBook/ 下执行）
# 输出：YuXiaotuBook/deploy/release/yuxiaotu-book-ubuntu2404-YYYYMMDD.tar.gz
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
DEPLOY_DIR="$REPO_ROOT/YuXiaotuBook/deploy"
RELEASE_DIR="$DEPLOY_DIR/release"
STAMP=$(date +%Y%m%d)
ARCHIVE="yuxiaotu-book-ubuntu2404-${STAMP}.tar.gz"
FRONTEND_DIR="$REPO_ROOT/YuXiaotuBook/frontend"
PROJECT_ROOT="/usr/local/projects/yuxiaotu"

log() { echo "[pack] $*"; }

mkdir -p "$RELEASE_DIR"

if command -v npm >/dev/null 2>&1; then
  log "构建前端 dist..."
  cd "$FRONTEND_DIR"
  if [[ -f package-lock.json ]]; then npm ci; else npm install; fi
  if npm run build 2>/dev/null; then
    log "npm run build 成功"
  else
    log "npm run build 失败，改用 npx vite build"
    npx vite build
  fi
  cd "$REPO_ROOT"
else
  log "未检测到 npm，跳过前端构建（请确保 frontend/dist 已存在或到服务器上 build）"
fi

log "规范化 shell 脚本（LF）..."
while IFS= read -r -d '' f; do
  sed -i 's/\r$//' "$f" 2>/dev/null || sed -i '' 's/\r$//' "$f"
done < <(find "$REPO_ROOT/YuXiaotuBook" "$REPO_ROOT/yuxiaotu-trade-service" -type f -name '*.sh' -print0 2>/dev/null)

log "打包到 $RELEASE_DIR/$ARCHIVE ..."
tar -czf "$RELEASE_DIR/$ARCHIVE" \
  --exclude='YuXiaotuBook/frontend/node_modules' \
  --exclude='YuXiaotuBook/backend/.venv' \
  --exclude='YuXiaotuBook/backend/uploads' \
  --exclude='YuXiaotuBook/backend/__pycache__' \
  --exclude='**/__pycache__' \
  --exclude='yuxiaotu-trade-service/target' \
  --exclude='.git' \
  --exclude='deploy/.env' \
  --exclude='deploy/release/*.tar.gz' \
  --exclude='网站素材' \
  -C "$REPO_ROOT" \
  YuXiaotuBook \
  yuxiaotu-trade-service

cat > "$RELEASE_DIR/MANIFEST-${STAMP}.txt" <<EOF
宇小兔每日读书 — Ubuntu 24.04.4 部署包
打包时间: $(date -Iseconds)
归档文件: $ARCHIVE
项目根: $PROJECT_ROOT

1. 创建目录:
  sudo mkdir -p $PROJECT_ROOT/{app,data/uploads,data/mysql-backup,env,logs}
  sudo mkdir -p /var/backups/yuxiaotu/mysql

2. 解压代码:
  sudo tar -xzf $ARCHIVE -C $PROJECT_ROOT/app

2b. 修复脚本（若 ./install-all.sh 报 command not found）:
  bash $PROJECT_ROOT/app/YuXiaotuBook/deploy/scripts/fix-shell-scripts.sh

3. 安装环境:
  cd $PROJECT_ROOT/app/YuXiaotuBook/deploy/ubuntu2404
  sudo MYSQL_PASSWORD='你的密码' ./install-all.sh

4. 初始化目录与环境:
  cd $PROJECT_ROOT/app/YuXiaotuBook/deploy
  ./scripts/setup-server-dirs.sh
  nano $PROJECT_ROOT/env/.env

5. 部署:
  ./deploy.sh
EOF

log "完成：$RELEASE_DIR/$ARCHIVE"
log "清单：$RELEASE_DIR/MANIFEST-${STAMP}.txt"
ls -lh "$RELEASE_DIR/$ARCHIVE"
