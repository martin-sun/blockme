# Multi-Stage Pipeline Architecture

**BeanFlow-CRA Skill 生成系统技术架构文档**

深入了解 6 阶段流水线的设计理念、实现细节和最佳实践。

---

## 📐 架构概述

### 设计理念

**从单体到模块化**

```
传统单体架构:
PDF → [800+ 行黑盒脚本] → Skill 输出
❌ 中断 = 全部重来
❌ 难以调试
❌ 无法复用

多阶段 Pipeline:
PDF → Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5 → Stage 6
      ↓ cache   ↓ cache   ↓ cache   ↓ cache   ↓ output
✅ 每阶段独立运行
✅ 结果可复用
✅ 断点续传
✅ 易于调试和优化
```

### 核心原则

1. **单一职责**: 每个 Stage 只做一件事
2. **缓存优先**: 所有中间结果持久化
3. **可恢复性**: 失败后可从断点继续
4. **可观测性**: 清晰的进度和日志
5. **解耦设计**: Stage 之间松耦合

---

## 🔬 Stage 详解

### Stage 1: PDF 文本提取

**脚本**: `stage1_extract_pdf.py`
**模块**: `app/document_processor/pdf_extractor.py`

#### 核心功能

```python
class PDFTextExtractor:
    """PDF 文本提取器"""

    def extract(self, pdf_path: Path) -> ExtractionResult:
        """
        提取 PDF 文本内容

        Returns:
            ExtractionResult:
                - total_text: 完整文本
                - pages: 分页结果
                - metadata: PDF 元数据
        """
```

#### 技术细节

**PDF 库**: PyMuPDF (fitz)
- ✅ 高性能（C++ 实现）
- ✅ 精确的文本提取
- ✅ 保留布局信息

**分页提取**:
```python
for page_num in range(total_pages):
    page = doc[page_num]
    text = page.get_text("text")

    # 保存每页元数据
    page_result = PageResult(
        page_number=page_num + 1,
        text=text,
        char_count=len(text),
        line_count=text.count('\n')
    )
```

**页数限制**:
- 默认: 前 10 页（快速测试）
- `--full`: 所有页面
- `--max-pages N`: 自定义页数

#### 缓存策略

**Hash 计算**:
```python
def hash_file(file_path: Path) -> str:
    """SHA256 hash 的前 16 位"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]
```

**缓存键**: `extraction_{pdf_hash}.json`

**缓存失效条件**:
1. PDF 文件内容改变（hash 不同）
2. `--max-pages` 参数改变
3. 使用 `--force` 强制重新提取

#### 性能指标

| PDF 大小 | 页数 | 提取时间 | 缓存大小 |
|---------|------|---------|---------|
| 870 KB | 151 | 30秒 - 2分钟 | ~1.5 MB |
| 200 KB | 30 | 10-20秒 | ~400 KB |
| 2 MB | 300 | 1-3分钟 | ~3 MB |

---

### Stage 2: 内容分类

**脚本**: `stage2_classify_content.py`
**模块**: `app/document_processor/content_classifier.py`

#### 智能多信号分类算法

**5 个评分维度**:

1. **关键词覆盖** (Keyword Coverage)
   ```python
   # 计算匹配的关键词数量
   matched_keywords = [kw for kw in category_keywords if kw in content]
   score = len(matched_keywords) / len(category_keywords)
   ```

2. **结构质量** (Structure Quality)
   ```python
   # 检测文档结构特征
   has_headings = bool(re.search(r'^#{1,3}\s+', content, re.M))
   has_lists = bool(re.search(r'^\s*[-*]\s+', content, re.M))
   has_sections = detect_chapters(content) > 0
   score = (has_headings + has_lists + has_sections) / 3
   ```

3. **内容深度** (Content Depth)
   ```python
   # 评估内容深度
   char_count = len(content)
   paragraph_count = content.count('\n\n')
   avg_paragraph_length = char_count / max(paragraph_count, 1)
   score = min(avg_paragraph_length / 500, 1.0)
   ```

4. **特异性分数** (Specificity Score)
   ```python
   # 检测特定术语
   specific_terms = ['T4', 'T2', 'RRSP', 'Line 150', etc.]
   found_terms = [t for t in specific_terms if t in content]
   score = len(found_terms) / len(specific_terms)
   ```

5. **完整性分数** (Completeness Score)
   ```python
   # 评估文档完整性
   has_intro = 'introduction' in content.lower()
   has_examples = 'example' in content.lower()
   has_references = 'reference' in content.lower()
   score = (has_intro + has_examples + has_references) / 3
   ```

**最终分类**:
```python
# 加权平均
final_score = (
    keyword_coverage * 0.4 +
    structure_quality * 0.2 +
    content_depth * 0.15 +
    specificity_score * 0.15 +
    completeness_score * 0.1
)
```

#### 分类类别

```python
class TaxCategory(str, Enum):
    PERSONAL_INCOME = "personal_income"
    EMPLOYMENT_INCOME = "employment_income"
    SELF_EMPLOYMENT = "self_employment"
    BUSINESS_INCOME = "business_income"
    CAPITAL_GAINS = "capital_gains"
    DEDUCTIONS = "deductions"
    CREDITS = "credits"
    RRSP = "rrsp"
    TFSA = "tfsa"
    GST_HST = "gst_hst"
    # ... 更多类别
```

#### 性能

- **时间**: < 5 秒（纯规则匹配，无 LLM 调用）
- **准确率**: ~85-90%（基于关键词和结构）

---

### Stage 3: 内容分块

**脚本**: `stage3_chunk_content.py`

#### 智能章节检测

**3 种检测方法**（优先级递减）:

1. **Markdown 标题** (confidence: 1.0)
   ```python
   # 检测 # 和 ## 标题
   pattern = r'^(#{1,2})\s+(.+)$'
   ```

2. **模式匹配** (confidence: 0.9)
   ```python
   patterns = [
       r'^Chapter\s+(\d+)[:\-\s](.+)$',
       r'^Part\s+(\d+)[:\-\s](.+)$',
       r'^Section\s+(\d+(?:\.\d+)?)[:\-\s](.+)$',
       r'^(\d+)\.\s+([A-Z][^\n]{5,50})$',  # "1. Introduction"
   ]
   ```

3. **全大写标题** (confidence: 0.7)
   ```python
   # 检测 INTRODUCTION, OVERVIEW 等
   pattern = r'^([A-Z][A-Z\s]{5,50})$'
   # 过滤 false positives: PDF, CRA, GST, etc.
   ```

#### 分块策略

**目标**: 每个 chunk ≤ 300K 字符（Claude 限制）

**算法**:
```python
def split_by_chapters(content: str, max_chunk_size: int):
    chapters = detect_chapters(content)

    for chapter in chapters:
        chapter_content = extract_chapter(chapter)

        if len(chapter_content) > max_chunk_size:
            # 章节过大，进一步分割
            sub_chunks = split_by_paragraphs(chapter_content)
            for sub in sub_chunks:
                yield ChunkResult(...)
        else:
            yield ChunkResult(...)
```

**段落级分割**:
```python
def split_by_paragraphs(content: str, max_size: int):
    paragraphs = content.split('\n\n')

    current_chunk = ""
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) <= max_size:
            current_chunk += paragraph + "\n\n"
        else:
            yield current_chunk
            current_chunk = paragraph + "\n\n"
```

#### Chunk 元数据

```python
class ChunkResult:
    chunk_id: int           # 1-indexed
    title: str              # "Chapter 1: ..."
    slug: str               # "chapter-1-..."
    content: str            # 章节内容
    char_count: int         # 字符数
    chapter_num: int        # 章节编号
```

#### 典型输出

**151 页 PDF**:
- 总字符数: 721K
- Chunk 数量: 83
- 平均大小: ~8,700 chars/chunk
- 最大 chunk: ~295K chars

---

### Stage 4: AI 增强 ⭐

**脚本**: `stage4_enhance_chunks.py`
**最复杂的阶段** - 耗时最长，支持断点续传

#### 架构设计

**核心思想**: 渐进式处理 + 立即保存

```python
for chunk_id in chunks_to_process:
    # 1. 增强单个 chunk
    enhanced = enhance_single_chunk(chunk, provider)

    # 2. 立即保存（关键！）
    pipeline.save_enhanced_chunk(content_hash, chunk_id, enhanced)

    # 3. 更新进度
    progress['completed_chunks'] = chunk_id
    pipeline.save_enhancement_progress(content_hash, progress)

    # 4. 计算 ETA
    eta = calculate_eta(completed, remaining, avg_time)
```

#### 断点续传实现

**进度文件** `cache/enhanced_chunks_{hash}/progress.json`:

```json
{
  "total_chunks": 83,
  "completed_chunks": 40,
  "failed_chunks": [15, 23],
  "start_time": "2025-11-04T10:05:00",
  "last_update": "2025-11-04T13:30:00",
  "estimated_remaining": "180 minutes",
  "provider": "codex"
}
```

**续传逻辑**:
```python
if args.resume:
    progress = load_progress(content_hash)
    completed = progress['completed_chunks']

    # 从下一个 chunk 开始
    chunks_to_process = range(completed + 1, total_chunks + 1)

    print(f"Resuming from chunk {completed + 1}")
```

**失败重试**:
```python
if args.retry_failed:
    progress = load_progress(content_hash)
    failed_chunks = progress['failed_chunks']

    # 只处理失败的 chunks
    chunks_to_process = failed_chunks
```

#### LLM Provider 抽象

**支持多个 LLM**:

```python
class LLMCLIProvider(ABC):
    @abstractmethod
    def build_command(self, prompt: str) -> List[str]:
        """构建 CLI 命令"""

    @abstractmethod
    def parse_output(self, stdout: str, stderr: str) -> str:
        """解析 LLM 输出"""

    @abstractmethod
    def get_timeout(self, content_length: int) -> int:
        """计算超时时间"""
```

**实现**:
- `ClaudeCLIProvider`: Claude Code CLI
- `GeminiCLIProvider`: Gemini CLI
- `CodexCLIProvider`: OpenAI Codex

#### Prompt 设计

```python
prompt = f"""Please optimize this CRA tax content for the '{category}' category.

Requirements:
1. Keep all factual information accurate and complete
2. Add practical examples where appropriate
3. Improve clarity and structure
4. Use professional Canadian tax terminology
5. Format as clean Markdown with proper headers (##, ###)
6. Make it actionable for developers building tax applications

IMPORTANT: Output ONLY the enhanced Markdown content, nothing else.

Content to enhance:
{chunk}

Enhanced content (Markdown only):"""
```

#### 超时策略

**动态超时**:
```python
def get_timeout(content_length: int) -> int:
    MIN_TIMEOUT = 240  # 4 分钟基础
    TIMEOUT_PER_1K_CHARS = 5  # 每 1K 字符 +5 秒

    return max(MIN_TIMEOUT, content_length // 1000 * TIMEOUT_PER_1K_CHARS)
```

**示例**:
- 10K chars → 240秒 (4分钟)
- 100K chars → 500秒 (8.3分钟)
- 300K chars → 1500秒 (25分钟)

#### 错误处理

```python
try:
    enhanced = enhance_single_chunk(...)
    save_chunk(enhanced)
    progress['completed_chunks'] += 1

except subprocess.TimeoutExpired:
    logger.error(f"Chunk {id} timeout")
    progress['failed_chunks'].append(id)

except Exception as e:
    logger.error(f"Chunk {id} failed: {e}")
    progress['failed_chunks'].append(id)

finally:
    save_progress(progress)
```

#### 性能优化

**1. 并行处理** (未实现，规划中):
```python
# 使用 asyncio 并行处理多个 chunks
async def enhance_chunks_parallel(chunks, max_concurrent=4):
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [enhance_chunk_async(c, semaphore) for c in chunks]
    return await asyncio.gather(*tasks)
```

**2. 批量处理** (未实现，规划中):
```python
# 将多个小 chunks 合并成一个请求
def batch_small_chunks(chunks, max_size=300_000):
    batch = []
    current_size = 0

    for chunk in chunks:
        if current_size + len(chunk) <= max_size:
            batch.append(chunk)
            current_size += len(chunk)
        else:
            yield batch
            batch = [chunk]
            current_size = len(chunk)
```

---

### Stage 5: Skill 生成

**脚本**: `stage5_generate_skill.py`
**模块**: `app/document_processor/skill_generator.py`

#### 目录结构生成

```python
def save_skill_directory(
    skill_id: str,
    raw_text: str,
    reference_chunks: List[dict],
    metadata: SkillMetadata
) -> Path:
    """
    生成 Skill 目录结构

    skill_id/
    ├── SKILL.md               # 索引文件
    ├── references/
    │   ├── index.md           # 导航索引
    │   ├── chunk-1-slug.md    # 增强内容
    │   ├── chunk-2-slug.md
    │   └── ...
    └── raw/
        └── full-extract.txt   # 原始文本
    """
```

#### SKILL.md 基础版本

**生成逻辑**:
```python
def _create_skill_index(
    path: Path,
    metadata: SkillMetadata,
    reference_files: List[dict],
    raw_text_size: int
):
    content = f"""---
id: {metadata.id}
title: {metadata.title}
tags: {metadata.tags}
description: {metadata.description}
category: {metadata.category}
---

# {metadata.title}

## 📖 When to Use This Skill

{generate_use_cases(metadata.category)}

## 📚 Reference Documentation

{generate_toc(reference_files)}

## 📊 Document Statistics

- Total chapters: {len(reference_files)}
- Raw text size: {raw_text_size:,} chars
- Category: {metadata.category}
    """
```

**质量**: 3/10（基础版本）

---

### Stage 6: SKILL.md 增强（可选）

**脚本**: `enhance_skill.py`
**模块**: `app/document_processor/skill_enhancer.py`

详见 [SKILL_ENHANCEMENT.md](SKILL_ENHANCEMENT.md)

**提升**: 3/10 → 9/10

---

## 💾 缓存系统详解

### Cache Manager

**核心类**: `app/document_processor/pipeline_manager.py`

```python
class CacheManager:
    """缓存管理器"""

    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path("backend/cache")

    def hash_file(self, file_path: Path) -> str:
        """计算文件 SHA256 hash（前16位）"""

    def save_cache(self, stage: PipelineStage, hash: str, data: dict):
        """保存缓存"""

    def load_cache(self, stage: PipelineStage, hash: str) -> Optional[dict]:
        """加载缓存"""

    def cache_exists(self, stage: PipelineStage, hash: str) -> bool:
        """检查缓存是否存在"""
```

### 缓存键设计

**统一 Hash**: 所有 stage 使用相同的 PDF hash 作为标识

```
PDF → hash: abc123

cache/
├── extraction_abc123.json
├── classification_abc123.json
├── chunks_abc123.json
└── enhanced_chunks_abc123/
```

**优势**:
- ✅ 同一 PDF 的所有 stages 关联
- ✅ 易于批量清理
- ✅ 自动失效（PDF 改变 → 新 hash）

### 缓存格式

**标准格式**:
```json
{
  "stage": "extraction",
  "content_hash": "abc123",
  "timestamp": "2025-11-04T10:00:00",
  "metadata": {
    "pdf_path": "../mvp/pdf/t4012-24e.pdf",
    "total_pages": 151
  },
  "data": {
    // Stage-specific data
  }
}
```

### 缓存管理

**清理策略**:
```python
# 按时间清理
cache_mgr.clean_cache(older_than_days=7)

# 按 hash 清理
cache_mgr.clean_cache(content_hash="abc123")
```

**查看缓存**:
```python
# 列出所有缓存的 PDFs
pdfs = cache_mgr.list_cached_pdfs()
for pdf in pdfs:
    print(f"{pdf['content_hash']}: {pdf['pdf_path']}")
```

---

## 🔄 Pipeline Manager

### 编排逻辑

**核心类**: `PipelineManager`

```python
class PipelineManager:
    """Pipeline 编排器"""

    def get_stage_status(self, content_hash: str) -> Dict[PipelineStage, bool]:
        """获取所有 stage 的完成状态"""

    def get_enhancement_progress(self, content_hash: str) -> Optional[dict]:
        """获取 enhancement 进度"""

    def save_enhancement_progress(self, content_hash: str, progress: dict):
        """保存 enhancement 进度"""

    def load_enhanced_chunks(self, content_hash: str) -> List[dict]:
        """加载所有增强后的 chunks"""
```

### Stage 依赖关系

```
Stage 1: PDF Extraction
  ↓ (needs: PDF file)

Stage 2: Content Classification
  ↓ (needs: extraction_<hash>.json)

Stage 3: Content Chunking
  ↓ (needs: extraction_<hash>.json)

Stage 4: AI Enhancement
  ↓ (needs: chunks_<hash>.json + classification_<hash>.json)

Stage 5: Skill Generation
  ↓ (needs: enhanced_chunks_<hash>/ + classification_<hash>.json)

Stage 6: SKILL.md Enhancement
  (needs: skill directory)
```

### 统一入口

**`generate_skill.py`**: Pipeline 编排器

```python
def main():
    # 1. 计算 PDF hash
    pdf_hash = cache_mgr.hash_file(args.pdf)

    # 2. 检查缓存状态
    status = pipeline.get_stage_status(pdf_hash)

    # 3. 依次运行各 stage（跳过已缓存）
    run_stage_script('stage1_extract_pdf.py', ...)
    run_stage_script('stage2_classify_content.py', ...)
    run_stage_script('stage3_chunk_content.py', ...)
    run_stage_script('stage4_enhance_chunks.py', ...)
    run_stage_script('stage5_generate_skill.py', ...)

    # 4. 可选: 增强 SKILL.md
    if args.enhance_skill:
        run_stage_script('enhance_skill.py', ...)
```

---

## 📊 性能分析

### 瓶颈识别

**Stage 4 占 99%+ 时间**:

```
Stage 1-3: < 3 分钟 (< 1%)
Stage 4:   415-664 分钟 (>99%)
Stage 5-6: < 10 分钟 (< 1%)
```

### 优化方向

**1. 并行化** (最有效):
- 4 个并发 → 理论加速 4x
- 实际: 100-150 分钟（151页）

**2. 更大的 Chunk**:
- Gemini: 1.5M tokens → 17 chunks (vs 83)
- 加速: ~5x

**3. 更快的 LLM**:
- Gemini 2.0 Flash: 响应更快
- 但可能牺牲质量

**4. 批量请求**:
- 将多个小 chunks 合并成一个请求
- 减少请求数

---

## 🐛 调试指南

### 日志分析

**Stage 输出格式**:
```
============================================================
Stage N: [Description]
============================================================
[Progress information]
[Status updates]
✅ Success / ❌ Failed
```

### 常见问题定位

**1. 查看缓存状态**:
```bash
ls -lh backend/cache/
cat backend/cache/extraction_*.json | jq .
```

**2. 查看进度**:
```bash
cat backend/cache/enhanced_chunks_*/progress.json | jq .
```

**3. 检查失败 chunk**:
```bash
jq '.failed_chunks' backend/cache/enhanced_chunks_*/progress.json
```

**4. 重新运行特定 stage**:
```bash
# 强制重新提取
uv run python stage1_extract_pdf.py --pdf FILE.pdf --force

# 重试失败的 chunks
uv run python stage4_enhance_chunks.py --chunks-id abc123 --retry-failed
```

---

## 🎯 最佳实践

### 开发迭代

**1. 快速测试**:
```bash
# 只处理 10 页
uv run python generate_skill.py --pdf FILE.pdf --glm-api
```

**2. 调试 Pipeline**:
```bash
# 手动运行各 stage，观察输出
uv run python stage1_extract_pdf.py --pdf FILE.pdf
uv run python stage2_classify_content.py --extraction-id abc123
```

**3. 测试 AI 增强**:
```bash
# 只处理 30 页，减少等待时间
uv run python generate_skill.py --pdf FILE.pdf --max-pages 30 --local-codex
```

### 生产部署

**1. 批量处理**:
```bash
for pdf in pdfs/*.pdf; do
    uv run python generate_skill.py --pdf "$pdf" --local-codex --full
done
```

**2. 监控进度**:
```bash
# 定期检查进度
watch -n 60 'cat backend/cache/enhanced_chunks_*/progress.json | jq .'
```

**3. 定期清理缓存**:
```bash
# 每周清理
python -c "from app.document_processor.pipeline_manager import CacheManager; \
           CacheManager().clean_cache(older_than_days=7)"
```

---

## 📚 相关文档

- **[Backend README](../README.md)** - 快速开始指南
- **[SKILL Enhancement](SKILL_ENHANCEMENT.md)** - SKILL.md 增强功能
- **[Cache README](../cache/README.md)** - 缓存格式说明

---

**作者**: BeanFlow Team
**版本**: 2.0
**更新**: 2025-11-04
