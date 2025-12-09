# BeanFlow-CRA System Architecture

**BeanFlow-CRA 全栈问答系统架构文档**

本文档描述系统的分层架构设计、当前实现状态和未来规划。

---

## 系统概述

BeanFlow-CRA 是一个基于 LLM 的 CRA 税务文档处理与智能问答系统，采用三层架构设计：

```
┌─────────────────────────────────────────────────────────────┐
│                    BeanFlow-CRA 全栈问答系统                  │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: 交互层 (❌ 未实现)                                 │
│  - Svelte 前端界面                                          │
│  - FastAPI 聊天接口                                         │
│  - 实时对话 (SSE/WebSocket)                                │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: 智能检索层 (❌ 未实现)                             │
│  - 用户意图识别                                             │
│  - Skill 路由 (Claude 辅助)                                │
│  - 知识检索引擎                                             │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: 知识库生成层 (✅ 已完成 95%)                       │
│  - Skill 生成 Pipeline (6 阶段)                            │
│  - 多 LLM Provider 支持 (Claude/GLM/Gemini/Codex)         │
│  - 缓存和断点续传                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer 1: 知识库生成层

**状态**: ✅ 已完成 95%

### 核心能力

将 CRA 税务 PDF 文档转换为结构化的 Skill 知识库。

### 技术实现

**6 阶段 Pipeline**:

| 阶段 | 说明 | 状态 |
|------|------|------|
| Stage 1 | PDF 文本提取 | ✅ |
| Stage 2 | 内容分类（LLM 语义分类） | ✅ |
| Stage 3 | 内容分块 | ✅ |
| Stage 4 | AI 内容增强 | ✅ |
| Stage 5 | Skill 目录生成 | ✅ |
| Stage 6 | SKILL.md 增强（可选） | ✅ |

**关键特性**:
- 多 LLM Provider 支持
- 智能缓存和断点续传
- 动态超时策略
- 质量验证机制

### 详细文档

- [Pipeline 架构](PIPELINE_ARCHITECTURE.md) - 6 阶段流水线详解
- [SKILL.md 增强](SKILL_ENHANCEMENT.md) - Skill 文件增强功能
- [LLM Provider 系统](LLM_PROVIDERS.md) - 多 Provider 集成

---

## Layer 2: 智能检索层

**状态**: ✅ MVP 已验证

### 设计目标

根据用户问题智能检索和加载相关 Skill 知识。

### 核心组件

| 组件 | 说明 | 状态 |
|------|------|------|
| Skill Loader | 加载和索引 Skill 文件 | ✅ 已实现 |
| Skill Router | LLM 驱动的 Skill 路由 | ✅ 已实现 |
| Chat Service | 基于 Skill 生成回答 | ✅ 已实现 |

### 技术方案

**两层路由架构**:
1. **Prefilter** (可选): 关键词/标签/触发词匹配，适用于 50+ Skills
2. **LLM Router**: Claude Haiku 4.5 或 GLM-4-Flash 智能选择

**支持的路由器**:
| 路由器 | 模型 | 特点 |
|--------|------|------|
| SkillRouter | Claude Haiku 4.5 | 高准确率，推荐 |
| SkillRouterGLM | GLM-4-Flash | 免费替代方案 |

### 详细文档

- [Skills 组织架构](SKILLS_ORGANIZATION.md) - Skill 目录结构和路由机制

---

## Layer 3: 交互层

**状态**: ❌ 规划中

### 设计目标

提供用户友好的 Web 界面和实时对话能力。

### 核心组件

| 组件 | 说明 | 参考文档 |
|------|------|---------|
| Svelte 前端 | 现代化 Web 界面 | [18-svelte-frontend-development.md](../llm-agent-prompts/phase-05-testing-optimization/18-svelte-frontend-development.md) |
| FastAPI 后端 | 聊天 API 服务 | [15-fastapi-chat-integration.md](../llm-agent-prompts/phase-04-dynamic-loading/15-fastapi-chat-integration.md) |
| 实时通信 | SSE/WebSocket 流式传输 | - |

### 技术栈

**前端**:
- SvelteKit
- TypeScript
- Tailwind CSS

**后端**:
- FastAPI
- Python 3.11+
- WebSocket/SSE

---

## 技术栈总览

### 核心依赖

| 类别 | 技术 |
|------|------|
| 前端框架 | SvelteKit + TypeScript |
| 后端框架 | FastAPI + Python 3.11+ |
| LLM 服务 | Claude API, GLM API, Gemini API |
| PDF 处理 | PyMuPDF (fitz) |
| 包管理 | uv |

### LLM Provider

| Provider | 类型 | 用途 |
|----------|------|------|
| Claude Code | CLI | 内容增强 |
| GLM API | API | 语义分类（默认） |
| Gemini | CLI/API | 大文档处理 |
| Codex | CLI | 内容增强 |

详见 [LLM Provider 系统](LLM_PROVIDERS.md)

---

## 项目结构

```
BeanFlow-CRA/
├── backend/                 # Python 后端
│   ├── app/
│   │   └── document_processor/  # Layer 1 核心模块
│   ├── scripts/            # Pipeline 脚本
│   └── cache/              # 处理缓存
├── frontend/               # SvelteKit 前端 (Layer 3)
├── mvp/                    # MVP 验证代码
├── docs/
│   ├── architecture/       # 架构文档（本目录）
│   ├── guides/             # 使用指南
│   └── llm-agent-prompts/  # 开发 prompts
└── skills_output/          # 生成的 Skill 文件
```

---

## 开发路线图

### Phase 1: 知识库生成（已完成）

- [x] 6 阶段 Pipeline
- [x] 多 LLM Provider
- [x] 缓存和断点续传
- [x] 动态语义分类

### Phase 2: 智能检索（MVP 已验证）

- [x] Skill Loader (目录结构支持)
- [x] Skill Router (Claude Haiku / GLM)
- [x] Chat Service (基于 Skill 生成回答)
- [x] 两层路由架构设计

### Phase 3: 交互层（规划中）

- [ ] FastAPI 聊天接口
- [ ] Svelte 前端开发
- [ ] 实时对话功能

---

## 相关文档

### 架构文档

- [Pipeline 架构](PIPELINE_ARCHITECTURE.md)
- [Skills 组织架构](SKILLS_ORGANIZATION.md)
- [SKILL.md 增强](SKILL_ENHANCEMENT.md)
- [LLM Provider 系统](LLM_PROVIDERS.md)

### 使用指南

- [快速开始](../guides/QUICK_START.md)
- [故障排查](../guides/TROUBLESHOOTING.md)
- [缓存管理](../guides/CACHE_MANAGEMENT.md)

### 开发资源

- [LLM Agent Prompts](../llm-agent-prompts/README.md)
- [更新日志](../CHANGELOG.md)

---

**版本**: 1.0
**更新**: 2025-12-08
