# 解析器与票种

每个票种由哪个模块解析、特殊版式怎么处理的。

| 模块 | 匹配类型 |
| --- | --- |
| `parsers/invoice.py` | 新电子发票（标准双栏、京东、京东大药房、水费、通行费变体） |
| `parsers/platform_invoice.py` | 平台下载版电子发票（票面标签块在上、值块在下） |
| `parsers/old_invoice.py` | 旧版电子发票（含密码区、校验码） |
| `parsers/merged_code.py` | 合并代码 / 成品油（坐标解析人名） |
| `parsers/airline_ticket.py` | 航空运输电子客票行程单 |
| `parsers/train_ticket.py` | 铁路电子客票 |
| `parsers/non_tax_receipt.py` | 中央非税收入统一票据（专利年费等） |
| `parsers/xml_invoice.py` | XML 全电发票（`EInvoice` schema） |
| `parsers/ofd_invoice.py` | OFD 全电票 (GB/T 33190，结构化 `CustomTag.xml` + 布局兜底) |

## 票种路由

`parsers/dispatch.py` 负责按票面特征选择解析器。调用方不需要写 `if-else`
判断票种 —— 传什么票它就用什么解析器。

票种对外可见的标识见 [`GET /formats`](api-formats.md)。

## 平台下载版电子发票

部分发票平台（下载页导出的 PDF）把票面拆成两段写进 PDF 内容流：第一段是
**标签块**（`发票号码：` / `开票日期：` / `名称：` / 统一社会信用代码…），第二段
才是**值块**（号码 / 日期 / 名称 / 税号 / 明细 / 合计 / 大写金额）。两段在票面
上其实**同行相邻**，但 PDF 文本层的顺序就是内容流顺序，于是 `发票号码：` 后面
是空的，号码却排在文本末尾 —— 依赖「标签: 值」同行的标准解析器会把号码、
日期、金额全部丢掉。

`parsers/platform_invoice.py` 按**词坐标**重建阅读顺序：把词按 `(top, x0)`
排序、按行距聚成行，逐行拼回文本，再交给 `parsers/invoice.py` 里已验证的取值
函数；同时剔除「购买方信息 / 销售方信息」的竖排表头字（它们与买方 / 卖方名称
同行，混进文本会把卖方名称截成「售」）。

版式识别用**结构特征**而不是关键字：`发票号码 / 发票代码 / 开票日期 / 开票人`
里至少有两个以「标签 + 冒号」独占一行（冒号后面没有值）。普通票面这些标签
都带值同行，因此不会误判。若重建结果反而比原始文本少命中字段，会自动退回
原始文本 —— 永远不会比原来更差。

> PDF 发票的 `items[]` 仍为空数组（与其它 PDF 票种一致）；明细只在 XML 全电
> 发票里填充，见 [输出字段](output-fields.md#items-商品明细)。

> ⚠️ **H43：XML schema 同步责任**：`parsers/xml_invoice.py` 通过 `defusedxml.ElementTree`
> 解析 XML 文档，字段名（如 `SellerInformation/SellerName`、
> `BasicInformation/TotalTax-includedAmount`）与发票平台当前的 `EInvoice` schema
> **硬编码对应**。若国家税务总局 / 发票平台升级 schema（命名空间 URI 变化、字段重命名等）
> 需要手动同步本文件（同时影响 `parsers/ofd_invoice.py`，因为 OFD 内部嵌入的
> `<EInvoice>` 复用同一 schema）。建议在升级前先跑一次 XML/OFD 样本回归。

> 📦 **报关单解析器不在本表里**：`parsers/customs_declaration.py` 已下沉到企业版发行包
> `invoice_cn_ee`（私有仓库），开源版不含其任何实现 —— 见 [发行版与许可证](editions.md)。

## 固有的解析边界

- **不做 OCR** —— 扫描件（图片型 PDF）没有文字层，解析会失败并说明原因。本项目处理的是电子发票，不是拍照件。
- **PDF 票面没有明细行时，`items[]` 返回空数组** —— 商品明细只有 XML / OFD 全电票才有。这是票面本身就没有，不是解析失败。
- **解析失败不会静默返回空字段** —— `message` 字段给出原因。

## 相关

- [输出字段](output-fields.md)
- [票种列表](api-formats.md)
- [测试](testing.md)
