# 配置项

环境变量前缀 `IC_`，可通过 `.env` 或 `docker-compose.yml` 注入。

## 服务

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `IC_HOST` / `IC_PORT` | `0.0.0.0` / `8091` | 绑定地址 / 端口 |
| `IC_APP_ROOT` | （空） | 应用根目录，仅 `/health/full` 用。留空时按源码布局推导；镜像内置为 `/app` |
| `IC_APP_USER` | （空） | 镜像内置为 `invoice_cn_ce` |
| `IC_CORS_ALLOW_ORIGINS` | `*` | CORS 允许来源（CSV）；浏览器前端跨域用 |
| `IC_CORS_ALLOW_METHODS` | `GET,POST,OPTIONS` | CORS 允许方法 |
| `IC_CORS_ALLOW_HEADERS` | `Content-Type,Authorization` | CORS 允许请求头 |

## 限额与并发

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `IC_MAX_FILE_MB` | `10` | 单文件最大字节（`/invoice` 与所有批量端点共用） |
| `IC_MAX_BATCH_FILES` | `50` | 批量最大文件数 |
| `IC_MAX_BATCH_TOTAL_MB` | `500` | 批量总大小 |
| `IC_BATCH_WORKERS` | `4` | 批量端点并行线程数 |
| `IC_CACHE_SIZE` | `128` | LRU 缓存条目数（`0` 关闭） |

## 鉴权

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `IC_API_AUTH_ENABLED` | `true` | 鉴权总开关 |
| `IC_API_KEYS` | （空） | 逗号分隔 API key（simple 模式，**全作用域**） |
| `IC_API_KEYS_FILE` | （空） | JSON 文件路径（结构化模式，推荐生产） |
| `IC_API_KEY_DEFAULT_RPM` | `60` | 默认每分钟请求上限（`extract` 作用域） |
| `IC_API_KEY_DEFAULT_BURST` | `10` | 默认令牌桶容量 |
| `IC_API_KEY_DEFAULT_VERIFY_RPM` | `30` | `/verify` 端点独立每分钟上限（0 关闭） |
| `IC_REQUIRE_CONFIGURED_KEYS` | `true` | dev 兜底：未配置任何 key 时是否拒绝启动（生产建议保持 true） |
| `IC_API_LEGACY_ALLOW` | `false` | 双轨兼容：未带 token 也放行（仅迁移期） |
| `IC_ALLOWED_FILE_PATHS` | （空） | `file_path` 输入白名单目录（CSV）；留空则禁用该入参 |

## 国税查验代理

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `IC_VERIFY_ENABLED` | `false` | 启用国税查验代理 |
| `IC_VERIFY_ENDPOINT` | （空） | 国税代理 URL |
| `IC_VERIFY_API_KEY` | （空） | 代理侧 Bearer token |
| `IC_VERIFY_TIMEOUT` | `15` | 代理超时（秒） |

## 业务

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `IC_EXPENSE_CATEGORY_ENABLED` | `true` | 消费类别分类总开关；false 时三字段恒为空字符串 |
| `IC_LICENSE_FILE` | （空） | 企业版许可证路径（JSON，Ed25519 签名）。只被 `invoice_cn_ee` 解释；缺失/过期/签名不合法时**降级成开源版行为**。**没有 `IC_EDITION` 之类的版本开关** —— 改环境变量不能解锁企业版 |

## 没有 `IC_EDITION`

刻意不提供。版本只由两件事决定：**装了哪个发行包** + **许可证是否有效**。
有了环境变量开关，开源版用户改一个变量就解锁了，整套体系作废。
详见 [发行版与许可证](editions.md)。

## 相关

- [鉴权与审计](auth.md)
- [部署与开发](deployment.md)
