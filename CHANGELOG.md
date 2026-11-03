# Changelog

本文件记录 **invoice_cn_ce** 的版本变更。格式遵循
[Keep a Changelog](https://keepachangelog.com/)，版本号遵循
[语义化版本](https://semver.org/)。

## [1.0.0] - 2026-11-01

首个正式版本。

### 票种覆盖

- **PDF**
  - 电子发票（增值税专用发票 / 普通发票）标准新格式（含京东、水费、通行费变体）
  - 电子发票（普通发票）平台下载版 —— 票面标签块在上、值块在下，按词坐标重建阅读顺序
  - 电子发票（普通发票）旧格式（含密码区、校验码）
  - 电子发票（普通发票）合并代码 / 成品油变体
  - 中央非税收入统一票据（电子）—— 专利年费、行政事业性收费等
  - 电子发票（航空运输电子客票行程单）
  - 电子发票（铁路电子客票）
- **XML / OFD** —— 全电发票（数电票），**唯一会填满 `items[]` 商品明细的路径**

### 接口

| 端点 | 说明 | 发行版 |
| --- | --- | --- |
| `GET /health`、`GET /health/full` | 健康检查 | CE |
| `POST /invoice` | 单份发票提取 | CE |
| `POST /invoice/batch` | 批量提取（并行，按输入顺序返回数组） | CE |
| `POST /raw` | PDF 原始文本 | CE |
| `POST /verify` | 国税查验代理（需 `IC_VERIFY_ENABLED=true`） | CE |
| `POST /extract-and-verify` | 提取 + 查验一站式 | CE |
| `GET /formats`、`GET /formats/invoice`、`GET /formats/customs`、`GET /formats/acceptance` | 字段字典 | CE |
| `GET /capabilities` | 能力位与许可证状态 | CE |
| `POST /customs/batch` | 海关出口货物报关单 | EE |
| `POST /acceptance/batch` | 电子银行承兑汇票 | EE |

### 特性

- **纯 Python 实现**（`pdfplumber`）—— 无 JVM、无外部 OCR 服务，Apache-2.0。
  既能作为 HTTP 服务部署，也能 `from invoice_cn_ce import parse_pdf` 进程内调用。
- **固定字段名、统一 `snake_case`**，跨票种一致，可直接映射系统表结构。
  字段含义见 [输出字段](docs/output-fields.md)。
- **解析失败不静默返回空字段** —— `message` 给出具体原因；批量端点里错误落在**该项**上，
  整批照常返回，不会因为一张坏票丢掉整批。
- **票种误投有守门** —— 报关单发到 `/invoice` 返回 422，`message` 里指明该走哪个端点。
- **API Key 鉴权 + scope**；审计日志只记路径、字节数、状态码，**不记票面内容**。
- **票据原件不落盘** —— 服务只读传入的字节；本地部署时数据不出内网。
- **不做 OCR** —— 扫描件（图片型 PDF）没有文字层，会解析失败并说明原因。

### 文档

- `docs/` 目录，**每个接口一份独立文件**，索引见 [文档索引](docs/README.md)。

### 发行版

- `invoice-cn-ce` —— Apache-2.0，开源版。PyPI 发行名 `invoice-cn-ce`，导入名
  `invoice_cn_ce`，命令行入口 `invoice_cn_ce` / `invoice_cn_ce-server`。
- `invoice-cn-ee` —— 商业授权，追加报关单与电子承兑汇票解析；未授权时自动降级为开源版
  行为，接口返回结构化 403 `feature_not_available`，不会让服务起不来。
  详见 [发行版与许可证](docs/editions.md)。

### 配置

- 全部环境变量前缀为 `IC_*`（如 `IC_PORT`、`IC_API_KEYS`、`IC_VERIFY_ENABLED`）。
- 旧前缀 `FC_*` 仍然可用，作为回落项：`IC_*` 优先于 `FC_*`，真实环境变量优先于
  `.env` 文件。老部署升级后不必立刻改配置。
