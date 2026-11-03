# `GET /formats` —— 票种与字段字典

一组"只读、不解析"的端点，告诉客户端**能拿到什么字段**，好把界面渲染出来。
三个端点都需要 `extract` scope。

## 支持的全部票种

端点：`GET /formats`

```bash
curl -H "X-API-Key: $KEY" http://localhost:8091/formats
```

```json
{
  "formats": {
    "new": "电子发票（增值税专用发票/普通发票）- 标准新格式（含京东、水费、通行费变体）",
    "platform": "电子发票（普通发票）- 平台下载版（票面标签块在上、值块在下，按词坐标重建阅读顺序）",
    "old": "电子发票（普通发票）- 旧格式（含密码区、校验码）",
    "merged_code": "电子发票（普通发票）- 合并代码/成品油变体",
    "non_tax_receipt": "中央非税收入统一票据（电子）（如专利年费、行政事业性收费）",
    "airline": "电子发票（航空运输电子客票行程单）",
    "train": "电子发票（铁路电子客票）"
  }
}
```

**未授权的企业版票种不出现** —— 解析规则只在被授权时才注册（`sync_parsers`），
所以这个列表直接反映"这台服务真的能解析什么"，不会泄漏未授权的能力。

## 报关单字段字典

端点：`GET /formats/customs`

```bash
curl -H "X-API-Key: $KEY" http://localhost:8091/formats/customs
```

```json
{
  "fields": [
    {"name": "customs_no", "type": "string", "description": "海关编号"},
    {"name": "items", "type": "CustomsItem[]", "description": "商品明细"}
  ]
}
```

字段名与中文标签的完整对照，见
[`/customs/batch` 文档](api-customs-batch.md#明细字段与票面列的对应关系)。

> 这份 schema 是**两版共有的响应契约** —— 开源版也能取到（字段名、类型、说明），
> 只是没有报关单解析器，实际调用会返回 403。

## 电子承兑汇票字段字典

端点：`GET /formats/acceptance`

```bash
curl -H "X-API-Key: $KEY" http://localhost:8091/formats/acceptance
```

```json
{
  "fields": [
    {"name": "bill_no", "type": "string", "description": "票据号码（票面整串）"},
    {"name": "total_amount", "type": "string", "description": "票据金额 (元, 2 位小数)"},
    {"name": "endorsements", "type": "AcceptanceEndorsement[]", "description": "转让背书记录"}
  ]
}
```

完整字段表（25 个）见
[`/acceptance/batch` 文档](api-acceptance-batch.md#响应字段与票面的对应关系)。

> 同样是**两版共有的响应契约**。

## 为什么要单独给字段字典

客户端不用把字段名写死在代码里 —— 启动时拉一次 `/formats`，按返回的
`name` / `type` / `description` 渲染界面和建表。票种或字段有变化时，
客户端跟着变，不用跟着发版。

## 相关

- [接口一览](api-overview.md) —— 端点总表
- [输出字段](output-fields.md)
