# 任务04：安装 Python 依赖环境

## 任务目标

为 BlockMe 的文档处理、FastAPI 服务以及 `mvp/` CLI 链路搭建统一的 Python 开发环境，安装文档处理、AI API 调用、轻量知识管理等必需依赖。使用 `uv` 管理虚拟环境，确保后续各阶段共享同一依赖集合。

## 技术要求

**必需工具：**
- Python >= 3.10
- `uv` 包管理器（用户全局指令要求）
- Git（用于克隆示例代码）

**依赖类别：**
1. **文档处理**：pdf2image, PyMuPDF, python-docx
2. **AI API**：anthropic, zhipuai, openai
3. **Web 框架**：fastapi, pydantic
4. **工具库**：pillow, requests, python-dotenv, pyyaml
5. **可选依赖**：sentence-transformers（语义缓存用）

## 实现步骤

### 1. 安装 uv 包管理器

根据用户指令，使用 `uv` 管理所有 Python 项目：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 验证安装
uv --version
```

### 2. 初始化项目虚拟环境

在项目根目录创建 `.venv` 虚拟环境：

```bash
cd /Users/woohelps/CascadeProjects/blockme

# 使用 uv 创建虚拟环境
uv venv .venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
```

### 3. 创建 pyproject.toml

使用现代化的 `pyproject.toml` 管理依赖（推荐方式）：

```bash
uv init
```

编辑 `pyproject.toml`，定义项目依赖：

```toml
[project]
name = "blockme-knowledge-system"
version = "0.1.0"
description = "BlockMe 知识库系统"
requires-python = ">=3.10"

dependencies = [
    # AI API 客户端
    "anthropic>=0.40.0",
    "zhipuai>=2.1.0",
    "openai>=1.50.0",

    # 文档处理
    "pdf2image>=1.17.0",
    "PyMuPDF>=1.24.0",
    "python-docx>=1.1.0",
    "Pillow>=10.0.0",

    # Web 框架
    "fastapi>=0.115.0",
    "uvicorn>=0.30.0",
    "pydantic>=2.9.0",

    # 工具库
    "requests>=2.32.0",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "black>=24.0.0",
    "ruff>=0.6.0",
]

semantic-cache = [
    "sentence-transformers>=2.7.0",  # 用于语义缓存（任务17）
]
```

### 4. 安装依赖

使用 `uv` 快速安装所有依赖：

```bash
# 同步并安装所有依赖（推荐）
uv sync

# 安装开发依赖
uv sync --extra dev

# 安装语义缓存依赖（可选）
uv sync --extra semantic-cache

# 或使用传统方式
uv pip install -e ".[dev,semantic-cache]"
```

### 5. 系统级依赖（文档处理）

某些库需要系统级工具支持：

**macOS:**
```bash
# pdf2image 需要 poppler
brew install poppler

# PyMuPDF 需要 mupdf
brew install mupdf-tools

# Office 文档转换（可选）
brew install libreoffice
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils mupdf-tools libreoffice
```

### 6. 验证安装

创建测试脚本 `test_dependencies.py`：

```python
#!/usr/bin/env python3
"""验证所有依赖是否正确安装"""

def test_imports():
    print("测试依赖导入...")

    # AI API
    import anthropic
    import zhipuai
    import openai
    print("✓ AI API 客户端")

    # 文档处理
    import fitz  # PyMuPDF
    from pdf2image import convert_from_path
    from docx import Document
    from PIL import Image
    print("✓ 文档处理库")

    # Web 框架
    from fastapi import FastAPI
    from pydantic import BaseModel
    import yaml
    print("✓ Web 框架和工具库")

    # 可选：语义缓存
    try:
        from sentence_transformers import SentenceTransformer
        print("✓ 语义缓存库（可选）")
    except ImportError:
        print("⚠️  语义缓存库未安装（可选功能）")

    print("\n核心依赖安装成功！")

if __name__ == "__main__":
    test_imports()
```

运行测试：
```bash
python test_dependencies.py
```

## 关键代码提示

**uv 常用命令：**

```bash
# 添加新依赖
uv add package-name

# 更新依赖
uv sync --upgrade

# 查看已安装包
uv pip list

# 生成 requirements.txt（用于 Docker）
uv pip freeze > requirements.txt
```

**创建 .gitignore：**

```gitignore
# Python
.venv/
__pycache__/
*.pyc
*.pyo
*.egg-info/

# 环境配置
.env
.env.local

# IDE
.vscode/
.idea/

# 数据和缓存
data/
uploads/
*.db
```

**Docker 集成（可选）：**

如果需要在 Docker 中运行自定义 Pipeline：

```dockerfile
FROM python:3.12-slim

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    poppler-utils \
    mupdf-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制依赖配置
COPY pyproject.toml .

# 使用 uv 安装依赖
RUN uv venv && \
    uv pip install -r pyproject.toml

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 测试验证

### 1. 文档处理能力测试

```python
from pdf2image import convert_from_path
import fitz  # PyMuPDF

# 测试 PDF 转图像
images = convert_from_path("test.pdf", first_page=1, last_page=1)
print(f"✓ PDF 转图像成功：{len(images)} 页")

# 测试 PDF 文本提取
doc = fitz.open("test.pdf")
text = doc[0].get_text()
print(f"✓ PDF 文本提取成功：{len(text)} 字符")
```

### 2. AI API 连接测试

```python
import anthropic
from zhipuai import ZhipuAI
import os

# Claude API
claude_client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
response = claude_client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[{"role": "user", "content": "测试"}]
)
print(f"✓ Claude API 连接成功")

# GLM API
glm_client = ZhipuAI(api_key=os.getenv("GLM_API_KEY"))
response = glm_client.chat.completions.create(
    model="glm-4-flash",
    messages=[{"role": "user", "content": "测试"}]
)
print(f"✓ GLM API 连接成功")
```

### 3. Skill 索引测试

```python
import json
import yaml

# 测试 YAML 解析（Skill metadata）
skill_meta = """
title: "测试 Skill"
domain: "test"
topics: ["测试"]
"""

metadata = yaml.safe_load(skill_meta)
print(f"✓ YAML 解析成功：{metadata['title']}")

# 测试 JSON 索引
index = {
    "skill-1": {"title": "Test", "path": "/path/to/skill"}
}
json_str = json.dumps(index, ensure_ascii=False)
print(f"✓ JSON 序列化成功")
```

## 注意事项

**虚拟环境管理：**
1. 始终在 `.venv` 中安装依赖
2. 不要全局安装项目依赖
3. 团队成员使用相同的 `pyproject.toml`

**版本锁定：**
- 使用 `uv.lock` 锁定依赖版本
- 提交 `uv.lock` 到 Git 确保可复现
- 定期更新依赖解决安全漏洞

**性能优化：**
- `sentence-transformers`（可选）首次运行会下载模型（约 500MB）
- 使用国内镜像加速：
  ```bash
  export HF_ENDPOINT=https://hf-mirror.com
  ```
- Skill-like 方案不需要向量数据库，性能开销低

**常见问题：**

1. **pdf2image 报错 "poppler not found"**
   - 确保安装了 poppler：`brew install poppler`

2. **PyMuPDF 编译失败**
   - macOS 使用预编译版本：`uv pip install PyMuPDF-binary`

3. **uv sync 失败**
   - 检查 Python 版本：`python --version` (需要 >= 3.10)
   - 清除缓存：`uv cache clean`

**IDE 配置：**
确保 VS Code 使用正确的 Python 解释器：
1. Cmd+Shift+P → "Python: Select Interpreter"
2. 选择 `.venv/bin/python`

## 依赖关系

**前置任务：**
- 任务02：配置 Claude API（准备环境变量）
- 任务03：配置 GLM API（确保 SDK 密钥可用）

**后置任务：**
- 任务05：PDF 转图像模块开发
- 任务07：Claude Vision API 集成
- 任务08：GLM Vision API 集成
