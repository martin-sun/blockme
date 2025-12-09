# LLM Provider 系统

BeanFlow-CRA 支持多种 LLM Provider，用于文档处理和内容增强。本文档详细说明各 Provider 的配置、特性和使用场景。

---

## 架构概述

### Provider 抽象层

系统通过统一的 Provider 接口支持多种 LLM 服务。每个 Provider 实现以下核心方法：

| 方法 | 说明 |
|------|------|
| `is_available()` | 检查 Provider 是否可用（CLI/API 就绪） |
| `build_command()` | 构建 CLI 命令（CLI 类 Provider） |
| `parse_output()` | 解析 LLM 输出或执行 API 调用 |
| `get_timeout()` | 根据内容长度计算超时时间 |
| `get_max_chunk_size()` | 返回最大支持的 chunk 大小 |
| `uses_stdin()` | 是否通过 stdin 传递 prompt |
| `is_api_based()` | 是否为 API 类 Provider |

### Provider 类型

系统支持两种类型的 Provider：

**CLI 类 Provider**（通过命令行工具调用）：
- Claude Code CLI
- Gemini CLI
- Codex CLI

**API 类 Provider**（直接调用 API）：
- GLM API
- Gemini API

---

## Provider 详细说明

### 1. Claude Code Provider

**类型**: CLI

**用途**: 使用本地 Claude Code CLI 进行内容增强

**命令行参数**: `--local-claude`

**适用阶段**: Stage 4 内容增强、Stage 6 SKILL.md 增强

#### 配置要求

| 项目 | 要求 |
|------|------|
| CLI 工具 | `claude` 命令需在 PATH 中可用 |
| 认证方式 | Claude 订阅账户（通过 `claude login` 登录） |
| 模型 | Sonnet 4.5（平衡质量和速度） |

#### 技术规格

| 参数 | 值 |
|------|------|
| 最大 chunk 大小 | 300,000 字符 |
| 输入 token 限制 | 200K tokens |
| 输出 token 限制 | 64K tokens |
| 基础超时 | 240 秒 |
| 超时计算 | max(240s, 5s × 内容KB数) |
| 输入方式 | stdin |

#### CLI 命令格式

```
claude --print --tools '' --model sonnet
```

参数说明：
- `--print`: 非交互模式，输出到 stdout
- `--tools ''`: 禁用工具使用
- `--model sonnet`: 使用 Sonnet 4.5 模型

#### 安装验证

```bash
# 检查 CLI 是否安装
which claude

# 验证登录状态
claude --help
```

---

### 2. GLM API Provider

**类型**: API

**用途**: 智谱 GLM-4.6 直接 API 调用

**命令行参数**: `--glm-api`

**适用阶段**:
- Stage 2 语义分类（**默认必需**）
- Stage 4 内容增强（可选）

#### 配置要求

| 项目 | 要求 |
|------|------|
| 环境变量 | `GLM_API_KEY` |
| Python 包 | `zhipuai>=2.0.0` |
| 模型 | glm-4.6（默认） |

#### 技术规格

| 参数 | 值 |
|------|------|
| 最大 chunk 大小 | 400,000 字符 |
| 上下文窗口 | 128K tokens |
| 最大输出 tokens | 8,192 |
| 基础超时 | 120 秒 |
| 超时计算 | max(120s, 2s × 内容KB数) |
| API 端点 | `https://open.bigmodel.cn/api/coding/paas/v4/` |

#### API 参数配置

| 参数 | 值 | 说明 |
|------|------|------|
| temperature | 0.3 | 低温度保证输出一致性 |
| max_tokens | 8192 | 合理的输出限制 |
| top_p | 0.95 | 核采样阈值 |
| thinking | 可选 | 支持深度推理模式 |

#### 特殊功能

**Thinking 模式**: GLM Provider 支持启用思考模式（thinking mode），用于复杂推理任务：

```python
provider = GLMAPIProvider(model="glm-4.6", enable_thinking=True)
```

**响应截断检测**: 自动检测并报告因 token 限制导致的响应截断。

#### 环境变量配置

```bash
# .env 文件
GLM_API_KEY=your_api_key_here
```

#### 安装依赖

```bash
uv pip install zhipuai>=2.0.0
```

---

### 3. Gemini CLI Provider

**类型**: CLI

**用途**: Google Gemini CLI 调用

**命令行参数**: `--local-gemini`

**适用阶段**: Stage 4 内容增强

#### 配置要求

| 项目 | 要求 |
|------|------|
| CLI 工具 | `gemini` 命令需在 PATH 中可用 |
| 安装方式 | `npm install -g @google/gemini-cli` |
| 认证方式 | Google 账户（首次运行时交互认证） |
| 模型 | gemini-2.5-pro |

#### 技术规格

| 参数 | 值 |
|------|------|
| 最大 chunk 大小 | 1,500,000 字符 |
| 上下文窗口 | 1M tokens |
| 免费配额 | 1000 请求/天, 60 请求/分钟 |
| 基础超时 | 180 秒 |
| 超时计算（小文档 <100K） | max(180s, 2s × 内容KB数) |
| 超时计算（中文档 100K-500K） | 2s × 内容KB数 |
| 超时计算（大文档 >500K） | 3s × 内容KB数 + 10% 安全余量 |
| 输入方式 | 命令行参数 |

#### CLI 命令格式

```
gemini -m gemini-2.5-pro -p "prompt" --output-format text
```

参数说明：
- `-m gemini-2.5-pro`: 使用 Gemini 2.5 Pro 模型
- `-p`: 提供 prompt
- `--output-format text`: 纯文本输出

#### 安装验证

```bash
# 安装 CLI
npm install -g @google/gemini-cli

# 验证安装
gemini --version

# 首次使用需要认证
gemini -p "Hello"
```

---

### 4. Gemini API Provider

**类型**: API

**用途**: Google Gemini API 直接调用

**适用阶段**: Stage 4 内容增强、Stage 5 动态语义分类

#### 配置要求

| 项目 | 要求 |
|------|------|
| 环境变量 | `GEMINI_API_KEY` |
| Python 包 | `google-generativeai>=0.3.0` |
| 模型 | gemini-2.5-pro（默认，可配置） |

#### 技术规格

| 参数 | 值 |
|------|------|
| 最大 chunk 大小 | 1,500,000 字符 |
| 上下文窗口 | 1M tokens |
| 最大输出 tokens | 8,192 |
| 基础超时 | 180 秒 |

#### API 参数配置

| 参数 | 值 | 说明 |
|------|------|------|
| temperature | 0.3 | 低温度保证输出一致性 |
| top_p | 0.95 | 核采样阈值 |
| top_k | 40 | Top-k 采样参数 |
| max_output_tokens | 8192 | 最大输出限制 |

#### 环境变量配置

```bash
# .env 文件
GEMINI_API_KEY=your_api_key_here
```

#### 安装依赖

```bash
uv pip install google-generativeai>=0.3.0
```

---

### 5. Codex CLI Provider

**类型**: CLI

**用途**: OpenAI Codex CLI 调用

**命令行参数**: `--local-codex`

**适用阶段**: Stage 4 内容增强

#### 配置要求

| 项目 | 要求 |
|------|------|
| CLI 工具 | `codex` 命令需在 PATH 中可用 |
| 安装方式 | 从 GitHub 下载: https://github.com/openai/codex |
| 认证方式 | ChatGPT 订阅或 API Key |

#### 技术规格

| 参数 | 值 |
|------|------|
| 最大 chunk 大小 | 250,000 字符 |
| 上下文窗口 | ~128K tokens（估计） |
| 基础超时 | 240 秒 |
| 超时计算 | max(240s, 5s × 内容KB数) |
| 输入方式 | 命令行参数 |
| 运行模式 | 默认只读模式（安全） |

#### CLI 命令格式

```
codex exec "prompt"
```

**输出行为**:
- 活动日志输出到 stderr
- 最终结果输出到 stdout

#### 认证方式

```bash
# 交互式登录
codex login

# 或通过环境变量
export CODEX_API_KEY=your-key
codex exec "prompt"
```

#### 安装验证

```bash
# 验证安装
which codex

# 测试调用
codex exec "Hello"
```

---

## 各阶段 Provider 使用

| 阶段 | 默认 Provider | 可选 Provider | 说明 |
|------|--------------|--------------|------|
| Stage 2 分类 | GLM-4.6 API | - | 语义分类，必须使用 GLM |
| Stage 4 增强 | 用户指定 | Claude, GLM, Gemini, Codex | 内容增强，用户选择 |
| Stage 5 分类 | dynamic-semantic | Gemini API, GLM API | 动态语义分类 |
| Stage 6 增强 | 用户指定 | 同 Stage 4 | SKILL.md 增强 |

---

## Provider 性能对比

### 上下文窗口对比

| Provider | 上下文窗口 | 最大 chunk | 适合场景 |
|----------|-----------|-----------|---------|
| Gemini CLI/API | 1M tokens | 1.5M chars | 大文档整体分析 |
| GLM API | 128K tokens | 400K chars | 中等文档，分类任务 |
| Claude Code | 200K tokens | 300K chars | 高质量内容生成 |
| Codex CLI | ~128K tokens | 250K chars | 代码相关任务 |

### 处理效率对比（以 721K 字符文档为例）

| Provider | Chunk 数量 | 预计时间 | 说明 |
|----------|-----------|---------|------|
| Gemini | 1 chunk | 5-10 分钟 | 大上下文优势明显 |
| GLM | 2 chunks | 10-15 分钟 | 性价比高 |
| Claude | 3 chunks | 15-25 分钟 | 输出质量最高 |
| Codex | 3 chunks | 15-25 分钟 | 与 Claude 相当 |

### 超时策略对比

| Provider | 小文档 (<100K) | 中文档 (100K-500K) | 大文档 (>500K) |
|----------|---------------|-------------------|---------------|
| Claude Code | 240s 基础 | 5s/KB | 5s/KB |
| GLM API | 120s 基础 | 2s/KB | 3s/KB + 10% |
| Gemini | 180s 基础 | 2s/KB | 3s/KB + 10% |
| Codex | 240s 基础 | 5s/KB | 5s/KB |

---

## 扩展新 Provider

### 实现步骤

1. 在 `app/document_processor/providers/` 目录下创建新模块
2. 实现 Provider 类，包含所有必需方法
3. 在 `__init__.py` 中导出
4. 在 `llm_cli_providers.py` 的 `get_provider()` 函数中注册

### Provider 接口规范

```python
class NewProvider:
    """新 Provider 模板"""

    def is_available(self) -> bool:
        """检查 Provider 是否可用"""
        pass

    def build_command(self, prompt: str) -> list[str]:
        """构建 CLI 命令（API 类返回空列表）"""
        pass

    def parse_output(self, stdout: str, stderr: str) -> str:
        """解析输出或执行 API 调用"""
        pass

    def get_timeout(self, content_length: int) -> int:
        """计算超时时间"""
        pass

    def uses_stdin(self) -> bool:
        """是否使用 stdin 传递 prompt"""
        pass

    def is_api_based(self) -> bool:
        """是否为 API 类 Provider"""
        pass

    def get_max_chunk_size(self) -> int:
        """返回最大 chunk 大小"""
        pass

    @property
    def name(self) -> str:
        """Provider 显示名称"""
        pass

    def get_env(self) -> Optional[dict]:
        """自定义环境变量（可选）"""
        return None
```

### 代码位置

| 文件 | 说明 |
|------|------|
| `app/document_processor/providers/__init__.py` | Provider 包导出 |
| `app/document_processor/providers/*.py` | 各 Provider 实现 |
| `app/document_processor/llm_cli_providers.py` | Provider 工厂和注册 |

---

## 常见问题

### Provider 不可用

**症状**: `Provider 'xxx' not available`

**排查步骤**:
1. CLI 类: 检查命令是否在 PATH 中
2. API 类: 检查环境变量是否设置
3. API 类: 检查依赖包是否安装

### API 调用失败

**症状**: `API call failed: ...`

**排查步骤**:
1. 验证 API Key 是否正确
2. 检查网络连接
3. 确认配额是否用尽

### 响应截断

**症状**: GLM 返回 `finish_reason=length`

**解决方案**:
1. 减小输入内容大小
2. 将文档拆分为更小的 chunks
3. 检查 max_tokens 配置

---

## 相关文档

- [Pipeline 架构](PIPELINE_ARCHITECTURE.md) - 了解各阶段如何使用 Provider
- [故障排查](../guides/TROUBLESHOOTING.md) - Provider 相关问题详细解决方案
- [快速开始](../guides/QUICK_START.md) - Provider 基本配置

---

**版本**: 2.0
**更新**: 2025-12-08
