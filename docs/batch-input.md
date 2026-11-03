# 批量端点入参

`/invoice/batch`、`/customs/batch`、`/acceptance/batch` 三个批量端点，以及单文件
端点 `/invoice`、`/raw` —— **入参规则是同一套**，这里一次说清。

## 每个文件的四种来源

| 来源 | JSON | multipart |
| --- | --- | --- |
| 上传的二进制 | — | `-F "files=@a.pdf"`（可重复） |
| 远端 URL | `{"files": [{"filename": "...", "url": "https://..."}]}` | `-F "urls=https://..."`（可重复）/ `-F "url=https://..."` |
| 服务端路径 | `{"files": [{"filename": "...", "file_path": "/data/a.pdf"}]}` | `-F "file_paths=/data/a.pdf"`（可重复） |
| base64 | `{"files": [{"filename": "...", "base64": "..."}]}` | — |

单文件端点的 JSON 顶层快捷写法（等价于一份文件）：

```json
{"url": "https://..."}
{"file_path": "/data/a.pdf"}
{"file_base64": "..."}
```

键名与 `/invoice` 完全一致。

## 例子

```bash
# 远端 URL：JSON
curl -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"files": [{"filename": "a.pdf", "url": "https://example.com/a.pdf"}]}' \
  http://localhost:8091/invoice/batch

# 远端 URL：multipart（也可以直接写进 files 字段）
curl -H "X-API-Key: $KEY" \
  -F "urls=https://example.com/a.pdf" \
  -F "urls=https://example.com/b.pdf" \
  http://localhost:8091/invoice/batch

# 混着传也行，顺序按输入顺序返回
curl -H "X-API-Key: $KEY" \
  -F "files=@本地发票.pdf" \
  -F "urls=https://example.com/远程发票.pdf" \
  http://localhost:8091/invoice/batch
```

## 几条约定

- **顶层与 `files` 数组不能同时给** —— 同时给返回 400，不会有哪一份被悄悄忽略。
- **URL 抓取走的是和 `/invoice` 同一套防护**：云元数据地址（`169.254.169.254` 等）
  一律拒绝、响应体按 `IC_MAX_FILE_MB` 截断、请求 30 秒超时、只允许 http/https。
- **`file_path` 受 `IC_ALLOWED_FILE_PATHS` 白名单约束**，白名单为空时该来源整体关闭。
- **文件名**：JSON 里给了 `filename` 就用它；没给则从 URL 路径（或路径）推导。
- **失败是整批 400**：某个 URL 抓不到、base64 解不开、文件超限，都会让整批请求
  返回 400 并说明是哪一项。

## 400 与 422 的区别

| 情况 | HTTP | 含义 |
| --- | --- | --- |
| 取不到文件（URL 挂了 / base64 坏了 / 超限） | **400** | **整批**失败 |
| 文件拿到了但解析不出来 | **422 / 200** | 落到**该项**的 `message` 上，整批照常返回 |

这个区分是刻意的：**取文件**是请求本身有问题，所以整批拒；**解析**是内容问题，
所以逐项报 —— 一张坏票不该让同批的其它票一起丢掉。
