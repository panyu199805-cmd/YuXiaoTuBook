# 宇小兔每日读书网站 · 开发需求文档（Dev PRD）

| 项目 | 说明 |
|------|------|
| 文档版本 | **v1.8-dev（开发者定稿 · 可行性与合理性复核）** |
| 更新日期 | 2026-07-02 |
| **开发者** | **潘宇**（单人全栈 · Java 5 年 + Python） |
| 开发模式 | 单人全栈 |
| 本机 Python | **3.8.10**（MVP 锁定；扩展期再升 3.11，见 §3.4） |
| 基于原文档 | 《宇小兔每日读书网站 · 产品需求文档（PRD）｜光厂视觉风格》 |
| 关联文档 | 《一期完整初始化脚手架代码（可直接运行）》· **[《技术选型.md》](./技术选型.md)（Python/Java 执行定版）** · [《技术选型定版.md》](./技术选型定版.md)（架构与阶段） |
| 文档用途 | 单人开发开工手册 + 扩展架构准绳 |
| 规模目标 | 百万注册用户；峰值读 5k～20k QPS（见 §十六） |
| 优化原则 | 技术可落地、需求无矛盾、可交付、可扩展、验收可测试 |

---

## 〇、快速摘要（1 分钟读完）

| 问题 | 答案 |
|------|------|
| 一期做什么？ | 氛围首页 + 书单 + 视频详情 + 登录收藏 + 模拟下单 + 管理后台 |
| 二期核心（已实现）？ | 每日专栏 + 会员模拟开通 + 游客 3 分钟试看 + 浏览记录 + Admin 每日/会员 |
| v1.5（已实现）？ | 个人中心 `/user/center`、读书喜好（最多 8 分类）、购书收发货、Admin 发货 |
| **v1.6（已实现）？** | **Admin 用户管理**：省/市树形分组，查看会员/收藏/图书订单 |
| 仍未做？ | 真实支付、AI、看板、HLS 服务端鉴权、偏好推荐算法、订单超时取消 |
| 视频要不要登录？ | **游客 3 分钟试看**（前端截断）；**登录全片**；MP4 可被直链绕过（S3 解决） |
| 技术栈（现网）？ | Vue3 + FastAPI + Python **3.8** + MySQL（MinIO/Redis **S1 起补齐**） |
| 项目目录？ | `Customer-YuXiaotuBook/backend` + `frontend`（用户端 + `/admin`） |
| 本地端口？ | API **8000**；前台 **5188**；Swagger `/docs` |
| 管理后台怎么进？ | **仅** `http://localhost:5188/admin/login`（顶栏不暴露） |
| 个人中心怎么进？ | 登录后顶栏 **「个人中心」** → `/user/center` |
| 用户管理怎么进？ | Admin 登录 → 左侧 **「用户管理」** → `/admin/users` |
| 首页风格（已实现）？ | 光厂风 Hero：**视频/图片背景** + 悬浮搜索 + 右下角客服 |
| 后端语言策略？ | **Python 为主**（Admin/运营/AI）+ **Java 补交易**（订单/支付，S2 起） |
| 百万用户靠什么？ | **CDN + Redis + MySQL 主从** 先于拆微服务；详见 **§十六** |
| 扩展详案在哪？ | **[《技术选型定版.md》](./技术选型定版.md)**（单人实施以其中 §十一 为准） |

---

## 一、需求评审与优化记录

### 1.1 v1.0 → v1.1（摘要）

原 PRD 中光厂 1:1 对标、全站视频背景、必绑视频、支付未定义等问题，已在 v1.1 中收敛。详见 Git 历史或备份。

### 1.2 三次评审优化（v1.2，本次）

| # | 议题 | v1.1 问题 | v1.2 决策 |
|---|------|-----------|-----------|
| 1 | **视频权限表述矛盾** | 5.1 写「登录看全片」，6.4/7.3 写游客 3 分钟引导，且 MP4 无法 enforcement | **一期取消观看门槛**：全员免费看全片；登录仅用于收藏/下单；会员限观看二期再做 |
| 2 | **`play-auth` 过度设计** | 一期返回 `max_duration` 但无法真正截流 | 一期 `play-auth` 仅返回 `video_url`；去掉 `max_duration` |
| 3 | **库存扣减时机未定义** | 只说事务扣库存，未说何时扣 | **支付成功时扣库存**；下单仅校验库存充足 |
| 4 | **未支付订单占库存** | 可能导致恶意占单 | 订单 30 分钟未支付自动 `cancelled`（定时任务可二期；一期后台可手动取消） |
| 5 | **管理后台方案未锁定** | 三种方案并存，开发无从下手 | 团队版：`admin/` 独立；**单人版：合并进 `frontend`（§十五）** |
| 6 | **模拟支付上生产风险** | 任何人可刷「支付成功」 | 仅当 `MOCK_PAY_ENABLED=true` 时开放；生产默认 `false` |
| 7 | **HTTP 状态码混乱** | body.code 与 HTTP status 映射表易误解 | **统一**：HTTP 状态与语义一致（401→401）；body.code 同步 |
| 8 | **MySQL 异步驱动缺失** | 只写 pymysql，Tortoise 异步需 asyncmy | `requirements` 使用 `asyncmy` + `tortoise-orm` |
| 9 | **自研 VideoPlayer 范围不清** | 易做成重型播放器 | 一期基于 **原生 `<video>`** + 薄封装；不自研播放内核 |
| 10 | **浏览记录写入时机** | 未定义 | 进入详情页 `GET /books/{id}` 时后端异步写 type=2 |
| 11 | **播放量统计** | 未定义 | `play-report` 在 `position >= 30` 且首次上报时 `play_count +1` |
| 12 | **搜索实现** | 未说明 | 一期 `LIKE %keyword%` 匹配 `title`、`author` |
| 13 | **Redis 是否必须** | 一期可不用 | 本地开发可跳过 Redis；**生产建议启用**（热门缓存+限流） |
| 14 | **一期 scope 仍偏大** | admin 独立 + 自研 UI + 氛围系统并行 | 增加 **MoSCoW** 分级（§五），压缩路径见 §十二 |

> **历史决策说明**：上表 #1、#2 为 **v1.2 一期** 时的临时收敛（全员免费、去掉 `max_duration`）。**二期核心已实现** 游客 180s 试看 + 登录全片；以 **§6.4 / §7.3 当前实现** 为准，勿与 v1.2 决策混用。

### 1.3 四次评审优化（v1.4，Python 3.8 锁定）

| # | 议题 | 问题 | v1.4 决策 |
|---|------|------|-----------|
| 1 | **Python 版本** | v1.3 要求 3.10+，与本机 3.8.10 冲突 | **锁定 Python 3.8.10**；脚手架与 Docker 均按 3.8 生成 |
| 2 | **FastAPI 新版本** | FastAPI ≥0.115 已放弃 3.8 | 锁定 `fastapi==0.109.2`（最后稳定支持 3.8 的版本线） |
| 3 | **类型注解语法** | `str \| None` 为 3.10+ 语法 | 代码统一 `Optional[str]` 或文件头 `from __future__ import annotations` |
| 4 | **bcrypt Windows** | 3.8 + passlib 在新版 bcrypt 上易报错 | 锁定 `bcrypt==4.0.1` |
| 5 | **MoSCoW 矛盾** | §5.1 写浏览记录 Must，§12.1 写砍掉 | 单人一期曾降为 Could；**二期已实现** `/user/history` |
| 6 | **Redis 表述** | 摘要仍写 Redis，单人本地不装 | 摘要改为 MinIO；Redis **一期可选** → **v1.8：S0 本地可缺，S1/生产必装**（§2.5） |
| 7 | **DATABASE_URL 格式** | Tortoise 需 `mysql://` + asyncmy | 统一 `mysql://user:pass@host:3306/db`（Tortoise 自动走 asyncmy） |
| 8 | **Docker 后端镜像** | 未指定 | `python:3.8-slim` |

### 1.5 五次评审优化（v1.5，用户个人中心 · 导航纠偏）

| # | 议题 | 现状问题 | v1.5 决策 |
|---|------|----------|-----------|
| 1 | **顶栏「管理」入口错误** | 登录管理员账号时，顶栏「管理」跳转 `/admin/books`（运营后台），与普通用户心智不符 | 顶栏改为 **「个人中心」**，统一跳转 `/user/center`；**移除**顶栏直达运营后台入口 |
| 2 | **个人中心缺失** | 产品 PRD 有 `/user/center`，实现仅有分散的 `/user/orders`、`/user/favorites`、`/user/history` | 新增 **聚合页** `/user/center`，作为登录用户自助管理入口 |
| 3 | **读书喜好订制** | 无用户偏好模型，首页/书单无法个性化 | 新增 `user_preference`，支持多选分类 + 阅读场景标签；用于首页/书单 **Should 级** 推荐加权（首版可仅保存偏好） |
| 4 | **购书收发货** | 订单仅有 `paid`，用户看不到发货进度；Admin 可改状态但前台无展示 | 订单表扩展物流字段；用户中心展示 **待发货 / 已发货 / 已完成** 时间轴；Admin 填单号后前台可见 |
| 5 | **与运营后台边界** | 用户端与运营端入口混淆 | **用户个人中心**（`/user/*`）≠ **运营后台**（`/admin/*`）；后者仅 `/admin/login` 或书签进入 |
| 6 | **管理员也是用户** | admin 账号同样需要个人中心 | admin 登录后顶栏同样进 `/user/center`；运营工作单独打开 `/admin/login` |

### 1.6 六次评审优化（v1.6，Admin 用户管理 · 与代码对齐）

| # | 议题 | 决策 | 已实现 |
|---|------|------|--------|
| 1 | **运营需按地区看用户** | 注册时采集 `province`/`city`；Admin 按 **省→市→用户** 树形展示 | ✅ |
| 2 | **单页聚合用户画像** | 选中用户展示：会员状态、收藏列表、图书订单（可展开物流/明细） | ✅ |
| 3 | **会员订单与图书订单分开展示** | 详情页 Tab：会员信息 + 会员订单 / 收藏 / 图书订单 | ✅ |
| 4 | **未填地区用户** | 归入 **「未填写」** 省/市节点，避免树断裂 | ✅ |
| 5 | **Admin 树不含管理员账号** | 仅 `role=user` 进入地区树；admin 不参与分组 | ✅ |
| 6 | **技术可行性** | 树在内存分组（用户量 <1 万足够）；无需 Elasticsearch | ✅ |
| 7 | **后续增强（未做）** | 省/市级联选择器、VIP/有订单筛选 | 文档 Won't v1.6 |

### 1.7 七次评审优化（v1.7，百万级扩展 · 技术选型定版）

| # | 议题 | 决策 | 合理性 |
|---|------|------|--------|
| 1 | **是否要全站 Java** | **否**；已有 Python MVP，重写 ROI 为负 | 单人可维护 |
| 2 | **双栈怎么拆** | **轻量协同**：Python 主站 + Admin；**仅 1 个 Java trade 服务**（订单/支付/会员） | 发挥 Java 事务优势 |
| 3 | **何时上 Java** | **S2**（完成 S1 Redis 基线后）；S0 继续 Python 功能迭代 | 避免并行大改造 |
| 4 | **Gateway 要不要** | 单人期 **Nginx 按路径分流**；团队 ≥2 人再上 Spring Cloud Gateway | 降低运维复杂度 |
| 5 | **Redis** | 从「可选」改为 **S1 必装**（热点读、限流、分布式锁） | 百万级前置条件 |
| 6 | **视频终态** | **HLS + CDN 签名**（S3）；当前 MP4 + 前端试看为过渡 | 应用层不扛视频流量 |
| 7 | **ECMS** | `Admin-YuXiaoTuBook` **独立**，不并入 C 端 compose | 边界清晰 |
| 8 | **文档关系** | 产品行为以 **本 Dev PRD** 为准；架构扩展以 **《技术选型定版.md》** 为准 | 分工明确 |

> 完整拓扑、API 归属、S0～S5 路线图见 **§十六** 与关联文档 **§十一（单人简化版）**。

### 1.8 技术可行性矩阵

| 能力 | 一期 | 可行性 | 关键依赖 |
|------|------|--------|----------|
| 氛围首页（光厂 Hero） | ✅ | 高 | 视频/图背景、`HeroSearchBox`、客服浮窗 |
| MP4 视频播放 | ✅ | 高 | OSS/MinIO、CDN；过渡方案 |
| 书单 CRUD | ✅ | 高 | — |
| 收藏/浏览记录 | ✅ | 高 | 登录态 |
| 订单+模拟支付 | ✅ | 高 | `MOCK_PAY_ENABLED` |
| 用户个人中心 | ✅ v1.5 | 高 | 偏好表 + 订单物流字段 |
| 读书喜好订制 | ✅ v1.5 | 高 | 关联 `category` |
| 购书收发货展示 | ✅ v1.5 | 中 | 模拟物流；不对接快递 API |
| Admin 用户管理（地区树） | ✅ v1.6 | 高 | `user.province/city` + 聚合查询 |
| 每日读书专栏 | ✅ 二期 | 高 | `daily_book` + Admin CRUD |
| 会员模拟开通 | ✅ 二期 | 高 | `mock-pay` + `member_order` |
| 游客 3 分钟试看 | ✅ 二期 | 中 | 前端截断可行；**非服务端防盗**（见 §6.4.1） |
| 独立 admin | ✅ | 中 | 合并进 `frontend` `/admin` |
| 游客视频 HLS 签名 | ❌ 待做 | 中 | 需 HLS + CDN 签名 |
| 微信/支付宝 | ❌ S4 | 低 | 商户资质 + Java trade 回调 |
| 每日定时发布 | ❌ 待做 | 高 | APScheduler |
| Redis 缓存基线 | ❌ S1 | 高 | Compose + 热点书单/play-auth |
| Java 交易服务 | ❌ S2 | 高 | `yuxiaotu-trade-service` |
| HLS + CDN 签名 | ❌ S3 | 中 | 防盗链 + 试看 enforcement |
| RocketMQ 异步写 | ❌ S5+ | 中 | history、play-report |

### 1.9 需求合理性结论

| 维度 | 评价 | 说明 |
|------|------|------|
| 产品价值 | ✅ 合理 | 「先看视频再买书」路径清晰，与传统书城差异化明确 |
| 一期范围 | ✅ 已收敛 | 去掉虚假防盗、手机号、会员后，单人 5–8 周可交付 |
| 商业模式 | ⚠️ 二期验证 | 一期模拟下单仅验证流程；真实 GMV 依赖支付与供应链 |
| 内容供给 | ⚠️ 运营依赖 | 技术可上线，但 <3 条视频会损害「种草」体验 |
| 光厂视觉 | ✅ 合理 | 参考风格而非复制，可控 |
| **百万级扩展** | ✅ 合理 | 不依赖纯换语言；**基础设施 + 交易域 Java** 路径已定义（§十六） |
| **单人双栈** | ✅ 合理 | Admin 永留 Python；仅 trade 迁 Java，维护成本可控 |
| **MVP 优先** | ✅ 合理 | 未达 §2.5 触发条件前，**禁止**超前建设 Gateway/catalog 集群 |

### 1.10 八次评审优化（v1.8，开发者定稿 · 潘宇 · 可行性与合理性复核）

| # | 议题 | 优化决策 | 类型 |
|---|------|----------|------|
| 1 | **百万用户表述易误解** | 定为 **扩展目标**；当前阶段以 MVP+ 可运营为准；S1 起才做 Redis | 合理性 |
| 2 | **Redis 历史表述** | §1.3「一期可选」已被 §1.7/S1 **取代**；生产/扩展前必装，本地 S0 可缺 | 可行性 |
| 3 | **试看安全性** | MP4 直链 + 前端 `max_duration` **非防盗**；文档明确；S3 HLS 签名才 enforcement | 可行性 |
| 4 | **会员价值** | 当前 VIP **仅角标**；无独家内容/折扣拦截 **合理（模拟期）**；真实权益随 S4 支付一起定义 | 合理性 |
| 5 | **喜好推荐** | 保存偏好 ✅；驱动书单推荐 **Could**，未做不算缺陷 | 合理性 |
| 6 | **客服浮窗** | 静态邮箱 + 站内跳转 **合理**；不接第三方 IM 为 Won't S0 | 合理性 |
| 7 | **Admin 用户树** | 内存分组 **≤1 万用户**可行；更大规模再 ES/分页树（S5+） | 可行性 |
| 8 | **订单超时取消** | 文档 Should 但未实现；**S0 必补**或 Admin 手动取消写进运维说明 | 合理性 |
| 9 | **双栈顺序** | **S1 Redis → S2 Java trade**；禁止跳步 | 可行性 |
| 10 | **开发者署名** | 全文开发者统一为 **潘宇** | 文档 |

> **文档优先级**：产品行为 → 本 Dev PRD；架构扩展 →《技术选型定版.md》；**历史评审行**若与 v1.8 冲突，以 **§1.10 + 当前实现** 为准。

## 二、产品定义

### 2.1 名称与 Slogan

- **宇小兔每日读书** — 「先看懂一本书，再决定买不买」

### 2.2 核心用户路径（当前）

```
进入首页 → 浏览/搜索/每日读书 → 详情页看视频（游客试看 180s → 引导登录）
→ 登录 → 全片 + 收藏 + 个人中心（喜好/收发货）→ 下单 / 会员开通
→ 运营 Admin 上架内容、发货、按省/市查看用户
```

### 2.3 一期 vs 二期的用户价值

| 阶段 | 用户得到什么 |
|------|--------------|
| 一期 | 免费看解读视频、发现好书、模拟购买体验 |
| 二期核心 | 每日专栏、会员（模拟）、游客试看、浏览记录 |
| v1.5 | 个人中心、读书喜好、购书收发货可视化 |
| **v1.6** | **Admin 按省/市管理用户，追踪会员/收藏/订单** |
| **v1.7（已实现 UI）** | **光厂风首页**：视频背景 + 悬浮搜索 + 客服浮窗 |
| **扩展 S1～S5** | Redis 基线 → Java 交易 → HLS/CDN → 真实支付 → 团队扩容（§十六） |
| 待做（产品） | 真实支付、AI 内容、数据看板、偏好推荐、订单超时取消 |
| 三期 | 社区、文创、出版社、SSR |

### 2.4 明确不做

社区 UGC、文创、出版社 B 端、原生 App、直播弹幕、短信登录、全站像素级复刻光厂、Day-1 微服务集群。

### 2.5 规模目标与扩展触发（需求合理性）

> **原则**：不为「未来可能」过早做复杂架构；**数据或业务触发后再投入 S1～S5**。

| 触发条件（满足任一） | 建议动作 | 不合理做法 |
|----------------------|----------|------------|
| DAU < 5k，API P95 < 500ms | 继续 **S0 Python** 迭代功能 | 上 Java 微服务集群 |
| DAU 5k～50k 或热点 API 变慢 | **S1**：Redis + 多 worker + 封面 CDN | 直接拆 catalog-service |
| 促销/并发下单出错、库存争议 | **S2**：Java trade + Nginx 分流 | 仅用 Python 硬扛事务 |
| 视频盗链/试看绕过成问题 | **S3**：HLS + CDN 签名 | 继续 MP4 直链 |
| 需真实收款 | **S4**：微信/支付宝 + `MOCK_PAY=false` | 模拟支付上生产 |
| 团队 ≥2 人或 P95 持续超标 | **S5**：Gateway / MQ / 读写分离 | 单人维护完整微服务 |

**当前阶段（2026-07）**：代码处于 **MVP+**；**尚未触发 S1**，以功能完善与冒烟测试为主。

---

## 三、技术架构

### 3.1 当前实现栈（MVP · v1.7 已落地）

> 下列为 **`Customer-YuXiaotuBook` 当前代码** 使用的技术；扩展期双栈与基础设施见 **§3.4、§十六**。

| 层级 | 选型 | 说明 |
|------|------|------|
| 用户端 | Vue 3 + TS + Vite + Pinia + Vue Router | 光厂风 CSS Variables；Hero 搜索/客服组件 |
| 管理端 | Vue 3 + TS + Element Plus | 合并于 `frontend` `/admin` |
| 后端（主） | FastAPI + **Python 3.8.10** | 书单、订单（暂）、Admin、每日、会员、偏好 |
| ORM | Tortoise-ORM 0.20 + Aerich | **禁止**生产 `generate_schemas()` |
| MySQL 驱动 | **asyncmy** | `DATABASE_URL=mysql://...` |
| 缓存 | Redis 7 | **S1 起必装**；当前 Compose 未含，见 §十六 S1 |
| 存储 | MinIO（dev）/ OSS（prod） | 封面、视频源 |
| 视频 | MP4 直链 + 前端试看 | **过渡**；终态 HLS + CDN（§十六 S3） |
| 反向代理 | Nginx | 静态 + API；S2 起分流 Java trade |
| 独立 ECMS | `Admin-YuXiaoTuBook` | PostgreSQL + FastAPI，**不并入 C 端** |

### 3.2 后端 `requirements.txt`（Python 3.8 锁定版）

> 版本经过 **Python 3.8.10 / Windows** 兼容筛选；请勿随意升级到 `fastapi>=0.115`（已不支持 3.8）。

```text
# Web
fastapi==0.109.2
uvicorn[standard]==0.27.1
python-multipart==0.0.6

# ORM & DB（Tortoise + asyncmy）
tortoise-orm==0.20.1
aerich==0.7.2
asyncmy==0.2.9

# Auth & utils
pyjwt==2.8.0
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
python-dotenv==1.0.0

# HTTP client（测试/回调用）
httpx==0.27.2

# 可选（启用 Redis 缓存/限流时取消注释）
# redis==5.0.1
```

**PyPI 安装命令（本机）**

```powershell
py -3.8 -m venv .venv
.\.venv\Scripts\activate
pip install -r backend\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3.2.1 Python 3.8 代码约束（后端必遵守）

| 约束 | 说明 |
|------|------|
| 类型注解 | 使用 `Optional[str]`、`List[int]`（`from typing import ...`），或文件首行 `from __future__ import annotations` |
| 禁用语法 | 不使用 `match/case`、不使用运行时的 `X \| Y` 联合类型 |
| 生命周期 | 使用 `@app.on_event("startup")` / `shutdown`（与 FastAPI 0.109 一致） |
| 异步入口 | `uvicorn app.main:app --reload`；模块路径 `app.main:app` |
| Pydantic | FastAPI 0.109 自带 Pydantic v2；模型用 `model_config` 或 `class Config` 均可 |

### 3.2.2 版本升级策略（二期再考虑）

| 组件 | 一期 | 升级时机 |
|------|------|----------|
| Python | 3.8.10 | 项目稳定后升 3.11+ |
| FastAPI | 0.109.2 | 随 Python 升级 |
| tortoise-orm | 0.20.1 | 随 Python 升级 |

### 3.3 项目目录

**单人全栈推荐（本项目管理方式）**

```
Customer-YuXiaotuBook/
├── backend/
│   └── app/
│       ├── api/v1/
│       ├── core/
│       ├── db/
│       ├── models/
│       ├── schemas/
│       ├── services/
│       └── main.py
├── frontend/                # 用户端 + 管理端（/admin 路由，dev 端口 5188）
│   └── src/
│       ├── views/           # 用户页面（含 UserCenter.vue）
│       ├── views/admin/     # 管理页面（含 Users.vue、Daily.vue）
│       ├── components/
│       ├── api/             # 共用请求封装
│       └── router/
├── deploy/
│   └── docker-compose.yml   # 项目名 YuXiaotuBookCustomer
└── scripts/
    ├── seed.py
    ├── api_smoke_test.py
    ├── migrate_v15_user_center.py
    └── migrate_user_region.py
```

> **为何单人合并 admin？** 一套 Vite 配置、一套 `api` 封装、一套登录态，少维护一个项目。管理区用 `AdminLayout` + Element Plus，与用户端光厂风样式隔离即可。

**团队版（二期或多人时可选拆分）**：将 `views/admin/` 抽到独立 `admin/` 子项目。

### 3.4 扩展架构（百万级 · 单人轻量协同 · 定版摘要）

> **详案**：[《技术选型定版.md》](./技术选型定版.md)（v1.1）；**单人实施以该文档 §十一 为准**。  
> **原则**：不全站 Java 重写；**Python 主站 + 单 Java 交易服务**；基础设施先于微服务。

#### 3.4.1 定版结论

| 问题 | 定版答案 |
|------|----------|
| 语言策略 | **Java + Python 轻量协同**（非完整微服务） |
| Java 做什么 | **仅** `yuxiaotu-trade-service`：订单、库存、mock/真实支付、会员开通 |
| Python 做什么 | Admin、每日、偏好、用户树、登录收藏、AI/脚本；书单读路径 **S2 前不拆 Java** |
| 百万用户靠什么 | **CDN + Redis + MySQL 主从 + 多实例**；视频 **不走应用服务器** |
| 单人不要做什么 | 暂不建 Gateway、catalog-service、RocketMQ 集群 |

#### 3.4.2 单人期拓扑（S0～S2）

```text
CDN（封面 / 后续 HLS）
        │
用户 ──► Nginx ──┬──► Python FastAPI:8000（默认全部 API）
                 └──► Java trade:8081（S2 起：/orders*、/member/subscribe* 等）
                          │
                 Redis + MySQL（JWT_SECRET 共用）
```

#### 3.4.3 语言 / 模块边界

| 模块 | MVP（现在） | 扩展定版（单人） |
|------|-------------|------------------|
| Admin CRUD / 用户树 | Python | **永久 Python** |
| 每日 / 偏好 / 收藏 / 登录 | Python | Python |
| 书单 / 首页 / play-auth | Python | Python + **Redis**（S1）；catalog Java 仅团队扩容后 |
| 订单 / 支付 / 会员交易 | Python（暂） | **Java trade**（S2） |
| 微信 / 支付宝回调 | 未做 | Java trade（S4） |
| AI / 推荐 | 未做 | Python |

#### 3.4.4 JWT 双栈约定

| 项 | 定版 |
|----|------|
| 算法 | HS256 |
| 密钥 | Python 与 Java **共用** `JWT_SECRET` |
| Payload | `{ sub, role, exp }` 与现网一致 |

#### 3.4.5 扩展阶段（S0～S5 · 与产品待办对齐）

| 阶段 | 交付 | 栈 | 前置 |
|------|------|-----|------|
| **S0** | 产品功能迭代（§5.6 待做项） | Python | 当前 |
| **S1** | Compose **+ Redis**；连接池；多 worker；封面 CDN | Python + Redis | 无 |
| **S2** | `yuxiaotu-trade-service`；Nginx 分流交易 API | **Java** + Python | **S1 完成** |
| **S3** | HLS + CDN 签名；试看服务端 enforcement | CDN + 后端 | S1 |
| **S4** | 微信/支付宝真实支付回调 | Java trade | **S2 完成** |
| **S5** | catalog / Gateway / MQ（按 QPS 或团队人数触发） | 对齐《技术选型定版》§一 | 团队 ≥2 人或瓶颈 |

**单人铁律**：同一时期只做一个「大改造」；**未完成 S1 不启动 S2**。

#### 3.4.6 Nginx 分流（S2 起 · 替代 Gateway）

```nginx
location ~ ^/api/v1/(orders|member/subscribe|member/orders) {
    proxy_pass http://127.0.0.1:8081;
}
location /api/ {
    proxy_pass http://127.0.0.1:8000;
}
```

### 3.5 环境变量

```env
# 必填
DATABASE_URL=mysql://root:123456@127.0.0.1:3306/yuxiaotu_book
JWT_SECRET=<32位以上随机串>
JWT_EXPIRE_HOURS=168

# 存储
STORAGE_TYPE=minio
MINIO_ENDPOINT=http://127.0.0.1:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=yuxiaotu
MINIO_PUBLIC_URL=http://127.0.0.1:9000/yuxiaotu

# Redis（S1 起必填；S0 本地可暂缺）
REDIS_URL=redis://127.0.0.1:6379/0

# 业务开关
MOCK_PAY_ENABLED=true              # 图书订单模拟支付；生产必须 false
MEMBER_MOCK_PAY_ENABLED=true       # 会员模拟开通
GUEST_VIDEO_PREVIEW_SECONDS=180    # 游客试看秒数；0=关闭限制
PAYMENT_PROVIDER=mock              # mock | wechat | alipay（后两者预留）
CORS_ORIGINS=http://localhost:5188,http://127.0.0.1:5188
```

### 3.6 Nginx 路由（生产）

| 路径 | 上游 | 阶段 |
|------|------|------|
| `/` | `frontend` 静态 | 现网 |
| `/admin/` | `frontend` 静态 | 现网 |
| `/api/v1/orders*`、`/member/subscribe*` 等 | **Java trade:8081** | **S2 起** |
| `/api/`（其余） | Python **backend:8000** | 现网 |
| `/sitemap.xml` | Python backend | 现网 |
| 封面 / 视频 | **CDN** → OSS/MinIO | **S1/S3** |

---

## 四、设计系统

### 4.1 Design Token

| Token | 值 |
|-------|-----|
| `--color-bg` | `#FAFAFA` |
| `--color-surface` | `#FFFFFF` |
| `--color-primary` | `#5B9AA0` |
| `--color-text` | `#1A1A1A` |
| `--color-text-secondary` | `#6B7280` |
| `--color-border` | `#E5E7EB` |
| `--color-accent` | `#C9A962` |

### 4.2 响应式断点

| 名称 | 宽度 | 书单列数 |
|------|------|----------|
| mobile | < 768px | 1 |
| tablet | 768–1023px | 2 |
| desktop | ≥ 1024px | 4 |

### 4.3 用户端组件（MoSCoW）

| 组件 | 优先级 | 说明 |
|------|--------|------|
| `AppHeader` / `AppFooter` | Must | 顶栏含：首页/书单/每日读书/会员中心；登录态含 VIP 角标、收藏、浏览记录、订单、**个人中心** |
| `BookCard` | Must | 书单/首页/收藏网格卡片 |
| `VideoPlayer` | Must | 封装 `<video>`；支持 `maxDuration` 试看截断（二期） |
| `SkeletonCard` | Must | |
| `AuthModal` | Should | 可先用 `/login` 页代替 |
| `AtmospherePlayer` | Should | 首页氛围；可降级静态图 |
| `EmptyState` | Could | |

---

## 五、功能分期与 MoSCoW

> **说明**：下列 `[x]` 表示已在 `Customer-YuXiaotuBook` 中实现；`[ ]` 为文档规划但未做或仅部分完成。

### 5.1 一期 Must

- [x] 首页：热门书、分类入口、氛围背景（**当前：静态背景图**）
- [x] 书单：分类筛选、分页、关键词搜索
- [x] 详情：书籍信息、视频播放、相似推荐
- [x] 用户：注册、登录、JWT
- [x] 收藏
- [x] 订单：创建、收货地址、模拟支付、列表
- [x] Admin：书籍/视频/分类/订单/氛围配置 CRUD
- [x] Docker 本地可跑通（`YuXiaotuBookCustomer` compose）

### 5.2 一期 Should

- [x] 首页今日主推 + 金句（`site_config`）
- [ ] `AuthModal` 登录弹窗（**实际：独立 `/login` 页**）
- [ ] 首页悬浮音乐（后台可配，前台未实现播放器）
- [ ] 订单 30 分钟超时取消（**实际：手动取消**）

### 5.3 二期核心 Must（已实现）

- [x] `/daily` 每日读书：今日、归档、点赞
- [x] `/member` 会员中心：套餐、模拟开通、`is_vip`
- [x] 游客 3 分钟试看 + 登录全片（`play-auth` + `VideoPlayer`）
- [x] `/user/history` 浏览记录
- [x] Admin：`/admin/daily`、`/admin/member`

### 5.4 v1.5 Must（已实现）

- [x] `/user/center` 个人中心聚合页
- [x] 读书喜好（最多 **8** 分类 + 4 场景标签）
- [x] 购书收发货 Tab + Admin 发货填单号

### 5.5 v1.6 Must（已实现）

- [x] 注册采集省份、城市（可选，未填归「未填写」）
- [x] Admin `/admin/users`：省→市→用户树
- [x] 用户详情：会员、收藏、图书订单（含物流追踪）

### 5.6 仍待做 / Won't / 扩展路线

#### 5.6.1 产品功能（S0 · Python）

| 功能 | 决策 |
|------|------|
| 真实支付（微信/支付宝） | S4；**前置 S2 trade**；商户资质就绪后再做 |
| 偏好驱动书单推荐 | Could；**已有喜好存储**，无推荐不阻塞上线 |
| AI 批量生成、Admin 数据看板 | S0/S1 后按需；**非 MVP 阻塞项** |
| 每日定时自动发布 | Should；**Admin 手动发布可接受**（现状） |
| 订单 30 分钟超时取消 | **S0 Should 必补**（或文档化 Admin 手动取消流程） |
| 省/市级联注册、用户筛选 | Could |
| 快递轨迹 API、用户确认收货 | Won't 当前版 / 三期 |
| 社区、文创、出版社、SSR | 三期 |
| 手机验证码、原生 App | Won't |

#### 5.6.2 基础设施与架构（S1～S5 · 见 §十六）

| 功能 | 阶段 | 决策 |
|------|------|------|
| Redis 接入 Compose + 热点缓存 | **S1** | Must（百万级前置） |
| FastAPI 多 worker / 连接池 | **S1** | Must |
| 封面 / 静态 CDN | **S1** | Should |
| Java `yuxiaotu-trade-service` | **S2** | Must（交易域） |
| Nginx 交易路径分流 | **S2** | Must |
| HLS + CDN 视频签名 | **S3** | Must（生产终态） |
| RocketMQ 异步写 | **S5+** | 瓶颈触发 |
| Spring Cloud Gateway / catalog Java | **S5+** | 团队 ≥2 人或 QPS 触发 |

---

## 六、页面开发规格

### 6.1 用户端路由

| 路由 | 页面 | 登录 |
|------|------|------|
| `/` | 首页 | 否 |
| `/books` | 书单 | 否 |
| `/books/:id` | 详情 | 否 |
| `/daily` | 每日读书专栏 | 否 |
| `/member` | 会员中心 | 否（开通需登录） |
| `/login` | 登录 | 否 |
| `/register` | 注册（含省份、城市） | 否 |
| **`/user/center`** | **个人中心（聚合页）** | **是** |
| `/user/orders` | 订单列表（可从个人中心跳转） | 是 |
| `/user/favorites` | 收藏 | 是 |
| `/user/history` | 浏览记录 | 是 |

### 6.2 首页 `/`（光厂风 Hero · v1.7 已实现）

**布局（自上而下）**

| 区域 | 说明 |
|------|------|
| Hero 全宽 | `site_config`：`bg_type=video\|image` + `bg_url`；视频 `muted/loop/playsinline`，失败降级图片 |
| 顶栏 | 首页路由下毛玻璃深色导航；滚动后恢复白底（`AppHeader`） |
| 主文案 | 标题 + `daily_sentence` 金句 |
| 悬浮搜索 | `HeroSearchBox`：Tab **书籍 / 每日读书**；热门分类标签 → `/books?keyword=` |
| 信任条 | 视频解读 / 精选书单 / 正版购书 / 每日共读 |
| 下方内容 | 今日主推、分类探索、热门书籍网格 |

**全局组件**

| 组件 | 说明 |
|------|------|
| `FloatSupportButton` | 全站右下角客服浮窗（邮箱 + 会员/书单入口） |

**接口**

```
GET /api/v1/site/config
GET /api/v1/home/featured      # 读 site_config.featured_book_id
GET /api/v1/home/hot-books?page=1&page_size=12
GET /api/v1/categories
```

**降级**

| 场景 | 处理 |
|------|------|
| 背景视频失败 | 用 `bg_type=image` 静态图 |
| autoplay 被拦 | 展示「点击播放」 |
| 无主推书 | 隐藏主推区块 |

### 6.3 书单 `/books`

```
GET /api/v1/books?category_id=&sort=hot|new&keyword=&page=1&page_size=12
```

**列表排序 SQL 逻辑**

```sql
ORDER BY
  (EXISTS valid video) DESC,  -- has_video 优先
  CASE WHEN :sort='hot' THEN view_count END DESC,
  CASE WHEN :sort='new' THEN created_at END DESC,
  id DESC
```

### 6.4 详情 `/books/:id`（P0）

**布局**：视频 → 信息 → 购买/收藏 → 相似书（同分类 6 本）

**视频规则（当前实现 · 对齐代码）**

| 规则 | 说明 |
|------|------|
| 游客 | `play-auth` 返回 `full_access=false`，`max_duration=180`；`VideoPlayer` 到点暂停并引导登录 |
| 登录用户 | `full_access=true`，可看全片 |
| 会员 | 额外返回 `is_vip`（角标展示；独家内容拦截三期扩展） |
| 无视频 | 展示封面 +「解读筹备中」 |
| 播放地址 | 仅 `play-auth` 返回 MP4 直链 |
| 统计 | 播放 ≥30s 首次上报 → `play_count+1` |
| 浏览记录 | 登录用户访问详情写 `collect_type=2` |

**接口**

```
GET  /api/v1/books/{id}
GET  /api/v1/books/{id}/play-auth
POST /api/v1/books/{id}/play-report     # { "position": 120 }
GET  /api/v1/books/{id}/similar
POST /api/v1/favorites                  # 需登录
DELETE /api/v1/favorites/{book_id}
POST /api/v1/orders                     # 需登录
```

**`play-auth` 响应（当前）**

```json
{
  "code": 200,
  "data": {
    "video_url": "https://cdn.example.com/videos/1.mp4",
    "poster": "https://cdn.example.com/posters/1.jpg",
    "duration": 360,
    "full_access": false,
    "max_duration": 180,
    "is_vip": false
  }
}
```

#### 6.4.1 试看与会员（技术边界 · 合理性）

| 项 | 当前实现 | 用户感知 | 生产风险 | 终态（S3/S4） |
|----|----------|----------|----------|---------------|
| 游客试看 | 前端 `VideoPlayer` 计时暂停 | ✅ 正常 | 懂 URL 可绕过 | HLS + 短签名 URL |
| 登录全片 | `full_access=true` 返回完整 MP4 | ✅ 正常 | 链接可分享 | CDN 鉴权 + 过期 |
| VIP 角标 | `is_vip` 展示 | ✅ 正常 | 无独家差异 | 会员专享内容/折扣 **S4 后定义** |

> **需求合理性**：模拟运营期不承诺「服务端不可逆防盗」；对外宣传避免「绝对防录屏」，改为「登录/VIP 解锁体验」。

**下单流程**

```mermaid
sequenceDiagram
  participant U as 用户
  participant F as 前端
  participant A as API
  U->>F: 点击购买
  F->>F: 未登录则跳转/login
  U->>F: 填写数量+收货信息
  F->>A: POST /orders
  A->>A: 校验 stock>=qty, status=published
  A-->>F: order_id, status=pending_payment
  U->>F: 模拟支付
  F->>A: POST /orders/{id}/mock-pay
  A->>A: MOCK_PAY_ENABLED?
  A->>A: 事务: status=paid, stock-=qty
  A-->>F: 支付成功
```

### 6.5 管理端（单人：`/admin/*` 路由）

| 路由 | 功能 |
|------|------|
| `/admin/login` | 管理员登录（`role=admin`） |
| `/admin/books` | 书籍 CRUD |
| `/admin/videos` | 绑定视频、上下架 |
| `/admin/categories` | 分类 |
| `/admin/orders` | 查询、取消、**发货**（填快递公司+运单号）、**完结** |
| `/admin/daily` | 每日读书 CRUD |
| `/admin/member` | 会员套餐 CRUD；会员订单列表 |
| **`/admin/users`** | **用户管理：省/市树 + 用户详情（v1.6）** |
| `/admin/site-config` | 氛围、主推、金句 |

路由守卫：`meta.admin === true` 时校验 `role=admin`。

**上传策略（一期）**

| 类型 | 方式 | 限制 |
|------|------|------|
| 封面图 | `POST /api/v1/admin/upload` | ≤ 5MB，jpg/png/webp |
| 视频 | 后台填 URL 或上传 MP4 | 上传 ≤ 200MB |
| 氛围背景 | 图片或短视频 URL | 视频 ≤ 50MB |

### 6.6 用户个人中心 `/user/center`（v1.5 新增）

> **定位**：登录用户的 **自助管理页**，对标产品 PRD §4.6「个人中心页」。  
> **不是** 运营后台（`/admin/*`）。顶栏原「管理」按钮 **必须改为此页**。

#### 6.6.1 入口与导航调整

| 位置 | 调整前 | 调整后 |
|------|--------|--------|
| `AppHeader` 顶栏（登录态） | `管理` → `/admin/books`（仅 `role=admin`） | **`个人中心` → `/user/center`（所有登录用户）** |
| 运营后台 | 顶栏可进 | **仅** `/admin/login` 或手动输入 URL |
| 个人中心内快捷入口 | — | 收藏、浏览记录、会员状态、订单详情链接保留 |

**路由守卫**：`/user/center` 需登录（`meta.login: true`），未登录跳转 `/login?redirect=/user/center`。

#### 6.6.2 页面信息架构

```
/user/center
├── 区块 A：账户概览（只读）
│   ├── 头像、昵称、用户名
│   ├── 会员状态（is_vip、到期日；无则引导 /member）
│   └── 快捷入口：收藏 / 浏览记录 / 会员中心
├── 区块 B：读书喜好私人订制（可编辑）★ 核心
│   ├── 偏好分类（多选，来自 category 表，**最多 8 个**）
│   ├── 阅读场景（多选标签：通勤 / 睡前 / 周末深度 / 职场充电）
│   ├── 一句话简介（可选，≤ 100 字）
│   └── 保存按钮 → PUT /api/v1/user/preferences
└── 区块 C：已购书籍收发货（只读列表）★ 核心
    ├── Tab：全部 / 待发货 / 运输中 / 已完成
    ├── 卡片：书名、数量、金额、订单号、当前状态
    ├── 物流信息（status=shipped 时）：快递公司、运单号、发货时间
    └── 空态：「暂无购书记录，去书单逛逛」→ /books
```

**视觉**：延续用户端光厂极简风（`page-card` 分区、圆角卡片），**不使用** Element Plus（与 `/admin` 区分）。

#### 6.6.3 读书喜好业务规则

| 规则 | 说明 |
|------|------|
| 默认偏好 | 未设置时，首页/书单仍按原逻辑（热门 + has_video 优先） |
| 保存后 | 写入 `user_preference`；**v1.5 首版**可在书单页增加「为你推荐」角标（同分类加权，Should） |
| 校验 | 分类 ID 必须存在且 `status=1`；**最多选 8 个分类** |
| 场景标签 | 固定枚举，存 JSON 数组，便于后续扩展推荐算法 |

#### 6.6.4 收发货业务规则

**展示范围**：仅展示 `status ∈ { paid, shipped, completed }` 的 **图书订单**（不含会员订单 `member_order`）。

**状态对用户的中文映射**

| 后端 status | 用户可见文案 | 说明 |
|-------------|--------------|------|
| `paid` | 待发货 | 已支付，等待仓库发货 |
| `shipped` | 运输中 | Admin 已填物流单号 |
| `completed` | 已完成 | 用户确认收货或 Admin 完结 |
| `pending_payment` | — | **不在**收发货区块展示（仍只在 `/user/orders`） |
| `cancelled` | 已取消 | 可选：在「全部」Tab 灰色展示 |

**物流字段（订单表扩展，v1.5）**

| 字段 | 类型 | 说明 |
|------|------|------|
| `ship_company` | varchar(50) nullable | 快递公司，如「顺丰速运」 |
| `ship_tracking_no` | varchar(64) nullable | 运单号 |
| `shipped_at` | datetime nullable | 发货时间 |
| `completed_at` | datetime nullable | 完成时间 |

**Admin 侧（扩展 §6.5）**：`/admin/orders` 增加「发货」操作：填写 `ship_company` + `ship_tracking_no` → 自动 `status=shipped`、`shipped_at=now()`。

**v1.5 不做**：对接快递 100 / 菜鸟轨迹 API；用户确认收货按钮（可三期）；真实仓库 WMS。

#### 6.6.5 接口清单（v1.5 新增）

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/v1/user/preferences` | 是 | 获取当前用户读书喜好 |
| PUT | `/api/v1/user/preferences` | 是 | 保存喜好（分类 + 场景 + 简介） |
| GET | `/api/v1/user/orders/shipping` | 是 | 已购书籍收发货列表（含物流字段） |
| PUT | `/api/v1/admin/orders/{id}/ship` | admin | 运营发货（填单号） |

**GET `/user/preferences` 响应示例**

```json
{
  "code": 200,
  "data": {
    "category_ids": [3, 5],
    "scene_tags": ["commute", "before_sleep"],
    "bio": "喜欢心理学和治愈类短阅读"
  }
}
```

**PUT `/user/preferences` 请求体**

```json
{
  "category_ids": [3, 5],
  "scene_tags": ["commute", "before_sleep"],
  "bio": "喜欢心理学和治愈类短阅读"
}
```

**GET `/user/orders/shipping` 响应示例**

```json
{
  "code": 200,
  "data": [
    {
      "id": 12,
      "order_no": "O202607011200001",
      "status": "shipped",
      "status_label": "运输中",
      "total_amount": 39.8,
      "items": [{ "book_id": 1, "book_title": "被讨厌的勇气", "quantity": 1 }],
      "receiver_name": "张三",
      "receiver_address": "上海市…",
      "ship_company": "顺丰速运",
      "ship_tracking_no": "SF1234567890",
      "shipped_at": "2026-07-02T10:00:00",
      "pay_time": "2026-07-01T12:00:00"
    }
  ]
}
```

#### 6.6.6 数据模型（v1.5 新增）

**user_preference**（1 用户 1 行）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int PK | |
| `user_id` | int UNIQUE | 关联 user |
| `category_ids` | text | JSON 数组，如 `[1,3,5]` |
| `scene_tags` | text | JSON 数组，枚举见 §6.6.3 |
| `bio` | varchar(100) nullable | 一句话简介 |
| `updated_at` | datetime | |

**orders 表增量字段**：见 §6.6.4 物流四字段。

#### 6.6.7 MoSCoW（v1.5 增量）

| 优先级 | 功能 |
|--------|------|
| **Must** | 顶栏改「个人中心」；`/user/center` 页面；喜好 GET/PUT；收发货列表 API + 展示 |
| **Must** | Admin 订单发货（填单号）；订单表物流字段 |
| **Should** | 个人中心内嵌账户概览 + 快捷入口；Tab 筛选收发货 |
| **Could** | 根据偏好加权书单「为你推荐」 |
| **Won't** | 快递轨迹实时查询、用户确认收货、修改已发货地址 |

#### 6.6.8 验收用例（v1.5）

| # | 场景 | 预期 |
|---|------|------|
| T17 | 登录用户点击顶栏「个人中心」 | 进入 `/user/center`，**不是** `/admin` |
| T18 | 保存读书喜好（选 2 个分类 + 场景） | 刷新后回显一致；再次 GET preferences 一致 |
| T19 | 用户有 `paid` 订单 | 收发货区显示「待发货」 |
| T20 | Admin 对订单执行发货 | 用户中心该单变「运输中」，展示快递公司与单号 |
| T21 | admin 账号登录顶栏 | 同样进 `/user/center`；手动访问 `/admin/login` 仍可进运营后台 |

### 6.7 每日读书 `/daily`（二期 · 已实现）

| 项 | 说明 |
|----|------|
| 页面 | `Daily.vue`：今日推荐 + 历史归档 |
| API | `GET /daily/today`、`GET /daily/list`、`POST /daily/{id}/like` |
| Admin | `/admin/daily` CRUD |

### 6.8 会员中心 `/member`（二期 · 已实现）

| 项 | 说明 |
|----|------|
| 页面 | `MemberCenter.vue`：套餐、模拟开通 |
| API | `GET /member/packages`、`POST /member/subscribe`、`POST .../mock-pay` |
| 预留 | `POST /member/orders/{id}/pay` → 501 |
| Admin | `/admin/member` 套餐 CRUD + 会员订单列表 |

### 6.9 Admin 用户管理 `/admin/users`（v1.6 · 已实现）

> 按 **注册省/市** 树形分组（仅 `role=user`），查看会员、收藏、图书订单及物流。

**页面布局（`Users.vue`）**

| 区域 | 内容 |
|------|------|
| 页头 | 标题「用户管理」+ 注册用户总数 |
| 左侧 | `el-tree`：省 → 市 → 用户（默认全部展开）；点击用户节点加载详情 |
| 右侧顶栏 | 昵称/用户名、省·市、注册日期、「编辑资料」按钮 |
| 统计卡片 | 会员（VIP/普通）、收藏数、图书订单数 |
| Tab 1 会员信息 | VIP 状态、套餐名、到期时间；下方会员订单表格 |
| Tab 2 收藏 | 书名、作者、分类、收藏时间 |
| Tab 3 图书订单 | 可展开行：收货人/地址/物流/明细；列：订单号、状态、金额、支付时间 |
| 编辑弹窗 | 昵称、省份、城市、账号状态（正常/禁用） |

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/users/tree` | 地区树 + 用户总数 |
| GET | `/api/v1/admin/users/{id}` | 详情含 member、favorites、orders、member_orders |
| PUT | `/api/v1/admin/users/{id}` | 改 nickname/province/city/status |

**注册**：`/register` 增加省份、城市文本输入；空值归 **「未填写」**。

**迁移**：`scripts/migrate_user_region.py` · **Seed**：`demo_hz`/`demo_sh`/`demo_bj`

**验收**：T22–T25（见 §十三）

---

## 七、核心业务规则

### 7.1 书籍状态

| status | 前台可见 |
|--------|----------|
| `draft` | 否 |
| `published` | 是 |
| `off_shelf` | 否 |

### 7.2 订单状态机

```
pending_payment → paid → shipped → completed
                ↘ cancelled
```

| 流转 | 触发 | 副作用 |
|------|------|--------|
| → pending_payment | 创建订单 | 不扣库存 |
| → paid | mock-pay / 二期真实支付 | **扣减库存** |
| → shipped | Admin 发货（v1.5：填 `ship_company` + `ship_tracking_no`） | 写 `shipped_at` |
| → completed | Admin 完结 / 三期用户确认收货 | 写 `completed_at` |
| → cancelled | 用户取消 / 后台取消 / 超时 | 若已 paid 则**回滚库存** |

### 7.3 权限矩阵（当前实现）

| 能力 | 游客 | 登录用户 | 管理员 |
|------|------|----------|--------|
| 浏览首页/书单/详情/每日 | ✅ | ✅ | ✅ |
| 观看视频 | 🔶 试看 180s | ✅ 全片 | ✅ 全片 |
| 收藏 / 浏览记录 | ❌ | ✅ | ✅ |
| 个人中心 / 会员开通 | ❌ | ✅ | ✅ |
| 下单 | ❌ | ✅ | ✅ |
| 运营后台 | ❌ | ❌ | ✅（`/admin/login`） |
| Admin 用户管理 | ❌ | ❌ | ✅ |

> 会员 `is_vip` 当前用于展示角标；独家内容与折扣拦截为 **待做**。

### 7.4 认证与安全

| 项 | 规则 |
|----|------|
| 注册 | `username` 4–20 位；`password` ≥ 8 位；**可选** `province`、`city`（供 Admin 地区树） |
| 密码存储 | `passlib` bcrypt |
| Token | JWT，`Authorization: Bearer` |
| Payload | `{ "sub": user_id, "role": "user"\|"admin", "exp": ... }` |
| Admin API | 必须 `role=admin` |
| 限流 | 登录 5 次/分钟/IP（需 Redis；无 Redis 时跳过） |

### 7.5 Seed 数据（最低上线内容）

| 类型 | 数量 | 说明 |
|------|------|------|
| 分类 | 6 | 成长、治愈、文学、职场、心理、育儿 |
| 书籍 | ≥ 10 | `published` |
| 视频 | ≥ 3 | 可播放 MP4 |
| 管理员 | 1 | `admin` / `admin123456` |
| 演示用户 | 3 | `demo_hz`、`demo_sh`、`demo_bj` / `demo123456` |
| 会员套餐 | 2 | 月度/年度 |
| 每日读书 | 7 | 近 7 天 seed 数据 |

---

## 八、数据模型

### 8.1 ER

```
category 1—N book 1—0..1 book_video
user 1—N order 1—N order_item
user 1—0..1 user_preference
user 1—0..1 user_member
user 1—N member_order
user 1—N user_book_collect
daily_book N—1 book
member_package 1—N user_member
site_config（取 id 最大或唯一行）
```

### 8.2 核心表（字段摘要）

#### user

`id, username, password_hash, nickname, avatar, province, city, role, status, created_at`

#### daily_book（二期）

`id, book_id, daily_sentence, daily_intro, publish_date(UNIQUE), is_top, status, like_count, created_at`

#### member_package / user_member / member_order（二期）

见 `backend/app/models/member.py`

#### book

`id, title, author, cover, category_id, price, stock, summary, highlight, target_audience, status, view_count, created_at, updated_at`

- 进入详情：`view_count += 1`（每 IP 每书每小时计 1 次，可用 Redis 去重；一期可简化为每次 +1）

#### book_video

`id, book_id(UNIQUE), video_cover, video_url, video_duration, video_intro, explain_content, play_count, status, created_at, updated_at`

#### order

`id, order_no, user_id, total_amount, status, receiver_name, receiver_phone, receiver_address, pay_time, ship_company, ship_tracking_no, shipped_at, completed_at, created_at, updated_at`

#### user_preference（v1.5）

`id, user_id(UNIQUE), category_ids(JSON text), scene_tags(JSON text), bio, updated_at`

#### order_item

`id, order_id, book_id, book_title, price, quantity`

#### user_book_collect

`id, user_id, book_id, type(1收藏/2浏览), created_at`  
唯一索引：`(user_id, book_id, type)`

#### site_config

`id, bg_type, bg_url, bg_music, white_noise, music_enabled, bg_enabled, featured_book_id, daily_sentence, updated_at`

---

## 九、API 规范

### 9.1 统一响应

```json
{ "code": 200, "msg": "操作成功", "data": {} }
```

**HTTP 状态码与 body.code 保持一致**：成功 200；参数错误 400；未登录 401；无权限 403；不存在 404；服务器 500。

### 9.2 业务错误码（常用）

| code | msg 示例 | 场景 |
|------|----------|------|
| 40001 | 库存不足 | 下单 |
| 40002 | 书籍已下架 | 下单/详情 |
| 40003 | 用户名已存在 | 注册 |
| 40004 | 模拟支付未开启 | mock-pay 且 MOCK_PAY=false |
| 40005 | 订单状态不允许支付 | 重复支付 |
| 40101 | 请先登录 | 未带 Token |
| 40301 | 无管理员权限 | admin API |

### 9.3 接口清单（截至 v1.6 · 与 Swagger 对齐）

**认证 / 用户**

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | `/api/v1/auth/register` | 否 | 含可选 `province`、`city` |
| POST | `/api/v1/auth/login` | 否 | 用户与 admin 共用 |
| GET | `/api/v1/auth/me` | 是 | 含 `is_vip`、会员到期 |
| GET | `/api/v1/user/preferences` | 是 | 读书喜好 |
| PUT | `/api/v1/user/preferences` | 是 | 分类最多 8 个 |
| GET | `/api/v1/user/orders/shipping` | 是 | 收发货列表 |

**站点 / 首页 / 书籍**

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/v1/site/config` | 否 | 氛围配置 |
| GET | `/api/v1/categories` | 否 | 公开分类 |
| GET | `/api/v1/health` | 否 | 健康检查 |
| GET | `/api/v1/home/featured` | 否 | 主推书 |
| GET | `/api/v1/home/hot-books` | 否 | 热门分页 |
| GET | `/api/v1/books` | 否 | 书单筛选/搜索 |
| GET | `/api/v1/books/{id}` | 否 | 详情；登录写浏览记录 |
| GET | `/api/v1/books/{id}/play-auth` | 否 | 含 `full_access`、`max_duration` |
| POST | `/api/v1/books/{id}/play-report` | 否 | 播放进度上报 |
| GET | `/api/v1/books/{id}/similar` | 否 | 相似推荐 |

**收藏 / 浏览 / 订单**

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | `/api/v1/favorites` | 是 | 收藏 |
| DELETE | `/api/v1/favorites/{book_id}` | 是 | 取消收藏 |
| GET | `/api/v1/favorites` | 是 | 收藏列表 |
| GET | `/api/v1/history` | 是 | 浏览记录 |
| POST | `/api/v1/orders` | 是 | 创建图书订单 |
| GET | `/api/v1/orders` | 是 | 订单列表 |
| GET | `/api/v1/orders/{id}` | 是 | 订单详情 |
| POST | `/api/v1/orders/{id}/mock-pay` | 是 | 模拟支付（`MOCK_PAY_ENABLED`） |
| POST | `/api/v1/orders/{id}/cancel` | 是 | 取消订单 |

**每日读书 / 会员（二期）**

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/v1/daily/today` | 否 | 今日推荐 |
| GET | `/api/v1/daily/list` | 否 | 历史归档 |
| POST | `/api/v1/daily/{id}/like` | 是 | 点赞 |
| GET | `/api/v1/member/packages` | 否 | 套餐列表 |
| GET | `/api/v1/member/status` | 是 | 当前会员状态 |
| POST | `/api/v1/member/subscribe` | 是 | 创建会员订单 |
| POST | `/api/v1/member/orders/{id}/mock-pay` | 是 | 模拟开通 |
| POST | `/api/v1/member/orders/{id}/pay` | 是 | 预留真实支付 → 501 |

**Admin（均需 `role=admin`）**

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/admin/upload` | 封面上传 |
| GET/POST/PUT/DELETE | `/api/v1/admin/books` | 书籍 CRUD |
| GET/POST | `/api/v1/admin/videos` | 视频绑定 |
| GET/POST/DELETE | `/api/v1/admin/categories` | 分类 |
| GET | `/api/v1/admin/orders` | 订单列表 |
| PUT | `/api/v1/admin/orders/{id}/ship` | 发货填单号 |
| PUT | `/api/v1/admin/orders/{id}/status` | 取消/完结 |
| GET/PUT | `/api/v1/admin/site-config` | 氛围配置 |
| GET/POST/PUT/DELETE | `/api/v1/admin/daily` | 每日读书 |
| GET/POST/PUT/DELETE | `/api/v1/admin/member/packages` | 会员套餐 |
| GET | `/api/v1/admin/member/orders` | 会员订单 |
| GET | `/api/v1/admin/users/tree` | 省/市用户树（v1.6） |
| GET/PUT | `/api/v1/admin/users/{id}` | 用户详情/编辑（v1.6） |

**其他**

| 方法 | 路径 | 认证 |
|------|------|------|
| GET | `/sitemap.xml` | 否 |

### 9.4 创建订单

**请求**

```json
{
  "book_id": 1,
  "quantity": 1,
  "receiver_name": "张三",
  "receiver_phone": "13800138000",
  "receiver_address": "北京市朝阳区xxx"
}
```

**校验清单**

- [ ] 用户已登录
- [ ] `quantity` 为正整数
- [ ] 书 `status=published`
- [ ] `stock >= quantity`
- [ ] `receiver_phone` 匹配 `/^1\d{10}$/`（一期简单校验）

---

## 十、非功能需求

### 10.1 性能目标

| 指标 | MVP（当前） | 扩展期（S1+） |
|------|-------------|---------------|
| 只读 API P95 | < 500ms | < 200ms（热点走 Redis） |
| 首页 LCP（PC） | < 3s | < 2.5s（封面 CDN） |
| 分页大小 | 12 | 12 |
| 并发用户（单机） | 演示/内测 | S1 后压测定基线 |

### 10.2 安全清单

- [ ] 生产 `MOCK_PAY_ENABLED=false`
- [ ] Admin 路由 + API 双重鉴权
- [ ] 上传 MIME 校验（不仅看扩展名）
- [ ] CORS 白名单
- [ ] `.env` 不入库

### 10.3 SEO（一期）

- `@unhead/vue`  per-route meta
- 详情页 `og:title` / `og:image` / `og:description`
- `GET /sitemap.xml`

### 10.4 扩展触发与非功能（与 §2.5 一致）

| 阶段 | 非功能必达 |
|------|------------|
| **S0** | 冒烟测试通过；生产 `MOCK_PAY=false`；无 P0 安全项遗漏 |
| **S1** | Redis 命中率可观测；Compose 一键起全依赖 |
| **S2** | 下单/支付链路压测；Java/Python JWT 互通 |
| **S3** | 视频 URL 过期；游客无法通过直链看全片 |
| **S4** | 支付回调幂等；对账日志 |

---

## 十一、部署

### 11.1 Docker Compose

| 服务 | 镜像 | 说明 |
|------|------|------|
| mysql | `mysql:8.0` | 数据库 |
| minio | `minio/minio` | 对象存储 |
| backend | `python:3.8-slim` 构建 | FastAPI，与本地 Python 一致 |
| nginx | `nginx:alpine` | 托管 `frontend` 构建物（含 `/admin`） |

> **S1 起** compose 增加 **Redis**；**S2 起** 增加 Java trade 容器或外挂进程。当前 MVP compose 见 `deploy/docker-compose.yml`（mysql + api，minio 按需）。

### 11.2 本地开发最小步骤

```powershell
# 1. 基础设施（项目根目录）
docker compose up -d mysql minio

# 2. 后端（Python 3.8 虚拟环境）
cd backend
py -3.8 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
# 首次：aerich init -t app.db.database.TORTOISE_ORM
aerich migrate
aerich upgrade
python ..\scripts\seed.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. 前端（用户端 + /admin）
cd ..\frontend
npm install
npm run dev    # http://localhost:5188
```

### 11.3 上线检查

- [ ] `MOCK_PAY_ENABLED=false`
- [ ] HTTPS
- [ ] Seed + ≥3 视频可播
- [ ] 无 `generate_schemas()` 生产调用

---

## 十二、单人全栈排期（锁定）

**假设**：你一人负责前后端；每周可投入 **25–40 小时** 为全职节奏，**10–15 小时** 为业余节奏。

### 12.1 一期范围（单人 Must，不再摇摆）

| 做（一期 Must · 已完成） | 不做 / 延后 |
|----|-------------------|
| 首页静态氛围图 + 热门书 + 分类 | 动态视频背景、悬浮音乐 |
| 书单筛选/搜索/分页 | AuthModal（用 `/login` 页） |
| 详情视频播放 + 相似推荐 | Redis（本地可不装） |
| 注册登录、收藏、下单 + 模拟支付 | 数据看板、完美光厂视觉 |
| `/admin` 最简 CRUD | — |

> **二期 / v1.5 / v1.6 已追加**：`/daily`、会员、游客试看、浏览记录、个人中心、Admin 用户管理等见 §5.3–§5.5。

### 12.2 开发顺序（垂直切片，避免「先写完后端再联调」）

```
W1 骨架 → W2 能逛 → W3 能看 → W4 能买 → W5 能管 → W6 能部署
```

| 周 | 目标（本周结束必须能演示） | 后端 | 前端 |
|----|---------------------------|------|------|
| **W1** | 项目跑通 + 能登录 | FastAPI 骨架、Aerich、User 模型、注册登录 JWT、`seed.py` 6 分类 | Vite 初始化、CSS Token、`AppHeader`、路由骨架 |
| **W2** | 能逛首页和书单 | Book/Category CRUD API、列表分页搜索、首页 hot-books | 首页（静态背景）、书单页、`BookCard`、骨架屏 |
| **W3** | 能看解读视频 | 详情 API、play-auth、play-report、相似推荐、收藏 API | 详情页、`<video>` 封装、收藏按钮 |
| **W4** | 能下单 | Order 创建、mock-pay、库存事务、订单列表 | 登录/注册页、下单表单、订单列表 |
| **W5** | 能后台上架 | Admin CRUD API、upload 封面、site-config | `/admin` + Element Plus 表格表单 |
| **W6** | 能 Docker 部署 | docker-compose、健康检查、修 Bug | 手机端适配核心页、自测 T1–T10 |

**业余节奏**：上表 ×2，约 **10–12 周**。

### 12.3 单人每周建议节奏

| 时段 | 建议 |
|------|------|
| 周一–周二 | 后端 API + 数据模型（上午效率做难的部分） |
| 周三–周四 | 前端页面对接 API |
| 周五 | 联调 + 记 Bug 清单 |
| 周末（可选） | 补 UI、写 seed 数据、录演示视频 |

### 12.4 单人开发优先级（卡住时砍顺序 · 一期遗留参考）

> 下列为 **一期排期** 时的砍功能顺序；二期/v1.5/v1.6 已实现项勿再砍。

从先砍到后砍（仅一期未做时适用）：

1. 相似推荐 → 2. 搜索 → 3. 首页金句/主推 → 4. 收藏 → 5. 订单

> **底线**：书单 + 详情视频 + 后台能上书，网站就有演示价值。

---

## 十三、验收标准（测试用例）

> 冒烟脚本：`Customer-YuXiaotuBook/scripts/api_smoke_test.py`（51 项，含二期/v1.5/v1.6）。

### 13.1 一期（T1–T10）

| # | 用例 | 预期 |
|---|------|------|
| T1 | 游客打开首页 | 看到热门书、分类 |
| T2 | 游客播放视频 | **约 3 分钟后暂停**，引导登录（非全片） |
| T3 | 游客点击收藏 | 跳转登录 |
| T4 | 用户注册登录 | 获得 Token；可填省/市 |
| T5 | 用户收藏书籍 | 收藏列表可见 |
| T6 | 用户下单并 mock-pay | 状态 paid，库存减 1 |
| T7 | 库存为 0 下单 | 返回 40001 |
| T8 | MOCK_PAY=false 调 mock-pay | 返回 40004 |
| T9 | 管理员 CRUD 书籍+视频 | 前台可见 |
| T10 | 手机访问详情页 | 布局可用 |

### 13.2 二期核心（T11–T16）

| # | 用例 | 预期 |
|---|------|------|
| T11 | 打开 `/daily` | 今日 + 历史归档 |
| T12 | 游客播放 | 试看 180s 截断 |
| T13 | 登录用户播放 | 全片可播 |
| T14 | 模拟开通会员 | `is_vip=true` |
| T15 | Admin 发布每日内容 | 前台 `/daily` 可见 |
| T16 | 登录浏览详情 | `/user/history` 有记录 |

### 13.3 v1.5 个人中心（T17–T21）

| # | 用例 | 预期 |
|---|------|------|
| T17 | 顶栏「个人中心」 | 进入 `/user/center`，非 `/admin` |
| T18 | 保存读书喜好 | 最多 8 分类；刷新回显 |
| T19 | paid 订单 | 收发货区「待发货」 |
| T20 | Admin 发货 | 用户中心「运输中」+ 单号 |
| T21 | admin 顶栏 | 进个人中心；`/admin/login` 进后台 |

### 13.4 v1.6 用户管理（T22–T25）

| # | 用例 | 预期 |
|---|------|------|
| T22 | Admin `/admin/users` | 省/市树 + 用户总数 |
| T23 | 点击树中用户 | 会员/收藏/订单 Tab |
| T24 | shipped 订单 | 展开可见物流信息 |
| T25 | 注册填省/市 | 出现在对应树节点 |

---

## 十四、风险与降级

| 风险 | 降级 |
|------|------|
| 视频不足 | 无视频角标 + 运营补素材 |
| 库存并发 | 支付时行锁；后付者失败提示 |
| 自研 UI 超时 | 先保证功能，视觉二期迭代 |
| 无 Redis | 本地跳过；生产再加 |
| **单人精力不足** | 按 §12.4 砍功能；W5 admin 可只做书籍+视频 |

---

## 十五、单人全栈实施要点

### 15.1 技术选型减负（单人 · 与 §十六 对齐）

| 项 | 单人做法 |
|----|----------|
| 管理后台 | `frontend` 内 `/admin`，Element Plus；**永久 Python** |
| 用户端 UI | 光厂 Hero + 搜索/客服已实现；不逐像素抠细节 |
| 首页氛围 | **视频/图背景**（Admin 氛围配置）；CDN 封面 S1 |
| Redis | **S1 必装**；S0 可直查 DB |
| Java | **S2 仅 trade 一个服务**；不做 Gateway/catalog |
| 上传 | 封面 upload；视频 URL 或 OSS；HLS 转码 S3 |
| 测试 | §十三 T1–T25 + `api_smoke_test.py` |

### 15.2 推荐第一周任务清单（可直接打勾）

**Day 1–2：后端**

- [ ] `Customer-YuXiaotuBook` 目录、`backend` 依赖、`main.py` 跑通
- [ ] Tortoise 模型：User、Category、Book
- [ ] Aerich 迁移
- [ ] `POST /auth/register`、`POST /auth/login`

**Day 3–4：前端**

- [ ] `frontend` Vite + Vue Router
- [ ] 全局 CSS 变量（§四 Token）
- [ ] `/login`、`/register` 对接 API

**Day 5：数据**

- [ ] `scripts/seed.py`：6 分类 + 1 admin + 3 本示例书
- [ ] Swagger `http://localhost:8000/docs` 可测通注册登录

### 15.3 环境准备（Windows · 本机已具备）

| 工具 | 版本 | 状态 |
|------|------|------|
| Python | **3.8.10** | ✅ 已检测到，作为唯一后端版本 |
| Node.js | 18+ | 需自行确认 `node -v` |
| Docker Desktop | 最新 | 跑 MySQL + MinIO |
| IDE | Cursor | 当前环境 |

```powershell
# 验证 Python
py -3.8 --version    # 应输出 Python 3.8.10

# 创建虚拟环境（在 backend 目录）
cd e:\AI项目\YuXiaoTuAIGC\Customer-YuXiaotuBook\backend
py -3.8 -m venv .venv
.\.venv\Scripts\activate
python --version     # 确认 3.8.10
pip install -r requirements.txt
```

**常见 3.8 问题**

| 现象 | 处理 |
|------|------|
| `bcrypt` 安装失败 | 先 `pip install bcrypt==4.0.1`，再装 requirements |
| `asyncmy` 编译错误 | 使用 `asyncmy==0.2.9` 预编译 wheel；升级 pip：`python -m pip install -U pip` |
| Tortoise 连接失败 | 检查 `DATABASE_URL` 格式与 MySQL 是否已启动 |
| `aerich` 找不到模块 | 在 `backend` 目录执行，且已 `activate` 虚拟环境 |

### 15.4 单人里程碑验收（每周五自评）

| 周末 | 演示清单 |
|------|----------|
| W1 末 | Postman 登录成功；前端能打开登录页 |
| W2 末 | 浏览器能看首页+书单列表 |
| W3 末 | 能点进详情并播放 MP4 |
| W4 末 | 能注册→收藏→下单→模拟支付 |
| W5 末 | admin 能新增一本书并前台可见 |
| W6 末 | `docker compose up` 全流程跑通 |

---

## 十六、扩展路线与百万级架构（定版摘要）

> **完整详案**：[《技术选型定版.md》](./技术选型定版.md) v1.1。  
> **冲突处理**：页面与业务规则以 **本 Dev PRD** 为准；架构、语言边界、阶段优先级以 **技术选型定版** 为准。  
> **单人实施**：以技术选型文档 **§十一 单人简化版** 为执行准绳。

### 16.1 规模目标与可行性

| 目标 | 定版 |
|------|------|
| 注册用户 | **扩展目标**百万级（非当前 KPI） |
| 峰值读 QPS | 5k～20k（**S1～S2 完成后压测验证**） |
| 交易 | 强一致；库存不超卖（**S2 Java trade**） |
| 视频 | **CDN 扛流量**；S3 前 MP4 过渡可接受 |

**可行性结论**：潘宇单人 **先 S0 产品、再 S1 Redis、再 S2 Java**，路径合理；禁止跳过 S1 直接微服务化。

### 16.2 语言策略（单人轻量协同）

| 路线 | 单人推荐 | 说明 |
|------|----------|------|
| 纯 Java 重写 | ❌ | 3～6 个月重写 MVP，ROI 为负 |
| Java + Python 完整微服务 | ❌ 前期 | Gateway + trade + catalog 维护过重 |
| **Python 主站 + Java trade** | ✅ **采用** | 见 §3.4 |

### 16.3 仓库规划

```text
YuXiaoTuAIGC/
├── Customer-YuXiaotuBook/     # Python 主站（当前主仓库）
├── yuxiaotu-trade-service/    # Java（S2 创建，唯一新建 Java 服务）
├── Admin-YuXiaoTuBook/        # ECMS 独立，非 C 端必经
└── 开发文档/前台文档/
    ├── 宇小兔每日读书网站 · 开发需求文档（Dev PRD）.md
    └── 技术选型定版.md
```

### 16.4 阶段路线图（S0～S5）

| 阶段 | 重点 | 完成标准 |
|------|------|----------|
| **S0** | 产品待办（§5.6.1） | 功能可演示、冒烟测试通过 |
| **S1** | Redis + 多 worker + 封面 CDN | Compose 含 Redis；热点 API 可缓存 |
| **S2** | Java trade + Nginx 分流 | 订单/会员支付走 Java；Python 可回滚 |
| **S3** | HLS + CDN 签名 | 生产不再依赖 MP4 直链 |
| **S4** | 真实支付 | 回调进 trade；`MOCK_PAY_ENABLED=false` |
| **S5** | Gateway / catalog / MQ | 触发条件：团队 ≥2 人或 P95 不达标 |

### 16.5 API 迁移至 Java（S2 起 · 摘要）

| 路径前缀 | S2 目标 |
|----------|---------|
| `/api/v1/orders*` | Java trade |
| `/api/v1/member/subscribe*`、`/member/orders/*` | Java trade |
| 微信/支付宝回调 | Java trade（S4） |
| 其余含 `/admin/*`、`/daily/*`、书单读 | **Python** |

### 16.6 明确 Won't（架构层）

| 项 | 原因 |
|----|------|
| 单机 Docker 扛生产百万用户 | 必须多实例 + Redis + 主从 |
| 应用服务器直出视频 | 必须 CDN |
| C 端合并 ECMS | 边界混乱 |
| S0 同时做 Java trade + HLS + Python 升版 | 违反单人铁律 |

### 16.7 下一步建议（潘宇 · 单人 · 优先级）

| 优先级 | 动作 | 理由 |
|--------|------|------|
| **P0** | 订单 30 分钟超时取消（或 Admin SOP） | 需求合理性；防占单 |
| **P1** | S1：Compose + Redis、热点 API 缓存 | 性价比最高的性能手段 |
| **P2** | S0 收尾：看板/真实支付 **仅做方案**不急于上线 | 避免分散精力 |
| **P3** | S2：`yuxiaotu-trade-service` + 接口对照表 | Java 优势在交易域 |

1. 完成 P0 后跑通 `api_smoke_test.py`。  
2. S1 通过后再创建 Java 仓库（勿并行 HLS + Java）。  
3. 详案见 [《技术选型定版.md》](./技术选型定版.md) §十一。

---

## 附录 A：与脚手架差异（必改）

| 项 | 脚手架 | v1.2 标准 |
|----|--------|-----------|
| 路由 | `/book/list` | `/books` |
| User | `password`, `is_admin` | `password_hash`, `role` |
| Book | `intro` | `summary` + `stock` |
| 初始化 | `generate_schemas()` | Aerich |
| 管理端 | 脚手架同 frontend | **单人：合并 `/admin` 路由** |
| 视频权限 | 未定义 | 二期：游客 180s 试看 + 登录全片（§6.4） |
| 驱动 | pymysql | asyncmy |

## 附录 B：用户故事（截至 v1.6）

| ID | 故事 |
|----|------|
| US-01 | 游客可浏览书单；视频试看约 3 分钟后引导登录 |
| US-02 | 登录用户可看全片并收藏、查看浏览记录 |
| US-03 | 用户可填写地址下单并模拟支付 |
| US-04 | 运营可在 Admin 上架书、绑视频、发货 |
| US-05 | 库存不足时系统拒绝下单 |
| US-06 | 用户可在个人中心订制读书喜好（最多 8 分类） |
| US-07 | 用户可查看已购书籍的发货进度与物流单号 |
| US-08 | 用户可浏览每日读书专栏并点赞 |
| US-09 | 用户可模拟开通会员并在顶栏看到 VIP 标识 |
| US-10 | 用户注册时可填写省份、城市 |
| US-11 | 运营可在 Admin 按省/市查看用户会员、收藏与图书订单 |

## 附录 C：版本变更日志

| 版本 | 日期 | 要点 |
|------|------|------|
| v1.0 | — | 首版 Dev PRD |
| v1.1 | 2026-07-01 | 对齐脚手架、补订单地址、分期策略 |
| v1.2 | 2026-07-01 | 消除视频权限矛盾；库存支付时扣减；MoSCoW；测试用例 |
| v1.3 | 2026-07-01 | 单人全栈版：合并 admin 路由、6 周排期 |
| v1.4 | 2026-07-01 | **锁定 Python 3.8.10**；依赖版本固定；3.8 代码约束；Docker 3.8-slim |
| v1.5 | 2026-07-01 | **用户个人中心** `/user/center`；顶栏「管理」改「个人中心」；读书喜好 + 购书收发货；订单物流字段 |
| v1.5.1 | 2026-07-01 | **附录 E**：开发进度对照表（已完成 vs 待办，供二期收尾/三期立项） |
| v1.6 | 2026-07-01 | **Admin 用户管理**：地区树、用户详情 Tab；§9.3 全量接口 |
| v1.7 | 2026-07-02 | **百万级扩展路线**：§1.7 七次评审、§3.4 双栈摘要、§5.6 分 S0/S1～S5、§6.2 光厂 Hero、**§十六**；关联《技术选型定版.md》 |
| v1.8 | 2026-07-02 | **开发者定稿（潘宇）**：§1.10 八次评审、§2.5 扩展触发、§6.4.1 试看边界、§10.1/10.4 性能与安全、§16.7 单人优先级；消除 Redis/试看/会员等历史矛盾 |

## 附录 D：Python 3.8 兼容性速查

| 包 | 锁定版本 | 不支持 3.8 的版本 |
|----|----------|-------------------|
| fastapi | 0.109.2 | ≥ 0.115 |
| tortoise-orm | 0.20.1 | 升级前需查 release note |
| pydantic | （随 FastAPI） | 独立升级需谨慎 |
| bcrypt | 4.0.1 | 4.1+ 与 passlib 偶发冲突 |

## 附录 E：开发进度对照表（截至 v1.8 · 2026-07-02）

> **用途**：对照 Dev PRD / 产品 PRD 与 `Customer-YuXiaotuBook` 实际代码，作为 **二期收尾 / 三期立项** 依据。  
> **图例**：✅ 已完成 · 🔶 部分完成（接口/结构预留） · ❌ 未开始 · ⏸ 文档 Won't / 长期不做

### E.1 总体进度（估算）

| 分期 | 文档项数（约） | 已完成 | 部分 | 未做 | 完成度 |
|------|----------------|--------|------|------|--------|
| 一期 Must/Should | ~25 | ~22 | ~2 | ~1 | **~90%** |
| 二期核心（§5.3） | ~10 | ~8 | ~1 | ~1 | **~80%** |
| v1.5 个人中心 | 6 | 6 | 0 | 0 | **100%** |
| v1.6 用户管理 | 7 | 7 | 0 | 0 | **100%** |
| **扩展 S1～S5（§十六）** | ~8 | 0 | ~1 | ~7 | **~5%**（光厂 Hero UI 已做） |
| 三期（§5.6.1） | ~8 | 0 | 0 | ~8 | **0%** |

**结论**：**MVP+ 可演示/可运营**；百万级扩展 **尚未启动 S1（Redis）**，架构路线已在 **§十六 + 技术选型定版** 锁定。

---

### E.2 一期功能对照

| 模块 | 需求要点 | 状态 | 说明 / 代码位置 |
|------|----------|------|-----------------|
| 首页氛围 | 背景图 + 金句 + 主推 | ✅ | `Home.vue` + `site_config`；静态背景图 |
| 首页氛围 | 动态视频背景 | 🔶 | Hero 视频/图已实现；悬浮音乐仍无 |
| 首页氛围 | 全局悬浮音乐 | ❌ | 后台可配 `bg_music`，前台无 `AtmospherePlayer` |
| 书单 | 分类/搜索/分页/has_video 优先 | ✅ | `Books.vue` + `GET /books` |
| 详情 | 信息 + 视频 + 相似推荐 | ✅ | `BookDetail.vue` + play-auth / similar |
| 详情 | play-report ≥30s 统计 | ✅ | `POST /books/{id}/play-report` |
| 用户 | 注册/登录/JWT | ✅ | `auth.py` + Login/Register |
| 收藏 | 增删查 | ✅ | `favorites.py` + `Favorites.vue` |
| 浏览记录 | 详情写入 + 列表页 | ✅ | `books.py` type=2 + `History.vue` |
| 订单 | 创建/mock-pay/列表/取消 | ✅ | `orders.py` + `Orders.vue` |
| 订单 | 30 分钟未支付自动取消 | ❌ | 文档 Should；仅 Admin/用户手动取消 |
| Admin | 书籍/视频/分类/订单/氛围 | ✅ | `/admin/*` + Element Plus |
| Admin | 图片 upload | ✅ | `POST /admin/upload` |
| 部署 | Docker MySQL + API | ✅ | `deploy/docker-compose.yml` |
| 部署 | Redis 缓存/限流 | ❌ | **S1 待做**；见 §十六 |
| 前端 | AuthModal 弹窗登录 | ❌ | 文档 Should；使用独立 `/login` 页 |
| 前端 | SkeletonCard / EmptyState | 🔶 | 部分页面有简单空态，无统一组件 |
| SEO | sitemap.xml | ✅ | `main.py` 静态 sitemap |
| SEO | 深度 SSR/预渲染 | ❌ | 三期 |
| 视觉 | 光厂 1:1 像素级 | 🔶 | Token + 布局已有，动效/氛围未抠满 |
| 验收 | T1–T10 | 🔶 | 冒烟测试覆盖大部分；T10 手机未自动化 |

---

### E.3 二期功能对照（文档 §5.4 + 产品 PRD §21.2）

| 模块 | 需求要点 | 状态 | 说明 |
|------|----------|------|------|
| 每日读书 | 今日/归档/点赞 | ✅ | `daily.py` + `Daily.vue` + Admin CRUD |
| 每日读书 | **定时自动发布** | ❌ | 无 APScheduler；Admin 手动发布 |
| 会员 | 套餐/模拟开通/状态 | ✅ | `member.py` + `MemberCenter.vue` |
| 会员 | **真实支付**（微信/支付宝） | 🔶 | `Wechat/AlipayPaymentProvider` 空壳；`mock-pay` 可用 |
| 会员 | 会员专属内容/折扣 | ❌ | 仅 `is_vip` 标识；无独家内容拦截 |
| 视频权限 | 游客 3 分钟试看 | ✅ | `play-auth` max_duration=180 + `VideoPlayer` |
| 视频权限 | 登录用户全片 | ✅ | `full_access=true` |
| 视频权限 | **HLS 签名鉴权** | ❌ | 仍为 MP4 直链 |
| 浏览记录 | 前台页面 | ✅ | v1.5 前已完成 |
| Admin | 每日/会员管理 | ✅ | `admin/Daily.vue` `MemberPackages.vue` |
| Admin | **数据看板图表** | ❌ | 无 `/admin` 仪表盘 |
| AI | **批量生成解说/金句入库** | ❌ | 产品 PRD 二期；代码无 AI 模块 |
| 图书支付 | 真实支付回调 | 🔶 | 图书订单仅 `mock-pay`；会员同 |

---

### E.4 v1.5 个人中心对照（文档 §6.6）

| 模块 | 需求要点 | 状态 | 说明 |
|------|----------|------|------|
| 导航 | 顶栏「个人中心」→ `/user/center` | ✅ | `AppHeader.vue`；不再暴露 Admin 入口 |
| 页面 | 账户概览 + 快捷入口 | ✅ | `UserCenter.vue` |
| 喜好 | 分类多选（**最多 8 个**）+ 场景标签 | ✅ | `user_preference` + PUT/GET preferences |
| 喜好 | 根据偏好推荐书单 | ❌ | Could；仅保存，未改推荐算法 |
| 收发货 | Tab + 物流展示 | ✅ | `GET /user/orders/shipping` |
| Admin | 发货填单号 | ✅ | `PUT /admin/orders/{id}/ship` |
| 收发货 | 用户确认收货 | ❌ | 文档 Won't v1.5 / 三期 |
| 收发货 | 快递轨迹 API | ❌ | 文档 Won't v1.5 |
| 验收 | T17–T21 | 🔶 | 冒烟测试覆盖 API；UI 需人工点验 |
| 迁移 | orders 物流字段 + user_preference | ✅ | `scripts/migrate_v15_user_center.py` |

---

### E.5 v1.6 Admin 用户管理对照（文档 §6.9）

| 模块 | 需求要点 | 状态 | 说明 |
|------|----------|------|------|
| 注册 | 省份、城市（可选） | ✅ | `Register.vue` + `auth.register` |
| 未填地区 | 归入「未填写」节点 | ✅ | `user_admin_service.build_user_region_tree` |
| Admin 树 | 省→市→用户 | ✅ | `GET /admin/users/tree` + `Users.vue` |
| 用户详情 | 会员 / 收藏 / 图书订单 Tab | ✅ | `GET /admin/users/{id}` |
| 订单物流 | 可展开运单号、发货时间 | ✅ | 详情 orders 含 `ship_*` 字段 |
| 编辑用户 | nickname / province / city / status | ✅ | `PUT /admin/users/{id}` |
| Admin 账号 | 不出现在地区树 | ✅ | 仅 `role=user` |
| 筛选增强 | VIP / 有订单筛选 | ❌ | 文档 Won't v1.6 |
| 级联选择 | 省/市级联注册 | ❌ | Could；当前为文本输入 |
| 验收 | T22–T25 | 🔶 | 冒烟测试覆盖 API；UI 需人工点验 |
| 迁移 / Seed | 地区字段 + 演示用户 | ✅ | `migrate_user_region.py`；`demo_hz`/`demo_sh`/`demo_bj` |

---

### E.6 三期功能对照（文档 §5.6 + 产品 PRD §21.3）

| 模块 | 需求要点 | 状态 | 优先级建议 |
|------|----------|------|--------------|
| 社区 | 书评、评论、点赞、回复 | ❌ | P2（生态） |
| 书单 | 用户创建/编辑/分享书单 | ❌ | P2；`collect_type=3` 模型 PRD 有，未实现 |
| 文创 | 周边商城 | ❌ | P3 |
| 出版社 | B 端合作专区 | ❌ | P3 |
| 工程 | SSR / 深度 SEO | ❌ | P2 |
| 工程 | CDN / 性能优化 | ❌ | P2 |
| 订单 | 用户确认收货 | ❌ | P1（闭环物流） |
| 登录 | 手机验证码 | ⏸ | 一期 Won't |
| 客户端 | 原生 App | ⏸ | 明确不做 |
| 其他 | 直播弹幕、UGC 社区大规模 | ⏸ | 明确不做 |

---

### E.7 建议后续迭代顺序（立项参考 · 与 §十六 对齐）

| 批次 | 名称 | 建议内容 | 阶段 |
|------|------|----------|------|
| **S1** | 性能基线 | Redis + 多 worker + 封面 CDN | 基础设施 |
| **S2** | 交易域 Java | `yuxiaotu-trade-service` + Nginx 分流 | 强一致 |
| **S0 产品** | 商业化准备 | **订单 30 分钟超时取消（P0）**、Admin 看板 | Python |
| **S3** | 视频终态 | HLS + CDN 签名 | 防盗链 |
| **S4** | 真实支付 | 微信/支付宝 → Java trade | GMV |
| **S5+** | 扩容 | catalog / Gateway / MQ | 团队或 QPS 触发 |
| **3A 社区** | 互动 | 书评、书单分享 | 三期 |

---

### E.8 与产品 PRD 交付标准差距（摘要）

| PRD 交付标准 | 当前 |
|--------------|------|
| 21.1 一期：氛围正常、视频可播、可下单、后台可管 | ✅ 基本满足（氛围为静态图降级版） |
| 21.2 二期：每日自动更新、会员可用、**AI 批量**、权限分层 | 🔶 每日/会员/试看已实现；缺自动发布、AI、看板；VIP 暂无独家内容 |
| 21.3 三期：社区、分享、文创、SEO 深度优化 | ❌ 未开始 |

---

*附录 E 随代码变更更新；下次大版本发布请同步修订完成度列。*

---

*v1.8 为当前生效版本（开发者：**潘宇**）；架构详案见 [《技术选型定版.md》](./技术选型定版.md)。*
