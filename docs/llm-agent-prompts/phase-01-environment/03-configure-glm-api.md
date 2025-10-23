# 任务03：配置 GLM API 接入

## 任务目标

在 Open WebUI 中配置智谱 AI 的 GLM API，启用 GLM-4 系列模型（特别是 GLM-4V 视觉模型）用于中文文档处理。GLM-4V 在中文识别准确率达到 99.3%，且提供免费的 GLM-4V-Flash API，非常适合处理中文专业文档。

## 技术要求

**必需资源：**
- 智谱 AI API Key（从 https://open.bigmodel.cn 获取）
- Open WebUI 已部署并运行（任务01完成）
- 网络能访问 `open.bigmodel.cn`

**推荐模型：**
- `glm-4v-flash`：免费视觉模型，适合中文文档处理
- `glm-4v-plus`：高级视觉模型，准确率更高
- `glm-4-plus`：纯文本模型，中文对话优秀
- `glm-4-flash`：快速文本模型，成本低

## 实现步骤

### 1. 获取 API Key

注册智谱 AI 开放平台：
1. 访问 https://open.bigmodel.cn/usercenter/apikeys
2. 点击 "创建 API Key"
3. 命名密钥（如 "openwebui-prod"）
4. 复制并保存密钥（格式：`xxxx.xxxxxxxxxxxxxxxx`）

**福利提示：**
- 新用户赠送免费 Token 额度
- GLM-4V-Flash 完全免费使用
- 实名认证后可获得更高配额

### 2. 配置多模型支持

由于需要同时使用 Claude 和 GLM，需要配置多个 API 端点：

编辑 `docker-compose.yml`：

```yaml
environment:
  # Claude API
  - OPENAI_API_BASE_URLS=https://api.anthropic.com/v1,https://open.bigmodel.cn/api/paas/v4
  - OPENAI_API_KEYS=${CLAUDE_API_KEY},${GLM_API_KEY}
```

**注意逗号分隔的多端点配置格式。**

### 3. 通过管理界面配置（推荐方式）

登录 Open WebUI 管理员账号：

1. **Admin Panel** → **Settings** → **Connections**
2. 在 **OpenAI API** 下点击 "Add Connection"
3. 填写 GLM 配置：
   - **Name**: `GLM API`
   - **Base URL**: `https://open.bigmodel.cn/api/paas/v4`
   - **API Key**: 你的智谱 API Key
4. 保存配置

### 4. 添加 GLM 模型

**Admin Panel** → **Models** → **Add Model**：

为文本模型配置：
- **Model ID**: `glm-4-plus`
- **Display Name**: `GLM-4 Plus（中文优化）`
- **Context Length**: 128000
- **Max Tokens**: 4096

为视觉模型配置：
- **Model ID**: `glm-4v-flash`
- **Display Name**: `GLM-4V Flash（免费中文视觉）`
- **Supports Vision**: ✅ 勾选
- **Max Image Size**: 20MB
- **Context Length**: 8000

### 5. 配置模型路由策略

在后续的 Filter Pipeline 中，可以根据任务类型自动选择模型：

- **中文文档** → GLM-4V-Flash（免费）
- **英文文档** → Claude Vision（准确）
- **复杂表格/公式** → Claude Opus（最强）
- **日常对话** → GLM-4-Flash（快速）

## 关键代码提示

**完整 .env 文件示例：**

```bash
# Open WebUI 基础配置
WEBUI_SECRET_KEY=your-random-secret-key-here

# Claude API
CLAUDE_API_KEY=sk-ant-api03-xxxxx

# GLM API
GLM_API_KEY=xxxx.xxxxxxxxxxxxxxxx

# 多模型配置
OPENAI_API_BASE_URLS=https://api.anthropic.com/v1,https://open.bigmodel.cn/api/paas/v4
OPENAI_API_KEYS=${CLAUDE_API_KEY},${GLM_API_KEY}
```

**Python 测试脚本（验证 GLM API）：**

```python
from zhipuai import ZhipuAI

client = ZhipuAI(api_key="xxxx.xxxxxxxxxxxxxxxx")

# 测试文本模型
response = client.chat.completions.create(
    model="glm-4-plus",
    messages=[
        {"role": "user", "content": "你好，请用中文介绍你自己"}
    ],
)
print(response.choices[0].message.content)

# 测试视觉模型
vision_response = client.chat.completions.create(
    model="glm-4v-flash",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "这张图片里有什么内容？"},
                {"type": "image_url", "image_url": {"url": "图片URL或base64"}}
            ]
        }
    ],
)
print(vision_response.choices[0].message.content)
```

**智谱 API SDK 安装：**

```bash
pip install zhipuai
```

## 测试验证

### 1. 文本对话测试

在 Open WebUI 中：
1. 选择 "GLM-4 Plus" 模型
2. 发送中文问题："请解释一下量子纠缠现象"
3. 验证回复质量和速度

### 2. 中文视觉识别测试

上传一张中文文档截图：
1. 切换到 "GLM-4V Flash" 模型
2. 上传图片（如发票、合同扫描件）
3. 询问："请提取图片中的所有文字并整理成 Markdown"
4. 验证识别准确率

### 3. 成本对比测试

使用同一张图片分别测试：
- GLM-4V-Flash（免费）
- Claude Vision（付费）

比较：
- 识别准确率
- 处理速度
- 成本差异

### 4. API 配额查看

访问智谱 AI 控制台：
- 查看 Token 使用量
- 确认剩余额度
- 查看调用日志

## 注意事项

**免费额度优化：**
1. **GLM-4V-Flash 完全免费**，优先用于中文文档
2. 复杂任务才切换到付费模型
3. 实现自动降级：GLM 失败时回退到 Claude

**API 限制：**
- 免费用户 QPM（每分钟请求数）较低
- 单张图片建议 < 10MB
- 超长文档需分页处理

**中文优化建议：**
1. GLM 模型对中文理解更深，提示词用中文效果更好
2. 中文文档、中文对话优先使用 GLM
3. 英文学术论文使用 Claude 更准确

**模型选择策略：**

| 任务类型 | 推荐模型 | 原因 |
|---------|---------|------|
| 中文发票/合同 | GLM-4V-Flash | 免费 + 中文准确 |
| 英文 PDF | Claude Vision | 英文理解好 |
| 复杂图表 | GLM-4V-Plus | 图表识别强 |
| 日常聊天 | GLM-4-Flash | 快速且免费 |

**网络配置：**
- 智谱 API 国内访问稳定，无需代理
- 响应速度通常快于国外 API
- 建议配置超时时间为 30 秒

**错误处理：**
常见错误码：
- `1301`：API Key 无效
- `1302`：余额不足
- `1303`：速率限制

建议在 Pipeline 中实现重试和降级逻辑。

**版本兼容性：**
- 智谱 API 遵循 OpenAI 兼容格式
- 可直接用 OpenAI SDK 调用（设置 base_url）
- 部分高级功能可能需要专用 SDK

## 依赖关系

**前置任务：**
- 任务01：Docker 部署 Open WebUI
- 任务02：配置 Claude API（可选，但建议一起配置）

**后置任务：**
- 任务08：GLM-4V API 集成（文档处理 Pipeline）
- 任务13：意图识别模块（智能路由到 GLM 或 Claude）
