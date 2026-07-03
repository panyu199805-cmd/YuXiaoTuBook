# yuxiaotu-trade-service

宇小兔每日读书 · **交易域**（订单 / 会员 / 模拟支付）。

## 端口

- **8081**（与 Python 8000 并存；前端 Vite 按路径分流）

## 本地运行

```bash
# 需 JDK 17+、Maven 3.9+，MySQL 与 Python 共用 yuxiaotu_book
cd yuxiaotu-trade-service
mvn spring-boot:run
```

环境变量（与 Python 保持一致）：

| 变量 | 说明 |
|------|------|
| `JWT_SECRET` | 与 Customer backend 相同 |
| `MOCK_PAY_ENABLED` | 图书 mock 支付 |
| `MEMBER_MOCK_PAY_ENABLED` | 会员 mock 支付 |
| `DATABASE_URL` | JDBC URL，默认 `jdbc:mysql://127.0.0.1:3306/yuxiaotu_book?...` |

## Docker

```bash
cd Customer-YuXiaotuBook/deploy
docker compose up -d trade
```

## 接口范围

见 [《P1 交易域 Java 接口对照表》](../开发文档/前台文档/P1-交易域Java接口对照表.md)
