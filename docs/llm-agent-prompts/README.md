# LLM Code Agent 提示词文档集

这是一套完整的提示词文档，用于指导 LLM Code Agent 实现 **Open WebUI + Claude/GLM API + 动态知识加载系统**。

## 📋 项目概述

**目标**：搭建一个基于 Open WebUI 的专业知识库系统，通过上传专业领域文档生成 Markdown 知识库，并实现类似 Claude Skill 的动态知识加载机制。

**核心特性**：
- ✅ 支持 PDF/Word/Excel/PPT 等多种文档格式
- ✅ 使用 Claude/GLM 多模态 API 提取文档内容
- ✅ 自动生成结构化 Markdown 知识库
- ✅ Skill-like 动态知识加载机制（类似 Claude Code Skill）
- ✅ Claude 辅助的智能 Skill 路由
- ✅ 轻量级索引（无需向量数据库）
- ✅ 成本优化策略（缓存、智能路由）
- ✅ 完整的用户界面和工作流

## 📂 文档结构

```
docs/llm-agent-prompts/
├── README.md                          # 本文档
├── phase-01-environment/              # 阶段1：环境搭建（4个文档）
│   ├── 01-docker-deploy-openwebui.md
│   ├── 02-configure-claude-api.md
│   ├── 03-configure-glm-api.md
│   └── 04-setup-python-dependencies.md
├── phase-02-document-processing/      # 阶段2：文档处理（5个文档）
│   ├── 05-pdf-to-image-converter.md
│   ├── 06-office-document-converter.md
│   ├── 07-claude-vision-integration.md
│   ├── 08-glm-vision-integration.md
│   └── 09-markdown-generation-optimizer.md
├── phase-03-knowledge-management/     # 阶段3：知识库管理（3个文档）
│   ├── 10-knowledge-collection-design.md
│   ├── 11-markdown-storage-indexing.md
│   └── 12-document-metadata-manager.md
├── phase-04-dynamic-loading/          # 阶段4：动态加载引擎（3个文档）
│   ├── 13-intent-recognition-module.md
│   ├── 14-knowledge-retrieval-engine.md
│   └── 15-filter-pipeline-integration.md
└── phase-05-testing-optimization/     # 阶段5：测试优化（3个文档）
    ├── 16-document-processing-tests.md
    ├── 17-cost-optimization-strategies.md
    └── 18-ui-workflow-optimization.md
```

## 🚀 使用指南

### 1. 按阶段顺序执行

建议按照以下顺序完成开发：

#### **阶段1：环境搭建（1-2天）**
1. [01 - Docker 部署 Open WebUI](./phase-01-environment/01-docker-deploy-openwebui.md)
2. [02 - 配置 Claude API](./phase-01-environment/02-configure-claude-api.md)
3. [03 - 配置 GLM API](./phase-01-environment/03-configure-glm-api.md)
4. [04 - 安装 Python 依赖](./phase-01-environment/04-setup-python-dependencies.md)

#### **阶段2：文档处理（3-5天）**
5. [05 - PDF 转图像模块](./phase-02-document-processing/05-pdf-to-image-converter.md)
6. [06 - Office 文档转换](./phase-02-document-processing/06-office-document-converter.md)
7. [07 - Claude Vision API 集成](./phase-02-document-processing/07-claude-vision-integration.md)
8. [08 - GLM Vision API 集成](./phase-02-document-processing/08-glm-vision-integration.md)
9. [09 - Markdown 生成优化](./phase-02-document-processing/09-markdown-generation-optimizer.md)

#### **阶段3：知识库管理（2-3天）**
10. [10 - Knowledge Collection 设计](./phase-03-knowledge-management/10-knowledge-collection-design.md)
11. [11 - Markdown 存储和索引](./phase-03-knowledge-management/11-markdown-storage-indexing.md)
12. [12 - 文档元数据管理](./phase-03-knowledge-management/12-document-metadata-manager.md)

#### **阶段4：动态加载引擎（3-4天）**
13. [13 - 用户意图识别模块](./phase-04-dynamic-loading/13-intent-recognition-module.md)
14. [14 - 知识检索引擎](./phase-04-dynamic-loading/14-knowledge-retrieval-engine.md)
15. [15 - Filter Pipeline 集成](./phase-04-dynamic-loading/15-filter-pipeline-integration.md)

#### **阶段5：测试优化（2-3天）**
16. [16 - 文档处理功能测试](./phase-05-testing-optimization/16-document-processing-tests.md)
17. [17 - API 成本优化策略](./phase-05-testing-optimization/17-cost-optimization-strategies.md)
18. [18 - 用户界面和工作流优化](./phase-05-testing-optimization/18-ui-workflow-optimization.md)

### 2. 每个文档包含什么？

每个提示词文档（约600字）包含：

- **任务目标**：明确要实现什么
- **技术要求**：使用的技术栈和工具
- **实现步骤**：详细的开发指导
- **关键代码提示**：代码结构建议和示例
- **测试验证**：如何验证完成
- **注意事项**：常见坑和最佳实践
- **依赖关系**：前置和后置任务

### 3. 如何使用这些文档？

**方式一：人工开发**
- 作为开发手册，按顺序完成每个任务
- 参考代码提示实现功能
- 使用测试验证确保质量

**方式二：LLM Code Agent**
- 将文档作为 Prompt 提供给 LLM Code Agent
- Agent 根据文档自动生成代码
- 人工审核和测试生成的代码

**方式三：混合模式**
- 核心模块人工实现
- 重复性工作交给 Agent
- 持续迭代优化

## 🔧 技术栈

### 核心框架
- **Open WebUI**: AI 对话平台
- **FastAPI**: 后端 API 服务

### AI API
- **Anthropic Claude**: Vision API（英文文档优势） + Skill 路由
- **智谱 GLM-4V**: Vision API（中文文档优势，免费）

### 文档处理
- **pdf2image**: PDF 转图像
- **PyMuPDF**: PDF 处理
- **LibreOffice**: Office 文档转换
- **Pillow**: 图像处理

### Skill 管理
- **PyYAML**: YAML front matter 解析
- **JSON**: 轻量级索引
- **文件系统**: Skill 存储

### Python 工具
- **uv**: 包管理器
- **pytest**: 测试框架
- **pydantic**: 数据验证

## 💡 核心创新点

### 1. 多模态 LLM 文档处理
- 利用 Claude/GLM 的视觉能力直接处理文档图像
- 无需传统 OCR，准确率更高
- 支持复杂排版、表格、公式

### 2. Skill-like 动态知识加载
- 类似 Claude Code Skill 的设计
- 完整文档注入（不切断上下文）
- Claude 辅助的智能路由
- 轻量级实现（无需向量数据库）

### 3. 自动 Skill 组合
- 基于 YAML metadata 的关联关系
- 自动加载高优先级相关 Skills
- 智能控制总 token 消耗

### 4. 成本优化
- 路由结果缓存（减少重复调用）
- 模型智能路由（优先免费模型）
- 简化架构降低维护成本

## 📊 预期效果

### 功能指标
- ✅ 支持 10+ 种文档格式
- ✅ 文档处理准确率 > 95%
- ✅ Skill 路由准确率 > 90%
- ✅ 端到端响应时间 < 5秒

### 成本指标
- ✅ 中文文档处理成本接近 $0（使用 GLM-4V-Flash）
- ✅ 路由缓存命中率 > 50%
- ✅ 无需向量数据库和 embedding 模型成本

### 用户体验
- ✅ 文档上传即处理，无需等待
- ✅ 对话中自动注入相关知识
- ✅ 完整上下文，不切断语义
- ✅ 完整的 Web 界面，无需命令行

## 🎯 里程碑

### MVP（最小可行产品）- 2周
- 完成阶段 1-3（环境 + 文档处理 + 知识库）
- 支持基本的文档上传和检索
- 命令行操作

### 完整版 - 3周
- 完成所有阶段
- 动态知识加载
- 完整 UI

### 生产级 - 4周+
- 性能优化
- 安全加固
- 监控告警

## 📝 快速开始

```bash
# 1. 克隆或创建项目
cd /Users/woohelps/CascadeProjects/blockme

# 2. 阅读第一个文档
cat docs/llm-agent-prompts/phase-01-environment/01-docker-deploy-openwebui.md

# 3. 开始实施
# 按照文档指导逐步完成每个任务

# 4. 测试验证
# 每完成一个任务，运行对应的测试确保质量
```

## 🤝 贡献指南

如果你在使用这些文档时发现问题或有改进建议：

1. 记录遇到的问题
2. 提出优化建议
3. 分享实施经验
4. 补充最佳实践

## 📄 许可证

本文档集遵循项目许可证。

## 🙏 致谢

感谢以下开源项目和技术：
- Open WebUI
- Anthropic Claude
- 智谱 GLM
- ChromaDB
- Sentence Transformers

---

**开始你的知识库系统开发之旅吧！** 🚀

如有问题，请参考各阶段文档的详细说明。
