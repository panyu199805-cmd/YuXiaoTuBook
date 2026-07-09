#!/usr/bin/env bash
# 宿主机 MySQL 自动备份（配合 cron）
# 用法：编辑 env/prod.env 后 ./scripts/backup-mysql.sh
# cron：0 3 * * * /usr/local/projects/yuxiaotu/app/YuXiaotuBook/deploy/scripts/backup-mysql.sh >> /usr/local/projects/yuxiaotu/logs/mysql-backup.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ "$DEPLOY_DIR" == */app/YuXiaotuBook/deploy ]]; then
  PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$DEPLOY_DIR/../../.." && pwd)}"
else
  PROJECT_ROOT="${PROJECT_ROOT:-/usr/local/projects/yuxiaotu}"
fi

ENV_FILE="${ENV_FILE:-}"
if [[ -z "$ENV_FILE" ]]; then
  if [[ -f "$PROJECT_ROOT/env/prod.env" ]]; then
    ENV_FILE="$PROJECT_ROOT/env/prod.env"
  elif [[ -f "$PROJECT_ROOT/env/.env" ]]; then
    ENV_FILE="$PROJECT_ROOT/env/.env"
  else
    ENV_FILE="$PROJECT_ROOT/env/prod.env"
  fi
fi
if [[ ! -f "$ENV_FILE" ]] && [[ -f "$DEPLOY_DIR/.env" ]]; then
  ENV_FILE="$DEPLOY_DIR/.env"
fi

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

BACKUP_DIR="${BACKUP_DIR:-/var/backups/yuxiaotu/mysql}"
KEEP_DAYS="${KEEP_DAYS:-14}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:?请设置 MYSQL_PASSWORD}"
MYSQL_DATABASE="${MYSQL_DATABASE:-yuxiaotu_book}"

mkdir -p "$BACKUP_DIR"
DATE=$(date +%Y%m%d_%H%M)
OUT="$BACKUP_DIR/${MYSQL_DATABASE}_${DATE}.sql.gz"

export MYSQL_PWD="$MYSQL_PASSWORD"
mysqldump -u"$MYSQL_USER" -h127.0.0.1 --single-transaction --routines --triggers "$MYSQL_DATABASE" | gzip > "$OUT"
unset MYSQL_PWD

find "$BACKUP_DIR" -name "${MYSQL_DATABASE}_*.sql.gz" -mtime +"$KEEP_DAYS" -delete
echo "[backup] OK $OUT"
