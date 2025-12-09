# SKILL.md Enhancement Feature

**BeanFlow-CRA Skill 增强功能设计文档**

将基础 SKILL.md（质量 3/10）提升到 Skill_Seekers 标准（质量 9/10）。

---

## 📋 概述

### 问题：当前 SKILL.md 质量不足

**当前输出**（基础版本）:
- **长度**: ~70 行
- **质量**: 3/10
- **内容**:
  - 简单的 YAML 元数据
  - 泛泛的使用场景
  - 章节链接列表

**问题**:
- Description 过于简短
- "When to Use" 太泛泛，缺少具体指导
- 无实际示例和计算公式
- 缺少快速参考信息
- 无关键概念解释

### 目标：Skill_Seekers 质量标准

**期望输出**（增强版本）:
- **长度**: 500+ 行
- **质量**: 9/10
- **内容**:
  - 详细的 description (100-200 字)
  - 具体的使用场景（带税表引用）
  - 5-10 个真实税务计算示例
  - 快速参考部分
  - 关键税务概念解释
  - 重要截止日期
  - 多层次用户导航指南

---

## 🏗️ 技术方案

### 架构设计

**独立脚本 + 可选集成**

```
Pipeline Stage 6 (可选):
  ├── enhance_skill.py          # 独立 CLI 脚本
  └── app/document_processor/
      ├── skill_enhancer.py     # 核心增强逻辑
      └── enhancement_prompts.py # Prompt 模板
```

**优势**:
- ✅ 可独立运行，增强已有 skills
- ✅ 可集成到 `generate_skill.py` 作为 Stage 6
- ✅ 与 Pipeline 解耦，易于维护

### 工作流程

```
1. 读取当前 SKILL.md
2. 读取 references/*.md (最多 50K chars)
3. 构建增强 prompt
4. 调用 LLM CLI
5. 验证输出（保留 YAML、长度检查）
6. 自动备份 + 保存
```

---

## 📝 核心组件

### 1. Skill Enhancer (skill_enhancer.py)

**关键配置**:
```python
MAX_REFERENCE_CHARS = 50_000   # 所有 references 总量
MAX_CHARS_PER_FILE = 15_000    # 单个文件限制
```

**主要功能**:
- `read_references()`: 读取并截断 reference 文件
- `enhance_skill()`: 调用 LLM 增强
- `validate_enhanced_skill()`: 验证输出质量

### 2. Enhancement Prompts (enhancement_prompts.py)

**Prompt 模板结构**:

```python
SKILL_ENHANCEMENT_PROMPT = """
You are enhancing a Claude Skill's SKILL.md file...

CRITICAL REQUIREMENTS:
1. YAML front matter 必须保留完整不变
2. 生成 500+ 行高质量内容
3. 包含 5-10 个具体示例
4. 添加快速参考部分

OUTPUT FORMAT:
---
[保留原 YAML]
---

# [Skill Title]

[增强后的详细内容]
...
"""
```

**关键部分**:
- YAML 保留指令（避免 LLM 修改元数据）
- 输出格式约束（Markdown 结构）
- 示例要求（具体税务计算）
- 快速参考模板

### 3. CLI 脚本 (enhance_skill.py)

**命令行接口**:

```bash
# 增强单个 skill
uv run python enhance_skill.py \
  --skill-dir skills_output/employment-income-t4012-24e \
  --provider codex

# 批量增强
for dir in skills_output/*/; do
  uv run python enhance_skill.py --skill-dir "$dir" --provider codex
done
```

**功能**:
- 自动备份原 SKILL.md → SKILL.md.backup
- 进度显示（读取 references、LLM 调用）
- 错误处理（失败时保留原文件）

---

## 🔧 集成到 Pipeline

### generate_skill.py 集成

在 Stage 6 添加可选增强步骤：

```python
# Stage 6: SKILL.md Enhancement (optional, --enhance-skill flag)
if args.enhance_skill and provider_name:
    success = run_stage_script(
        'enhance_skill.py',
        ['--skill-dir', str(skill_dir), '--provider', provider_name],
        'Stage 6: SKILL.md Enhancement'
    )
```

**使用方式**:
```bash
# 自动增强 SKILL.md
uv run python generate_skill.py \
  --pdf ../mvp/pdf/t4012-24e.pdf \
  --local-codex \
  --enhance-skill  # 添加此参数
```

---

## 📊 Prompt 设计原则

### 基于 Skill_Seekers 最佳实践

**1. 明确输出格式约束**
```
OUTPUT FORMAT:
- YAML front matter 必须保留
- Markdown 标题层级规范
- 代码块使用正确语法高亮
```

**2. 提供具体示例要求**
```
Include 5-10 CONCRETE examples:
- Real tax calculations with numbers
- Actual CRA form references (T4, T2, etc.)
- Step-by-step calculation walkthroughs
```

**3. 快速参考模板**
```
## Quick Reference

### Key Limits and Rates
- [Tax rate/limit name]: $X,XXX (2024)
- [Deadline]: [Date description]

### Important Forms
- **[Form Code]**: [Purpose] - [When to use]
```

**4. 防止 YAML 修改**
```
CRITICAL: Preserve the YAML front matter EXACTLY as provided.
DO NOT change any metadata fields.
```

---

## 💡 使用场景

### 场景 1: 独立增强已有 skill

```bash
# 对已生成的 skill 进行增强
cd backend
uv run python enhance_skill.py \
  --skill-dir skills_output/employment-income-t4012-24e \
  --provider codex
```

**适用于**:
- ✅ 已有的 skill 需要升级
- ✅ 测试不同 prompt 模板
- ✅ 对比不同 LLM provider 效果

### 场景 2: 生成时自动增强

```bash
# 在 Pipeline 中自动增强
uv run python generate_skill.py \
  --pdf ../mvp/pdf/t4012-24e.pdf \
  --local-codex \
  --enhance-skill  # Stage 6 自动运行
```

**适用于**:
- ✅ 一次性生成高质量 skill
- ✅ 生产环境批量处理

### 场景 3: 批量增强多个 skills

```bash
# 批量处理脚本
for skill_dir in skills_output/*/; do
  echo "Enhancing: $skill_dir"
  uv run python enhance_skill.py \
    --skill-dir "$skill_dir" \
    --provider codex
done
```

**适用于**:
- ✅ 升级所有旧 skills
- ✅ 测试新 prompt 模板的效果

---

## 🎯 质量标准

### 增强前 vs 增强后对比

| 维度 | 增强前 (3/10) | 增强后 (9/10) |
|------|--------------|--------------|
| **长度** | ~70 行 | 500+ 行 |
| **Description** | 1-2 句话 | 100-200 字详细说明 |
| **使用场景** | 泛泛列表 | 具体场景 + 税表引用 |
| **示例** | 无 | 5-10 个真实计算示例 |
| **快速参考** | 无 | 关键限额、税率、截止日期 |
| **概念解释** | 无 | 重要税务术语解释 |
| **导航** | 简单链接 | 多层次目录 + 用户指南 |

### 验收标准

**必须满足**:
- ✅ YAML front matter 保持不变
- ✅ 文件长度 > 500 行
- ✅ 包含至少 5 个具体示例
- ✅ 有"Quick Reference"部分
- ✅ Markdown 格式正确（无 HTML artifacts）

**质量指标**:
- 📊 可读性：清晰的结构和章节
- 🎯 实用性：具体可执行的指导
- 📚 完整性：覆盖主要使用场景
- 🔍 可搜索：关键术语和表单编号

---

## ⚙️ 配置参数

### LLM Provider 配置

**Claude Sonnet 4.5** (推荐):
```python
model: "claude-sonnet-4-5-20250929"
max_input: 200K tokens
timeout: 300 seconds (5 minutes)
```

**Gemini 2.0 Flash**:
```python
model: "gemini-2.0-flash-exp"
max_input: 1M tokens
timeout: 300 seconds
```

**OpenAI Codex**:
```python
model: "o1-mini"
max_input: 128K tokens
timeout: 300 seconds
```

### Reference 读取配置

```python
# 从 skill_enhancer.py
MAX_REFERENCE_CHARS = 50_000    # 总量限制
MAX_CHARS_PER_FILE = 15_000     # 单文件限制

# 读取策略
truncate_strategy: "proportional"  # 按比例截断各文件
preserve_structure: True            # 保留 Markdown 结构
```

---

## 📈 性能估算

### 处理时间

| 阶段 | 时间 |
|------|------|
| 读取 references (50K chars) | < 1秒 |
| LLM 调用 (生成 500+ 行) | 3-5 分钟 |
| 验证 + 保存 | < 1秒 |
| **总计** | **3-5 分钟** |

### 成本估算（OpenAI Codex）

**输入**:
- Current SKILL.md: ~70 lines → ~200 tokens
- References: 50K chars → ~12,500 tokens
- Prompt: ~1,000 tokens
- **Total input**: ~13,700 tokens

**输出**:
- Enhanced SKILL.md: 500+ lines → ~2,000 tokens

**Cost**:
- o1-mini: $0.003/1K input + $0.012/1K output
- Total: ~$0.06 per skill

---

## 🔍 故障排查

### 常见问题

**1. YAML 被修改**

```bash
❌ Error: Enhanced skill has no YAML front matter
```

**原因**: LLM 未正确保留 YAML
**解决**: 增强 prompt 中的 YAML 保留指令

**2. 输出过短**

```bash
⚠️ Warning: Enhanced skill is only 200 lines (expected 500+)
```

**原因**: LLM 未生成足够内容
**解决**: 在 prompt 中明确要求 500+ 行输出

**3. Reference 文件过大**

```bash
⚠️ Truncating references from 80K to 50K chars
```

**原因**: References 超过 MAX_REFERENCE_CHARS
**解决**: 正常行为，会按比例截断各文件

**4. LLM 超时**

```bash
❌ Error: LLM call timed out after 300 seconds
```

**原因**: 内容过长或 LLM 响应慢
**解决**: 增加 timeout 参数

---

## 📚 相关文档

- **[Pipeline 架构](PIPELINE_ARCHITECTURE.md)** - 完整 Pipeline 设计
- **[Backend README](../README.md)** - 快速开始指南
- **[缓存格式](../cache/README.md)** - 缓存机制说明

---

## 📝 更新日志

**v2.0** (2025-11-04):
- ✅ 初始设计完成
- ✅ 集成到 Multi-Stage Pipeline
- ✅ 独立 CLI 脚本实现
- ✅ 支持多 LLM provider

**v1.0** (2025-10-30):
- ✅ 基于 Skill_Seekers 分析
- ✅ Prompt 模板设计
- ✅ 验证逻辑实现

---

**维护者**: BeanFlow Team
**版本**: 2.0
