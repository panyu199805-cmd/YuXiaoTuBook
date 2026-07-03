# P1 交易域 Java 接口对照表

| 项目 | 说明 |
|------|------|
| 文档版本 | **v1.0** |
| 定版日期 | 2026-07-02 |
| 开发者 | **潘宇** |
| 目标服务 | **`yuxiaotu-trade-service`**（Spring Boot 3.2 + MyBatis-Plus） |
| 实施阶段 | **S2**（前置：**S1 Redis 基线完成**） |
| 关联文档 | [《技术选型.md》](./技术选型.md) §四 · [《技术选型定版.md》](./技术选型定版.md) §十一 |
| 原则 | **对外 URL / 请求体 / 响应体与现网 Python 保持一致**；前端与冒烟测试零改动 |

---

## 〇、服务概览

| 项 | 定版 |
|----|------|
| 服务名 | `yuxiaotu-trade-service` |
| 端口 | `8081`（开发） |
| 上下文路径 | 无（与 Python 一致，路径从 `/api/v1` 开始） |
| 数据库 | **共用** MySQL `yuxiaotu_book`（与 Python 同库同表） |
| Redis | S2 起用于分布式锁、幂等、可选套餐缓存 |
| JWT | HS256 · 共用 `JWT_SECRET` · payload `{ sub, role, exp }` |
| 统一响应 | `{ "code": number, "msg": string, "data": any \| null }` |

### 0.1 Java 包结构（建议）

```text
com.yuxiaotu.trade
├── TradeApplication.java
├── config/          # JwtFilter, Redis, Mybatis, Cors
├── controller/
│   ├── OrderController.java
│   ├── MemberController.java
│   └── PaymentNotifyController.java   # S4
├── dto/
│   ├── request/
│   └── response/
├── entity/          # 与 MySQL 表 1:1
├── mapper/
├── service/
│   ├── OrderService.java
│   ├── MemberService.java
│   ├── StockService.java
│   └── PaymentService.java
├── task/            # OrderTimeoutJob（30 分钟取消）
└── common/          # ApiResponse, BizException, ErrorCodes
```

### 0.2 Nginx 分流（S2 上线）

```nginx
location ~ ^/api/v1/(orders|member/subscribe|member/orders|member/status|member/packages) {
    proxy_pass http://127.0.0.1:8081;
    proxy_set_header Authorization $http_authorization;
}

location /api/ {
    proxy_pass http://127.0.0.1:8000;
}
```

S4 追加：

```nginx
location ~ ^/api/v1/payment/(wechat|alipay)/notify {
    proxy_pass http://127.0.0.1:8081;
}
```

---

## 一、统一约定

### 1.1 响应封装

| Python | Java |
|--------|------|
| `success(data, msg)` | `ApiResponse.ok(data, msg)` → HTTP 200 |
| `fail(msg, code)` | `ApiResponse.fail(code, msg)` → HTTP 见下表 |

**HTTP 状态码映射（与 Python 一致）**

| `code` | HTTP |
|--------|------|
| 200 | 200 |
| 400, 40001～40005 | 400 |
| 401 | 401 |
| 403 | 403 |
| 404 | 404 |
| 501 | 501 |
| 500 | 500 |

### 1.2 鉴权

| Python | Java |
|--------|------|
| `get_current_user` | `JwtAuthFilter` → `@AuthenticationPrincipal Long userId` |
| Header | `Authorization: Bearer {token}` |
| 未登录 | `{ "code": 401, "msg": "请先登录", "data": null }` |

> trade 服务 **不实现** 登录；token 由 Python `/auth/login` 签发。

### 1.3 业务错误码（图书订单 · 与 Python 对齐）

| code | msg 关键词 | 场景 |
|------|------------|------|
| 40001 | 库存不足 | 下单或支付时 stock 不够 |
| 40002 | 书籍已下架 | book.status ≠ published |
| 40004 | 模拟支付 | `MOCK_PAY_ENABLED=false` |
| 40005 | 订单状态 | 非 pending_payment 时支付 |
| 400 | 其它 | 数量无效、手机号格式等 |

### 1.4 订单状态机（图书 `orders.status`）

```text
pending_payment ──mock-pay──► paid ──Admin ship──► shipped ──Admin──► completed
       │                         │
       └──── cancel ────────────┴──── cancel（Admin/用户，paid 时回滚库存）
       │
       └── timeout 30min ──► cancelled（S2 新增定时任务）
```

| status | status_label（响应字段） |
|--------|--------------------------|
| pending_payment | 待支付 |
| paid | 待发货 |
| shipped | 运输中 |
| completed | 已完成 |
| cancelled | 已取消 |

### 1.5 库存规则（与 Dev PRD 一致）

| 时机 | 行为 |
|------|------|
| 创建订单 | 仅校验 `book.stock >= quantity`，**不扣减** |
| mock-pay / 真实支付成功 | `SELECT ... FOR UPDATE` 扣减 `book.stock` |
| 已支付订单取消 | 回滚库存 |
| Admin 改库存 | **Python Admin** 写 `book.stock`，trade 不参与 |

### 1.6 订单号生成

| 类型 | Python 现网 | Java 必须一致 |
|------|-------------|---------------|
| 图书订单 | `YT` + `yyyyMMddHHmmss` | 同左 |
| 会员订单 | `M` + `yyyyMMddHHmmss` + UUID 前 8 位大写 | 同左 |

---

## 二、数据库表对照

### 2.1 `orders`（Python `models/order.py`）

| 字段 | 类型 | Java Entity | 说明 |
|------|------|-------------|------|
| id | INT PK | `Long id` | |
| order_no | VARCHAR(32) UNIQUE | `String orderNo` | |
| user_id | INT | `Long userId` | JWT sub |
| total_amount | DECIMAL(10,2) | `BigDecimal totalAmount` | |
| status | VARCHAR(20) | `String status` | 见 §1.4 |
| receiver_name | VARCHAR(50) | `String receiverName` | |
| receiver_phone | VARCHAR(20) | `String receiverPhone` | |
| receiver_address | VARCHAR(500) | `String receiverAddress` | |
| pay_time | DATETIME NULL | `LocalDateTime payTime` | |
| ship_company | VARCHAR(50) NULL | `String shipCompany` | Admin Python 写 |
| ship_tracking_no | VARCHAR(64) NULL | `String shipTrackingNo` | Admin Python 写 |
| shipped_at | DATETIME NULL | `LocalDateTime shippedAt` | |
| completed_at | DATETIME NULL | `LocalDateTime completedAt` | |
| created_at | DATETIME | `LocalDateTime createdAt` | |
| updated_at | DATETIME | `LocalDateTime updatedAt` | |

### 2.2 `order_item`

| 字段 | 类型 | Java Entity |
|------|------|-------------|
| id | INT PK | `Long id` |
| order_id | INT | `Long orderId` |
| book_id | INT | `Long bookId` |
| book_title | VARCHAR(200) | `String bookTitle` |
| price | DECIMAL(10,2) | `BigDecimal price` |
| quantity | INT | `Integer quantity` |

### 2.3 `book`（trade 只读 + 扣库存）

| 字段 | trade 用法 |
|------|------------|
| id, title, price, status, stock | 下单校验、支付扣减 |

### 2.4 `member_package`（trade 只读）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | |
| package_name | VARCHAR(50) | |
| price | FLOAT | |
| valid_day | INT | |
| rights | TEXT | JSON 字符串，响应时 parse 为数组 |
| status | INT | 1=上架 |

### 2.5 `member_order`

| 字段 | 类型 | Java Entity |
|------|------|-------------|
| id | INT PK | `Long id` |
| order_no | VARCHAR(64) UNIQUE | `String orderNo` |
| user_id | INT | `Long userId` |
| package_id | INT | `Long packageId` |
| amount | FLOAT | `BigDecimal amount` |
| status | VARCHAR(20) | `String status` |
| pay_channel | VARCHAR(20) | `String payChannel` |
| pay_time | DATETIME NULL | `LocalDateTime payTime` |
| created_at / updated_at | DATETIME | |

### 2.6 `user_member`（trade 写）

| 字段 | 说明 |
|------|------|
| user_id | UNIQUE |
| package_id | 当前套餐 |
| expire_time | 续费叠加：未过期则在原 expire 上 + valid_day |
| is_vip | 支付成功后 true |

---

## 三、图书订单 API 对照

> Python 源文件：`api/v1/orders.py` · `services/order_service.py` · `services/order_helpers.py`

### 3.1 创建订单

| 项 | 内容 |
|----|------|
| **方法·路径** | `POST /api/v1/orders` |
| **Java** | `OrderController.createOrder` |
| **鉴权** | Bearer 必须 |

**请求体**

| Python `CreateOrderRequest` | Java `CreateOrderRequest` | 校验 |
|-------------------------------|---------------------------|------|
| book_id: int | Long bookId | 必填 |
| quantity: int = 1 | Integer quantity = 1 | ≥ 1 |
| receiver_name: str | String receiverName | 必填 |
| receiver_phone: str | String receiverPhone | `^1\d{10}$` |
| receiver_address: str | String receiverAddress | 必填 |

**成功响应** `data`（与 `order_to_dict` 一致）

```json
{
  "id": 1,
  "order_no": "YT20260702143000",
  "total_amount": 59.0,
  "status": "pending_payment",
  "status_label": "待支付",
  "receiver_name": "张三",
  "receiver_phone": "13800138000",
  "receiver_address": "浙江省杭州市…",
  "pay_time": null,
  "created_at": "2026-07-02T14:30:00",
  "items": [{ "book_id": 1, "book_title": "…", "price": 59.0, "quantity": 1 }],
  "ship_company": null,
  "ship_tracking_no": null,
  "shipped_at": null,
  "completed_at": null
}
```

**业务逻辑（Java `OrderService.createOrder`）**

1. 查 `book`：`status=published`，否则 40002  
2. `stock >= quantity`，否则 40001  
3. `total_amount = price * quantity`  
4. 插入 `orders` + `order_item`（快照 title/price）  
5. **不扣库存**

---

### 3.2 我的订单列表

| 项 | 内容 |
|----|------|
| **方法·路径** | `GET /api/v1/orders` |
| **Java** | `OrderController.listOrders` |
| **鉴权** | Bearer |

**Query**：无

**响应** `data`：`OrderVO[]`，按 `created_at DESC`

---

### 3.3 订单详情

| 项 | 内容 |
|----|------|
| **方法·路径** | `GET /api/v1/orders/{order_id}` |
| **Java** | `OrderController.getOrder` |
| **鉴权** | Bearer · 仅本人 `user_id` |

**失败**：404 · `{ "code": 404, "msg": "订单不存在" }`

---

### 3.4 模拟支付

| 项 | 内容 |
|----|------|
| **方法·路径** | `POST /api/v1/orders/{order_id}/mock-pay` |
| **Java** | `OrderController.mockPay` |
| **鉴权** | Bearer |
| **配置** | `MOCK_PAY_ENABLED=true`（环境变量，与 Python 同名） |

**业务逻辑（事务 + 行锁）**

1. 若 `MOCK_PAY_ENABLED=false` → 40004  
2. 订单属于当前用户且 `status=pending_payment`，否则 40005  
3. `SELECT book FOR UPDATE`，库存足够则 `stock -= quantity`  
4. 订单 `status=paid`，`pay_time=now`  

**成功 msg**：`"支付成功"`

---

### 3.5 取消订单

| 项 | 内容 |
|----|------|
| **方法·路径** | `POST /api/v1/orders/{order_id}/cancel` |
| **Java** | `OrderController.cancelOrder` |
| **鉴权** | Bearer · 仅本人 |

**业务逻辑**

- `cancelled` / `completed` 不可取消  
- 若 `status=paid`：回滚 `book.stock`  
- 置 `status=cancelled`  

**成功 msg**：`"订单已取消"`

> **Admin 取消** 仍走 Python `PUT /admin/orders/{id}/status?status=cancelled`；S2 后建议 Python 调 trade 内部 API 或共享 cancel 逻辑，避免双实现漂移。

---

### 3.6 定时任务（S2 新增 · Python 未实现）

| 项 | 内容 |
|----|------|
| **Java** | `OrderTimeoutJob`（`@Scheduled` 或 XXL-JOB） |
| **规则** | `status=pending_payment` 且 `created_at < now - 30min` → `cancelled` |
| **库存** | 不涉及（未支付未扣库存） |

---

## 四、会员 API 对照

> Python 源文件：`api/v1/member.py` · `services/member_service.py` · `services/payment_service.py`

### 4.1 套餐列表

| 项 | 内容 |
|----|------|
| **方法·路径** | `GET /api/v1/member/packages` |
| **Java** | `MemberController.listPackages` |
| **鉴权** | 无 |

**响应 `data` 单项**

| 字段 | 类型 | 来源 |
|------|------|------|
| id | int | member_package.id |
| package_name | string | |
| price | number | |
| valid_day | int | |
| rights | array | `JSON.parse(rights)`，失败则 `[]` |

**过滤**：`status = 1`

---

### 4.2 会员状态

| 项 | 内容 |
|----|------|
| **方法·路径** | `GET /api/v1/member/status` |
| **Java** | `MemberController.getStatus` |
| **鉴权** | Bearer |

**响应 `data`**

```json
{
  "is_vip": true,
  "expire_time": "2026-08-02T12:00:00",
  "package_id": 1,
  "package_name": "月度会员"
}
```

**逻辑**：若 `expire_time < now`，更新 `is_vip=false` 并返回（与 Python `is_vip()` 一致）

---

### 4.3 创建会员订单

| 项 | 内容 |
|----|------|
| **方法·路径** | `POST /api/v1/member/subscribe` |
| **Java** | `MemberController.subscribe` |
| **鉴权** | Bearer |

**请求体**

| Python | Java |
|--------|------|
| `MemberSubscribeRequest.package_id` | `SubscribeRequest.packageId` |

**成功 `data`**

```json
{
  "id": 10,
  "order_no": "M20260702143000A1B2C3D4",
  "amount": 29.9,
  "status": "pending_payment"
}
```

**失败**：套餐不存在或下架 → 400

---

### 4.4 模拟支付开通会员

| 项 | 内容 |
|----|------|
| **方法·路径** | `POST /api/v1/member/orders/{order_id}/mock-pay` |
| **Java** | `MemberController.mockPay` |
| **鉴权** | Bearer |
| **配置** | `MEMBER_MOCK_PAY_ENABLED=true` |

**成功 `data`**

```json
{
  "order_id": 10,
  "member": {
    "is_vip": true,
    "expire_time": "2026-08-02T12:00:00",
    "package_id": 1,
    "package_name": "月度会员"
  },
  "expire_time": "2026-08-02T12:00:00"
}
```

**成功 msg**：`"开通成功"`

**业务逻辑**

1. 校验订单归属与 `pending_payment`  
2. `member_order.status=paid`，`pay_time=now`，`pay_channel=mock`  
3. `activateMember`：续期写 `user_member`  

---

### 4.5 发起真实支付（S4 · 预留）

| 项 | 内容 |
|----|------|
| **方法·路径** | `POST /api/v1/member/orders/{order_id}/pay` |
| **Java** | `MemberController.createPayment` |
| **鉴权** | Bearer |

| 条件 | 响应 |
|------|------|
| `PAYMENT_PROVIDER=mock` | 501 · `"真实支付尚未配置，请使用 mock-pay"` |
| wechat/alipay 未配置 | 501 · NotImplemented 文案 |

**成功 `data`**（规划，与 Python Provider 对齐）：支付参数对象，供前端调起 SDK。

---

## 五、支付回调 API（S4）

| 方法·路径 | Java | 说明 |
|-----------|------|------|
| `POST /api/v1/payment/wechat/notify` | `PaymentNotifyController.wechatNotify` | 验签 + 幂等 |
| `POST /api/v1/payment/alipay/notify` | `PaymentNotifyController.alipayNotify` | 验签 + 幂等 |

**幂等键**：`order_no` + `pay_channel` + 第三方交易号 → Redis / DB 唯一索引

**处理**：更新 `member_order` 或 `orders`，写 `user_member` 或扣库存，与 mock-pay 同事务语义。

---

## 六、Python ↔ Java 类名速查

### 6.1 Controller 映射

| Python 路由函数 | Java Controller 方法 |
|-----------------|------------------------|
| `orders.create_order` | `OrderController.createOrder` |
| `orders.list_orders` | `OrderController.listOrders` |
| `orders.get_order` | `OrderController.getOrder` |
| `orders.mock_pay` | `OrderController.mockPay` |
| `orders.cancel_order` | `OrderController.cancelOrder` |
| `member.member_packages` | `MemberController.listPackages` |
| `member.member_status` | `MemberController.getStatus` |
| `member.member_subscribe` | `MemberController.subscribe` |
| `member.member_mock_pay` | `MemberController.mockPay` |
| `member.member_real_pay` | `MemberController.createPayment` |

### 6.2 DTO 映射

| Python (Pydantic) | Java (record / class) |
|-------------------|------------------------|
| `CreateOrderRequest` | `CreateOrderRequest` |
| `MemberSubscribeRequest` | `SubscribeRequest` |
| `order_to_dict()` 输出 | `OrderVO` + `OrderItemVO` |
| `get_member_profile()` 输出 | `MemberProfileVO` |
| `list_packages()` 单项 | `MemberPackageVO` |
| `mock_pay_member_order()` 输出 | `MemberPayResultVO` |

### 6.3 Service 映射

| Python | Java |
|--------|------|
| `OrderService.create_order` | `OrderService.createOrder` |
| `OrderService.mock_pay` | `OrderService.mockPay` + `StockService.deduct` |
| `OrderService.cancel` | `OrderService.cancel` |
| `create_subscribe_order` | `MemberService.createSubscribeOrder` |
| `mock_pay_member_order` | `MemberService.mockPay` |
| `activate_member` | `MemberService.activateMember` |
| `get_member_profile` / `is_vip` | `MemberService.getProfile` |
| `get_payment_provider()` | `PaymentService` + `MockProvider` / `WechatProvider` |

---

## 七、环境变量（与 Python 对齐）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | 同 Python | JDBC 改写：`jdbc:mysql://...` |
| `JWT_SECRET` | **必须与 Python 相同** | |
| `JWT_EXPIRE_HOURS` | 168 | 仅签发在 Python；trade 只验签 |
| `MOCK_PAY_ENABLED` | true | 图书 mock-pay |
| `MEMBER_MOCK_PAY_ENABLED` | true | 会员 mock-pay |
| `PAYMENT_PROVIDER` | mock | S4：wechat / alipay |
| `ORDER_TIMEOUT_MINUTES` | 30 | S2 定时取消 |

---

## 八、S2 上线检查清单

### 8.1 开发完成

- [ ] 11 个 C 端交易接口与 Python 响应 **字段级一致**（含 `status_label`、ISO8601 时间）
- [ ] 错误码 40001～40005 与 msg 关键词一致
- [ ] 订单号格式一致
- [ ] 支付扣库存事务 + 行锁压测通过
- [ ] 30 分钟超时取消任务运行
- [ ] JWT 与 Python 互通（同一 token 调 Python `/auth/me` 与 Java `/orders`）

### 8.2 部署

- [ ] Nginx 分流规则上线
- [ ] Python 侧 `orders.py` / `member.py` 交易路由 **关闭或仅内网回滚**
- [ ] 冒烟：`scripts/api_smoke_test.py` 全绿（交易段走 8081）

### 8.3 回滚

- [ ] Nginx 改回全量 `proxy_pass` Python 8000
- [ ] Java 容器停止；Python 交易路由重新启用

---

## 九、不在本服务范围（明确排除）

| 接口 | 归属 |
|------|------|
| `PUT /api/v1/admin/orders/{id}/ship` | Python Admin |
| `PUT /api/v1/admin/orders/{id}/status` | Python Admin |
| `GET /api/v1/admin/orders` | Python Admin（只读） |
| `GET /api/v1/user/orders/shipping` | Python（只读 orders 表） |
| `POST/PUT/DELETE /api/v1/admin/member/packages` | Python Admin |
| `GET /api/v1/admin/member/orders` | Python Admin |
| `POST /api/v1/auth/*` | Python |

---

## 附录 A：接口总表

| # | 方法 | 路径 | Java Controller | 阶段 |
|---|------|------|-----------------|------|
| 1 | POST | `/api/v1/orders` | OrderController.createOrder | S2 |
| 2 | GET | `/api/v1/orders` | OrderController.listOrders | S2 |
| 3 | GET | `/api/v1/orders/{id}` | OrderController.getOrder | S2 |
| 4 | POST | `/api/v1/orders/{id}/mock-pay` | OrderController.mockPay | S2 |
| 5 | POST | `/api/v1/orders/{id}/cancel` | OrderController.cancelOrder | S2 |
| 6 | GET | `/api/v1/member/packages` | MemberController.listPackages | S2 |
| 7 | GET | `/api/v1/member/status` | MemberController.getStatus | S2 |
| 8 | POST | `/api/v1/member/subscribe` | MemberController.subscribe | S2 |
| 9 | POST | `/api/v1/member/orders/{id}/mock-pay` | MemberController.mockPay | S2 |
| 10 | POST | `/api/v1/member/orders/{id}/pay` | MemberController.createPayment | S4 |
| 11 | POST | `/api/v1/payment/wechat/notify` | PaymentNotifyController.wechatNotify | S4 |
| 12 | POST | `/api/v1/payment/alipay/notify` | PaymentNotifyController.alipayNotify | S4 |

---

## 附录 B：版本变更日志

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-07-02 | 首版：12 接口 · 表字段 · DTO · 错误码 · 上线清单 |

---

*本文档随 S2 开发更新；接口变更须同步 [《技术选型.md》](./技术选型.md) 与冒烟测试。*
