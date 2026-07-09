#!/usr/bin/env bash
# 初始化生产服务器目录布局（/usr/local/projects/yuxiaotu）
# 用法：./scripts/setup-server-dirs.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ "$DEPLOY_DIR" == */app/YuXiaotuBook/deploy ]]; then
  PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$DEPLOY_DIR/../../.." && pwd)}"
else
  PROJECT_ROOT="${PROJECT_ROOT:-/usr/local/projects/yuxiaotu}"
fi

export PROJECT_ROOT

log() { echo "[setup] $*"; }

mkdir -p "$PROJECT_ROOT"/{data/uploads,data/mysql-backup,env,logs}
mkdir -p /var/backups/yuxiaotu/mysql

ENV_TARGET="$PROJECT_ROOT/env/prod.env"
DEPLOY_ENV_LINK="$DEPLOY_DIR/.env"

if [[ ! -f "$ENV_TARGET" ]] && [[ -f "$PROJECT_ROOT/env/.env" ]]; then
  mv "$PROJECT_ROOT/env/.env" "$ENV_TARGET"
  log "已将隐藏文件 env/.env 迁移为 env/prod.env"
fi

if [[ ! -f "$ENV_TARGET" ]]; then
  if [[ -f "$DEPLOY_DIR/.env.prod.example" ]]; then
    cp "$DEPLOY_DIR/.env.prod.example" "$ENV_TARGET"
    chmod 600 "$ENV_TARGET"
    log "已创建 $ENV_TARGET，请编辑 MYSQL_PASSWORD、JWT_SECRET 等后重新部署"
  elif [[ -f "$DEPLOY_DIR/.env" ]]; then
    cp "$DEPLOY_DIR/.env" "$ENV_TARGET"
    chmod 600 "$ENV_TARGET"
    log "已从 deploy/.env 复制到 $ENV_TARGET"
  fi
fi

if [[ -f "$ENV_TARGET" ]]; then
  ln -sf "$ENV_TARGET" "$DEPLOY_ENV_LINK"
fi

chmod 775 "$PROJECT_ROOT/data/uploads" 2>/dev/null || true

log "目录就绪："
log "  项目根：$PROJECT_ROOT"
log "  上传：  $PROJECT_ROOT/data/uploads"
log "  备份：  /var/backups/yuxiaotu/mysql（或 env 中 BACKUP_DIR）"
log "  环境：  $ENV_TARGET"
