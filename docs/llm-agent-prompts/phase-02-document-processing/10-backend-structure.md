# Backend 目录结构规划

## 目标

设计完整的 backend 目录结构，支持 CRA 文档处理、Skill 生成、API 服务和系统集成。

## 目录结构设计

```
backend/
├── pyproject.toml                    # 项目配置和依赖管理
├── .env                              # 环境变量配置
├── .env.example                      # 环境变量示例
├── README.md                         # 项目说明
├── pytest.ini                       # 测试配置
├── uv.lock                          # 依赖锁定文件
├── src/                             # 源代码目录
│   ├── __init__.py
│   ├── main.py                      # 主应用入口
│   ├── config.py                    # 配置管理
│   ├── api/                         # API 服务模块
│   │   ├── __init__.py
│   │   ├── app.py                   # FastAPI 应用实例
│   │   ├── routes/                  # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── skills.py            # Skills 相关 API
│   │   │   ├── documents.py         # 文档处理 API
│   │   │   └── health.py            # 健康检查 API
│   │   ├── models/                  # Pydantic 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── skill.py             # Skill 模型
│   │   │   ├── document.py          # 文档模型
│   │   │   └── response.py          # 响应模型
│   │   └── middleware/              # 中间件
│   │       ├── __init__.py
│   │       ├── cors.py              # CORS 处理
│   │       └── error_handler.py     # 错误处理
│   ├── document_processor/          # 文档处理模块
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py         # PDF 文本提取器
│   │   ├── content_classifier.py    # 内容分类器
│   │   ├── skill_generator.py       # Skill 生成器
│   │   ├── markdown_optimizer.py    # Markdown 优化器
│   │   └── utils.py                 # 工具函数
│   ├── skills/                      # 生成的 Skills 存储目录
│   │   ├── README.md                # Skills 目录说明
│   │   ├── cra-tax-guide-index.md   # 总索引
│   │   ├── business-*.md            # 商业收入相关
│   │   ├── capital-gains-*.md       # 资本收益相关
│   │   ├── rental-*.md              # 租金收入相关
│   │   ├── deductions-*.md          # 税务抵扣相关
│   │   ├── tax-credits-*.md         # 税收优惠相关
│   │   ├── rrsp-*.md                # RRSP 相关
│   │   └── gst-hst-*.md             # GST/HST 相关
│   ├── services/                    # 业务服务模块
│   │   ├── __init__.py
│   │   ├── skill_service.py         # Skill 管理服务
│   │   ├── document_service.py      # 文档处理服务
│   │   ├── classification_service.py # 分类服务
│   │   └── export_service.py        # 导出服务
│   ├── database/                    # 数据库相关
│   │   ├── __init__.py
│   │   ├── connection.py            # 数据库连接
│   │   ├── models.py                # 数据模型
│   │   └── migrations/              # 数据库迁移
│   │       └── __init__.py
│   └── utils/                       # 通用工具
│       ├── __init__.py
│       ├── logger.py                # 日志工具
│       ├── file_handler.py          # 文件处理工具
│       ├── text_processor.py        # 文本处理工具
│       └── validators.py            # 验证器
├── tests/                           # 测试目录
│   ├── __init__.py
│   ├── conftest.py                  # pytest 配置
│   ├── test_document_processor/     # 文档处理测试
│   │   ├── __init__.py
│   │   ├── test_pdf_extractor.py
│   │   ├── test_content_classifier.py
│   │   ├── test_skill_generator.py
│   │   └── test_markdown_optimizer.py
│   ├── test_api/                    # API 测试
│   │   ├── __init__.py
│   │   ├── test_skills_api.py
│   │   ├── test_documents_api.py
│   │   └── test_health_api.py
│   ├── test_services/               # 服务测试
│   │   ├── __init__.py
│   │   ├── test_skill_service.py
│   │   └── test_document_service.py
│   └── fixtures/                    # 测试数据
│       ├── sample_pdfs/             # 测试 PDF 文件
│       │   └── t4012_sample.pdf
│       ├── expected_skills/         # 期望的 Skill 输出
│       └── test_data/               # 其他测试数据
├── data/                            # 数据目录
│   ├── raw_documents/               # 原始文档存储
│   ├── processed_data/              # 处理后的数据
│   ├── exports/                     # 导出文件
│   └── logs/                        # 日志文件
├── scripts/                         # 脚本目录
│   ├── setup_dev.py                 # 开发环境设置
│   ├── process_cra_document.py      # CRA 文档处理脚本
│   ├── update_skills.py             # Skills 更新脚本
│   └── backup_data.py               # 数据备份脚本
└── docs/                            # 文档目录
    ├── api.md                       # API 文档
    ├── deployment.md                # 部署文档
    └── development.md               # 开发文档
```

## 核心模块说明

### 1. API 服务模块 (`src/api/`)

**职责：** 提供 RESTful API 接口

**主要文件：**
- `app.py`: FastAPI 应用配置
- `routes/skills.py`: Skills CRUD 操作
- `routes/documents.py`: 文档上传和处理
- `models/skill.py`: Skill 数据模型

### 2. 文档处理模块 (`src/document_processor/`)

**职责：** 实现 PDF 到 Skill 的完整处理流程

**核心功能：**
- PDF 文本提取（基于 Skill Seeker PyMuPDF）
- 智能内容分类
- Skill 文件生成
- Markdown 格式优化

### 3. Skills 存储目录 (`src/skills/`)

**职责：** 存储生成的 Markdown Skill 文件

**结构特点：**
- 兼容 MVP Skill 系统格式
- 按税务主题分类组织
- 包含完整的 YAML Front Matter

### 4. 业务服务模块 (`src/services/`)

**职责：** 封装业务逻辑，供 API 调用

**主要服务：**
- Skill 管理服务
- 文档处理服务
- 分类服务
- 导出服务

## 配置文件详细说明

### pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "blockme-backend"
version = "0.1.0"
description = "BlockMe CRA Document Processing Backend"
authors = [
    {name = "BlockMe Team", email = "team@blockme.ai"}
]
dependencies = [
    # FastAPI 核心依赖
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",

    # 文档处理依赖
    "PyMuPDF>=1.24.0",
    "Pillow>=11.0.0",
    "pytesseract>=0.3.13",

    # 分类和生成依赖
    "scikit-learn>=1.3.0",
    "nltk>=3.8.0",
    "jinja2>=3.1.0",
    "PyYAML>=6.0",

    # 工具依赖
    "python-multipart>=0.0.6",
    "httpx>=0.25.0",
    "python-dotenv>=1.0.0",
    "loguru>=0.7.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.7.0"
]
spaCy = [
    "spacy>=3.7.0"
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=html"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
multi_line_output = 3
```

### .env.example

```env
# API 配置
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# LLM API 配置
ANTHROPIC_API_KEY=sk-ant-...
ZHIPU_API_KEY=...

# 数据库配置
DATABASE_URL=sqlite:///./data/blockme.db

# 文档处理配置
UPLOAD_DIR=./data/raw_documents
EXPORT_DIR=./data/exports
SKILLS_DIR=./src/skills

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./data/logs/app.log

# 处理配置
MAX_FILE_SIZE=100MB
ALLOWED_PDF_TYPES=application/pdf
ENABLE_OCR=false
```

## API 设计

### Skills API

```python
# GET /api/skills - 获取所有 Skills
# GET /api/skills/{skill_id} - 获取特定 Skill
# POST /api/skills/search - 搜索 Skills
# POST /api/skills/{skill_id}/update - 更新 Skill
# DELETE /api/skills/{skill_id} - 删除 Skill
```

### Documents API

```python
# POST /api/documents/upload - 上传文档
# POST /api/documents/process - 处理文档
# GET /api/documents/{doc_id}/status - 获取处理状态
# GET /api/documents/{doc_id}/result - 获取处理结果
```

## 开发工作流

### 1. 环境设置

```bash
# 创建虚拟环境
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 安装依赖
uv sync

# 设置环境变量
cp .env.example .env
# 编辑 .env 文件
```

### 2. 开发模式启动

```bash
# 启动开发服务器
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# 或使用脚本
python scripts/setup_dev.py
```

### 3. 测试

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_document_processor/

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

## 部署架构

### 开发环境
- 单机部署
- SQLite 数据库
- 本地文件存储

### 生产环境
- Docker 容器化部署
- PostgreSQL 数据库
- 云存储（S3/MinIO）

### Docker 配置

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY src/ ./src/
COPY scripts/ ./scripts/

EXPOSE 8000

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 监控和日志

### 日志配置

```python
# src/utils/logger.py
from loguru import logger
import sys

def setup_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "data/logs/app.log",
        rotation="1 day",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
```

### 健康检查

```python
# src/api/routes/health.py
from fastapi import APIRouter
from src.utils.logger import logger

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }
```

## 性能优化

### 1. 异步处理

```python
# 大文件处理使用后台任务
from src.services.document_service import process_document_async

@router.post("/documents/process")
async def process_document_background(doc_id: str):
    # 异步处理文档
    task = process_document_async.delay(doc_id)
    return {"task_id": task.id, "status": "processing"}
```

### 2. 缓存策略

```python
# Skills 缓存
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_skill_cached(skill_id: str):
    return skill_service.get_skill(skill_id)
```

### 3. 数据库优化

```python
# 连接池配置
DATABASE_URL = "postgresql://user:pass@localhost/blockme?pool_size=20&max_overflow=30"
```

## 安全考虑

### 1. 文件上传安全

- 文件类型验证
- 文件大小限制
- 病毒扫描（可选）

### 2. API 安全

- 请求频率限制
- 输入验证
- CORS 配置

### 3. 数据保护

- 敏感信息加密
- 访问日志记录
- 数据备份策略

## 扩展性设计

### 1. 插件化架构

```python
# 支持自定义处理器
class DocumentProcessor:
    def __init__(self):
        self.processors = {
            'pdf': PDFProcessor(),
            'docx': DocxProcessor(),
            # 可扩展
        }
```

### 2. 微服务化准备

- 模块间松耦合设计
- API 版本控制
- 配置外部化

### 3. 多租户支持

- 数据隔离设计
- 配置隔离
- 资源配额管理

这个目录结构设计支持 CRA 文档处理的完整生命周期，从文档上传到 Skill 生成的所有环节，同时保持了良好的可扩展性和维护性。