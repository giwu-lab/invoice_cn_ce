# `POST /customs/batch` —— 报关单批量提取

一次传多份**海关出口货物报关单**（操作联 / 出口退税联），返回数组，顺序与上传
顺序一致。

> ⚠️ **企业版能力**。开源版里这个路径存在但返回 403 `feature_not_available`
> （feature=`customs`）。详见 [发行版与许可证](editions.md)。

## 请求

入参与 [`/invoice/batch`](api-invoice-batch.md) **完全对齐** —— multipart 里
**重复的 `files` 字段**，或 JSON 的 `{"files": [...]}`：

```bash
# multipart：同一个字段名重复多次
curl -H "X-API-Key: $KEY" \
     -F "files=@报关单A.pdf" \
     -F "files=@报关单B.pdf" \
     http://localhost:8091/customs/batch

# 远端报关单地址
curl -H "X-API-Key: $KEY" \
     -F "urls=https://example.com/报关单A.pdf" \
     http://localhost:8091/customs/batch
```

限额与 `/invoice/batch` 相同（最多 50 个、单文件 10 MB、总 500 MB），并发由
`IC_BATCH_WORKERS` 控制。

## 响应

数组，每项一份报关单：

```json
[
  {
    "customs_no": "223120260000000001",
    "items": [
      {
        "item_no": 1,
        "hs_code": "7318150090",
        "name_and_spec": "螺栓 M12×60",
        "declared_qty": "1000",
        "unit_price": "1.20",
        "total_price": "1200.00"
      }
    ]
  }
]
```

字段名与中文标签的完整对照，见下文。

## 明细字段与票面列的对应关系

`items[]` 每行：

| 字段 | 票面列 |
| --- | --- |
| `item_no` | 项号 / 商品序号 |
| `hs_code` | 商品编号（HS 编码，10 位） |
| `name_and_spec` | 商品名称及规格型号（`品名\|规格型号`，规格在票面**折行处直接接续**） |
| `legal_qty` | 法定数量 + 法定单位 |
| `second_qty` | 第二数量 + 第二单位 |
| `declared_qty` | 申报数量 + 申报单位（操作联上为成交数量） |
| `unit_price` / `total_price` | 单价 / 总价 |
| `currency_code` / `currency_name` | 币制代码（`USD`）/ 币制名（`美元`） |
| `origin_country_code` / `origin_country_name` | 原产国（地区）代码 / 名称 |
| `final_destination_code` / `final_destination_name` | 最终目的国（地区）代码 / 名称 |
| `source_region_code` / `source_region_name` | 境内货源地代码 / 名称 |
| `tax_status` | 征免（照章征税 / 全免 …） |

## 两种版式，列不一样

- **出口退税联**没有原产国 / 货源地 / 征免列 —— 对应字段为空；
- **操作联**没有法定数量与申报数量的分列标签，「数量及单位」一格里可能同时印着
  法定数量、第二数量与成交数量，解析时按「单价 × 数量 = 总价」认出成交数量。

## 误投会报错，不会静默丢字段

把报关单发到 `/invoice` 或 `/invoice/batch` → 返回 **422**，`message` 里指明
「请走 `/customs/batch`」。

> 报关单**只有批量端点** `POST /customs/batch`：多文件、返回数组，multipart 里重复的
> 字段名是 `files`（不是 `file`）。没有单文件路径（请求它得到 404）。

## 相关

- [批量端点入参](batch-input.md)
- [`GET /formats/customs`](api-formats.md#报关单字段字典) —— 字段字典
- [发行版与许可证](editions.md)
