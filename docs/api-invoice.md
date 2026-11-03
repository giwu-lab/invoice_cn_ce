# `POST /invoice` —— 单文件提取

一次传一份发票，返回结构化字段。**开源版就有**，不需要许可证。

## 请求

```bash
curl -H "X-API-Key: $KEY" \
     -F "file=@samples/新电子发票-标准/购_材料_01.pdf" \
     http://localhost:8091/invoice
```

支持的入参形式与 `/invoice/batch` 完全一致 —— 上传二进制、服务端路径、远端 URL、
base64 都行，详见 [批量端点入参](batch-input.md)。

## 响应

```json
{
  "file": "购_材料_01.pdf",
  "page_count": 1,
  "invoice_type": "电子发票（增值税专用发票）",
  "invoice_number": "25502000000000000001",
  "issue_date": "2025-11-27",
  "buyer_name": "示例采购方有限公司",
  "buyer_tax_id": "91330100MAEXAMPLE1X",
  "seller_name": "示例销售方科技有限公司",
  "seller_tax_id": "91330100MAEXAMPLE2Y",
  "amount_without_tax": "124018.66",
  "tax_amount": "16122.43",
  "total_amount": "140141.09",
  "total_amount_upper": "壹拾肆万零壹佰肆拾壹圆零玖分",
  "payee": "",
  "reviewer": "",
  "drawer": "张某某",
  "items": [],
  "expense_category": "unclassified",
  "expense_category_label": "未归类",
  "expense_category_source": "",
  "message": "success"
}
```

字段逐个说明见 [输出字段](output-fields.md)。

> `items[]` 为空是正常的 —— **商品明细只有 XML / OFD 全电票才填**，PDF 票面本身
> 就没有明细行。详见 [items[] 说明](output-fields.md#items-商品明细)。

## 失败时

解析类错误返回 **HTTP 422**，响应体仍然是上面那个 `ExtractResponse` 结构，
原因在 `message`：

```json
{"message": "error: parse_failed: ...", "invoice_number": "", "...": ""}
```

`message` 的完整取值表见 [message 语义](output-fields.md#message-字段语义)。

**解析失败不会返回一堆看起来正常的空字段而不吭声** —— 想要"静默成功"的场景
不存在，批量场景下失败会落到该项的 `message` 上。

## 限额

单文件最大 10 MB（`IC_MAX_FILE_MB`）。

## 相关

- 一次多份 → [`POST /invoice/batch`](api-invoice-batch.md)（企业版）
- 只要原始文本 → [`POST /raw`](api-raw.md)
- 提取 + 查验 → [`POST /extract-and-verify`](api-extract-and-verify.md)
