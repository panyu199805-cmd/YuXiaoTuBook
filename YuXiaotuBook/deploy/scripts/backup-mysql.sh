#!/usr/bin/env bash
# 宿主机 MySQL 自动备份（配合 cron）
# 用法：deploy/.env 中配置 MYSQL_* 后
#   chmod +x scripts/backup-mysql.sh
#   ./scripts/backup-mysql.sh
# cron：0 3 * * * /opt/YuXiaoTuBook/YuXiaotuBook/deploy/scripts/backup-mysql.sh >> /var/log/yuxiaotu-mysql-backup.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="${ENV_FILE:-$DEPLOY_DIR/.env}"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

BACKUP_DIR="${BACKUP_DIR:-/backup/mysql}"
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
