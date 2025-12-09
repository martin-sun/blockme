# BeanFlow-CRA

基于 LLM 的 CRA 税务文档处理与智能问答系统。

---

## 系统概述

BeanFlow-CRA 包含两个核心部分：

| 组件 | 状态 | 说明 |
|------|------|------|
| **Part 1: Skill 生成 Pipeline** | ✅ 已实现 | 将 CRA 税务 PDF 转换为结构化 Skill 文件 |
| **Part 2: FastAPI 问答服务** | 🚧 开发中 | 基于 Skill 文件提供实时税务问答 |

---

## 项目结构

```
BeanFlow-CRA/
├── frontend/          # SvelteKit 5 + TypeScript 前端
├── backend/           # Python 后端（PDF 处理 + FastAPI）
├── mvp/               # MVP 验证代码
└── docs/              # 项目文档
```

---

## 快速开始

### 环境准备

```bash
# macOS 系统依赖
brew install poppler mupdf-tools

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API keys
```

### 后端
```bash
cd backend
uv venv .venv && source .venv/bin/activate
uv sync
uv run python generate_skill.py --pdf ../mvp/pdf/t4012-24e.pdf --glm-api
```

### 前端
```bash
cd frontend
npm install && npm run dev
# 访问 http://localhost:5173
```

---

## 文档导航

| 文档 | 说明 |
|------|------|
| [docs/README.md](docs/README.md) | 文档中心入口 |
| [docs/guides/QUICK_START.md](docs/guides/QUICK_START.md) | 详细安装指南 |
| [docs/architecture/PIPELINE_ARCHITECTURE.md](docs/architecture/PIPELINE_ARCHITECTURE.md) | 6 阶段 Pipeline 架构 |
| [backend/README.md](backend/README.md) | 后端详细使用说明 |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | SvelteKit 5, TypeScript, Tailwind CSS 4 |
| 后端 | Python 3.11+, FastAPI, PyMuPDF |
| LLM | Claude API, 智谱 GLM-4, Gemini |

---

## 项目阶段

- ✅ **Phase 01**: 环境搭建
- ✅ **Phase 02**: 文档处理（6 阶段 Pipeline）
- ⏳ **Phase 03**: 知识管理
- 🚧 **Phase 04**: 动态加载
- 📝 **Phase 05**: 测试优化

---

## License

私有项目
