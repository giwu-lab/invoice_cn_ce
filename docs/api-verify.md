# `POST /verify` —— 国税查验代理

把一份发票的关键信息转发给**你自己配置的**查验上游（国税官方接口、第三方聚合
服务、或你自己的中间层），返回上游的查验结果。

> **默认关闭**。要开：`IC_VERIFY_ENABLED=true` + `IC_VERIFY_ENDPOINT=<上游 URL>`。
> 没开或没配 → **503**。

## 请求

```bash
curl -H "X-API-Key: $KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "invoice_type": "电子发票（增值税专用发票）",
           "invoice_number": "25502000000000000001",
           "issue_date": "2025-11-27",
           "total_amount": "140141.09"
         }' \
     http://localhost:8091/verify
```

请求体字段（全部可选，空串即可）：

| 字段 | 说明 |
| --- | --- |
| `invoice_type` | 发票类型 |
| `invoice_number` | 发票号码 |
| `issue_date` | 开票日期 |
| `total_amount` | 价税合计 |

字段名**刻意与 `ExtractResponse` 同名** —— 提取结果可以直接喂给查验，不用改字段名。

## 响应

上游返回什么就返回什么（没有 `response_model` 强约束）。约定形状：

```json
{
  "valid": true,
  "source": "proxy",
  "detail": {}
}
```

| 字段 | 含义 |
| --- | --- |
| `valid` | 是否查验通过（`null` = 上游没给） |
| `source` | 哪个上游答的，便于下游记日志 |
| `detail` | 上游特有的附加信息，原样透传 |

## 配置

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `IC_VERIFY_ENABLED` | `false` | 总开关 |
| `IC_VERIFY_ENDPOINT` | （空） | 上游 URL |
| `IC_VERIFY_API_KEY` | （空） | 转发给上游的 Bearer token |
| `IC_VERIFY_TIMEOUT` | `15` | 超时（秒） |

## 错误

| HTTP | `detail` | 触发 |
| --- | --- | --- |
| 503 | `verify_disabled: set IC_VERIFY_ENABLED=true to enable` | 没开 |
| 503 | `verify_unconfigured: set IC_VERIFY_ENDPOINT to a proxy URL` | 开了但没配地址 |
| 502 | `verify_proxy_error: <exc>` | 上游网络错误 / 4xx / 5xx |

## 上游响应体大小有限制

上游返回体有上限（防止失控的上游把内存吃满）：已知 `Content-Length` 超限直接拒绝；
未知长度则边收边停。

## 一次搞定提取 + 查验

不想发两次请求，用 [`POST /extract-and-verify`](api-extract-and-verify.md)。
