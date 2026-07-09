# Ubuntu 24.04.4 LTS 部署包说明

目标系统：**Ubuntu 24.04.4 LTS**（Noble Numbat）  
部署方式：**Docker Compose**（API + Java 交易 + Nginx）+ **宿主机 MySQL**

---

## 服务器目录布局

```
/usr/local/projects/yuxiaotu/
├── app/                               # 解压 / git clone 的代码
│   ├── YuXiaotuBook/
│   │   ├── backend/
│   │   ├── frontend/dist/
│   │   ├── deploy/                    # docker-compose、deploy.sh
│   │   └── scripts/
│   └── yuxiaotu-trade-service/
├── data/
│   ├── uploads/                       # 用户上传（持久化）
│   └── mysql-backup/                  # 可选
├── env/
│   └── .env                           # 生产配置（chmod 600）
└── logs/

/etc/mysql/          # MySQL 配置（apt）
/var/lib/mysql/      # MySQL 数据
/var/backups/yuxiaotu/mysql/   # 备份目录
/var/lib/docker/     # Docker 数据
```

---

## 方式 A：Git 拉取

```bash
sudo mkdir -p /usr/local/projects/yuxiaotu/{app,data/uploads,env,logs}
sudo mkdir -p /var/backups/yuxiaotu/mysql
cd /usr/local/projects/yuxiaotu/app
git clone https://github.com/panyu199805-cmd/YuXiaoTuBook.git .

cd YuXiaotuBook/deploy/ubuntu2404
sudo MYSQL_PASSWORD='你的强密码' ./install-all.sh

cd ..
./scripts/setup-server-dirs.sh
nano /usr/local/projects/yuxiaotu/env/.env
./deploy.sh
```

---

## 方式 B：上传部署包 tar.gz

**本机打包：**

```powershell
cd YuXiaotuBook\YuXiaotuBook\deploy
.\pack-release.ps1
```

**服务器：**

```bash
sudo mkdir -p /usr/local/projects/yuxiaotu/{app,data/uploads,data/mysql-backup,env,logs}
sudo mkdir -p /var/backups/yuxiaotu/mysql
sudo tar -xzf yuxiaotu-book-ubuntu2404-*.tar.gz -C /usr/local/projects/yuxiaotu/app

cd /usr/local/projects/yuxiaotu/app/YuXiaotuBook/deploy/ubuntu2404
sudo MYSQL_PASSWORD='你的强密码' ./install-all.sh

cd ..
./scripts/setup-server-dirs.sh
nano /usr/local/projects/yuxiaotu/env/.env
./deploy.sh
```

---

## .env 必填项

| 变量 | 说明 |
|------|------|
| `MYSQL_PASSWORD` | 宿主机 MySQL 密码 |
| `DATABASE_URL` | Python；密码 `@` → `%40` |
| `JDBC_DATABASE_URL` | Java JDBC 地址 |
| `JWT_SECRET` | ≥32 位，API 与 Java 相同 |
| `CORS_ORIGINS` | 站点 URL |
| `DOMAIN` | 域名或 IP |
| `UPLOAD_DATA_DIR` | 默认 `/usr/local/projects/yuxiaotu/data/uploads` |
| `BACKUP_DIR` | 默认 `/var/backups/yuxiaotu/mysql` |

---

## 常用命令

```bash
DEPLOY=/usr/local/projects/yuxiaotu/app/YuXiaotuBook/deploy
ENV=/usr/local/projects/yuxiaotu/env/.env

cd $DEPLOY

docker compose -f docker-compose.prod.yml --env-file $ENV ps
./deploy.sh
docker compose -f docker-compose.prod.yml --env-file $ENV up -d --build api trade
docker compose -f docker-compose.prod.yml --env-file $ENV --profile init run --rm seed
./scripts/backup-mysql.sh
```

---

## 防火墙与安全组

仅开放：**22、80、443**  
**不要**对公网开放 3306、8000、8081

详细说明见 [DEPLOY.md](../DEPLOY.md)
