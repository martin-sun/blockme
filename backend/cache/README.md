# Cache Directory

This directory stores intermediate results from the multi-stage PDF processing pipeline.

## Purpose

The cache enables:
- **Faster re-processing**: Skip completed stages when re-running
- **Resumability**: Continue from where you left off after interruption
- **Debugging**: Inspect intermediate results at each stage
- **Failure recovery**: Retry only failed chunks without re-processing everything

## Structure

```
cache/
├── extraction_<pdf-hash>.json          # Stage 1: PDF text extraction
├── classification_<pdf-hash>.json      # Stage 2: Content classification
├── chunks_<pdf-hash>.json              # Stage 3: Content chunking
└── enhanced_chunks_<pdf-hash>/         # Stage 4: AI-enhanced chunks
    ├── progress.json                    # Enhancement progress tracking
    ├── chunk-001.json                   # Enhanced chunk 1
    ├── chunk-002.json                   # Enhanced chunk 2
    └── ...                              # More chunks
```

## File Formats

### extraction_<hash>.json
```json
{
  "stage": "extraction",
  "content_hash": "abc123...",
  "timestamp": "2025-11-04T10:00:00",
  "metadata": {
    "pdf_path": "../mvp/pdf/t4012-24e.pdf",
    "total_pages": 151
  },
  "data": {
    "pdf_path": "../mvp/pdf/t4012-24e.pdf",
    "pdf_hash": "abc123...",
    "total_pages": 151,
    "total_text": "...",
    "pages": [...],
    "extraction_time": "2025-11-04T10:00:00"
  }
}
```

### classification_<hash>.json
```json
{
  "stage": "classification",
  "content_hash": "abc123...",
  "timestamp": "2025-11-04T10:02:00",
  "data": {
    "primary_category": "employment_income",
    "confidence": 0.85,
    "secondary_categories": [...],
    "quality_metrics": {...},
    "matched_keywords": [...]
  }
}
```

### chunks_<hash>.json
```json
{
  "stage": "chunking",
  "content_hash": "abc123...",
  "timestamp": "2025-11-04T10:02:10",
  "data": {
    "total_chunks": 83,
    "chunks": [
      {
        "chunk_id": 1,
        "chapter_num": 1,
        "title": "Chapter 1: Page 1 of T2 return",
        "slug": "chapter-1-page-1-of-t2-return",
        "content": "...",
        "char_count": 8500
      },
      ...
    ],
    "chunking_strategy": "chapter_detection"
  }
}
```

### enhanced_chunks_<hash>/progress.json
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

### enhanced_chunks_<hash>/chunk-001.json
```json
{
  "chunk_id": 1,
  "original_title": "Chapter 1: Page 1 of T2 return",
  "slug": "chapter-1-page-1-of-t2-return",
  "enhanced_content": "# Chapter 1: Page 1 of T2 return\n\n...",
  "enhancement_time": "2025-11-04T10:10:00",
  "provider": "codex",
  "status": "completed",
  "token_count": 75000
}
```

## Hash Calculation

The `<pdf-hash>` is calculated as the first 16 characters of the SHA256 hash of:
- For extraction: The PDF file content
- For subsequent stages: The extraction JSON content

This ensures:
- Same PDF = same hash = reuse cache
- Different content = different hash = separate cache
- Cache invalidation when PDF changes

## Cache Management

### List cached PDFs
```bash
# Python API
from app.document_processor.pipeline_manager import CacheManager
cache_mgr = CacheManager()
pdfs = cache_mgr.list_cached_pdfs()
```

### Clean old caches
```bash
# Delete caches older than 7 days
cache_mgr.clean_cache(older_than_days=7)

# Delete specific hash
cache_mgr.clean_cache(content_hash="abc123")
```

### Check cache status
```bash
# Check which stages are cached
from app.document_processor.pipeline_manager import PipelineManager
pipeline = PipelineManager()
status = pipeline.get_stage_status(content_hash="abc123")
# Returns: {PipelineStage.EXTRACTION: True, ...}
```

## .gitignore

This directory is excluded from git via `.gitignore`:
```
backend/cache/
!backend/cache/README.md
```

Cache files are local artifacts and should not be committed.

## Disk Space

Typical cache sizes:
- extraction_*.json: ~500 KB - 2 MB (depends on PDF size)
- classification_*.json: ~5-50 KB
- chunks_*.json: ~500 KB - 2 MB
- enhanced_chunks_*/: ~5-20 MB (83 chunks × ~60-240 KB each)

**Total per PDF**: ~10-25 MB

For a 151-page PDF:
- Extraction: ~1.5 MB
- Classification: ~10 KB
- Chunks: ~1.5 MB
- Enhanced chunks: ~15 MB (83 chunks)
- **Total: ~18 MB**

## Best Practices

1. **Keep cache during development**: Speeds up iteration
2. **Clean periodically**: Remove old caches to free disk space
3. **Backup before major changes**: Copy cache if testing risky changes
4. **Don't edit manually**: Cache files are machine-generated
5. **Check progress.json**: Monitor enhancement progress

## Troubleshooting

### Cache not detected
- Check file permissions
- Verify hash calculation matches
- Look for corrupted JSON files

### Enhancement not resuming
- Check `progress.json` exists
- Verify chunk files are not corrupted
- Try with `--force` to restart

### Disk space issues
- Clean old caches: `cache_mgr.clean_cache(older_than_days=7)`
- Check largest directories: `du -sh cache/*`
- Remove specific failed runs manually

## Related Files

- `app/document_processor/pipeline_manager.py`: Cache management logic
- `stage1_extract_pdf.py` through `stage5_generate_skill.py`: Use cache
- `generate_skill.py`: Orchestrates pipeline with caching
