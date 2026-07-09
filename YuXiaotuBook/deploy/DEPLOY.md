# 宇小兔每日读书 — 生产部署指南

> **Ubuntu 24.04.4 LTS 快速入口** → [deploy/ubuntu2404/README.md](ubuntu2404/README.md)  
> **本机打部署包** → `deploy/pack-release.ps1`（Windows）或 `deploy/scripts/pack-release.sh`（Linux）

## 架构

```
浏览器 → Docker Nginx (:80)
           ├─ /              → frontend/dist（Vue 静态）
           ├─ /api/v1/orders|member → Java trade (:8081)
           └─ /api、/uploads、/placeholders → Python API (:8000)
宿主机 MySQL（127.0.0.1:3306，/var/lib/mysql）← Docker 经 host.docker.internal 连接
用户上传 → /usr/local/projects/yuxiaotu/data/uploads（bind mount，持久化）
```

**MySQL 用 apt 装在系统里（非 Docker）**，数据目录 `/var/lib/mysql`，配置 `/etc/mysql`。  
**Nginx 在 Docker 内**，无需单独安装 `/usr/local/nginx`。

---

## 服务器目录布局

```
/usr/local/projects/yuxiaotu/          # 项目根
├── app/                               # 代码（git clone 或 tar 解压）
│   ├── YuXiaotuBook/
│   └── yuxiaotu-trade-service/
├── data/
│   ├── uploads/                       # 用户上传（API 挂载）
│   └── mysql-backup/                  # 可选本地备份副本
├── env/
│   └── .env                           # 生产环境变量（chmod 600）
└── logs/                              # 备份/运维日志

/etc/mysql/                            # MySQL 配置（apt）
/var/lib/mysql/                        # MySQL 数据（apt 默认）
/var/backups/yuxiaotu/mysql/           # mysqldump 备份（推荐）
/var/lib/docker/                       # Docker 镜像/容器（系统默认）
```

---

## 0. 首次环境安装

### 创建目录

```bash
sudo mkdir -p /usr/local/projects/yuxiaotu/{app,data/uploads,data/mysql-backup,env,logs}
sudo mkdir -p /var/backups/yuxiaotu/mysql
```

### 上传代码（二选一）

**Git：**

```bash
cd /usr/local/projects/yuxiaotu/app
git clone https://github.com/panyu199805-cmd/YuXiaoTuBook.git .
```

**部署包：**

```bash
sudo tar -xzf yuxiaotu-book-ubuntu2404-*.tar.gz -C /usr/local/projects/yuxiaotu/app
```

### 安装 Docker / Node.js / MySQL

```bash
cd /usr/local/projects/yuxiaotu/app/YuXiaotuBook/deploy/ubuntu2404
sudo MYSQL_PASSWORD='你的强密码' ./install-all.sh
```

### 初始化目录与环境

```bash
cd /usr/local/projects/yuxiaotu/app/YuXiaotuBook/deploy
./scripts/setup-server-dirs.sh
nano /usr/local/projects/yuxiaotu/env/.env
```

`setup-server-dirs.sh` 会创建 `data/`、`env/`、`logs/`，并将 `deploy/.env` 软链到 `env/.env`。

---

## 1. 配置环境变量

编辑 `/usr/local/projects/yuxiaotu/env/.env`（模板见 `.env.prod.example`）。

必改项：

| 变量 | 说明 |
|------|------|
| `DOMAIN` | 你的域名或 IP |
| `MYSQL_USER` / `MYSQL_PASSWORD` | 宿主机 MySQL 账号 |
| `DATABASE_URL` | Python 用；密码含 `@` 须 URL 编码为 `%40` |
| `JDBC_DATABASE_URL` | Java 用，`host.docker.internal` |
| `JWT_SECRET` | ≥32 位随机串，**API 与 Java 共用** |
| `CORS_ORIGINS` | `https://你的域名` |
| `UPLOAD_DATA_DIR` | 默认 `/usr/local/projects/yuxiaotu/data/uploads` |
| `BACKUP_DIR` | 默认 `/var/backups/yuxiaotu/mysql` |
| `DEBUG` | `false` |
| `MOCK_PAY_ENABLED` | `false` |

**DATABASE_URL 示例**（密码 `Ab@c123`）：

```
MYSQL_PASSWORD=Ab@c123
DATABASE_URL=mysql://root:Ab%40c123@host.docker.internal:3306/yuxiaotu_book
```

---

## 2. 执行部署

```bash
cd /usr/local/projects/yuxiaotu/app/YuXiaotuBook/deploy
chmod +x deploy.sh scripts/*.sh
./deploy.sh
```

---

## 3. 首次初始化数据

```bash
docker compose -f docker-compose.prod.yml --env-file /usr/local/projects/yuxiaotu/env/.env --profile init run --rm seed
```

默认管理员：`admin` / `admin123456`（**上线后立即修改**）。

---

## 4. 验证

```bash
docker compose -f docker-compose.prod.yml --env-file /usr/local/projects/yuxiaotu/env/.env ps
curl -s http://127.0.0.1/api/health
```

浏览器访问：`http://你的域名/`、`http://你的域名/admin/login`

---

## Navicat 连接（SSH 隧道）

| 项 | 值 |
|----|-----|
| SSH | 服务器 IP + root/密钥 |
| 主机 | `127.0.0.1` |
| 端口 | `3306` |
| 用户名 | `root` |
| 密码 | `env/.env` 中的 `MYSQL_PASSWORD` |
| 数据库 | `yuxiaotu_book` |

`bind-address = 127.0.0.1`，勿对公网开放 3306。

---

## MySQL 自动备份

```bash
cd /usr/local/projects/yuxiaotu/app/YuXiaotuBook/deploy
./scripts/backup-mysql.sh

# 每天 3 点备份，保留 14 天
crontab -e
0 3 * * * /usr/local/projects/yuxiaotu/app/YuXiaotuBook/deploy/scripts/backup-mysql.sh >> /usr/local/projects/yuxiaotu/logs/mysql-backup.log 2>&1
```

备份目录：`/var/backups/yuxiaotu/mysql/`（可在 `.env` 中改 `BACKUP_DIR`）

---

## 本机构建前端 + 服务器只跑 Docker

**本机 Windows：**

```powershell
cd YuXiaotuBook\deploy
.\deploy.ps1
```

将 `release-dist.zip` 上传到服务器 `app/YuXiaotuBook/frontend/dist` 解压，再执行：

```bash
cd /usr/local/projects/yuxiaotu/app/YuXiaotuBook/deploy
./deploy.sh
```

---

## 可选：宿主机 Nginx（不用 Compose 里的 nginx）

1. 在 `docker-compose.prod.yml` 中注释 `nginx` 服务
2. 为 `api`、`trade` 映射本机端口：

```yaml
api:
  ports: ["127.0.0.1:8000:8000"]
trade:
  ports: ["127.0.0.1:8081:8081"]
```

3. 使用 `nginx/yuxiaotu.host.conf`，修改 `YOUR_DOMAIN` 后安装到系统 Nginx（`apt install nginx`）

---

## HTTPS

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d 你的域名.com
```

证书配置后，将 `.env` 中 `CORS_ORIGINS` 改为 `https://你的域名.com`，重启 API：

```bash
docker compose -f docker-compose.prod.yml --env-file /usr/local/projects/yuxiaotu/env/.env up -d api
```

---

## 日常更新

```bash
cd /usr/local/projects/yuxiaotu/app
git pull
cd YuXiaotuBook/deploy
./deploy.sh
```

仅后端变更：

```bash
docker compose -f docker-compose.prod.yml --env-file /usr/local/projects/yuxiaotu/env/.env up -d --build api trade
```

---

## 常见问题

| 问题 | 处理 |
|------|------|
| 前端 404 / 白屏 | 确认 `frontend/dist` 存在且 Nginx `try_files` 正确 |
| 登录/API 失败 | 检查 Nginx 代理与 `CORS_ORIGINS` |
| 订单/会员接口 502 | `docker logs yuxiaotu-trade-prod` |
| 上传图片丢失 | 确认 `data/uploads` 存在且 compose 已 bind mount |
| `npm run build` TS 报错 | 可临时 `npx vite build` 跳过类型检查 |

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `docker-compose.prod.yml` | 生产 Docker 编排（MySQL 在宿主机） |
| `.env.prod.example` | 环境变量模板 |
| `scripts/setup-server-dirs.sh` | 初始化服务器目录与 env 软链 |
| `deploy.sh` | 服务器一键部署 |
| `pack-release.ps1` / `scripts/pack-release.sh` | 打 Ubuntu 部署包 |
| `ubuntu2404/` | 安装 Docker / Node / MySQL |
| `scripts/mysql-init-server.sh` | 宿主机 MySQL 初始化 |
| `scripts/backup-mysql.sh` | MySQL 自动备份 |
| `deploy.ps1` | 本机构建 dist zip |
| `nginx/yuxiaotu.docker.conf` | Compose 内 Nginx |
| `nginx/yuxiaotu.host.conf` | 宿主机 Nginx 模板（可选） |
| `release/` | 部署包 tar.gz 输出目录 |
