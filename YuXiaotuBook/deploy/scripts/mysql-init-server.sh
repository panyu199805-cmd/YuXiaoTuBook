#!/usr/bin/env bash
# 在 Ubuntu 服务器上安装 MySQL 并创建 yuxiaotu_book 库
# 用法：sudo ./scripts/mysql-init-server.sh

set -euo pipefail

DB_NAME="${MYSQL_DATABASE:-yuxiaotu_book}"
DB_USER="${MYSQL_USER:-root}"
DB_PASS="${MYSQL_PASSWORD:?请设置 MYSQL_PASSWORD 环境变量}"

echo "[mysql-init] 安装 mysql-server..."
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server

echo "[mysql-init] 创建数据库 $DB_NAME ..."
mysql -uroot <<SQL
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SQL

if [[ "$DB_USER" != "root" ]]; then
  mysql -uroot <<SQL
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
CREATE USER IF NOT EXISTS '${DB_USER}'@'127.0.0.1' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'127.0.0.1';
FLUSH PRIVILEGES;
SQL
else
  mysql -uroot <<SQL
ALTER USER 'root'@'localhost' IDENTIFIED BY '${DB_PASS}';
FLUSH PRIVILEGES;
SQL
fi

# 仅本机访问
CONF="/etc/mysql/mysql.conf.d/mysqld.cnf"
if grep -q "^bind-address" "$CONF"; then
  sed -i 's/^bind-address.*/bind-address = 127.0.0.1/' "$CONF"
else
  echo "bind-address = 127.0.0.1" >> "$CONF"
fi

systemctl restart mysql
echo "[mysql-init] 完成。root 密码已设为配置值，仅监听 127.0.0.1:3306"
