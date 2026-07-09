#!/usr/bin/env bash
# Ubuntu 24.04 — 安装 Node.js 20（服务器上构建前端用；也可在本机构建 dist 后上传）
set -euo pipefail

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "[nodejs] 请使用 root 或 sudo 运行"
  exit 1
fi

if command -v node >/dev/null 2>&1; then
  echo "[nodejs] 已安装：$(node -v) $(npm -v)"
  exit 0
fi

apt-get update
apt-get install -y ca-certificates curl
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

echo "[nodejs] 安装完成：$(node -v) $(npm -v)"
