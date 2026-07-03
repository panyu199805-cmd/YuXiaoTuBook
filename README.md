# 宇小兔每日读书（yuxiaotu-book）

基于 Dev PRD v1.4 的一期 MVP 脚手架：氛围首页、书单、视频详情、登录收藏、模拟下单、管理后台。

## 技术栈

- **后端**：Python 3.8 + FastAPI 0.109 + Tortoise ORM + MySQL
- **前端**：Vue 3 + TypeScript + Vite + Pinia + Element Plus（仅 `/admin`）

## 快速启动

### 1. 启动 Docker 服务（MySQL + 后端 API）

```powershell
cd deploy
docker compose up -d mysql api
```

Docker Desktop 中显示：
- 项目组名：**YuXiaotuBookCustomer**
- 后端容器名：**YuXiaotuBook**（端口 8000）

- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/health
- 默认管理员：`admin` / `admin123456`

### 2. 本地开发（可选，不用 Docker 跑后端）

```powershell
cd backend
py -3.8 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
copy .env.example .env
python ..\scripts\seed.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端

```powershell
cd frontend
npm install
npm run dev
```

- 用户端：http://localhost:5188
- 管理后台：http://localhost:5188/admin/login

## 目录结构

```
yuxiaotu-book/
├── backend/          # FastAPI
├── frontend/         # Vue3（含 /admin）
├── deploy/           # docker-compose
├── scripts/seed.py   # 初始化数据
└── 开发文档/         # PRD（在上级 AIECWeb/开发文档）
```

## 一期功能

- [x] 首页氛围 + 热门书 + 分类
- [x] 书单筛选/搜索
- [x] 详情页视频播放
- [x] 注册登录 / 收藏
- [x] 下单 + 模拟支付（`MOCK_PAY_ENABLED=true`）
- [x] 管理后台 CRUD

## 注意事项

- 生产环境请设置 `MOCK_PAY_ENABLED=false`
- `seed.py` 含 `generate_schemas` 仅限本地首次初始化
- 正式迁移请使用 Aerich
