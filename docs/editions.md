# 发行版与许可证

本项目分两个**互相独立的发行包**：

| 发行包 | 内容 | 能力 |
| --- | --- | --- |
| `invoice_cn_ce` | 开源版（CE） | 发票 / 客票 / 费用分类 / 查验代理 |
| `invoice_cn_ee` | 企业版（EE），依赖 `invoice-cn-ce==<同版本>` | **报关单解析**（`/customs/batch`）、**批量提取**（`/invoice/batch`）、**电子承兑汇票解析**（`/acceptance/batch`） |

**商业边界落在发行包上，不是运行时的 if。** CE 的 wheel 里没有报关单解析器，
CE 的镜像里连 `invoice_cn_ee` 的字节码都不存在（构建时按 `ARG EDITION` 把
企业版 wheel 从依赖目录剔除），所以"改一行代码就能解锁"这条路是堵死的。

## 三个正交的维度

| 维度 | 回答什么 | 载体 |
| --- | --- | --- |
| `edition` | 装的是什么发行包 | 发行包构成 + 许可证 |
| `feature` | 这个版本能做哪些事 | 许可证授权的子集 |
| `scope` | 哪个 API key 能用 | `keys.json` 里的 scopes |

有效权限 = `edition ∩ license ∩ key scope`。**scope 不能当商业边界** ——
key 是使用者自己配的；`edition` / `license` 才是墙。

## 没有 `IC_EDITION` 这类开关

版本只由两件事决定：**装了哪个发行包** + **许可证是否有效**。刻意不提供
`IC_EDITION` 环境变量 —— 有了它，开源版用户改一个环境变量就解锁了，
整套体系作废。

## 许可证

企业版包装了还不够，运行时还要用 `IC_LICENSE_FILE` 指一份 Ed25519 签名的
JSON 许可证：

```bash
docker run ... \
  -e IC_LICENSE_FILE=/app/license.json \
  -v /path/to/license.json:/app/license.json:ro \
  invoice_cn_ce:1.0.0-ee
```

- 许可证有效 → 开放被授权的能力；
- 缺失 / 过期 / 签名不合法 → **自动降级成 CE 行为**（企业版端点返回
  `403 feature_not_available`，其余功能照常，**不拒绝启动**）；
- `SIGHUP` 可热重载许可证 —— 续期 / 换证不用重启容器。

公钥编译在 `invoice_cn_ee` 包里（私钥只在签发方手里），签发工具与私钥都放在
**仓库外**的签发目录里，轮换签发密钥 = 换公钥 + 重签。

## 未授权时的响应

两个版本**路由表一致**（不会因为版本差异拿到 404），未授权时返回结构化 403：

```json
{
  "detail": {
    "error": "feature_not_available",
    "feature": "customs",
    "required_edition": "ee",
    "current_edition": "ce",
    "reason": "ee_package_absent",
    "upgrade": "https://github.com/giwu-lab/invoice_cn_ce/blob/main/docs/editions.md"
  }
}
```

鉴权优先于版本判定：没有 key 的请求先得到 **401**，不会先撞到 403
（否则等于向未鉴权方泄漏"这是企业版功能"）。

## 前端怎么用

`GET /capabilities`（公开）返回当前能力：

```json
{
  "edition": "ce",
  "features": {
    "extract": true,
    "batch": false,
    "customs": false,
    "acceptance": false,
    "verify": true
  },
  "limits": {"max_file_mb": 10, "max_batch_files": 50, "max_batch_total_mb": 500},
  "license": {"status": "absent", "license_id": "", "customer": "", "expires_at": ""}
}
```

前端据此显示/隐藏「批量上传」「报关单解析」「电子承兑」入口 —— 用户看得见能力边界，
也知道该买什么。

> `acceptance` 是**独立**的能力位：授权了 `batch` 不等于授权电子承兑汇票解析。

## 构建两个版本

企业版源码在**私有仓库** `invoice_cn_ee`（本仓库不含其任何实现），两个仓库
各自独立构建：

```bash
# ① 开源版：直接在本仓库构建
docker build -t invoice_cn_ce:1.0.0-ce .

# ② 企业版：在企业版仓库（与本仓库同级检出）里把 wheel 产出到本仓库的 wheels/
python ../invoice_cn_ee/scripts/build_ee_wheel.py \
    --ce-root . --wheels-dir ./wheels
docker build --build-arg EDITION=ee -t invoice_cn_ce:1.0.0-ee .
```

`build_ee_wheel.py` 不进 wheel（只进 sdist），签发工具与厂商密钥始终留在
私有仓库这一侧。

## 扩展点

CE ↔ EE 的接缝在 `invoice_cn_ce.plugins.InvoiceCnPlugin`：企业版实现
`entitlements()` / `register_customs_route()` / `register_batch_route()` /
`register_acceptance_route()` / `sync_parsers()` 五个方法即可。**本仓库是公开的，
企业版实现在私有仓库 `invoice_cn_ee` 里**，两边靠这个契约对接，契约不用改。

> 完整的签发、部署、续期与排障手册见**企业版私有仓库**里的
> `AUTHORIZATION.md`（随企业版源码一起分发）。

## 相关

- [能力查询](api-capabilities.md)
- [接口一览](api-overview.md)
- [部署与开发](deployment.md)
