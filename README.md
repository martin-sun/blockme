# BlockMe Knowledge System

基于 LLM 的文档处理和问答系统，专注于加拿大税务知识库管理。

## 项目结构

```
blockme/
├── frontend/          # Svelte 5 + TypeScript 前端
│   ├── package.json
│   └── node_modules/
├── backend/           # FastAPI 后端服务（独立）
│   ├── pyproject.toml
│   ├── .venv/
│   ├── tests/
│   └── app/
├── mvp/              # MVP 验证代码（参考用）
└── docs/             # 项目文档
```

## 技术栈

### 前端
- SvelteKit 5 + TypeScript
- Tailwind CSS 4
- Vite

### 后端
- Python 3.11+
- FastAPI + Uvicorn
- Anthropic Claude API (Skill 路由)
- 智谱 GLM API (文档理解和回答)

### 文档处理
- pdf2image + PyMuPDF (PDF 处理)
- python-docx (Word 文档)
- Pillow (图像处理)

## 开发指南

### 环境准备

1. **安装系统依赖**（macOS）:
```bash
brew install poppler mupdf-tools
```

2. **配置环境变量**:
```bash
# 在根目录创建 .env
cp .env.example .env
# 编辑 .env 填入 API keys
```

### 启动前端

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### 启动后端

```bash
cd backend

# 创建虚拟环境并安装依赖
uv venv .venv
source .venv/bin/activate
uv sync --extra dev

# 配置后端环境变量
cp .env.example .env
# 编辑 backend/.env 填入 API keys

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
# API 文档: http://localhost:8000/docs
```

### 运行测试

```bash
cd backend
source .venv/bin/activate

# 运行所有测试
pytest tests/ -v

# 环境验证
python tests/test_dependencies.py
python tests/test_api_connections.py
```

## 项目阶段

根据 `docs/llm-agent-prompts/` 中的规划，项目分为 5 个阶段：

- ✅ **Phase 01**: 环境搭建
- ⏳ **Phase 02**: 文档处理
- ⏳ **Phase 03**: 知识管理
- ⏳ **Phase 04**: 动态加载
- ⏳ **Phase 05**: 测试优化

## License

私有项目
