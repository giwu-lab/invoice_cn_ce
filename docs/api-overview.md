# 接口一览与通用约定

所有端点的总表、通用入参形状、限额与错误约定。**每个端点另有独立文档**，见
[文档索引](README.md)。

## 端点总表

| 方法 | 路径 | 说明 | 发行版 | 独立文档 |
| --- | --- | --- | --- | --- |
| GET | `/health` | Liveness probe（公开） | CE | [能力与健康检查](api-capabilities.md) |
| GET | `/health/full` | Readiness probe + 依赖 / 缓存 / 发行版状态（需 `admin` scope） | CE | [能力与健康检查](api-capabilities.md#健康检查) |
| GET | `/capabilities` | 当前发行版与可用能力（公开） | CE | [能力查询](api-capabilities.md) |
| GET | `/formats` | 支持的全部票种 | CE | [票种列表](api-formats.md) |
| GET | `/formats/customs` | 海关出口货物报关单字段 schema（**两版共有的响应契约**，只有企业版能实际解析报关单） | 两版共有契约 | [报关单字段字典](api-formats.md#报关单字段字典) |
| GET | `/formats/acceptance` | 电子银行承兑汇票字段 schema（**两版共有的响应契约**，只有企业版能实际解析承兑汇票） | 两版共有契约 | [承兑汇票字段字典](api-formats.md#电子承兑汇票字段字典) |
| POST | `/invoice` | 单文件提取 | CE | [单文件提取](api-invoice.md) |
| POST | `/invoice/batch` | 批量提取（并行，按输入顺序返回） | EE | [批量提取](api-invoice-batch.md) |
| POST | `/customs/batch` | 海关出口货物报关单**批量**提取（操作联 / 出口退税联） | EE | [报关单批量提取](api-customs-batch.md) |
| POST | `/acceptance/batch` | 电子银行承兑汇票**批量**提取 | EE | [电子承兑批量提取](api-acceptance-batch.md) |
| POST | `/raw` | 仅返回 PDF 原始文本，XML/OFD 拒绝 | CE | [原始文本](api-raw.md) |
| POST | `/verify` | 国税查验代理（需 `IC_VERIFY_ENABLED=true`） | CE | [国税查验代理](api-verify.md) |
| POST | `/extract-and-verify` | 提取 + 查验一站式 | CE | [提取 + 查验](api-extract-and-verify.md) |

> 「发行版」列里的 **EE** 表示该能力由企业版发行包 `invoice_cn_ee` 提供。开源版里
> 这些路径**依然存在**，但返回 `403 feature_not_available`（结构化错误，不是
> 404），这样前端可以按能力位显示入口。详见 [发行版与许可证](editions.md)。

## 端点约定

- **发票**：`POST /invoice`（单份，返回对象）与 `POST /invoice/batch`（多份，返回数组）。
  两者请求体与响应结构一致，鉴权 scope 是 `extract`。
- **报关单**（企业版）：**只有** `POST /customs/batch` —— 多文件、返回数组，multipart 里
  重复的字段名是 `files`（不是 `file`）。
- **电子承兑汇票**（企业版）：**只有** `POST /acceptance/batch` —— 没有单文件端点，
  请求 `POST /acceptance` 得到 404（不是 403）。要解析单张票据，用批量端点提交一份即可。
- `/raw`、`/verify`、`/extract-and-verify`、`/formats/*`、`/capabilities` 的路径如上表。

## 鉴权

除 `/health` 外默认需要 API Key，Header 两种形式任选：

```bash
curl -H "Authorization: Bearer $IC_KEY" http://localhost:8091/invoice -F file=@发票.pdf
curl -H "X-API-Key: $IC_KEY"            http://localhost:8091/invoice -F file=@发票.pdf
```

Key 的配置方式（Simple / JSON 模式）、scope 与端点的对应关系、错误码、审计日志，
见 [鉴权与审计](auth.md)。

## 入参形状

`/invoice`、`/invoice/batch`、`/raw` 支持 `multipart/form-data`（`file` / `files` 字段）
和 `application/json`（`file_path` / `file_base64` / `url`）两种入参：

```bash
# multipart
curl -F "file=@samples/新电子发票-标准/购_材料_01.pdf" http://localhost:8091/invoice

# JSON
curl -H "Content-Type: application/json" \
  -d '{"file_path": "samples/新电子发票-标准/购_材料_01.pdf"}' \
  http://localhost:8091/invoice

# /raw 响应
# {"text": "...", "lines": ["..."], "page_count": 1}
```

批量端点的三种文件来源（远端 URL / 服务端路径 / base64）与混传规则，见
[批量端点入参](batch-input.md)。

## 限额

| 限制 | 默认值 | 环境变量 | 适用范围 |
| --- | --- | --- | --- |
| 单文件大小 | 10 MB | `IC_MAX_FILE_MB` | `/invoice`、`/invoice/batch`、`/customs/batch`、`/acceptance/batch` |
| 批量文件数 | 50 | `IC_MAX_BATCH_FILES` | 三个批量端点 |
| 批量总大小 | 500 MB | `IC_MAX_BATCH_TOTAL_MB` | 三个批量端点 |
| 批量并发线程 | 4 | `IC_BATCH_WORKERS` | 三个批量端点 |
| 每 key 请求速率 | 60 rpm / burst 10 | `IC_API_KEY_DEFAULT_RPM` / `_BURST` | 所有受保护端点 |

全部环境变量见 [配置项](config.md)。

## 错误约定

| 情况 | HTTP | 响应体形状 |
| --- | --- | --- |
| 解析类错误（空文件、超限、解析失败） | 422 | `ExtractResponse` / `PdfRaw` 等**业务结构体**，原因在 `message` 字段 |
| 鉴权失败 | 401 | `{"detail": ...}` + `WWW-Authenticate` |
| scope 不足 / 发行版能力未授权 | 403 | `{"detail": {...}}` |
| 请求参数非法（如报关单误发到 `/invoice`） | 422 | 业务结构体，`message` 指明正确端点 |
| 限速 | 429 | `{"detail": ...}` + `Retry-After` |
| 内部异常 | 500 | `{"detail": ...}` |

**HTTP 422 的响应体就是正常的业务结构**（不是 `{"detail": ...}` 信封），错误字符串完整
保留在 `message` 字段里。400 / 500 / 502-503 仍走 FastAPI 的 `{"detail": ...}` 信封。

`message` 的完整取值表见 [message 语义](output-fields.md#message-字段语义)。

## 相关

- [输出字段](output-fields.md) —— 响应里每个字段的含义
- [批量端点入参](batch-input.md)
- [鉴权与审计](auth.md)
- [配置项](config.md)
