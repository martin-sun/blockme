# 缓存管理

BeanFlow-CRA 使用文件缓存加速重复处理。本文档详细说明缓存机制、管理方法和最佳实践。

---

## 缓存机制概述

### 设计目标

| 目标 | 说明 |
|------|------|
| **加速重处理** | 跳过已完成阶段，重新运行时节省时间 |
| **断点续传** | 中断后可从上次位置继续 |
| **调试支持** | 检查各阶段中间结果 |
| **故障恢复** | 仅重试失败部分，无需全部重来 |

### 工作原理

```
PDF 文件 → SHA256 Hash（前 16 位）→ 作为缓存键

运行时流程:
1. 计算 PDF 文件 hash
2. 检查各阶段缓存是否存在
3. 跳过已缓存阶段，执行未完成阶段
4. 保存新结果到缓存
```

### Hash 计算方式

系统使用 PDF 文件内容的 SHA256 哈希（前 16 位）作为唯一标识：

```python
def hash_file(file_path: Path) -> str:
    """计算文件 SHA256 hash（前16位）"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]
```

**特性**:
- 同一 PDF 文件 → 相同 hash → 复用缓存
- PDF 内容变化 → 新 hash → 新缓存
- 自动缓存失效机制

---

## 缓存目录结构

### 目录位置

默认缓存目录: `backend/cache/`

可通过 `--cache-dir` 参数自定义：
```bash
uv run python generate_skill.py --pdf file.pdf --cache-dir /custom/cache
```

### 文件结构

```
backend/cache/
├── README.md                           # 缓存说明文档
├── extraction_<pdf-hash>.json          # Stage 1: PDF 提取结果
├── classification_<pdf-hash>.json      # Stage 2: 分类结果
├── chunks_<pdf-hash>.json              # Stage 3: 分块结果
└── enhanced_chunks_<pdf-hash>/         # Stage 4: AI 增强结果
    ├── progress.json                   # 进度追踪
    ├── chunk-001.json                  # 增强后的 chunk 1
    ├── chunk-002.json                  # 增强后的 chunk 2
    └── ...                             # 更多 chunks
```

---

## 缓存文件格式详解

### Stage 1: extraction_&lt;hash&gt;.json

PDF 文本提取结果：

```json
{
  "stage": "extraction",
  "content_hash": "abc123def456789",
  "timestamp": "2025-11-04T10:00:00",
  "metadata": {
    "pdf_path": "../mvp/pdf/t4012-24e.pdf",
    "total_pages": 151
  },
  "data": {
    "pdf_path": "../mvp/pdf/t4012-24e.pdf",
    "pdf_hash": "abc123def456789",
    "total_pages": 151,
    "total_text": "完整提取文本...",
    "pages": [
      {
        "page_number": 1,
        "text": "第1页文本...",
        "char_count": 3500,
        "line_count": 85
      }
    ],
    "extraction_time": "2025-11-04T10:00:00"
  }
}
```

| 字段 | 说明 |
|------|------|
| `stage` | 阶段标识 |
| `content_hash` | PDF 文件 hash |
| `timestamp` | 创建时间 |
| `metadata.total_pages` | 总页数 |
| `data.total_text` | 完整提取文本 |
| `data.pages` | 分页提取结果 |

---

### Stage 2: classification_&lt;hash&gt;.json

内容分类结果：

```json
{
  "stage": "classification",
  "content_hash": "abc123def456789",
  "timestamp": "2025-11-04T10:02:00",
  "data": {
    "primary_category": "employment_income",
    "confidence": 0.85,
    "secondary_categories": [
      {"category": "deductions", "confidence": 0.45},
      {"category": "credits", "confidence": 0.30}
    ],
    "quality_metrics": {
      "keyword_coverage": 0.78,
      "structure_quality": 0.82,
      "content_depth": 0.75,
      "specificity_score": 0.88,
      "completeness_score": 0.70
    },
    "matched_keywords": ["T4", "employment", "income", "withholding"]
  }
}
```

| 字段 | 说明 |
|------|------|
| `primary_category` | 主分类 |
| `confidence` | 置信度（0-1） |
| `secondary_categories` | 次要分类列表 |
| `quality_metrics` | 质量评分详情 |
| `matched_keywords` | 匹配的关键词 |

---

### Stage 3: chunks_&lt;hash&gt;.json

内容分块结果：

```json
{
  "stage": "chunking",
  "content_hash": "abc123def456789",
  "timestamp": "2025-11-04T10:02:10",
  "data": {
    "total_chunks": 83,
    "chunks": [
      {
        "chunk_id": 1,
        "chapter_num": 1,
        "title": "Chapter 1: Page 1 of T2 return",
        "slug": "chapter-1-page-1-of-t2-return",
        "content": "章节内容...",
        "char_count": 8500
      }
    ],
    "chunking_strategy": "chapter_detection",
    "avg_chunk_size": 8693,
    "max_chunk_size": 295000,
    "min_chunk_size": 1200
  }
}
```

| 字段 | 说明 |
|------|------|
| `total_chunks` | 总 chunk 数量 |
| `chunks` | chunk 列表 |
| `chunking_strategy` | 分块策略 |
| `avg_chunk_size` | 平均 chunk 大小 |

---

### Stage 4: enhanced_chunks_&lt;hash&gt;/

#### progress.json - 进度追踪

```json
{
  "total_chunks": 83,
  "completed_chunks": 40,
  "failed_chunks": [15, 23],
  "start_time": "2025-11-04T10:05:00",
  "last_update": "2025-11-04T13:30:00",
  "estimated_remaining": "180 minutes",
  "provider": "glm-api",
  "avg_processing_time": 4.5
}
```

| 字段 | 说明 |
|------|------|
| `total_chunks` | 总 chunk 数 |
| `completed_chunks` | 已完成数 |
| `failed_chunks` | 失败的 chunk ID 列表 |
| `provider` | 使用的 LLM Provider |
| `avg_processing_time` | 平均处理时间（分钟/chunk） |

#### chunk-XXX.json - 增强后的 chunk

```json
{
  "chunk_id": 1,
  "original_title": "Chapter 1: Page 1 of T2 return",
  "slug": "chapter-1-page-1-of-t2-return",
  "enhanced_content": "# Chapter 1: Page 1 of T2 return\n\n增强后的内容...",
  "enhancement_time": "2025-11-04T10:10:00",
  "provider": "glm-api",
  "status": "completed",
  "token_count": 75000,
  "processing_duration": 245
}
```

| 字段 | 说明 |
|------|------|
| `enhanced_content` | 增强后的 Markdown 内容 |
| `status` | 状态: completed/failed |
| `token_count` | 输出 token 数 |
| `processing_duration` | 处理耗时（秒） |

---

## 缓存文件大小参考

### 单 PDF 缓存大小

| 文件类型 | 典型大小 | 说明 |
|----------|----------|------|
| `extraction_*.json` | 500 KB - 2 MB | 取决于 PDF 页数和文本量 |
| `classification_*.json` | 5 - 50 KB | 分类结果较小 |
| `chunks_*.json` | 500 KB - 2 MB | 与 extraction 相近 |
| `enhanced_chunks_*/` | 5 - 20 MB | 每个 chunk 60-240 KB |

### 实际案例（151 页 PDF）

| 文件 | 大小 |
|------|------|
| extraction_xxx.json | ~1.5 MB |
| classification_xxx.json | ~10 KB |
| chunks_xxx.json | ~1.5 MB |
| enhanced_chunks_xxx/ | ~15 MB (83 chunks) |
| **总计** | **~18 MB** |

### 估算公式

```
单 PDF 缓存 ≈ (页数 × 10 KB) + (chunk数 × 180 KB)

例如 151 页 PDF:
= (151 × 10 KB) + (83 × 180 KB)
= 1.5 MB + 15 MB
≈ 16.5 MB
```

---

## 缓存管理命令

### 查看缓存状态

```bash
# 查看缓存目录大小
du -sh backend/cache/

# 查看各文件大小
du -sh backend/cache/*

# 列出所有缓存的 PDF hash
ls backend/cache/extraction_*.json | sed 's/.*extraction_\(.*\)\.json/\1/'

# 查看特定 hash 的所有缓存
ls -la backend/cache/*abc123*
```

### 查看处理进度

```bash
# 查看 Stage 4 进度
cat backend/cache/enhanced_chunks_*/progress.json | python -m json.tool

# 查看已完成的 chunks
ls backend/cache/enhanced_chunks_*/chunk-*.json | wc -l

# 查看失败的 chunks
jq '.failed_chunks' backend/cache/enhanced_chunks_*/progress.json
```

### 清理缓存

#### 方法 1: 命令行清理

```bash
# 删除所有缓存（保留 README）
rm -rf backend/cache/*
git checkout backend/cache/README.md

# 删除特定 hash 的缓存
rm backend/cache/*_abc123*
rm -rf backend/cache/enhanced_chunks_abc123/

# 删除 7 天前的缓存
find backend/cache -name "*.json" -mtime +7 -delete
find backend/cache -type d -name "enhanced_chunks_*" -mtime +7 -exec rm -rf {} \;

# 只删除 Stage 4 缓存（保留 Stage 1-3）
rm -rf backend/cache/enhanced_chunks_*/
```

#### 方法 2: Python API 清理

```python
from app.document_processor.pipeline_manager import CacheManager

cache_mgr = CacheManager()

# 清理 7 天前的缓存
cache_mgr.clean_cache(older_than_days=7)

# 清理特定 hash 的缓存
cache_mgr.clean_cache(content_hash="abc123def456789")

# 列出所有缓存的 PDFs
pdfs = cache_mgr.list_cached_pdfs()
for pdf in pdfs:
    print(f"{pdf['content_hash']}: {pdf['pdf_path']}")
```

### 强制重新处理

```bash
# 强制重新处理所有阶段
uv run python generate_skill.py --pdf file.pdf --glm-api --force

# 只强制重新提取（Stage 1）
uv run python generate_skill.py --pdf file.pdf --glm-api --force-extract

# 重试失败的 chunks（Stage 4）
uv run python stage4_enhance_chunks.py --chunks-id <hash> --retry-failed --provider glm-api
```

---

## 断点续传机制

### 工作原理

Stage 4 支持中断后自动恢复：

```
首次运行:
Chunk 1 → 完成 → 保存
Chunk 2 → 完成 → 保存
Chunk 3 → 完成 → 保存
[Ctrl+C 中断]

再次运行:
读取 progress.json → completed_chunks=3
从 Chunk 4 继续 → ...
```

### 使用方法

```bash
# 首次运行
uv run python generate_skill.py --pdf file.pdf --glm-api --full
# 按 Ctrl+C 中断

# 恢复运行（自动检测并续传）
uv run python generate_skill.py --pdf file.pdf --glm-api --full
# 输出: 💡 Detected incomplete enhancement (40/83 chunks)
#       Will resume from chunk 41
```

### 手动控制

```bash
# 明确指定续传
uv run python stage4_enhance_chunks.py --chunks-id <hash> --resume --provider glm-api

# 从头开始（删除进度后重新处理）
rm backend/cache/enhanced_chunks_<hash>/progress.json
uv run python stage4_enhance_chunks.py --chunks-id <hash> --provider glm-api
```

---

## 缓存失效条件

### 自动失效

| 条件 | 影响阶段 | 说明 |
|------|---------|------|
| PDF 内容变化 | 所有阶段 | 新 hash，全部重新处理 |
| `--max-pages` 改变 | Stage 1+ | 提取页数不同，需重新处理 |
| `--force` 参数 | 所有阶段 | 强制忽略缓存 |
| `--force-extract` 参数 | Stage 1+ | 强制重新提取 |

### 手动失效

```bash
# 删除特定阶段缓存，触发重新处理
rm backend/cache/classification_<hash>.json  # 重新分类
rm backend/cache/chunks_<hash>.json          # 重新分块
rm -rf backend/cache/enhanced_chunks_<hash>/ # 重新增强
```

---

## 最佳实践

### 开发期间

1. **保留缓存**: 加速迭代，避免重复处理
2. **善用 `--no-ai`**: 测试 Stage 1-3 时跳过耗时的 Stage 4
3. **使用小页数测试**: `--max-pages 10` 快速验证

```bash
# 开发测试命令
uv run python generate_skill.py --pdf file.pdf --no-ai --max-pages 10
```

### 生产环境

1. **定期清理**: 避免磁盘空间耗尽
2. **监控大小**: 设置告警阈值
3. **备份重要缓存**: 长时间处理的结果

```bash
# 定期清理脚本（可加入 cron）
#!/bin/bash
# 清理 7 天前的缓存
find /path/to/backend/cache -name "*.json" -mtime +7 -delete
find /path/to/backend/cache -type d -name "enhanced_chunks_*" -mtime +7 -exec rm -rf {} \;

# 发送告警（如磁盘使用超过 80%）
USAGE=$(du -s /path/to/backend/cache | cut -f1)
if [ $USAGE -gt 10000000 ]; then  # 10GB
    echo "Cache size warning: ${USAGE}KB"
fi
```

### 批量处理

```bash
# 批量处理多个 PDF
for pdf in pdfs/*.pdf; do
    echo "Processing: $pdf"
    uv run python generate_skill.py --pdf "$pdf" --glm-api --full
done

# 监控总缓存大小
watch -n 60 'du -sh backend/cache/'
```

---

## 注意事项

### 不要手动编辑缓存

缓存文件由系统自动生成和管理。手动编辑可能导致：
- 数据不一致
- 处理失败
- 无法断点续传

### 缓存不纳入版本控制

`.gitignore` 已配置排除缓存目录：

```gitignore
backend/cache/
!backend/cache/README.md
```

### 跨机器缓存

缓存文件可以跨机器复制使用（如果 PDF 文件相同），但需注意：
- 确保 `pdf_path` 在目标机器有效
- Stage 4 使用的 Provider 需一致

---

## 相关文档

- [Pipeline 架构](../architecture/PIPELINE_ARCHITECTURE.md) - 详细的缓存设计说明
- [故障排查](TROUBLESHOOTING.md) - 缓存相关问题解决
- [backend/cache/README.md](../../backend/cache/README.md) - 缓存目录说明

---

**版本**: 2.0
**更新**: 2025-12-08
