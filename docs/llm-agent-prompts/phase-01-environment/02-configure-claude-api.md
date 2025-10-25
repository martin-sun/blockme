# 任务02：配置 Claude API 接入

## 任务目标

为整个 BlockMe 项目（现有 `mvp/` CLI、即将上线的 FastAPI 服务、以及 Svelte 前端调试接口）准备 Anthropic Claude API 的访问能力。目标是在本地/CI 环境中安全地管理 `ANTHROPIC_API_KEY`，并验证 Claude Haiku/Sonnet 可用于 Skill 路由、文档理解和后续多模态处理。

## 技术要求

- Anthropic 账户与有效的 API Key（https://console.anthropic.com）
- Python 3.11+，`uv` 或其他依赖管理工具
- 能访问 `https://api.anthropic.com` 的网络（如需可配置代理）
- `.env` 管理或密钥托管方案（direnv, Doppler, 1Password CLI 等均可）

**推荐模型：**
- `claude-haiku-4-5-20251001`：用于 Skill 路由（快速、便宜）
- `claude-3-5-sonnet-20241022`：用于需要更深推理的场景（后端/测试）

## 实现步骤

### 1. 获取 API Key

1. 登录 Anthropic Console：`https://console.anthropic.com/settings/keys`
2. 点击 **Create Key**，命名（如 `blockme-dev`）
3. 复制密钥（格式 `sk-ant-...`），安全保存；UI 只展示一次

### 2. 仓库级 `.env` 管理

在仓库根目录创建 `.env`：

```bash
cd /Users/woohelps/CascadeProjects/blockme
cp mvp/.env.example .env  # 如已存在可跳过

cat <<'EOF' > .env
ANTHROPIC_API_KEY=sk-ant-xxx
GLM_API_KEY=  # 任务03 中填充
EOF
```

- 将 `.env` 添加到 `.gitignore`（已配置）
- 运行任务前执行 `export $(grep -v '^#' .env | xargs)` 或使用 `direnv` 自动加载

### 3. 让 `mvp/` CLI 感知密钥

`mvp/main.py` 在启动时会从 `mvp/.env` 加载配置：

```bash
cp .env mvp/.env  # 或者在 shell 中 export
cd mvp
uv venv && source .venv/bin/activate
uv sync
python skill_router.py  # 第一次调用 Claude Haiku
```

（`load_env()` 会自动解析 `mvp/.env`，无需额外代码修改。）

### 4. 为 FastAPI/服务端预留配置

当创建 `backend/.env` 时沿用同一变量名：

```bash
mkdir -p backend
cat <<'EOF' > backend/.env
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
GLM_API_KEY=${GLM_API_KEY}
EOF
```

在 FastAPI 启动脚本中加载：

```python
from dotenv import load_dotenv
load_dotenv()  # 允许 uvicorn 在本地读取 backend/.env
```

CI/CD 中可以通过密钥管理服务（GitHub Actions secrets、1Password Connect 等）注入同名环境变量，保证多环境一致。

### 5. API 可用性自检

使用以下脚本验证连接：

```bash
python - <<'PY'
from anthropic import Anthropic
import os

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
resp = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=256,
    messages=[{"role": "user", "content": "测试一下 BlockMe 开发环境"}]
)
print(resp.content[0].text)
PY
```

若打印出 Claude 的回复，即表示配置成功。若失败请检查：
- 变量是否已导出
- 网络/代理是否允许访问 `api.anthropic.com`
- Key 是否过期或超额

## 关键代码提示

### `.env` 模板

```bash
# 仓库根目录 .env / backend/.env
ANTHROPIC_API_KEY=sk-ant-xxx
GLM_API_KEY=sk-glm-xxx
HTTP_PROXY=
HTTPS_PROXY=
```

### Skill Router 读取方式

`mvp/skill_router.py` 默认按如下逻辑读取：

```python
self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
if not self.api_key:
    raise ValueError("未找到 ANTHROPIC_API_KEY")
```

只需确保环境变量在进程启动时可见即可，无需修改代码。

### FastAPI 依赖（后续任务引用）

```python
from anthropic import Anthropic
claude = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

def route_skills(query: str):
    return claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": build_prompt(query)}]
    )
```

## 测试验证

1. **脚本连通性**：运行第 5 步脚本，确保能返回文本
2. **MVP 路由测试**：`python mvp/skill_router.py`，验证 Haiku 输出 JSON
3. **CLI 端到端**：`python mvp/main.py`，提问“萨省 PST 税率是多少？”，confirm 路由/回答
4. **（未来）FastAPI 健康检查**：在后端实现后，调用 `/health` 并触发一次 Claude 请求确认配置复用

## 注意事项

- **成本监控**：Haiku 费用低（~$0.004/次），Sonnet 较高；优先在路由/推理场景区分模型
- **速率限制**：若并发高，需实现指数退避重试；MVP 阶段建议串行
- **安全**：禁止将 API Key 写入仓库或日志；CI 中使用密钥服务注入
- **代理**：若需代理，设置 `HTTP_PROXY`/`HTTPS_PROXY` 环境变量，并告知 `requests`/`anthropic`
- **多环境策略**：可设置 `ANTHROPIC_API_KEY_DEV/PROD`，通过启动脚本决定加载哪个 key

## 依赖关系

**前置任务：**
- 任务01：搭建 Svelte 前端环境（可选同步执行；本任务只需准备密钥）

**后置任务：**
- 任务07：Claude Vision API 集成（依赖同一 Key）
- 任务13：意图识别/路由模块（直接使用 Haiku）
- 任务15：FastAPI 聊天接口（统一从环境读取配置）
