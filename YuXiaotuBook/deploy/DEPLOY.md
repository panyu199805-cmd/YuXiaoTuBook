# 宇小兔每日读书 — 生产部署指南

## 架构

```
浏览器 → Nginx (:80)
           ├─ /              → frontend/dist（Vue 静态）
           ├─ /api/v1/orders|member → Java trade (:8081)
           └─ /api、/uploads、/placeholders → Python API (:8000)
宿主机 MySQL（127.0.0.1:3306）← Docker 内 api / trade 经 host.docker.internal 连接
```

**MySQL 装在系统里（非 Docker）**，便于 Navicat 管理与 mysqldump 备份。

---

## 0. 服务器安装 MySQL（首次）

```bash
cd YuXiaoTuBook/YuXiaotuBook/deploy
sudo MYSQL_PASSWORD='你的强密码' ./scripts/mysql-init-server.sh
```

或手动安装 MySQL 后设置 root 密码，并创建库：

```sql
CREATE DATABASE yuxiaotu_book CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

`bind-address = 127.0.0.1`（勿对公网开放 3306）。

### Navicat 连接服务器数据库（SSH 隧道）

| 项 | 值 |
|----|-----|
| SSH | 服务器 IP + root/密钥 |
| 主机 | `127.0.0.1` |
| 端口 | `3306` |
| 用户名 | `root`（或你在 `.env` 中配置的 `MYSQL_USER`） |
| 密码 | 服务器 `deploy/.env` 里的 `MYSQL_PASSWORD` |
| 数据库 | `yuxiaotu_book` |

### 自动备份

```bash
cp .env.prod.example .env   # 确认 MYSQL_PASSWORD 等
chmod +x scripts/backup-mysql.sh
./scripts/backup-mysql.sh

# 每天 3 点备份，保留 14 天
crontab -e
0 3 * * * /opt/YuXiaoTuBook/YuXiaotuBook/deploy/scripts/backup-mysql.sh >> /var/log/yuxiaotu-mysql-backup.log 2>&1
```

备份目录默认：`/backup/mysql/`

---

## 方式一：一键 Docker 部署（推荐）

### 1. 服务器准备

- Ubuntu 22.04+，2 核 4G 起
- 安装 Docker、Docker Compose、Node.js 18+
- 安全组开放：**80**（及 **443** 若上 HTTPS）

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# 重新登录 SSH 后生效
```

### 2. 拉取代码

```bash
sudo mkdir -p /opt && cd /opt
git clone https://github.com/panyu199805-cmd/YuXiaoTuBook.git
cd YuXiaoTuBook/YuXiaotuBook/deploy
```

### 3. 配置环境变量

```bash
cp .env.prod.example .env
nano .env   # 修改域名、密码、JWT_SECRET
```

必改项：

| 变量 | 说明 |
|------|------|
| `DOMAIN` | 你的域名 |
| `MYSQL_USER` / `MYSQL_PASSWORD` | 宿主机 MySQL 账号（仅写在服务器 `.env`） |
| `DATABASE_URL` | Python 用；密码含 `@` 须 URL 编码为 `%40` |
| `JDBC_DATABASE_URL` | Java 用，`host.docker.internal` |
| `JWT_SECRET` | ≥32 位随机串，**API 与 Java 共用** |
| `CORS_ORIGINS` | `https://你的域名` |
| `DEBUG` | `false` |
| `MOCK_PAY_ENABLED` | `false` |

**DATABASE_URL 写法示例**（假设密码为 `Ab@c123`）：

```
MYSQL_PASSWORD=Ab@c123
DATABASE_URL=mysql://root:Ab%40c123@host.docker.internal:3306/yuxiaotu_book
```

### 4. 执行部署

```bash
chmod +x deploy.sh
./deploy.sh
```

### 5. 首次初始化数据（仅第一次）

```bash
docker compose -f docker-compose.prod.yml --env-file .env --profile init run --rm seed
```

默认管理员：`admin` / `admin123456`（**上线后立即修改**）。

### 6. 验证

```bash
docker compose -f docker-compose.prod.yml ps
curl -s http://127.0.0.1/api/health
```

浏览器访问：`http://你的域名/`、`http://你的域名/admin/login`

---

## 方式二：本机构建前端 + 服务器只跑 Docker

适合服务器不装 Node.js：

**本机 Windows：**

```powershell
cd YuXiaotuBook\deploy
.\deploy.ps1
```

将 `release-dist.zip` 上传到服务器 `frontend/dist` 解压，再在服务器执行：

```bash
cd YuXiaotuBook/deploy
cp .env.prod.example .env && nano .env
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```

---

## 方式三：宿主机 Nginx（不用 Compose 里的 nginx 服务）

1. 在 `docker-compose.prod.yml` 中注释或删除 `nginx` 服务
2. 为 `api`、`trade` 临时映射端口（仅本机）：

```yaml
api:
  ports: ["127.0.0.1:8000:8000"]
trade:
  ports: ["127.0.0.1:8081:8081"]
```

3. 使用 `nginx/yuxiaotu.host.conf`，修改 `YOUR_DOMAIN` 与 `root` 路径后安装到系统 Nginx

---

## HTTPS

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d 你的域名.com
```

证书配置后，将 `.env` 中 `CORS_ORIGINS` 改为 `https://你的域名.com`，重启 API：

```bash
docker compose -f docker-compose.prod.yml --env-file .env up -d api
```

---

## 日常更新

```bash
cd /opt/YuXiaoTuBook
git pull
cd YuXiaotuBook/deploy
./deploy.sh
```

仅后端变更、无需重建前端时：

```bash
docker compose -f docker-compose.prod.yml --env-file .env up -d --build api trade
```

---

## 常见问题

| 问题 | 处理 |
|------|------|
| 前端 404 / 白屏 | 确认 `frontend/dist` 存在且 Nginx `try_files` 配置正确 |
| 登录/API 失败 | 检查 Nginx 代理与 `CORS_ORIGINS` |
| 订单/会员接口 502 | `docker logs yuxiaotu-trade-prod` |
| 上传图片丢失 | `api_uploads` 卷是否挂载，勿删卷 |
| `npm run build` TS 报错 | 可临时 `npx vite build` 跳过类型检查 |

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `docker-compose.prod.yml` | 生产编排（MySQL 在宿主机） |
| `.env.prod.example` | 环境变量模板 |
| `scripts/mysql-init-server.sh` | 服务器安装 MySQL |
| `scripts/backup-mysql.sh` | 自动备份脚本 |
| `deploy.sh` | Linux 一键部署 |
| `deploy.ps1` | Windows 本机构建前端 |
| `nginx/yuxiaotu.docker.conf` | Compose 内 Nginx |
| `nginx/yuxiaotu.host.conf` | 宿主机 Nginx 模板 |
