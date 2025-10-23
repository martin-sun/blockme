# 任务16：文档处理功能测试

## 任务目标

编写全面的测试套件，验证文档处理流程的正确性和稳定性。测试涵盖 PDF/Office 转换、Vision API 提取、Markdown 优化、元数据管理等所有关键模块，确保系统在各种场景下正常工作。

## 技术要求

**测试框架：**
- pytest（主测试框架）
- pytest-asyncio（异步测试）
- pytest-cov（代码覆盖率）
- faker（测试数据生成）

**测试类型：**
- 单元测试（模块级）
- 集成测试（多模块协作）
- 端到端测试（完整流程）
- 性能测试（响应时间、资源使用）

**覆盖率目标：**
- 核心模块 > 80%
- 关键路径 100%
- 边界情况全覆盖

## 实现步骤

### 1. 创建测试目录结构

```bash
mkdir -p tests/{unit,integration,e2e,fixtures}
touch tests/conftest.py
touch tests/unit/test_pdf_converter.py
touch tests/unit/test_vision_api.py
touch tests/integration/test_full_pipeline.py
```

### 2. 准备测试数据

创建测试文档集：
- 简单 PDF（纯文本）
- 复杂 PDF（表格、图片）
- Word 文档
- Excel 表格
- 损坏文件（边界测试）

### 3. 编写单元测试

测试每个独立模块：
- PDF 转图像
- Vision API 调用
- Markdown 优化
- 元数据验证

### 4. 编写集成测试

测试模块间协作：
- 文档 → 图像 → Markdown 完整流程
- 知识库添加和检索
- Pipeline 端到端

### 5. 性能和压力测试

验证系统性能：
- 大文件处理
- 并发请求
- 内存泄漏检测

## 关键代码提示

**测试配置（conftest.py）：**

```python
import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录"""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def temp_dir():
    """临时目录（每个测试后自动清理）"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def sample_pdf(test_data_dir):
    """示例 PDF 文件"""
    return test_data_dir / "sample.pdf"

@pytest.fixture
def sample_markdown():
    """示例 Markdown 内容"""
    return """# 测试文档

## 第一章

这是一段测试内容。

| 列1 | 列2 |
|-----|-----|
| A   | B   |

```python
def test():
    pass
```
"""

@pytest.fixture
def mock_claude_response():
    """模拟 Claude API 响应"""
    return {
        "content": [
            {
                "text": "# 提取的标题\n\n这是提取的内容"
            }
        ],
        "usage": {
            "input_tokens": 100,
            "output_tokens": 50
        }
    }
```

**单元测试示例：**

```python
# tests/unit/test_pdf_converter.py

import pytest
from src.document_processor.pdf_converter import PDFToImageConverter

class TestPDFConverter:
    """PDF 转换器测试"""

    def test_convert_simple_pdf(self, sample_pdf, temp_dir):
        """测试转换简单 PDF"""
        converter = PDFToImageConverter()

        images = converter.convert_pdf(
            str(sample_pdf),
            output_dir=str(temp_dir)
        )

        # 验证生成了图像
        assert len(images) > 0
        assert all(Path(img).exists() for img in images)

        # 验证文件格式
        assert all(img.endswith('.jpg') for img in images)

    def test_convert_page_range(self, sample_pdf, temp_dir):
        """测试指定页面范围"""
        converter = PDFToImageConverter()

        images = converter.convert_pdf(
            str(sample_pdf),
            output_dir=str(temp_dir),
            page_range=(1, 2)  # 只转换前2页
        )

        assert len(images) == 2

    def test_image_size_limit(self, sample_pdf, temp_dir):
        """测试图像大小限制"""
        converter = PDFToImageConverter(max_image_size_mb=1.0)

        images = converter.convert_pdf(
            str(sample_pdf),
            output_dir=str(temp_dir)
        )

        # 验证所有图像小于 1MB
        for img_path in images:
            size_mb = Path(img_path).stat().st_size / (1024 * 1024)
            assert size_mb <= 1.0

    def test_invalid_pdf(self, temp_dir):
        """测试无效 PDF"""
        converter = PDFToImageConverter()

        with pytest.raises(FileNotFoundError):
            converter.convert_pdf("nonexistent.pdf", str(temp_dir))

    def test_pdf_info_extraction(self, sample_pdf):
        """测试 PDF 信息提取"""
        converter = PDFToImageConverter()
        info = converter.get_pdf_info(str(sample_pdf))

        assert "pages" in info
        assert info["pages"] > 0
        assert "file_size_mb" in info
```

```python
# tests/unit/test_markdown_optimizer.py

import pytest
from src.document_processor.markdown_optimizer import MarkdownOptimizer

class TestMarkdownOptimizer:
    """Markdown 优化器测试"""

    def test_clean_content(self):
        """测试内容清理"""
        optimizer = MarkdownOptimizer()

        dirty_md = """以下是提取的内容：

# 标题


---
---

内容"""

        cleaned = optimizer._clean_content(dirty_md)

        assert "以下是提取的内容" not in cleaned
        assert cleaned.count("---") == 1
        assert cleaned.count("\n\n\n") == 0

    def test_table_fixing(self):
        """测试表格修复"""
        optimizer = MarkdownOptimizer()

        broken_table = """
| 列1|列2 |
|---|---|
|A|B|
"""

        fixed = optimizer._fix_tables(broken_table)

        assert "| 列1 | 列2 |" in fixed
        assert "| A | B |" in fixed

    def test_metadata_generation(self, sample_markdown):
        """测试元数据生成"""
        optimizer = MarkdownOptimizer()

        metadata = optimizer._generate_metadata(
            sample_markdown,
            source_file="test.pdf",
            document_type="generic"
        )

        assert metadata["title"] == "测试文档"
        assert metadata["source"] == "test.pdf"
        assert "created_at" in metadata
        assert len(metadata["keywords"]) > 0

    def test_quality_validation(self):
        """测试质量验证"""
        optimizer = MarkdownOptimizer()

        # 高质量文档
        good_md = "# 标题\n\n## 章节\n\n" + "内容 " * 100
        quality = optimizer.validate_quality(good_md)
        assert quality["is_valid"] == True
        assert quality["score"] >= 80

        # 低质量文档
        bad_md = "short"
        quality = optimizer.validate_quality(bad_md)
        assert quality["is_valid"] == False
        assert len(quality["issues"]) > 0

    def test_full_optimization(self, sample_markdown):
        """测试完整优化流程"""
        optimizer = MarkdownOptimizer()

        optimized = optimizer.optimize(
            sample_markdown,
            source_file="test.pdf",
            document_type="generic"
        )

        # 验证包含 Front Matter
        assert optimized.startswith("---")
        assert "title:" in optimized

        # 验证包含目录
        assert "## 目录" in optimized or "第一章" in optimized
```

**集成测试示例：**

```python
# tests/integration/test_full_pipeline.py

import pytest
import asyncio
from src.document_processor.pdf_converter import PDFToImageConverter
from src.document_processor.claude_vision import ClaudeVisionExtractor
from src.document_processor.markdown_optimizer import MarkdownOptimizer
from src.knowledge_manager.collection_manager import KnowledgeCollectionManager
from src.knowledge_manager.metadata_manager import MetadataManager

@pytest.mark.integration
class TestFullPipeline:
    """完整文档处理流程测试"""

    @pytest.mark.asyncio
    async def test_pdf_to_knowledge_base(
        self,
        sample_pdf,
        temp_dir,
        mock_claude_api_key
    ):
        """测试 PDF → 知识库完整流程"""

        # 1. PDF → 图像
        pdf_converter = PDFToImageConverter()
        images = pdf_converter.convert_pdf(
            str(sample_pdf),
            output_dir=str(temp_dir / "images")
        )
        assert len(images) > 0

        # 2. 图像 → Markdown（使用模拟 API）
        vision_extractor = ClaudeVisionExtractor(api_key=mock_claude_api_key)
        # 这里应该 mock API 调用
        raw_markdown = "# 测试文档\n\n内容..."

        # 3. Markdown 优化
        optimizer = MarkdownOptimizer()
        optimized_md = optimizer.optimize(
            raw_markdown,
            source_file="sample.pdf",
            document_type="generic"
        )
        assert "title:" in optimized_md

        # 4. 添加到知识库
        collection_manager = KnowledgeCollectionManager(
            base_dir=str(temp_dir / "knowledge_base")
        )
        collection = collection_manager.create_collection(
            name="测试集合",
            description="测试",
            domain="general"
        )

        from src.knowledge_manager.metadata_manager import DocumentMetadataSchema
        metadata = DocumentMetadataSchema(
            id="test_001",
            title="测试文档",
            source_file="sample.pdf",
            collection_id=collection.id,
            domain="general"
        )

        doc_id = collection_manager.add_document(
            collection.id,
            optimized_md,
            metadata
        )

        assert doc_id is not None

        # 5. 验证可以检索
        docs = collection_manager.search_documents(query="测试")
        assert len(docs) > 0

    @pytest.mark.integration
    def test_concurrent_processing(self, temp_dir):
        """测试并发文档处理"""
        from concurrent.futures import ThreadPoolExecutor

        converter = PDFToImageConverter()

        # 模拟多个文档同时处理
        pdf_files = ["file1.pdf", "file2.pdf", "file3.pdf"]

        def process_pdf(pdf_file):
            # 这里应该实际处理
            return f"processed_{pdf_file}"

        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(process_pdf, pdf_files))

        assert len(results) == 3
```

**性能测试：**

```python
# tests/performance/test_performance.py

import pytest
import time
from src.skill_engine import SkillEngine
import os

@pytest.mark.performance
class TestPerformance:
    """性能测试"""

    def test_skill_routing_speed(self):
        """测试 Skill 路由速度"""
        engine = SkillEngine(
            skills_dir="knowledge_base/skills",
            claude_api_key=os.getenv("CLAUDE_API_KEY"),
            glm_api_key=os.getenv("GLM_API_KEY")
        )

        queries = [
            "Python 编程基础",
            "机器学习算法",
            "数据分析方法"
        ]

        durations = []
        for query in queries:
            start = time.time()
            routing_result = engine.skill_router.route(query)
            duration = time.time() - start
            durations.append(duration)

        avg_duration = sum(durations) / len(durations)

        print(f"平均路由时间: {avg_duration*1000:.2f} ms")
        # Haiku 4.5 路由通常 1-2秒，缓存命中 <10ms
        assert avg_duration < 3.0

    def test_memory_usage(self):
        """测试内存使用"""
        import tracemalloc

        tracemalloc.start()

        # 处理大量文档
        converter = PDFToImageConverter()
        # ... 处理逻辑

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / 1024 / 1024
        print(f"峰值内存: {peak_mb:.2f} MB")
        assert peak_mb < 2048  # 应小于 2GB
```

**运行测试：**

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/unit/test_pdf_converter.py -v

# 运行并生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 运行性能测试
pytest tests/performance/ -v -m performance

# 并行运行测试（加速）
pytest tests/ -n auto
```

## 测试验证

### 1. 覆盖率检查

```bash
pytest --cov=src --cov-report=term-missing
```

目标：核心模块 > 80% 覆盖率

### 2. 边界测试

- 空文件
- 超大文件（100+ 页）
- 损坏文件
- 特殊字符文件名

### 3. 异常测试

- API 失败
- 网络超时
- 磁盘空间不足
- 权限问题

## 注意事项

**测试数据管理：**
- 使用 fixtures 复用测试数据
- 不要提交大文件到 Git
- 使用 Git LFS 管理测试文档

**Mock 外部依赖：**
- Mock Claude/GLM API 调用
- Mock 文件系统操作
- 使用 pytest-mock

**CI/CD 集成：**
- GitHub Actions 自动运行测试
- 合并前强制通过测试
- 覆盖率报告自动生成

**测试隔离：**
- 每个测试独立运行
- 清理临时文件
- 避免测试间相互影响

## 依赖关系

**前置任务：**
- 所有开发任务（01-15）

**后置任务：**
- 任务17：成本优化策略
- 任务18：用户界面优化
