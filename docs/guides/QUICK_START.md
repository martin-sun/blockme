# 快速开始

本指南帮助您快速设置和运行 BeanFlow-CRA 系统。

---

## 环境要求

### 系统要求

| 要求 | 最低版本 | 推荐版本 |
|------|---------|---------|
| 操作系统 | macOS / Linux | macOS 14+ / Ubuntu 22.04+ |
| Python | 3.11+ | 3.12 |
| Node.js | 18+ | 20 LTS |
| 磁盘空间 | 2 GB | 10 GB（含缓存） |

### 系统依赖

**macOS**:
```bash
# PDF 处理依赖
brew install poppler mupdf-tools

# 验证安装
pdfinfo --version
mutool --version
```

**Ubuntu/Debian**:
```bash
# PDF 处理依赖
sudo apt-get update
sudo apt-get install -y poppler-utils mupdf-tools

# 验证安装
pdfinfo --version
mutool --version
```

### Python 环境管理

系统使用 `uv` 作为 Python 包管理工具：

```bash
# 安装 uv（如未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 验证安装
uv --version
```

---

## 安装步骤

### 1. 克隆项目

```bash
git clone <repo-url>
cd BeanFlow-CRA
```

### 2. 后端安装

```bash
cd backend

# 创建虚拟环境
uv venv .venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux

# 安装依赖
uv sync
```

**验证后端安装**:
```bash
# 检查 Python 版本
python --version  # 应显示 3.11+

# 检查关键依赖
python -c "import fitz; print(f'PyMuPDF: {fitz.version}')"
```

### 3. 前端安装（可选）

```bash
cd frontend
npm install
```

### 4. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用其他编辑器
```

**必需的环境变量**:

```bash
# GLM API（Stage 2 分类必需）
GLM_API_KEY=your_glm_api_key

# 以下根据使用的 Provider 选择配置
GEMINI_API_KEY=your_gemini_api_key  # 如使用 Gemini API
```

**获取 API Key**:

| Provider | 获取地址 |
|----------|---------|
| GLM (智谱) | https://open.bigmodel.cn/usercenter/apikeys |
| Gemini | https://aistudio.google.com/app/apikey |

### 5. 安装 LLM CLI 工具（可选）

根据您选择的 Provider 安装相应工具：

**Claude Code CLI**:
```bash
# 需要 Claude 订阅
npm install -g @anthropic-ai/claude-code
claude login
```

**Gemini CLI**:
```bash
npm install -g @google/gemini-cli
# 首次运行时会提示认证
```

**Codex CLI**:
```bash
# 从 GitHub 下载并安装
# https://github.com/openai/codex
codex login
```

---

## 第一次运行

### 一键运行（推荐）

使用 `run_pipeline.py` 一键运行完整处理流程：

```bash
cd backend
source .venv/bin/activate

# 使用 GLM API 处理 PDF（推荐）
uv run python run_pipeline.py \
  --pdf ../mvp/pdf/rc4022-24e.pdf \
  --provider glm-api

# 处理完整文档
uv run python run_pipeline.py \
  --pdf ../mvp/pdf/rc4022-24e.pdf \
  --provider glm-api \
  --full

# 并行加速（4 个 worker）
uv run python run_pipeline.py \
  --pdf ../mvp/pdf/rc4022-24e.pdf \
  --provider glm-api \
  --full \
  --workers 4
```

**预期输出**:
```
======================================================================
BeanFlow-CRA: PDF Processing Pipeline
======================================================================
📄 PDF: ../mvp/pdf/rc4022-24e.pdf
🤖 Provider: glm-api
📦 Pages: First 10
📁 Output: skills_output
👷 Workers: 1
======================================================================

🔹 Stage 1/5: PDF Extraction
   ✅ Extraction ID: abc123def456

🔹 Stage 2/5: Content Classification
   ✅ Category: gst_hst_registrants

🔹 Stage 3/5: Content Chunking
   ✅ Chunks: 15

🔹 Stage 4/5: AI Enhancement
   ✅ Enhancement complete

🔹 Stage 5/5: Generate Skill Directory
   ✅ Skill: skills_output/gst-hst-registrants-rc4022

======================================================================
✅ Pipeline Complete!
======================================================================
📁 Skill Directory: skills_output/gst-hst-registrants-rc4022
⏱️  Total Time: 0:15:32
======================================================================
```

### 快速测试（跳过 AI 增强）

最快速的测试方式，跳过耗时的 Stage 4：

```bash
uv run python run_pipeline.py \
  --pdf ../mvp/pdf/rc4022-24e.pdf \
  --provider glm-api \
  --skip-enhance
```

### 使用不同 Provider

```bash
# GLM API（推荐，需要 GLM_API_KEY）
uv run python run_pipeline.py --pdf file.pdf --provider glm-api

# Claude Code CLI（需要 claude login）
uv run python run_pipeline.py --pdf file.pdf --provider claude

# Gemini CLI（需要 gemini login）
uv run python run_pipeline.py --pdf file.pdf --provider gemini

# Codex CLI（需要 codex login）
uv run python run_pipeline.py --pdf file.pdf --provider codex
```

### 处理部分页面

控制处理页数以节省时间：

```bash
# 处理前 30 页
uv run python run_pipeline.py \
  --pdf ../mvp/pdf/t4012-24e.pdf \
  --provider glm-api \
  --max-pages 30
```

### 分阶段运行（高级用法）

如需单独运行各阶段（调试或断点续传）：

```bash
# Stage 1: PDF 提取
uv run python stage1_extract_pdf.py --pdf ../mvp/pdf/rc4022-24e.pdf --full

# Stage 2: 内容分类（需要指定 provider）
uv run python stage2_classify_content.py --extraction-id <ID> --provider glm-api

# Stage 3: 内容分块
uv run python stage3_chunk_content.py --extraction-id <ID>

# Stage 4: AI 增强（需要指定 provider）
uv run python stage4_enhance_chunks.py --chunks-id <ID> --provider glm-api

# Stage 5: 生成 Skill
uv run python stage5_generate_skill.py --enhanced-id <ID>
```

---

## 命令行参数速查

### run_pipeline.py 参数

#### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--pdf PATH` | PDF 文件路径 | `--pdf file.pdf` |
| `--provider NAME` | LLM provider | `--provider glm-api` |

#### 页面控制

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--full` | 处理完整文档 | 否（仅前 10 页） |
| `--max-pages N` | 最大处理页数 | 10 |

#### LLM Provider 选择

| Provider | 说明 | 环境要求 |
|----------|------|----------|
| `glm-api` | 智谱 GLM-4 API（推荐） | GLM_API_KEY |
| `claude` | Claude Code CLI | claude login |
| `gemini` | Gemini CLI | gemini login |
| `codex` | Codex CLI | codex login |

#### 处理选项

| 参数 | 说明 |
|------|------|
| `--skip-enhance` | 跳过 Stage 4（AI 增强），快速测试 |
| `--workers N` | 并行 worker 数（1-8，默认 1） |

#### 缓存控制

| 参数 | 说明 |
|------|------|
| `--force` | 强制重新处理所有阶段（忽略缓存） |
| `--cache-dir DIR` | 自定义缓存目录 |
| `--output-dir DIR` | Skill 输出目录（默认 skills_output） |

---

## 输出目录结构

成功运行后，输出目录结构如下：

```
skills_output/
└── employment-income-t4012/          # Skill 目录
    ├── SKILL.md                      # 主索引文件
    ├── references/                   # 增强后的参考文档
    │   ├── index.md                  # 参考文档索引
    │   ├── chunk-001-chapter-1.md    # 章节内容
    │   ├── chunk-002-chapter-2.md
    │   └── ...
    └── raw/                          # 原始提取内容
        └── full-extract.txt          # 完整提取文本
```

### 文件说明

| 文件 | 说明 |
|------|------|
| `SKILL.md` | Skill 主入口，包含使用说明和目录 |
| `references/index.md` | 所有参考文档的导航索引 |
| `references/chunk-*.md` | AI 增强后的章节内容 |
| `raw/full-extract.txt` | PDF 原始提取文本 |

---

## 处理时间参考

### 不同配置的处理时间

| 配置 | 页数 | Stage 1-3 | Stage 4 | 总时间 |
|------|------|-----------|---------|--------|
| `--glm-api` | 10 | ~30s | ~5min | ~6min |
| `--glm-api --full` | 151 | ~2min | ~3h | ~3h |
| `--glm-api --full --workers 4` | 151 | ~2min | ~1h | ~1h |
| `--local-gemini --full` | 151 | ~2min | ~2h | ~2h |

### 缓存加速效果

**首次运行**: 完整执行所有阶段

**后续运行**: 自动跳过已缓存阶段
- Stage 1-3 通常可跳过（~2 分钟节省）
- Stage 4 支持断点续传

---

## 断点续传

Pipeline 支持中断后自动恢复：

```bash
# 首次运行（处理到一半中断）
uv run python run_pipeline.py --pdf file.pdf --provider glm-api --full
# Ctrl+C 中断

# 继续处理（自动从断点恢复）
uv run python run_pipeline.py --pdf file.pdf --provider glm-api --full
# 自动检测缓存并从上次中断处继续
```

**查看当前进度**:
```bash
cat backend/cache/enhanced_chunks_*/progress.json | python -m json.tool
```

**手动恢复 Stage 4**:
```bash
# 使用 --resume 从断点继续
uv run python stage4_enhance_chunks.py --chunks-id <ID> --resume

# 重试失败的 chunks
uv run python stage4_enhance_chunks.py --chunks-id <ID> --retry-failed
```

---

## 常见安装问题

### Python 版本过低

**症状**: `Python 3.11+ required`

**解决方案**:
```bash
# macOS (使用 pyenv)
brew install pyenv
pyenv install 3.12
pyenv local 3.12

# 或使用 uv 管理 Python
uv python install 3.12
```

### 缺少 PDF 处理依赖

**症状**: `ModuleNotFoundError: No module named 'fitz'`

**解决方案**:
```bash
# 确保在虚拟环境中
source .venv/bin/activate
uv sync
```

### GLM API Key 未配置

**症状**: `GLM_API_KEY environment variable is required`

**解决方案**:
```bash
# 方法 1: 设置环境变量
export GLM_API_KEY=your_api_key

# 方法 2: 写入 .env 文件
echo "GLM_API_KEY=your_api_key" >> .env
```

### CLI 工具找不到

**症状**: `Provider 'xxx' not available`

**解决方案**:
```bash
# 检查 PATH
which claude  # 或 gemini, codex

# 如果未找到，确认安装并重新加载 shell
source ~/.bashrc  # 或 ~/.zshrc
```

---

## 下一步

安装完成后，建议：

1. **了解系统架构**: 阅读 [Pipeline 架构](../architecture/PIPELINE_ARCHITECTURE.md)
2. **选择 LLM Provider**: 参考 [LLM Provider 系统](../architecture/LLM_PROVIDERS.md)
3. **问题排查**: 查看 [故障排查](TROUBLESHOOTING.md)
4. **管理缓存**: 了解 [缓存管理](CACHE_MANAGEMENT.md)

---

## 验证清单

使用此清单确认安装完成：

- [ ] Python 3.11+ 已安装
- [ ] uv 包管理器已安装
- [ ] 系统依赖已安装（poppler, mupdf-tools）
- [ ] 后端依赖已安装（`uv sync` 成功）
- [ ] 至少一个 LLM Provider 可用（推荐 GLM_API_KEY）
- [ ] 快速测试通过：
  ```bash
  uv run python run_pipeline.py \
    --pdf ../mvp/pdf/rc4022-24e.pdf \
    --provider glm-api \
    --skip-enhance
  ```

---

**版本**: 3.0
**更新**: 2025-12-09
