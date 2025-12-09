# 更新日志 (CHANGELOG)

BeanFlow-CRA 项目的开发历史和版本变更记录。

---

## [Unreleased]

### 进行中
- FastAPI 问答服务（Part 2）开发
- 前端 SvelteKit 界面完善

---

## [2.0.0] - 2025-11-08

### Stage 4 系统性增强

#### 新增
- **内容质量监控**: 实时验证 enhanced_char_count vs original_char_count 比例
- **进度文件完整性验证**: 自动检测和修复 progress.json 问题
- **增强错误处理**: 失败时自动重试最多 2 次，使用指数退避
- **缓存一致性检查**: 检测 missing 和 orphaned chunks
- **详细调试日志**: 全程跟踪处理过程和性能指标

#### 改进
- 修改 prompt 要求 GLM 保持至少 70% 的原始内容长度
- 当压缩比例低于 60% 时发出警告日志
- 提供针对性的错误解决建议

---

## [1.5.0] - 2025-11-07

### 动态语义分类系统

#### 新增
- **动态分类器**: `app/document_processor/dynamic_classifier.py`
- **三阶段分析**: 深度语义分析 → 动态分类生成 → 验证优化
- **真实 LLM 集成**: 通过 GLM API provider 实现
- **数据模型**: DynamicCategory, SemanticTag, DynamicClassification, DocumentProfile

#### 改进
- Stage 5 集成 `--provider dynamic-semantic` 选项
- 元数据转换函数 `convert_dynamic_to_skill_metadata`
- 保持与现有 provider 选项的向后兼容性

### Provider 系统优化

#### 变更
- Stage 2 统一使用 GLM-4.6 进行分类
- 双 Provider 支持: `--local-claude` 和 `--glm-api`
- 直接使用 GLM API，无需 ccm 依赖

#### 修复
- 移除过时的 `--provider gemini-api` 参数传递
- 更新依赖验证逻辑 (Gemini API → GLM-4.6)
- 修复 stage2_classify_content.py 文档

---

## [1.0.0] - 2025-11-04

### Multi-Stage Pipeline 架构

#### 新增
- **6 阶段流水线**:
  - Stage 1: PDF 提取
  - Stage 2: 内容分类
  - Stage 3: 内容分块
  - Stage 4: AI 增强（支持断点续传）
  - Stage 5: Skill 生成
  - Stage 6: SKILL.md 增强（可选）

- **智能缓存机制**: 基于 SHA256 hash 的缓存系统
- **断点续传**: Stage 4 支持中断后继续
- **多 LLM Provider 支持**: Claude, Gemini, Codex

#### 技术决策
- PDF 库选择 PyMuPDF (fitz) - 高性能 C++ 实现
- 每个 chunk ≤ 300K 字符（Claude 限制）
- 缓存键格式: `{stage}_{pdf_hash}.json`

---

## [0.1.0] - 2025-10-25

### 项目初始化

#### 新增
- 项目基础结构
- 前端 SvelteKit 5 + TypeScript 框架
- 后端 FastAPI + Python 3.11 框架
- 设计系统文档 (BEANFLOW_DESIGN_SYSTEM.md)
- LLM Agent Prompts 开发指南

---

## 版本约定

- **MAJOR**: 不兼容的架构变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修复

---

**维护者**: BeanFlow Team
