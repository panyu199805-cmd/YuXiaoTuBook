#!/usr/bin/env bash
# 解压部署包后执行一次：修复 Windows 打包带来的 CRLF 与无执行权限
set -euo pipefail

ROOT="${1:-/usr/local/projects/yuxiaotu/app}"

if [[ ! -d "$ROOT" ]]; then
  echo "[fix] 目录不存在: $ROOT"
  exit 1
fi

log() { echo "[fix] $*"; }

while IFS= read -r -d '' f; do
  sed -i 's/\r$//' "$f"
  chmod +x "$f"
done < <(find "$ROOT" -type f -name '*.sh' -print0)

log "已处理 $(find "$ROOT" -type f -name '*.sh' | wc -l) 个 shell 脚本"
log "现在可执行："
log "  cd $ROOT/YuXiaotuBook/deploy/ubuntu2404"
log "  sudo MYSQL_PASSWORD='你的密码' ./install-all.sh"
