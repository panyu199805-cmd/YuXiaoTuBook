#!/usr/bin/env bash
# Ubuntu 24.04 LTS — 安装 Docker Engine + Compose 插件
set -euo pipefail

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "[docker] 请使用 root 或 sudo 运行"
  exit 1
fi

. /etc/os-release
if [[ "${ID:-}" != "ubuntu" ]]; then
  echo "[docker] 警告：此脚本针对 Ubuntu，当前系统 ID=${ID:-unknown}"
fi

echo "[docker] 安装依赖..."
apt-get update
apt-get install -y ca-certificates curl gnupg

install -m 0755 -d /etc/apt/keyrings
if [[ ! -f /etc/apt/keyrings/docker.asc ]]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
fi

CODENAME="${VERSION_CODENAME:-noble}"
ARCH="$(dpkg --print-architecture)"
echo "deb [arch=${ARCH} signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${CODENAME} stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable docker
systemctl start docker

echo "[docker] 版本："
docker --version
docker compose version

if [[ -n "${SUDO_USER:-}" ]]; then
  usermod -aG docker "$SUDO_USER"
  echo "[docker] 已将用户 ${SUDO_USER} 加入 docker 组，重新登录 SSH 后生效"
fi

echo "[docker] 安装完成"
