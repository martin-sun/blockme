# 任务03：配置 GLM API 接入

## 任务目标

为 BlockMe 的文档理解与回答模块准备智谱 GLM API，特别是 `glm-4-flash`（免费）与 `glm-4-vision-preview`（多模态）。本任务完成后：
- `mvp/chat_service.py` 可直接使用本地配置调用 GLM 生成回答
- 后续 FastAPI 服务能够共用同一密钥
- 多模态/Markdown 生成流水线具备中文文档处理能力

## 技术要求

- 注册并完成实名认证的智谱 AI 账户（https://open.bigmodel.cn/）
- 通过控制台创建 API Key，具备调用 GLM-4/GLM-4V 权限
- Python 3.11+、`uv`，以及 `zhipuai` SDK（已在 `mvp/pyproject.toml` 中列出）
- 网络可访问 `https://open.bigmodel.cn`

## 实现步骤

### 1. 获取 GLM API Key

1. 登录 https://open.bigmodel.cn/console/
2. 访问 **API Key 管理**，点击 **创建 API Key**
3. 记录密钥（格式 `glm-...` 或 `fU0l...`），后续写入 `.env`
4. 若计划调用付费模型（如 `glm-4-plus`），务必完成企业认证并充值

### 2. 将密钥写入 `.env`

沿用任务02中的 `.env` 文件：

```bash
cat <<'EOF' >> .env
GLM_API_KEY=your-glm-key
EOF

# 同步到 mvp/.env
cp .env mvp/.env
```

（若 `.env` 已存在 `GLM_API_KEY` 行，请直接编辑。）

### 3. 让 `mvp/` 组件读取密钥

- `mvp/chat_service.py` 会在初始化阶段读取 `os.getenv("GLM_API_KEY")`
- 确保运行 CLI 前已经 `source .venv/bin/activate && export $(grep -v '^#' ../.env | xargs)`
- 后续 FastAPI 服务也将复用同名变量，保持一致

### 4. 进行 SDK 连通性测试

```bash
python - <<'PY'
import os
from zhipuai import ZhipuAI

client = ZhipuAI(api_key=os.environ.get("GLM_API_KEY"))
resp = client.chat.completions.create(
    model="glm-4-flash",
    messages=[{"role": "user", "content": "测试 BlockMe 开发环境"}],
    temperature=0.2,
    max_tokens=512,
)
print(resp.choices[0].message.content)
PY
```

如返回文本表示配置成功；若失败请检查：
- 环境变量是否导出
- SDK 版本是否与 `pyproject.toml` 一致
- 控制台是否已为该 Key 分配调用权限

### 5. 预留多模态（Vision）配置

为文档处理/Markdown 流水线准备图像接口：

```python
vision_resp = client.response.create(
    model="glm-4-vision-preview",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "提取截图中的表格内容"},
                {"type": "image_url", "url": "https://example.com/page.png"}
            ]
        }
    ]
)
```

该片段可嵌入任务07/08的文档转换实现中，密钥沿用 `GLM_API_KEY`。

## 关键代码提示

### `.env`

```bash
ANTHROPIC_API_KEY=sk-ant-xxx
GLM_API_KEY=glm-xxx
```

### `chat_service.py`（节选）

```python
self.api_key = api_key or os.getenv("GLM_API_KEY")
self.client = ZhipuAI(api_key=self.api_key)
self.model = "glm-4-flash"  # 可根据成本切换
```

### FastAPI 统一配置（示例）

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str = ""
    glm_api_key: str = ""

settings = Settings()
chat_client = ZhipuAI(api_key=settings.glm_api_key)
```

## 测试验证

1. **命令行自检**：运行第 4 步脚本
2. **MVP 回答**：`python mvp/chat_service.py`，提问 “PST 税率是多少？”
3. **端到端**：`python mvp/main.py`，确保在加载 Skills 后 GLM 输出正常
4. **Vision 试跑**：在任务07/08完成后，用同一 Key 调用图像接口，确认权限一致

## 注意事项

- **速率与配额**：免费 Key 对 RPM 有限制；批量调用时请实现重试/排队
- **模型选择**：
  - `glm-4-flash`：默认、免费、延迟低
  - `glm-4-plus`：推理更强，适合复杂问题
  - `glm-4-vision-preview`：多模态提取
- **网络与代理**：如需代理，设置 `ZHIPUAI_API_BASE` 或通过系统代理变量
- **安全**：GLM Key 同样不要提交到 Git；CI 使用密钥管理服务
- **成本控制**：大批量处理前，可优先使用 Flash 模型验证，满足质量后再切换到付费模型

## 依赖关系

**前置任务：**
- 任务02：配置 Claude API（复用同一 `.env` 管理方式）

**后置任务：**
- 任务07/08：Vision 集成（读取同一 Key）
- 任务14：Skill 引擎（GLM 回答）
- 任务15：FastAPI 聊天接口（统一注入 GLM 客户端）
