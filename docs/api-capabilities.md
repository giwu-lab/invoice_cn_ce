# `GET /capabilities` 与健康检查

三个**公开或管理用**的只读端点。客户端靠 `/capabilities` 决定界面上显示哪些
入口 —— 用户看得见能力边界，也知道该买什么。

## 当前能力

端点：`GET /capabilities`

```bash
curl http://localhost:8091/capabilities
```

```json
{
  "edition": "ce",
  "features": {
    "extract": true,
    "batch": false,
    "customs": false,
    "acceptance": false,
    "verify": true
  },
  "limits": {"max_file_mb": 10, "max_batch_files": 50, "max_batch_total_mb": 500},
  "license": {"status": "absent", "license_id": "", "customer": "", "expires_at": ""}
}
```

| 字段 | 说明 |
| --- | --- |
| `edition` | `ce`（开源版）或 `ee`（企业版） |
| `features` | 每个能力位的开关 |
| `limits` | 当前生效的限额，客户端可以据此提前校验 |
| `license` | 许可证状态：`absent` / `active` / 其它 reason；含 `license_id` / `customer` / `expires_at` |

**公开、无需鉴权** —— 前端在用户还没登录时也要能拿到。

> `acceptance` 是**独立**的能力位：授权了 `batch` 不等于授权电子承兑汇票解析。

前端据此显示/隐藏「批量上传」「报关单解析」「电子承兑」入口。

## 健康检查

### `GET /health` —— Liveness（公开）

```bash
curl http://localhost:8091/health
```

进程活着就返回 200。**始终公开，不消耗配额** —— 给 Docker HEALTHCHECK 和
K8s livenessProbe 用。

### `GET /health/full` —— Readiness（需 `admin` scope）

```bash
curl -H "X-API-Key: $ADMIN_KEY" http://localhost:8091/health/full
```

返回依赖、缓存、发行版、许可证的完整状态。给 K8s readinessProbe 和运维巡检用。

`admin` scope 自动获得 `extract` / `verify` 全部权限。

## 相关

- [鉴权与审计](auth.md) —— scope 怎么配
- [发行版与许可证](editions.md) —— `edition` / `features` 怎么来的
