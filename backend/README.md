# BeanFlow-CRA Backend

CRA 税务文档处理后端服务，包含 Skill 生成 Pipeline 和 FastAPI 问答服务。

---

## 系统架构

| 组件 | 状态 | 说明 |
|------|------|------|
| **Part 1: Skill 生成 Pipeline** | ✅ 已实现 | 6 阶段流水线，将 PDF 转换为 Skill 文件 |
| **Part 2: FastAPI 问答服务** | 🚧 规划中 | 基于 Skill 提供实时问答 API |

---

## 快速开始

### 1. 环境配置

```bash
cd backend
uv venv .venv
source .venv/bin/activate  # macOS/Linux
uv sync
```

### 2. 基本使用

```bash
# 快速测试（前 10 页）
uv run python generate_skill.py --pdf ../mvp/pdf/t4012-24e.pdf --glm-api

# 完整处理（所有页面 + AI 增强）
uv run python generate_skill.py \
  --pdf ../mvp/pdf/t4012-24e.pdf \
  --glm-api \
  --full

# 断点续传
uv run python generate_skill.py \
  --pdf ../mvp/pdf/t4012-24e.pdf \
  --glm-claude \
  --full
```

---

## 命令行参数速查

| 参数 | 说明 |
|------|------|
| `--pdf PATH` | PDF 文件路径（必需） |
| `--full` | 处理完整文档 |
| `--max-pages N` | 只处理前 N 页 |
| `--local-claude` | 使用 Claude Code CLI |
| `--glm-api` | 使用 GLM API |
| `--enhance-skill` | 增强 SKILL.md（可选） |
| `--force` | 强制重新处理（忽略缓存） |

---

## 6 阶段 Pipeline

```
PDF → Stage 1: 提取 → Stage 2: 分类 → Stage 3: 分块
    → Stage 4: AI 增强 → Stage 5: 生成 → Stage 6: 增强（可选）
```

详细架构请参阅: [Pipeline 架构文档](../docs/architecture/PIPELINE_ARCHITECTURE.md)

---

## 项目结构

```
backend/
├── generate_skill.py          # 统一入口
├── stage1_extract_pdf.py      # PDF 提取
├── stage2_classify_content.py # 内容分类
├── stage3_chunk_content.py    # 内容分块
├── stage4_enhance_chunks.py   # AI 增强
├── stage5_generate_skill.py   # Skill 生成
├── enhance_skill.py           # SKILL.md 增强
├── app/document_processor/    # 核心处理模块
├── cache/                     # 缓存目录
└── skills_output/             # 输出目录
```

---

## 文档链接

| 文档 | 说明 |
|------|------|
| [Pipeline 架构](../docs/architecture/PIPELINE_ARCHITECTURE.md) | 6 阶段流水线详解 |
| [SKILL.md 增强](../docs/architecture/SKILL_ENHANCEMENT.md) | Skill 增强功能设计 |
| [LLM Provider](../docs/architecture/LLM_PROVIDERS.md) | Claude/GLM/Gemini 集成 |
| [缓存管理](../docs/guides/CACHE_MANAGEMENT.md) | 缓存机制和清理 |
| [故障排查](../docs/guides/TROUBLESHOOTING.md) | 常见问题解决 |

---

## 缓存和断点续传

- **缓存位置**: `backend/cache/`
- **断点续传**: Stage 4 支持中断后继续
- **查看进度**: `cat cache/enhanced_chunks_*/progress.json`
- **清理缓存**: 参阅 [缓存管理文档](../docs/guides/CACHE_MANAGEMENT.md)

---

## 性能参考

| 阶段 | 时间（151 页 PDF） |
|------|-------------------|
| Stage 1-3 | < 3 分钟 |
| Stage 4 (AI 增强) | 7-11 小时 |
| Stage 5-6 | < 10 分钟 |

---

**License**: MIT
**版本**: 2.0 (Multi-Stage Pipeline)
