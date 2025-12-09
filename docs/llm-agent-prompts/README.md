# LLM Code Agent 提示词文档集

这是一套用于指导 LLM Code Agent 实现 BeanFlow-CRA 系统的提示词文档。

---

## 系统分层架构

BeanFlow-CRA 采用三层架构设计：

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: 交互层 (❌ 未实现)                                 │
│  - Svelte 前端界面 + FastAPI 聊天接口                       │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: 智能检索层 (❌ 未实现)                             │
│  - 意图识别 + Skill 路由 + 知识检索                         │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: 知识库生成层 (✅ 已完成 95%)                       │
│  - 6 阶段 Pipeline + 多 LLM Provider                       │
└─────────────────────────────────────────────────────────────┘
```

**详细架构文档**: [SYSTEM_ARCHITECTURE.md](../architecture/SYSTEM_ARCHITECTURE.md)

---

## 文档结构

```
docs/llm-agent-prompts/
├── README.md                          # 本文档
├── phase-01-environment/              # 阶段1：环境搭建（4个文档）
│   ├── 01-setup-svelte-frontend.md
│   ├── 02-configure-claude-api.md
│   ├── 03-configure-glm-api.md
│   └── 04-setup-python-dependencies.md
├── phase-02-document-processing/      # 阶段2：文档处理（4个文档）
│   ├── 06-office-document-converter.md   # 未来功能
│   ├── 07-claude-vision-integration.md   # Vision 参考
│   ├── 08-glm-vision-integration.md      # Vision 参考
│   └── 10-backend-structure.md           # 后端架构
├── phase-04-dynamic-loading/          # 阶段4：动态加载引擎（3个文档）- Layer 2
│   ├── 13-intent-recognition-module.md
│   ├── 14-knowledge-retrieval-engine.md
│   └── 15-fastapi-chat-integration.md
└── phase-05-testing-optimization/     # 阶段5：测试优化（2个文档）
    ├── 16-document-processing-tests.md
    └── 18-svelte-frontend-development.md
```

---

## Layer 状态说明

### Layer 1: 知识库生成层 ✅ 已完成

Layer 1 的核心功能已在 Pipeline 中实现，相关规划文档已归档。

**实现文档**:
- [Pipeline 架构](../architecture/PIPELINE_ARCHITECTURE.md) - 6 阶段流水线
- [SKILL.md 增强](../architecture/SKILL_ENHANCEMENT.md) - Skill 增强功能
- [LLM Provider 系统](../architecture/LLM_PROVIDERS.md) - 多 Provider 支持

### Layer 2: 智能检索层 (规划中)

本目录的 `phase-04-dynamic-loading/` 文档描述 Layer 2 的规划：
- 意图识别模块
- 知识检索引擎
- FastAPI 聊天集成

### Layer 3: 交互层 (规划中)

本目录的 `phase-05-testing-optimization/18-svelte-frontend-development.md` 描述前端规划。

---

## 使用指南

### 按阶段顺序执行

#### 阶段1：环境搭建

1. [01 - 搭建 Svelte 前端环境](./phase-01-environment/01-setup-svelte-frontend.md)
2. [02 - 配置 Claude API](./phase-01-environment/02-configure-claude-api.md)
3. [03 - 配置 GLM API](./phase-01-environment/03-configure-glm-api.md)
4. [04 - 安装 Python 依赖](./phase-01-environment/04-setup-python-dependencies.md)

#### 阶段2：文档处理（参考）

5. [06 - Office 文档转换](./phase-02-document-processing/06-office-document-converter.md)
6. [07 - Claude Vision API 集成](./phase-02-document-processing/07-claude-vision-integration.md)
7. [08 - GLM Vision API 集成](./phase-02-document-processing/08-glm-vision-integration.md)
8. [10 - 后端结构设计](./phase-02-document-processing/10-backend-structure.md)

#### 阶段4：动态加载引擎（Layer 2）

9. [13 - 用户意图识别模块](./phase-04-dynamic-loading/13-intent-recognition-module.md)
10. [14 - 知识检索引擎](./phase-04-dynamic-loading/14-knowledge-retrieval-engine.md)
11. [15 - FastAPI 聊天接口集成](./phase-04-dynamic-loading/15-fastapi-chat-integration.md)

#### 阶段5：测试优化

12. [16 - 文档处理功能测试](./phase-05-testing-optimization/16-document-processing-tests.md)
13. [18 - Svelte 前端开发](./phase-05-testing-optimization/18-svelte-frontend-development.md)

---

## 技术栈

### 前端
- **SvelteKit**: 现代化前端框架
- **TypeScript**: 类型安全
- **Tailwind CSS**: 样式框架

### 后端
- **FastAPI**: 高性能 API 服务
- **Python 3.11+**: 后端语言
- **WebSocket**: 实时对话

### AI API
- **Claude API**: Vision + 对话
- **GLM API**: 中文文档处理
- **Gemini API**: 大上下文窗口

### Python 工具
- **uv**: 包管理器
- **pytest**: 测试框架
- **pydantic**: 数据验证

---

## 相关文档

### 架构文档
- [系统架构](../architecture/SYSTEM_ARCHITECTURE.md) - 分层架构总览
- [Pipeline 架构](../architecture/PIPELINE_ARCHITECTURE.md) - 文档处理流水线
- [LLM Provider](../architecture/LLM_PROVIDERS.md) - Provider 系统

### 使用指南
- [快速开始](../guides/QUICK_START.md) - 环境配置和运行
- [故障排查](../guides/TROUBLESHOOTING.md) - 常见问题

---

**维护者**: BeanFlow Team
**最后更新**: 2025-12-08
