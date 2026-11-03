# `POST /invoice/batch` —— 批量提取

一次传多份发票，并行处理，**按输入顺序**返回数组。

> ⚠️ **企业版能力**。开源版里这个路径存在但返回 403
> `feature_not_available`（feature=`batch`）。详见 [发行版与许可证](editions.md)。

## 请求

```bash
curl -H "X-API-Key: $KEY" \
     -F "files=@发票A.pdf" \
     -F "files=@发票B.pdf" \
     http://localhost:8091/invoice/batch
```

三种文件来源（上传二进制 / 服务端路径 / 远端 URL / base64）与混传规则，
见 [批量端点入参](batch-input.md)。

## 响应

数组，每项与单文件端点 [`POST /invoice`](api-invoice.md) 的响应体**同构**：

```json
[
  {
    "file": "发票A.pdf",
    "invoice_number": "25502000000000000001",
    "total_amount": "140141.09",
    "message": "success"
  },
  {
    "file": "发票B.pdf",
    "invoice_number": "",
    "message": "error: parse_failed: ..."
  }
]
```

**一项失败不影响其它项** —— 整批返回 200，错误只落在那一项的 `message` 上。
这是刻意设计：一张坏票不该让整个批次的其它票一起丢掉。

## 限额

| 限制 | 默认值 | 环境变量 |
| --- | --- | --- |
| 文件数 | 50 | `IC_MAX_BATCH_FILES` |
| 单文件大小 | 10 MB | `IC_MAX_FILE_MB`（与 `/invoice` 共用） |
| 总大小 | 500 MB | `IC_MAX_BATCH_TOTAL_MB` |
| 并发线程 | 4 | `IC_BATCH_WORKERS` |

## 与其它批量端点的关系

`/invoice/batch`、`/customs/batch`、`/acceptance/batch` 三个端点的**入参形状、
限额、错误语义完全一致**，只有解析的票种和响应字段不同。

| 端点 | 解析对象 | 响应 |
| --- | --- | --- |
| `/invoice/batch` | 常规发票票种 | `ExtractResponse[]` |
| [`/customs/batch`](api-customs-batch.md) | 海关出口货物报关单 | `CustomsDeclarationHeader[]` |
| [`/acceptance/batch`](api-acceptance-batch.md) | 电子银行承兑汇票 | `AcceptanceBill[]` |

## 相关

- [批量端点入参](batch-input.md) —— 三种来源与混传规则
- [输出字段](output-fields.md)
- [发行版与许可证](editions.md)
