# 鉴权与审计

服务端点（除 `/health` 与 `/capabilities`）默认需要 API Key。

## 两种 Header 任选

```bash
curl -H "Authorization: Bearer $IC_KEY" http://localhost:8091/invoice -F file=@发票.pdf
curl -H "X-API-Key: $IC_KEY"            http://localhost:8091/invoice -F file=@发票.pdf
```

dev 模式首次启动需要先写 key 到 `.env`：

```bash
echo "IC_API_KEYS=\"sk_dev_$(openssl rand -base64 24 | tr -d '=' | tr '/+' '_-')\"" >> .env
chmod 600 .env
curl -H "Authorization: Bearer $(grep IC_API_KEYS .env | cut -d= -f2 | tr -d '\"')" \
  http://localhost:8091/invoice -F file=@发票.pdf
```

## 配置 Key

**Simple 模式**（推荐少量内网调用方）：

```bash
IC_API_KEYS="key-for-n8n,key-for-cli,key-for-frontend"
# 每个 key 自动拥有 extract / verify / admin 全作用域，rpm=60 / burst=10
```

> ⚠️ **Simple 模式下所有 key 自动获得 admin scope**（含 `/health/full`）。
> 多调用方场景建议改用 JSON 模式，给不同 key 分发不同 scopes。
> 「simple 模式 = 全员 admin」是显式设计，**生产部署前必须评估**。

**JSON 模式**（多租户 / 精细控制，推荐生产）：

```bash
IC_API_KEYS_FILE=/etc/invoice_cn_ce/keys.json
```

```json
[
  {"key": "sk_live_abc...",  "label": "n8n-prod",    "scopes": ["extract"], "rpm": 30, "burst": 5},
  {"key": "sk_live_def...",  "label": "ops-verify", "scopes": ["extract", "verify"], "rpm": 120, "burst": 20},
  {"key": "sk_admin_xyz...", "label": "ops-admin",  "scopes": ["extract", "verify", "admin"]}
]
```

字段：

| 字段 | 说明 |
| --- | --- |
| `key` | ≥ 32 字节随机串（`openssl rand -base64 32`） |
| `key_id` | 审计日志里 `key=` 的 8 字符 sha256 前缀；**可选填**，填了启动期必须与 `sha256(key)[:8]` 一致，否则 `KeyStoreError: mismatched_key_id`。缺省则启动期自动派生 |
| `label` | 写审计日志 |
| `scopes` | `admin` 自动获得其他所有 |
| `rpm` / `burst` | 每分钟请求上限 / 令牌桶容量 |

## Scope → 端点

| Scope | 端点 |
| --- | --- |
| `extract` | `/invoice`、`/invoice/batch`、`/customs/batch`、`/acceptance/batch`、`/raw`、`/extract-and-verify`、`/formats`、`/formats/customs`、`/formats/acceptance` |
| `verify` | `/verify` |
| `admin` | `/health/full`（超集，含 extract / verify） |

> scope 解决"**哪个 key** 能用"，发行版解决"**装的是什么**"。两者独立：
> CE 里就算 key 带了 `extract` scope 也照样打不开企业版端点（见
> [发行版与许可证](editions.md)）。

## 错误码

| 状态 | 触发 | Header |
| --- | --- | --- |
| 401 | 缺 token / token 错 | `WWW-Authenticate: Bearer realm="invoice_cn_ce", error="invalid_token"` |
| 403 | scope 不足 | `WWW-Authenticate: Bearer realm="invoice_cn_ce", error="insufficient_scope"` |
| 403 | 发行版能力未授权 | `{"detail": {"error": "feature_not_available", "feature": "...", "required_edition": "ee"}}` |
| 429 | 限速 | `Retry-After: <sec>` + `WWW-Authenticate: ... error="rate_limited"` |

`/health` 始终公开，不消耗配额。`IC_API_KEYS` 与 `IC_API_KEYS_FILE` 都为空 → 启动
WARN + 全量放行（dev 兜底，**生产前必须显式配置**）。

## 审计日志

所有受保护请求（无论成功/失败）写入 `logs/audit.log`（10 MiB × 5 自动轮转）：

```
2026-09-18 10:23:45 [AUDIT] POST /invoice -> 200 (42ms) key=a1b2c3d4 label=n8n-prod from=10.0.0.7 in=1258291B out=1834B
2026-09-18 10:23:46 [AUDIT] GET /formats -> 401 (0ms) key=- label=- from=10.0.0.7 in=0B out=0B reason=missing_token
```

`key_id` 是 `sha256(key)[:8]`，**原 key 不落盘**。

## 密钥怎么管

Docker / K8s secret 用 mount 文件路径即可，**镜像不包含任何 key**：

```yaml
# docker-compose.yml
volumes:
  - /etc/invoice_cn_ce/keys.json:/app/keys.json:ro
environment:
  IC_API_KEYS_FILE: /app/keys.json
```

反查某个 `key_id` 对应哪个 key：

```bash
python3 scripts/show_key_ids.py keys.json
# label              key_id     key (trunc)      status
# frontend-spa       339740cb   OpEAA5V6qoPKSE…  match
```

> ⚠️ **关于本地 `keys.json` / `.env`**：两者均已 `.gitignore` 排除，不会进入 git
> 历史。但仓库根目录下的 `keys.json` 是开发测试副本 —— 若与生产工作目录共用，
> 可能误传到运维环境。**生产部署请用 secret manager / K8s Secret / Vault 注入**，
> **不要**把 `keys.json` 复制进镜像，也不要把它和真实生产文件备份到一起。

## 相关

- [配置项](config.md)
- [接口一览](api-invoice.md)
