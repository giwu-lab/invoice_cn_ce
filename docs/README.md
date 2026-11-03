# 文档索引

`invoice_cn_ce` 的完整文档。README 只讲这个项目是什么、为什么值得用；具体怎么用，在这里。

## 先看这三篇

| 文档 | 讲什么 |
| --- | --- |
| [部署与开发](deployment.md) | 怎么在你自己的机器 / 服务器上把它跑起来 |
| [接口一览](api-overview.md) | 端点总表与通用约定（鉴权、限额、入参形状） |
| [输出字段](output-fields.md) | 返回的每个字段是什么意思、`message` 怎么读 |

## 接口文档

每个端点一份独立文档。

| 端点 | 文档 | 发行版 |
| --- | --- | --- |
| `POST /invoice` | [单文件提取](api-invoice.md) | CE |
| `POST /invoice/batch` | [批量提取](api-invoice-batch.md) | EE |
| `POST /raw` | [原始文本](api-raw.md) | CE |
| `POST /verify` | [国税查验代理](api-verify.md) | CE |
| `POST /extract-and-verify` | [提取 + 查验](api-extract-and-verify.md) | CE |
| `GET /formats` | [票种列表](api-formats.md) | CE |
| `GET /formats/customs` | [报关单字段字典](api-formats.md#报关单字段字典) | 两版共有契约 |
| `GET /formats/acceptance` | [承兑汇票字段字典](api-formats.md#电子承兑汇票字段字典) | 两版共有契约 |
| `GET /capabilities` | [能力查询](api-capabilities.md) | CE |
| `GET /health` / `GET /health/full` | [健康检查](api-capabilities.md#健康检查) | CE |
| `POST /customs/batch` | [报关单批量提取](api-customs-batch.md) | EE |
| `POST /acceptance/batch` | [电子承兑汇票批量提取](api-acceptance-batch.md) | EE |

## 通用

| 文档 | 讲什么 |
| --- | --- |
| [批量端点入参](batch-input.md) | 三种文件来源（URL / 服务端路径 / base64）与混传规则 |
| [鉴权与审计](auth.md) | API Key、scope、错误码、`audit.log` |
| [配置项](config.md) | 全部 `IC_*` 环境变量 |
| [输出字段](output-fields.md) | 字段含义、`items[]`、`message` 语义、消费类别 |
| [发行版与许可证](editions.md) | CE / EE 的边界、许可证机制、扩展点 |
| [解析器与票种](parsers.md) | 每个票种由哪个模块解析、特殊版式怎么处理的 |
| [测试](testing.md) | 怎么跑测试、样本从哪来 |
| [部署与开发](deployment.md) | Docker、源码运行、构建、Windows 注意事项 |

## 一句话索引

- **想把服务跑起来** → [部署与开发](deployment.md)
- **想调一个接口** → [接口一览](api-overview.md)
- **想知道字段准不准** → [输出字段](output-fields.md)
- **想看能不能商用** → [发行版与许可证](editions.md)
- **想改代码** → [解析器与票种](parsers.md) + [部署与开发](deployment.md)
