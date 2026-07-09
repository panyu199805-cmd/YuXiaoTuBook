#!/usr/bin/env bash
# Ubuntu 24.04 — 安装宿主机 MySQL 8（业务 Docker 连接 host.docker.internal）
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/../scripts/mysql-init-server.sh"
