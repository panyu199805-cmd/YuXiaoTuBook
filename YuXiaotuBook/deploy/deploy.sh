#!/usr/bin/env bash
# 宇小兔每日读书 — 生产部署脚本（Linux 云服务器）
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ENV_FILE="${ENV_FILE:-.env}"
COMPOSE_FILE="docker-compose.prod.yml"

log() { echo "[deploy] $*"; }

if [[ ! -f "$ENV_FILE" ]]; then
  log "未找到 $ENV_FILE，正在从 .env.prod.example 复制..."
  cp .env.prod.example "$ENV_FILE"
  log "请编辑 $ENV_FILE 后重新运行本脚本"
  exit 1
fi

# shellcheck disable=SC1090
set -a
source "$ENV_FILE"
set +a

if [[ "${MYSQL_PASSWORD:-}" == "your_mysql_password" ]] \
  || [[ "${MYSQL_PASSWORD:-}" == "ChangeMe_Strong_Password_123!" ]] \
  || [[ "${DATABASE_URL:-}" == *"your_url_encoded_password"* ]] \
  || [[ "${JWT_SECRET:-}" == ChangeMe_* ]]; then
  log "请先在 $ENV_FILE 中修改 MYSQL_PASSWORD、DATABASE_URL 与 JWT_SECRET"
  exit 1
fi

if [[ -z "${DATABASE_URL:-}" ]] || [[ -z "${JDBC_DATABASE_URL:-}" ]]; then
  log "请在 $ENV_FILE 中设置 DATABASE_URL 与 JDBC_DATABASE_URL"
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  log "未安装 Docker，请先安装：https://docs.docker.com/engine/install/"
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  log "未安装 Node.js/npm，无法构建前端"
  exit 1
fi

log "构建前端..."
cd ../frontend
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi
npm run build
cd "$SCRIPT_DIR"

if [[ ! -d ../frontend/dist ]]; then
  log "前端构建失败：未生成 frontend/dist"
  exit 1
fi

log "启动 Docker 服务..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --build

log "等待 API 健康检查..."
for i in $(seq 1 30); do
  if docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T api \
    python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')" 2>/dev/null; then
    break
  fi
  sleep 2
done

PORT="${HTTP_PORT:-80}"
log "部署完成。"
log "  前台：http://${DOMAIN:-localhost}:${PORT}/"
log "  管理后台：http://${DOMAIN:-localhost}:${PORT}/admin/login"
log "  默认管理员（若已 seed）：admin / admin123456 — 上线后请立即修改"
log ""
log "首次部署初始化数据（宿主机 MySQL 已就绪后）："
log "  docker compose -f $COMPOSE_FILE --env-file $ENV_FILE --profile init run --rm seed"
log ""
log "MySQL 自动备份："
log "  chmod +x scripts/backup-mysql.sh && ./scripts/backup-mysql.sh"
