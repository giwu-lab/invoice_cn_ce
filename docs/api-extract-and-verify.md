# `POST /extract-and-verify` —— 提取 + 查验

一次请求做完两件事：解析发票，然后（如果查验开着）调查验上游，把两个结果合在一起返回。

## 请求

入参与 [`POST /invoice`](api-invoice.md) 完全一样 —— 传文件就行：

```bash
curl -H "X-API-Key: $KEY" \
     -F "file=@发票.pdf" \
     http://localhost:8091/extract-and-verify
```

## 响应

在 `POST /invoice` 的响应体上，**多两个字段**：

```json
{
  "invoice_type": "电子发票（增值税专用发票）",
  "invoice_number": "25502000000000000001",
  "total_amount": "140141.09",
  "message": "success",
  "verify_result": {"valid": true, "source": "proxy", "detail": {}}
}
```

| 字段 | 什么时候有 | 含义 |
| --- | --- | --- |
| `verify_result` | 查验开启且上游调用成功 | 上游的查验结果（形状见 [`/verify`](api-verify.md)） |
| `verify_error` | 查验开启但上游调用失败 | 失败原因（字符串） |

**查验失败不影响提取结果** —— 字段照样返回，只是多一个 `verify_error`。
这正是它跟"先提取再自己调查验"相比省事的地方：一次往返，失败也不会互相污染。

## 查验没开时

`IC_VERIFY_ENABLED=false` 或没配 `IC_VERIFY_ENDPOINT` → **只返回提取结果**，
不出现 `verify_result` 也不出现 `verify_error`。这个端点在查验关闭时依然可用。

## 错误

| HTTP | 情况 | 响应体 |
| --- | --- | --- |
| 400 | 没给文件 | `{"detail": "Provide file, url, file_path, or file_base64"}` |
| 422 | 解析失败 | `ExtractResponse` 本体，原因在 `message` |
| 500 | 解析器内部异常 | `ExtractResponse`，`message` 为 `error: internal_error: ...` |

注意：这里的 422 / 500 响应体是 `ExtractResponse` **本体**（不是 `detail` 信封），
和 `/invoice` 保持一致。

## 相关

- [`POST /invoice`](api-invoice.md) —— 只提取
- [`POST /verify`](api-verify.md) —— 只查验
