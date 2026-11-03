# 部署与开发

两种部署形态：

- **Docker（生产推荐）**：`docker compose up -d`，自带开机自启、崩溃重启、健康检查。
- **dev（本地开发 / CI）**：venv + `pip install -e .` + 控制台脚本或裸 uvicorn。

镜像特性：多阶段 `python:3.12-slim`、非 root、HEALTHCHECK 内置、`/app/logs` volume 挂载、时区 `Asia/Shanghai`、镜像 < 250 MB。Dockerfile 默认走国内 APT 镜像（`APT_MIRROR=mirrors.aliyun.com`），需要切回官方源：

```bash
docker build --build-arg APT_MIRROR= -t invoice_cn_ce:1.0.0-ce .
```

## 生产

```bash
docker compose up -d
curl -F file=@samples/新电子发票-标准/购_材料_01.pdf http://localhost:8091/invoice
```

**容器里不放任何 key** —— key 通过 `IC_API_KEYS_FILE` 指向的挂载文件注入：

```yaml
# docker-compose.yml
volumes:
  - /etc/invoice_cn_ce/keys.json:/app/keys.json:ro
environment:
  IC_API_KEYS_FILE: /app/keys.json
```

> ⚠️ 关于 `keys.json` / `.env`：两者均已 `.gitignore` 排除，不会进入 git 历史。但仓库根目录下的
> `keys.json` 是开发测试副本——若与生产工作目录共用，可能误传到运维环境。**生产部署请用
> secret manager / K8s Secret / Vault 注入**，不要把 `keys.json` 复制进镜像。

## 构建方案

依赖有两条来路，产出同样的镜像：

| | `wheels/` 里有 `.whl` | `wheels/` 为空（全新克隆 / CI） |
| --- | --- | --- |
| 构建期 pip | `--no-index --find-links=/wheels`（**全程不联网**） | 从镜像源在线下载 |
| 前置步骤 | 先跑 `scripts/prepare_wheels.sh` | 无 |

Dockerfile 会自动判断走哪条，**两条路都不需要改 Dockerfile**：

```bash
# 路线 1（离线，推荐给受限网络）：一次性准备 wheels
bash scripts/prepare_wheels.sh           # 等价于 pip wheel --wheel-dir=wheels <deps>
# 或指定 PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ bash scripts/prepare_wheels.sh

docker build -t invoice_cn_ce:1.0.0-ce .
```

> wheels/ 不用每次都重生成；只有锁定依赖版本时才需要重跑。脚本会自动用 `.venv/bin/python3`（如有）或系统 `python3`。
> `wheels/` 里的 wheel 本体不入库（`.gitignore`），只保留 `wheels/.gitkeep` 占位，保证全新克隆里 `COPY wheels /wheels` 依然成立。

**受限网络（buildx sandbox）** —— BuildKit 默认把 RUN 步骤网络隔离，受限环境里 DNS 仍 `Temporary failure in name resolution`（即便镜像源配对了也不行）。此时用离线路线（路线 1）即可彻底绕开；也可以共享主机网络栈：

```bash
docker buildx create --use --driver docker-container --network host   # 一次性建 host 网络 builder
docker buildx build -t invoice_cn_ce:1.0.0-ce .                              # 或老 builder：DOCKER_BUILDKIT=0 docker build --network=host .
```

**方案 C：完全离线**（路线 1 失败 + 上面共享网络也没法用时）—— 在主机上准备好 wheels **和** 基础 deb 包（apt-offline 工具链），用本地 deb 仓库喂给镜像。绝大多数情况下路线 1 + 共享网络已够用，此处不展开。

## 本地开发

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
pip install pytest ruff mypy     # 可选：测试 / lint

# 启动（任选一种）
invoice_cn_ce-server --port 8091              # 前台控制台脚本（日志到 stderr；不走 PID 管理）
python -m uvicorn invoice_cn_ce.server:app --host 0.0.0.0 --port 8091 --reload  # 裸前台 + reload
invoice_cn_ce start                           # 后台 + PID 文件（日志 logs/server.log）
invoice_cn_ce dev                             # 后台 + PID 文件 + --reload（日志 logs/server-dev.log）

# 测试 / lint
invoice_cn_ce test                            # 等价 python -m pytest tests/ -v
ruff check src tests
mypy src/invoice_cn_ce

# 看日志
tail -f logs/server.log                    # invoice_cn_ce start 模式
tail -f logs/server-dev.log                # invoice_cn_ce dev 模式
```

dev 模式默认需要 API Key，参见 [鉴权与审计](auth.md)开头。

### Windows

CI 只在 ubuntu 上跑，`invoice_cn_ce` CLI 的生命周期子命令在 Windows 上有两个已知问题，因此单独提供了 `scripts/start-win.ps1`：

1. `cli.py::_alive()` 用 `os.kill(pid, 0)` 探活，Windows 没有信号 0，该调用抛 `OSError: [Errno 22]`，于是 `_alive()` 恒为 `False`——`invoice_cn_ce status` 会把运行中的服务报成「stale pid file」，`invoice_cn_ce stop` 则只删 PID 文件、返回 0，**却不杀进程**。
2. venv 的 `Scripts\python.exe` 会再 fork 出真正持有 socket 的子进程，直接拿 `Start-Process -PassThru` 的 PID 写 PID 文件会导致 stop 打错进程。

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-win.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\start-win.ps1 -Status
powershell -ExecutionPolicy Bypass -File .\scripts\start-win.ps1 -Stop

# 解释器不在仓库 .venv 里时，显式指定
powershell -ExecutionPolicy Bypass -File .\scripts\start-win.ps1 `
  -Python D:\path\to\.venv\Scripts\python.exe
```

脚本会等 `/health` 真正返回 200 才算启动成功，从 TCP 监听表反查**真实**监听 PID 写入 `logs/invoice_cn_ce.pid`，并在端口被非本项目进程占用时拒绝启动 / 拒绝终止。

### `logs/` 目录约定

`logs/` 下只会出现以下 5 类文件，**除此以外**的 `server-*.log` 都是历史临时副产物，可以删除：

| 文件 | 来源 |
| --- | --- |
| `logs/server.log` | `invoice_cn_ce start` 写的 uvicorn 日志（结构化 `deploy/log_config.yaml`） |
| `logs/server-dev.log` | `invoice_cn_ce dev` 写的 uvicorn 日志（带 `--reload`） |
| `logs/audit.log` | 受保护请求审计日志（10 MiB × 5 自动轮转） |
| `logs/invoice_cn_ce.pid` | `start` / `dev` 写的进程 PID；`stop` / `restart` / `status` 读它 |
| `logs/invoice_cn_ce.endpoint` | `start` / `dev` 写的实际绑定端点 `host:port`；`stop` / `restart` 据此等待端口释放 |

> `start --port 9000` 之后，`IC_PORT` / `settings.port` 里的默认值并不是真正占用的端口。端点文件就是为了让 `stop` / `restart` 等到**真正被占用**的那个 socket 被释放。命令行 `--host` / `--port` 优先级高于该文件。

`invoice_cn_ce-server`（前台 console_script）和裸 `python -m uvicorn ...`（裸前台）都不重定向 stdout，**不会写日志文件**——它们的输出直接到调用方 shell 的 stderr。

## Python 包直接调用

```python
from invoice_cn_ce import parse_pdf
resp = parse_pdf(open("samples/新电子发票-标准/购_材料_01.pdf", "rb").read(), filename="购_材料_01.pdf")
print(resp.seller_name, resp.total_amount, resp.message)
```

进程内调用不经过 HTTP，**数据完全不出本进程** —— 不落盘、不进日志、不出网。

## 相关

- [配置项](config.md)
- [鉴权与审计](auth.md)
- [发行版与许可证](editions.md)
- [测试](testing.md)
