# 输出字段

`/invoice`（及 `/invoice/batch` 的每一项）响应体里每个字段的含义。

```json
{
  "file": "购_材料_01.pdf",
  "page_count": 1,
  "invoice_type": "电子发票（增值税专用发票）",
  "invoice_number": "25502000000000000001",
  "issue_date": "2025-11-27",
  "buyer_name": "...",
  "buyer_tax_id": "...",
  "seller_name": "...",
  "seller_tax_id": "...",
  "amount_without_tax": "124018.66",
  "tax_amount": "16122.43",
  "total_amount": "140141.09",
  "total_amount_upper": "壹拾肆万零壹佰肆拾壹圆零玖分",
  "payee": "", "reviewer": "", "drawer": "张某某",
  "items": [],
  "expense_category": "transportation",
  "expense_category_label": "交通",
  "expense_category_source": "seller",
  "message": "success"
}
```

**字段值保持中文原样**（票面就是这样印的），**字段名是统一的 snake_case**，跨票种一致。

## 金额一律是字符串

所有金额字段保持**字符串原值**，不做 float 转换：红字行带负号，且税率写法在不同票种间
不统一。直接映射到数据库的 `DECIMAL` / `NUMERIC` 列即可。

## `items[]` 商品明细

`/invoice` 的响应里带一个 `items` 数组。**目前仅 XML 全电发票填充；PDF 与 OFD 恒为 `[]`**
（OFD 的明细可解析但暂未启用——其 `CustomTag.xml` 同一文件内混用「`GoodsInfos` 包装」
与「`root` 直挂」两套布局，漏掉后者会静默少数据）。

| 字段 | 来源元素 | 说明 |
| --- | --- | --- |
| `item_no` | 解析器生成 | 1..N 按出现顺序（XML 不带行号） |
| `name` | `ItemName` | 已剥离 `*类别*` 前缀 |
| `category` | 从 `ItemName` 拆分 | 如 `齿轮` |
| `spec` | `SpecMod` | 规格型号 |
| `unit` | `MeaUnits` | 计量单位 |
| `quantity` | `Quantity` | 可能是 `4333千克` 这类带单位的串 |
| `unit_price` | `UnPrice` | 单价 |
| `amount` | `Amount` | 不含税金额（红字行为负数） |
| `tax_rate` | `TaxRate` | 如 `0.13` |
| `tax_amount` | `ComTaxAm` | 税额 |
| `total_amount` | `TotaltaxIncludedAmount` | 价税合计 |
| `tax_classification_code` | `TaxClassificationCode` | 19 位税收分类编码，退税申报必填 |
| `is_reversal` | 解析器推导 | 红字冲销行标记，报税时要单独统计 |

⚠️ **红字冲销行**（`is_reversal: true`）只有金额三项和税收分类编码，
`spec` / `unit` / `quantity` / `unit_price` 会是空串——这是票面本身就没有，
不是解析失败。

服务端会对「明细金额和 / 税额和 / 价税合计和」与表头做**自洽校验**，不一致时写
warning 日志。这是发现「明细被静默截断」的唯一手段：少掉的行不会报错，
每一行返回出来都看起来完全正常。

## `message` 字段语义

`message` 统一表示成功 / 软警告 / 硬错误：

| 值 | HTTP | 含义 |
| --- | --- | --- |
| `"success"` | 200 | 成功 |
| `"not_text"` | 200 | 空 PDF / 图片型 PDF 无文本层（软警告） |
| `"error: empty_file"` | 422 | 上传为空 |
| `"error: file_too_large: X > Y bytes"` | 422 | 超过大小限制 |
| `"error: parse_failed: <exc>"` | 422 | pdfplumber 解析异常 |
| `"error: xml_parse_failed: ..."` | 422 | XML 畸形 |
| `"error: ofd_parse_failed: ..."` | 422 | OFD 容器/ZIP/XML 异常或非数电发票 |
| `"error: internal_error: <exc>"` | 500 | 服务器内部异常 |

HTTP 422 响应体就是 `ExtractResponse` / `PdfRaw`，错误字符串完整保留在 `message` 字段。400 / 500 / 502-503 仍走 FastAPI 的 `{"detail": ...}` 信封。

## `expense_category` 消费类别

`/invoice` 响应里带 `expense_category` / `expense_category_label` / `expense_category_source` 三字段，对单张发票做企业报销常用的归类（适合按类目做预算统计、凭证归档、报销审批路由）。

| `expense_category` | `expense_category_label` | 含义 | 命中来源示例 |
| --- | --- | --- | --- |
| `transportation` | 交通 | 航空 / 铁路 / 网约车 / 出租车 | 票种 `airline`/`train`；卖方「滴滴/携华/出行/12306」；明细「交通运输服务/客运服」 |
| `lodging` | 住宿 | 酒店 / 民宿 / 公寓 | 卖方「如家/汉庭/锦江/民宿」；明细「住宿服务/房费」 |
| `dining` | 餐饮 | 餐厅 / 团餐 / 外卖 | 卖方「海底捞/美团/餐饮」；明细「餐饮服务/餐费」 |
| `courier` | 快递 | 顺丰 / 中通 / 京东物流 等 | 卖方「顺丰/京东物流/中通/圆通/申通/韵达/邮政」；明细「快递/收派服务费」 |
| `telecom` | 通信 | 三大运营商 / 广电 | 卖方「中国电信/中国移动/中国联通」；明细「电信服务/通信服务费」 |
| `water` | 水费 | 自来水 / 供水 | 卖方「自来水/供水/水资源」 |
| `electricity` | 电费 | 供电 / 电网 | 卖方「供电/电力/国网」 |
| `gas` | 燃气 | 燃气公司 / 天然气 | 卖方「燃气/港华燃气/华润燃气」；明细「燃气费」 |
| `fuel` | 成品油 | 加油站 / 中石化 / 中石油 | 票种 `merged_code`；卖方「中石化/中石油/加油站」；明细「成品油/汽油/柴油」 |
| `other` | 其他 | 票种级命中（行政事业性收费） | 票种 `non_tax_receipt` |
| `unclassified` | 未归类 | **兜底**：L1–L4 全未命中。**与 `other` 独立**——`other` 表示"识别为其他类目"，`unclassified` 表示"我们没规则命中它"。调用方按 `category == "unclassified"` 判断未识别票，按 `category == "other"` 判断显式归类的杂项。 | 所有规则未命中（`source=""`） |

`expense_category_source` 标识命中层级：

| 值 | 含义 |
| --- | --- |
| `"ticket"` | L1 票种命中（`parsers.dispatch` 直接路由） |
| `"seller"` | L2 卖方名称关键词命中 |
| `"item"` | L3 商品明细（XML 全电发票的 `items[]`）关键词命中 |
| `"code"` | L4 19 位 税分类编码前缀命中 |
| `""` | 兜底 `unclassified`（`category` 不为空字符串）；或报关单显式跳过 / `IC_EXPENSE_CATEGORY_ENABLED=false` 关闭（这两种 `category` 也是空字符串，调用方按上下文区分） |

**优先级**：`ticket` > `seller` > `item` > `code` > 兜底归 `unclassified`。同层冲突按规则 `priority` 数字从大到小取第一。完整规则表见 `src/invoice_cn_ce/expense_category.py`。

> **`other` vs `unclassified` 区分**：
> - `other` = "中央非税" 票种被显式归类（`source="ticket"`）—— 已知是行政事业性收费
> - `unclassified` = "没规则命中"（`source=""`）—— 卖方 / 明细 / 编码都不认识，待人工或后续 PR 补规则
>
> 报关单（`/customs/batch`）不属于企业报销场景，分类逻辑显式跳过该票种——即使卖方碰巧含「运输」「餐饮」等关键词，分类三字段也保持空字符串（与 `unclassified` 不同）。

> PDF 票面的 `items[]` 恒为空，所以 PDF 走 `seller` 路径（依赖卖方关键词）；XML 全电发票因有明细，`item` / `code` 也参与判定，**同一份内容（PDF 转 XML）可能归到不同细分类**——例如「购_零售_01」XML 因明细含「*餐饮服务*」被归到 `dining`，PDF 因无明细落到兜底空。
>
> OFD 全电票与 PDF 一样走 `seller` 路径（OFD 暂不解析明细），三条路径（PDF / XML / OFD）都会产出类目，不会出现「某个格式恒为空」的情况。

## 其它端点的响应结构

| 端点 | 响应 |
| --- | --- |
| `/invoice` | `ExtractResponse`（本文档） |
| `/invoice/batch` | `ExtractResponse[]`，按输入顺序 |
| `/customs/batch` | `CustomsDeclarationHeader[]`，字段见 [报关单批量提取](api-customs-batch.md) |
| `/acceptance/batch` | `AcceptanceBill[]`，字段见 [电子承兑批量提取](api-acceptance-batch.md) |
| `/raw` | `{text, lines[], page_count}` |
| `/formats` | 票种列表，见 [票种列表](api-formats.md) |
| `/capabilities` | 能力位与限额，见 [能力查询](api-capabilities.md) |

## 相关

- [接口一览与通用约定](api-overview.md)
- [单文件提取](api-invoice.md)
- [发行版与许可证](editions.md)
