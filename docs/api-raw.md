# `POST /raw` —— 原始文本

只返回 PDF 的原始文本层，不做字段提取。**调试票面解析时最有用**。

## 请求

```bash
curl -H "X-API-Key: $KEY" \
     -F "file=@发票.pdf" \
     http://localhost:8091/raw
```

入参形状与 [`POST /invoice`](api-invoice.md) 相同。

## 响应

```json
{
  "text": "电子发票（增值税专用发票）\n发票号码：25502000000000000001\n...",
  "lines": ["电子发票（增值税专用发票）", "发票号码：25502000000000000001", "..."],
  "page_count": 1
}
```

| 字段 | 含义 |
| --- | --- |
| `text` | 整份文档的原始文本（多页用换行拼接） |
| `lines` | 按行拆开的文本数组 |
| `page_count` | 页数 |

## 限制

**XML / OFD 直接 400 拒绝** —— 这个端点只处理 PDF 的文本层。

```bash
curl -F "file=@全电发票.xml" http://localhost:8091/raw
# {"detail": "..."}   HTTP 400
```

要看 XML / OFD 的结构化结果，用 [`POST /invoice`](api-invoice.md)。

## 相关

- [`POST /invoice`](api-invoice.md) —— 字段级提取
- [解析器与票种](parsers.md) —— 每个票种怎么解析的
