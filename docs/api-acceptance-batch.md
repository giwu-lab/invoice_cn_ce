# `POST /acceptance/batch` —— 电子银行承兑汇票批量提取

一次传多份**电子银行承兑汇票**（电子商业汇票），返回数组，顺序与上传顺序一致。

> ⚠️ **企业版能力**。开源版里这个路径存在但返回 403 `feature_not_available`
> （feature=`acceptance`）。详见 [发行版与许可证](editions.md)。

## 请求

入参与 [`/invoice/batch`](api-invoice-batch.md) 完全对齐：

```bash
curl -H "X-API-Key: $KEY" \
     -F "files=@承兑汇票A.pdf" \
     -F "files=@承兑汇票B.pdf" \
     http://localhost:8091/acceptance/batch
```

## 只有批量端点

> **单文件端点不存在**：本功能**只有** `POST /acceptance/batch` —— 两版都
> 没有 `POST /acceptance` 这个路径（请求得到 404，不是 403）。要解析单张
> 票据时，用批量端点提交一份即可：`-F "files=@承兑汇票A.pdf"`。响应是**数组**，
> 顺序与输入顺序一致。

## 响应

数组，每项一张汇票：

```json
[
  {
    "file": "承兑汇票A.pdf",
    "bill_type": "电子银行承兑汇票",
    "bill_no": "510000000000000000000000000000000000000000-000000000000",
    "bill_status": "已收票-可流通",
    "issue_date": "2026-10-27",
    "due_date": "2027-04-27",
    "acceptance_date": "2026-10-27",
    "amount": "94000.00",
    "amount_upper": "玖万肆仟元整",
    "currency": "人民币",
    "drawer_name": "示例出票人股份有限公司",
    "drawer_account": "6220000000000000",
    "drawer_bank": "示例银行股份有限公司示例支行",
    "payee_name": "示例收款人有限公司",
    "payee_account": "6220000000000001",
    "payee_bank": "示例工商银行股份有限公司示例支行",
    "acceptor_name": "示例银行股份有限公司示例支行",
    "acceptor_account": "0",
    "acceptor_bank_name": "示例银行股份有限公司示例支行",
    "acceptor_bank_no": "100000000001",
    "contract_no": "",
    "transferable": "可再转让-可分包",
    "display_date": "2026-10-29 08:26",
    "endorsements": [
      {"endorser": "...", "endorsee": "...", "endorsement_date": "...", "no_transfer": "..."}
    ],
    "message": "success"
  }
]
```

## 响应字段与票面的对应关系

| 字段 | 票面标签 |
| --- | --- |
| `bill_type` | 电子银行承兑汇票（固定值） |
| `bill_no` | 票据号码（**票面整串**，跨行拼接） |
| `bill_status` | 票据状态（如 已收票-可流通） |
| `issue_date` / `due_date` / `acceptance_date` | 出票日期 / 汇票到期日 / 承兑日期 |
| `amount` / `amount_upper` / `currency` | 票据金额（元）/ 金额大写 / 币种 |
| `drawer_name` / `drawer_account` / `drawer_bank` | 出票人 全称 / 账号 / 开户银行 |
| `payee_name` / `payee_account` / `payee_bank` | 收款人 全称 / 账号 / 开户银行 |
| `acceptor_name` / `acceptor_account` | 承兑人 全称 / 账号 |
| `acceptor_bank_name` / `acceptor_bank_no` | 承兑人 开户行名称 / 开户行行号 |
| `transferable` | 能否转让 |
| `contract_no` | 交易合同号 |
| `display_date` | 显示日期（含导出时间） |
| `endorsements[]` | 转让背书记录（`endorser` / `endorsee` / `endorsement_date` / `no_transfer`） |

## 为什么这么解析

票面是**两栏格子表单**，标签多为竖排单字（「出」「票」「日」「期」），票据号码
跨两行，金额数字位上方还压着一行「十 亿 千 百 … 元 角 分」位表 —— 解析走**词
坐标锚定**（竖直重叠聚行 + 标签字符序列 + x 窗口 + 分栏），不是「标签: 值」
的同行正则。已在 4 家银行（中国 / 宁波 / 兴业 / 平安）的样本上逐字段验证。

## 误投会报错，不会静默丢字段

把承兑汇票发到 `/invoice` 或 `/invoice/batch` → 返回 **422**，`message` 里指明
「请走 `/acceptance/batch`」。

## 相关

- [批量端点入参](batch-input.md)
- [`GET /formats/acceptance`](api-formats.md#电子承兑汇票字段字典) —— 字段字典
- [发行版与许可证](editions.md)
