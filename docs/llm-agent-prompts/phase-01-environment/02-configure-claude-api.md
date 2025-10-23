# 任务02：配置 Claude API 接入

## 任务目标

在 Open WebUI 中配置 Anthropic Claude API，使系统能够调用 Claude 3.5 Sonnet 等模型进行对话和文档处理。重点支持 Claude 的视觉能力（Vision API），用于后续的文档转 Markdown 功能。

## 技术要求

**必需资源：**
- Anthropic API Key（从 https://console.anthropic.com 获取）
- Open WebUI 已部署并运行（任务01完成）
- 网络能访问 `api.anthropic.com`

**推荐模型：**
- `claude-3-5-sonnet-20241022`：最新 Sonnet 版本，性价比高
- `claude-3-opus-20240229`：最强性能，适合复杂任务
- `claude-3-haiku-20240307`：快速响应，成本最低

## 实现步骤

### 1. 获取 API Key

登录 Anthropic Console：
1. 访问 https://console.anthropic.com/settings/keys
2. 点击 "Create Key"
3. 命名密钥（如 "open-webui-production"）
4. 复制并安全保存密钥（只显示一次）

### 2. 配置环境变量方式（推荐）

编辑 `docker-compose.yml`，添加 Claude API 配置：

```yaml
environment:
  - OPENAI_API_BASE_URLS=https://api.anthropic.com/v1
  - OPENAI_API_KEYS=sk-ant-api03-xxxxx  # 你的 Claude API Key
  - ENABLE_OPENAI_API=true
```

**说明：**
- Open WebUI 使用 OpenAI 兼容接口格式
- Anthropic API 支持 OpenAI 格式调用
- 通过环境变量配置避免明文存储密钥

### 3. 配置界面方式（灵活）

如果不使用环境变量，可以通过管理员界面配置：

1. 登录 Open WebUI 管理员账号
2. 进入 **Admin Panel** → **Settings** → **Connections**
3. 找到 **OpenAI API** 配置区域
4. 填写：
   - **API Base URL**: `https://api.anthropic.com/v1`
   - **API Key**: 你的 Claude API Key
5. 点击保存

### 4. 添加 Claude 模型

进入 **Admin Panel** → **Models**：

1. 点击 "Add Model"
2. 填写模型 ID：
   - `claude-3-5-sonnet-20241022`
   - `claude-3-opus-20240229`
3. 设置模型显示名称（如 "Claude 3.5 Sonnet"）
4. 配置参数：
   - **Max Tokens**: 4096（输出长度）
   - **Temperature**: 0.7（创造性）
   - **Context Length**: 200000（上下文窗口）

### 5. 配置 Vision API 支持

对于文档处理需求，需要确保启用图像输入：

在模型配置中：
1. 勾选 **"Supports Vision"** 选项
2. 设置 **Max Image Size**: 32MB
3. 设置 **Max Pages**: 100（PDF 处理限制）

## 关键代码提示

**docker-compose.yml 完整配置示例：**

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    environment:
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}
      - OPENAI_API_BASE_URLS=https://api.anthropic.com/v1
      - OPENAI_API_KEYS=${CLAUDE_API_KEY}
      - ENABLE_OPENAI_API=true
      # Vision 相关配置
      - ENABLE_IMAGE_GENERATION=false
      - IMAGE_SIZE_LIMIT=33554432  # 32MB in bytes
```

**使用 .env 文件管理密钥：**

创建 `.env` 文件：
```bash
WEBUI_SECRET_KEY=your-random-secret-key
CLAUDE_API_KEY=sk-ant-api03-xxxxx
```

在 `docker-compose.yml` 中引用：
```yaml
env_file:
  - .env
```

**Python 测试脚本（验证 API 可用性）：**

```python
import anthropic

client = anthropic.Anthropic(api_key="sk-ant-api03-xxxxx")

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "测试连接"}
    ]
)
print(message.content)
```

## 测试验证

### 1. 基础对话测试

在 Open WebUI 聊天界面：
1. 选择 Claude 模型
2. 发送测试消息："请用中文自我介绍"
3. 确认收到正常回复

### 2. Vision API 测试

上传一张包含文字的图片：
1. 点击上传图标
2. 选择一张截图或扫描文档
3. 询问："请提取图片中的文字"
4. 确认 Claude 能正确识别和提取内容

### 3. API 配额检查

访问 Anthropic Console 查看：
- API 调用次数
- Token 使用量
- 费用统计

### 4. 错误处理测试

故意输入错误的 API Key：
- 应显示友好的错误提示
- 不应泄露敏感信息

## 注意事项

**成本控制：**
1. Claude API 按 Token 计费：
   - 输入：~$3/M tokens（Sonnet）
   - 输出：~$15/M tokens（Sonnet）
2. Vision API 额外收费：~$0.003/图像
3. 建议设置每月预算上限

**速率限制：**
- 免费层：有较低的 RPM 限制
- 付费层：根据账户等级不同
- 超限会返回 429 错误，需实现重试逻辑

**安全最佳实践：**
1. 不要将 API Key 提交到 Git 仓库
2. 使用 `.env` 文件并添加到 `.gitignore`
3. 定期轮换 API Key
4. 使用只读权限的 Key（如果可能）

**国内网络问题：**
- Anthropic API 可能需要代理访问
- 配置 Docker 容器代理：
  ```yaml
  environment:
    - HTTP_PROXY=http://your-proxy:port
    - HTTPS_PROXY=http://your-proxy:port
  ```

**模型版本管理：**
- Claude 模型会定期更新
- 使用带日期的模型 ID（如 `-20241022`）确保稳定性
- 关注 Anthropic 发布公告，及时更新到新版本

**Open WebUI 适配说明：**
1. **OpenAI 兼容模式**：
   - Open WebUI 通过 OpenAI 兼容接口连接 Claude
   - 设置 `OPENAI_API_BASE_URLS=https://api.anthropic.com/v1`
   - 某些平台可能需要选择"Anthropic"连接器而非"OpenAI"

2. **模型 ID 格式**：
   - 使用完整模型 ID：`claude-haiku-4-5` 或 `claude-haiku-4-5-20251001`
   - 避免使用别名，可能导致识别失败

3. **API 密钥格式**：
   - Claude API Key 格式：`sk-ant-api03-xxxxx`
   - 与 OpenAI Key 格式不同，注意区分

4. **连接测试**：
   - 配置后务必在 Open WebUI 界面测试连接
   - 检查模型列表是否正确显示
   - 发送测试消息验证响应正常

5. **常见问题**：
   - 若连接失败，检查是否需要代理
   - 确认 API Key 有足够余额
   - 查看 Docker 日志排查错误：`docker logs <container-id>`

## 依赖关系

**前置任务：**
- 任务01：Docker 部署 Open WebUI

**后置任务：**
- 任务07：Claude Vision API 集成（文档处理）
- 任务13：意图识别模块（可选择使用 Claude）
