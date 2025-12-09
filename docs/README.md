# BeanFlow-CRA 文档中心

BeanFlow-CRA 是一个基于 LLM 的 CRA 税务文档处理与智能问答系统。

---

## 快速导航

### 入门指南
| 文档 | 说明 |
|------|------|
| [快速开始](guides/QUICK_START.md) | 环境配置、安装和第一次运行 |
| [故障排查](guides/TROUBLESHOOTING.md) | 常见问题和解决方案 |
| [缓存管理](guides/CACHE_MANAGEMENT.md) | 缓存机制和磁盘空间管理 |

### 架构文档
| 文档 | 说明 |
|------|------|
| [Pipeline 架构](architecture/PIPELINE_ARCHITECTURE.md) | 6 阶段文档处理流水线详解 |
| [Skills 组织架构](architecture/SKILLS_ORGANIZATION.md) | Skill 目录结构和路由机制 |
| [SKILL.md 增强](architecture/SKILL_ENHANCEMENT.md) | Skill 文件增强功能设计 |
| [LLM Provider 系统](architecture/LLM_PROVIDERS.md) | Claude、GLM、Gemini 等 Provider 集成 |

### 设计规范
| 文档 | 说明 |
|------|------|
| [设计系统](BEANFLOW_DESIGN_SYSTEM.md) | UI/UX 设计规范和品牌指南 |

### 开发资源
| 文档 | 说明 |
|------|------|
| [LLM Agent Prompts](llm-agent-prompts/README.md) | 开发阶段的 LLM 提示词模板 |
| [更新日志](CHANGELOG.md) | 开发历史和版本变更 |

---

## 按角色阅读

### 新用户
1. 阅读 [快速开始](guides/QUICK_START.md) 了解如何运行系统
2. 遇到问题查看 [故障排查](guides/TROUBLESHOOTING.md)

### 开发者
1. 了解 [Pipeline 架构](architecture/PIPELINE_ARCHITECTURE.md) 理解系统设计
2. 了解 [Skills 组织架构](architecture/SKILLS_ORGANIZATION.md) 理解路由机制
3. 查看 [LLM Provider 系统](architecture/LLM_PROVIDERS.md) 了解如何扩展

### 设计师
1. 参考 [设计系统](BEANFLOW_DESIGN_SYSTEM.md) 了解品牌规范

---

## 项目结构

```
BeanFlow-CRA/
├── backend/           # Python 后端 (PDF 处理 + FastAPI)
│   ├── README.md      # 后端入口文档
│   └── ...
├── frontend/          # SvelteKit 前端
│   ├── README.md      # 前端入口文档
│   └── ...
├── mvp/               # MVP 验证代码
│   └── README.md
├── docs/              # 项目文档（本目录）
│   ├── architecture/  # 架构设计文档
│   ├── guides/        # 使用指南
│   └── llm-agent-prompts/  # 开发 prompts
└── README.md          # 项目主入口
```

---

## 相关链接

- **后端文档**: [backend/README.md](../backend/README.md)
- **前端文档**: [frontend/README.md](../frontend/README.md)
- **MVP 文档**: [mvp/README.md](../mvp/README.md)

---

**维护者**: BeanFlow Team
**最后更新**: 2025-12-09
