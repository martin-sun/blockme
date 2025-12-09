# 故障排查

常见问题和解决方案汇总。本文档按问题类型分类，提供详细的排查步骤和解决方案。

---

## 快速诊断

### 问题分类速查

| 症状 | 可能原因 | 跳转章节 |
|------|---------|---------|
| `Python 3.11+ required` | Python 版本过低 | [环境问题](#环境问题) |
| `ModuleNotFoundError` | 依赖未安装 | [环境问题](#环境问题) |
| `Provider 'xxx' not available` | CLI 未安装或不在 PATH | [Provider 问题](#provider-问题) |
| `GLM_API_KEY environment variable is required` | API Key 未配置 | [Provider 问题](#provider-问题) |
| `API call failed` | 网络或认证问题 | [Provider 问题](#provider-问题) |
| `Timeout expired` | LLM 响应超时 | [处理问题](#处理问题) |
| `Output too short` | LLM 返回无效内容 | [处理问题](#处理问题) |
| `Cache mismatch` | 缓存数据不一致 | [缓存问题](#缓存问题) |

---

## 环境问题

### Python 版本不兼容

**症状**:
```
Python 3.11+ required
```
或
```
SyntaxError: invalid syntax
```

**原因**: 系统 Python 版本低于 3.11

**排查步骤**:
```bash
# 检查当前 Python 版本
python --version
python3 --version

# 检查虚拟环境是否激活
which python
```

**解决方案**:

方法 1 - 使用 pyenv（推荐）:
```bash
# 安装 pyenv
brew install pyenv  # macOS
# 或
curl https://pyenv.run | bash  # Linux

# 安装 Python 3.12
pyenv install 3.12

# 设置项目使用版本
cd BeanFlow-CRA/backend
pyenv local 3.12

# 重新创建虚拟环境
rm -rf .venv
uv venv .venv
source .venv/bin/activate
uv sync
```

方法 2 - 使用 uv 管理 Python:
```bash
# uv 自动安装 Python
uv python install 3.12
uv venv .venv --python 3.12
source .venv/bin/activate
uv sync
```

---

### 缺少系统依赖

**症状**:
```
Error: Could not find 'pdfinfo'
```
或
```
mutool: command not found
```

**原因**: PDF 处理工具未安装

**解决方案**:

macOS:
```bash
brew install poppler mupdf-tools

# 验证安装
pdfinfo --version
mutool --version
```

Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils mupdf-tools
```

---

### 虚拟环境问题

**症状**:
```
ModuleNotFoundError: No module named 'fitz'
```
或
```
ModuleNotFoundError: No module named 'zhipuai'
```

**原因**: 虚拟环境未激活或依赖未安装

**排查步骤**:
```bash
# 检查是否在虚拟环境中
which python
# 应显示: .../BeanFlow-CRA/backend/.venv/bin/python

# 检查已安装的包
pip list | grep -E "(fitz|zhipuai|PyMuPDF)"
```

**解决方案**:
```bash
# 激活虚拟环境
cd backend
source .venv/bin/activate

# 重新安装依赖
uv sync

# 如果还有问题，重建虚拟环境
rm -rf .venv
uv venv .venv
source .venv/bin/activate
uv sync
```

---

### uv 命令找不到

**症状**:
```
uv: command not found
```

**解决方案**:
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 重新加载 shell 配置
source ~/.bashrc  # 或 ~/.zshrc

# 验证安装
uv --version
```

---

## Provider 问题

### CLI 工具未安装

**症状**:
```
Provider 'claude' not available
Provider 'gemini' not available
Provider 'codex' not available
```

**排查步骤**:
```bash
# 检查 CLI 是否在 PATH 中
which claude
which gemini
which codex

# 检查 PATH 变量
echo $PATH
```

**解决方案**:

Claude CLI:
```bash
npm install -g @anthropic-ai/claude-code
claude login
```

Gemini CLI:
```bash
npm install -g @google/gemini-cli
# 首次使用时自动认证
gemini -p "test"
```

Codex CLI:
```bash
# 从 GitHub 下载并安装
# https://github.com/openai/codex
codex login
```

---

### API Key 配置错误

**症状**:
```
GLM_API_KEY environment variable is required
```
或
```
GEMINI_API_KEY environment variable is required
```

**排查步骤**:
```bash
# 检查环境变量是否设置
echo $GLM_API_KEY
echo $GEMINI_API_KEY

# 检查 .env 文件
cat .env
```

**解决方案**:

方法 1 - 设置环境变量:
```bash
export GLM_API_KEY=your_api_key_here
export GEMINI_API_KEY=your_api_key_here
```

方法 2 - 写入 .env 文件:
```bash
# 创建或编辑 .env 文件
echo "GLM_API_KEY=your_api_key_here" >> .env
echo "GEMINI_API_KEY=your_api_key_here" >> .env
```

方法 3 - 加载 .env 文件（如使用 python-dotenv）:
```bash
# 在脚本开头添加
source .env
```

---

### API 调用失败

**症状**:
```
GLM API call failed: ...
Gemini API call failed: ...
```

**可能原因**:

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `401 Unauthorized` | API Key 无效 | 检查并更新 API Key |
| `429 Too Many Requests` | 请求频率超限 | 等待后重试或升级配额 |
| `500 Internal Server Error` | 服务端错误 | 稍后重试 |
| `Connection refused` | 网络问题 | 检查网络连接 |
| `Timeout` | 响应超时 | 增加超时设置或简化请求 |

**详细排查**:

1. **验证 API Key**:
```bash
# GLM API 测试
curl -X POST https://open.bigmodel.cn/api/coding/paas/v4/chat/completions \
  -H "Authorization: Bearer $GLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-4.6","messages":[{"role":"user","content":"Hello"}]}'
```

2. **检查网络连接**:
```bash
# 测试连接
ping open.bigmodel.cn
curl -I https://open.bigmodel.cn
```

3. **检查配额**:
- GLM: https://open.bigmodel.cn/usercenter/resourcepack
- Gemini: https://aistudio.google.com/app/apikey

---

### 响应截断问题

**症状**:
```
GLM API response was truncated due to token limit (finish_reason=length)
```

**原因**: 输入内容过长，导致输出被截断

**解决方案**:

1. **减小输入大小**:
```bash
# 使用更小的 chunk 大小
# 修改代码中的 max_chunk_size 设置
```

2. **调整 max_tokens 参数**:
```python
# 在 GLMAPIProvider 中修改
request_params["max_tokens"] = 16384  # 增加输出限制
```

3. **拆分文档**:
```bash
# 分批处理
uv run python generate_skill.py --pdf file.pdf --max-pages 50 --glm-api
```

---

## 处理问题

### PDF 提取失败

**症状**:
```
Error extracting PDF: ...
fitz.FileNotFoundError: ...
```

**排查步骤**:
```bash
# 验证 PDF 文件存在
ls -la path/to/file.pdf

# 验证 PDF 文件有效
pdfinfo path/to/file.pdf

# 检查文件权限
file path/to/file.pdf
```

**解决方案**:

1. **文件路径问题**:
```bash
# 使用绝对路径
uv run python generate_skill.py --pdf /absolute/path/to/file.pdf
```

2. **PDF 损坏**:
```bash
# 尝试修复 PDF
mutool clean input.pdf output.pdf
```

3. **加密 PDF**:
```bash
# 解密 PDF（如果有密码）
qpdf --decrypt input.pdf output.pdf
```

---

### AI 增强超时

**症状**:
```
Timeout expired for chunk X
subprocess.TimeoutExpired: Command ... timed out
```

**原因**: LLM 处理时间超过设定的超时时间

**解决方案**:

1. **使用断点续传**:
```bash
# 重新运行，自动从断点继续
uv run python generate_skill.py --pdf file.pdf --glm-api --full
```

2. **减少单次处理量**:
```bash
# 减少页数
uv run python generate_skill.py --pdf file.pdf --glm-api --max-pages 30
```

3. **选择更快的 Provider**:
```bash
# Gemini 通常更快
uv run python generate_skill.py --pdf file.pdf --local-gemini --full
```

4. **使用并行处理**:
```bash
# 多 worker 并行
uv run python generate_skill.py --pdf file.pdf --glm-api --full --workers 4
```

---

### 输出质量问题

**症状**:
```
Output too short: X chars
```
或生成的内容质量低

**可能原因**:
- LLM 返回错误信息
- Prompt 格式问题
- 网络中断

**排查步骤**:
```bash
# 查看失败的 chunk 详情
cat backend/cache/enhanced_chunks_*/chunk-*.json | python -m json.tool

# 检查 progress.json
cat backend/cache/enhanced_chunks_*/progress.json
```

**解决方案**:

1. **重试失败的 chunks**:
```bash
uv run python stage4_enhance_chunks.py \
  --chunks-id <hash> \
  --retry-failed \
  --provider glm-api
```

2. **强制重新处理**:
```bash
uv run python generate_skill.py --pdf file.pdf --glm-api --force
```

---

## 缓存问题

### 缓存不一致

**症状**:
```
Cache mismatch: expected X, got Y
```
或处理结果与预期不符

**排查步骤**:
```bash
# 查看缓存状态
ls -la backend/cache/

# 检查各阶段缓存
cat backend/cache/extraction_*.json | python -m json.tool | head -50
cat backend/cache/classification_*.json | python -m json.tool
cat backend/cache/chunks_*.json | python -m json.tool | head -50
```

**解决方案**:

1. **强制重新处理**:
```bash
uv run python generate_skill.py --pdf file.pdf --glm-api --force
```

2. **清理特定缓存**:
```bash
# 删除特定 PDF 的所有缓存
rm backend/cache/*_<hash>.*
rm -rf backend/cache/enhanced_chunks_<hash>/
```

3. **完全清理缓存**:
```bash
# 备份后清理
cp -r backend/cache backend/cache_backup
rm -rf backend/cache/*
# 保留 README
git checkout backend/cache/README.md
```

---

### 磁盘空间不足

**症状**:
```
OSError: [Errno 28] No space left on device
```

**排查步骤**:
```bash
# 检查磁盘使用
df -h

# 检查缓存大小
du -sh backend/cache/
du -sh backend/cache/*
```

**解决方案**:

1. **清理旧缓存**:
```bash
# 删除 7 天前的缓存
find backend/cache -name "*.json" -mtime +7 -delete
find backend/cache -type d -name "enhanced_chunks_*" -mtime +7 -exec rm -rf {} \;
```

2. **使用外部存储**:
```bash
# 指定外部缓存目录
uv run python generate_skill.py --pdf file.pdf --glm-api --cache-dir /external/cache
```

---

### 进度文件损坏

**症状**:
```
JSONDecodeError: ...
```
或断点续传失败

**排查步骤**:
```bash
# 检查 progress.json 是否有效
python -m json.tool backend/cache/enhanced_chunks_*/progress.json
```

**解决方案**:

1. **修复 progress.json**:
```bash
# 查看已完成的 chunks
ls backend/cache/enhanced_chunks_<hash>/chunk-*.json | wc -l

# 手动修复 progress.json
# 根据实际完成的 chunk 数量更新 completed_chunks 字段
```

2. **重新开始 Stage 4**:
```bash
# 删除进度文件，重新处理
rm backend/cache/enhanced_chunks_<hash>/progress.json
uv run python stage4_enhance_chunks.py --chunks-id <hash> --provider glm-api
```

---

## 调试技巧

### 查看详细日志

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
uv run python generate_skill.py --pdf file.pdf --glm-api

# 或在代码中设置
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 检查缓存状态

```bash
# 列出所有缓存文件
ls -la backend/cache/

# 查看特定阶段缓存
cat backend/cache/extraction_*.json | python -m json.tool | head -100
cat backend/cache/classification_*.json | python -m json.tool
cat backend/cache/chunks_*.json | python -m json.tool | head -100

# 查看增强进度
cat backend/cache/enhanced_chunks_*/progress.json | python -m json.tool
```

### 检查失败的 chunks

```bash
# 列出失败的 chunk IDs
jq '.failed_chunks' backend/cache/enhanced_chunks_*/progress.json

# 查看失败 chunk 的错误信息
for f in backend/cache/enhanced_chunks_*/chunk-*.json; do
  if jq -e '.status == "failed"' "$f" > /dev/null 2>&1; then
    echo "=== $f ==="
    jq '.error' "$f"
  fi
done
```

### 手动运行单个阶段

```bash
# Stage 1: PDF 提取
uv run python stage1_extract_pdf.py --pdf file.pdf

# Stage 2: 内容分类
uv run python stage2_classify_content.py --extraction-id <hash>

# Stage 3: 内容分块
uv run python stage3_chunk_content.py --extraction-id <hash>

# Stage 4: AI 增强
uv run python stage4_enhance_chunks.py --chunks-id <hash> --provider glm-api

# Stage 5: 生成 Skill
uv run python stage5_generate_skill.py --enhanced-id <hash>
```

---

## 错误信息对照表

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `Provider 'xxx' not available` | CLI 未安装或不在 PATH | 安装 CLI 并检查 PATH |
| `GLM_API_KEY environment variable is required` | API Key 未设置 | 设置环境变量或 .env 文件 |
| `API call failed: 401` | API Key 无效 | 检查并更新 API Key |
| `API call failed: 429` | 请求频率超限 | 等待后重试 |
| `Timeout expired` | LLM 响应超时 | 使用 `--resume` 续传或减少页数 |
| `Output too short` | LLM 返回无效内容 | 重试或更换 Provider |
| `Cache mismatch` | 缓存数据不一致 | 使用 `--force` 重新处理 |
| `finish_reason=length` | 响应被截断 | 减小输入或增加 max_tokens |
| `JSONDecodeError` | JSON 文件损坏 | 删除损坏文件重新处理 |
| `No space left on device` | 磁盘空间不足 | 清理缓存或使用外部存储 |

---

## 获取帮助

如果以上方案无法解决问题：

1. **查看详细日志**: 启用 DEBUG 级别日志
2. **检查最近变更**: 查看 [CHANGELOG](../CHANGELOG.md)
3. **理解系统架构**: 参考 [Pipeline 架构](../architecture/PIPELINE_ARCHITECTURE.md)
4. **检查 Provider 配置**: 参考 [LLM Provider 系统](../architecture/LLM_PROVIDERS.md)

---

**版本**: 2.0
**更新**: 2025-12-08
