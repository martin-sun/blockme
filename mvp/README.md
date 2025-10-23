# BlockMe MVP - Skill 路由 + LLM 回答验证

## 项目目标

验证核心流程的可行性：
1. **用户输入问题**
2. **Claude Haiku 4.5** 路由相关 Skills
3. **加载 Skills** 内容
4. **GLM-4.6** 基于 Skills 生成回答

## 项目结构

```
mvp/
├── skills/                      # 知识库 (3个税务相关 Skill)
│   ├── saskatchewan-pst.md     # 萨省 PST
│   ├── canada-gst.md           # 加拿大 GST
│   └── tax-filing-basics.md    # 报税基础
├── skill_loader.py             # Skill 加载器
├── skill_router.py             # Claude Haiku 4.5 路由
├── chat_service.py             # GLM-4.6 回答生成
├── main.py                     # CLI 入口
├── pyproject.toml              # 依赖配置
├── .env.example                # 环境变量模板
└── README.md                   # 本文档
```

## 快速开始

### 1. 安装依赖

使用 `uv` 管理依赖（推荐）：

```bash
cd mvp

# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
uv sync
```

### 2. 配置 API Keys

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Keys：

```bash
ANTHROPIC_API_KEY=sk-ant-...
GLM_API_KEY=...
```

或者直接在终端导出：

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export GLM_API_KEY=...
```

### 3. 运行 MVP

```bash
python main.py
```

## 使用示例

启动后，你会看到交互式 CLI：

```
============================================================
  BlockMe 知识库助手 MVP
============================================================

提示:
  - 输入问题并按回车
  - 输入 'quit' 或 'exit' 退出
  - 输入 'skills' 查看所有 Skills

💬 你的问题:
```

### 测试问题示例

1. **问题**: "萨省的 PST 税率是多少？"
   - **预期**: 路由到 `saskatchewan-pst` Skill
   - **验证**: GLM 回答 6%

2. **问题**: "GST 和 PST 有什么区别？"
   - **预期**: 路由到 `saskatchewan-pst` + `canada-gst`
   - **验证**: 回答包含联邦税和省税的对比

3. **问题**: "如何报税？"
   - **预期**: 路由到 `tax-filing-basics`
   - **验证**: 回答包含报税流程

4. **问题**: "今天天气怎么样？"
   - **预期**: 未匹配到 Skills
   - **验证**: GLM 用通用知识回答

## 核心流程

```
┌─────────────┐
│ 用户输入问题 │
└──────┬──────┘
       │
       v
┌─────────────────────────┐
│ Claude Haiku 4.5 路由    │  ← 分析问题，选择相关 Skills
│ (SkillRouter)            │
└──────┬──────────────────┘
       │
       v
┌─────────────────────────┐
│ 加载 Skills 内容         │  ← 从 markdown 文件读取
│ (SkillLoader)            │
└──────┬──────────────────┘
       │
       v
┌─────────────────────────┐
│ GLM-4.6 生成回答         │  ← 基于 Skills 知识回答
│ (ChatService)            │
└──────┬──────────────────┘
       │
       v
┌─────────────┐
│ 输出回答     │
└─────────────┘
```

## 技术细节

### 1. Skill 文件格式

每个 Skill 是一个 markdown 文件，包含 YAML front matter：

```markdown
---
id: skill-id
title: Skill 标题
tags: [标签1, 标签2]
description: Skill 描述
domain: 领域
priority: high|medium|low
---

# Skill 内容

这里是 markdown 格式的知识内容...
```

### 2. Claude Haiku 4.5 路由

- **模型**: `claude-haiku-4-20250514`
- **输入**: 用户问题 + 所有 Skills 的元数据
- **输出**: JSON 格式的路由结果

```json
{
  "matched_skills": ["skill-id-1", "skill-id-2"],
  "confidence": "high",
  "reasoning": "推理过程..."
}
```

### 3. GLM-4.6 回答生成

- **模型**: `glm-4-flash` (免费)
- **输入**: 知识上下文 + 用户问题
- **输出**: 基于知识的准确回答

## 测试各个组件

### 测试 SkillLoader

```bash
python skill_loader.py
```

### 测试 SkillRouter

```bash
python skill_router.py
```

### 测试 ChatService

```bash
python chat_service.py
```

## 预期结果

✅ CLI 可以正常启动和接收输入
✅ Claude Haiku 4.5 能正确路由相关 Skills
✅ Skills 内容正确加载
✅ GLM-4.6 基于 Skills 生成准确回答
✅ 整个流程运行流畅，无报错

## 已知限制 (MVP)

- ❌ 无缓存功能（每次都会重新路由）
- ❌ 无对话历史（单轮问答）
- ❌ 无流式响应
- ❌ 无成本监控
- ❌ 无前端 UI

这些功能将在后续版本中实现。

## 下一步

如果 MVP 验证成功，可以继续：

1. 添加缓存功能（减少 API 调用成本）
2. 实现对话历史支持
3. 开发 Svelte 前端
4. 实现文档处理 Pipeline (PDF → Markdown)
5. 添加成本监控

## 故障排除

### 1. API Key 错误

```
❌ 错误: 未找到 ANTHROPIC_API_KEY 环境变量
```

**解决**: 确保 `.env` 文件存在并包含正确的 API Key，或导出环境变量。

### 2. 模块导入错误

```
ModuleNotFoundError: No module named 'anthropic'
```

**解决**: 确保已激活虚拟环境并运行 `uv sync`。

### 3. Skills 目录不存在

```
⚠️  Skills 目录不存在: skills
```

**解决**: 确保从 `mvp/` 目录运行 `python main.py`。

## 许可证

本项目为内部测试 MVP，暂无开源许可证。
