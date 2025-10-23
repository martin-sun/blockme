# 任务10：Skill 架构设计

## 任务目标

设计并实现类似 Claude Code Skill 的知识库架构，用于组织和管理从文档转换生成的 Markdown 知识库。设计采用轻量级 Skill-based 方案，支持多领域分类、智能路由和动态加载。

## 技术要求

**架构设计原则：**
- Skill 化组织：每个专业主题作为独立 Skill
- 领域分类：支持多个专业领域
- 元数据驱动：使用 YAML front matter 管理 Skill 信息
- 轻量级索引：无需向量数据库，基于文件系统

**存储要求：**
- Markdown 文件存储（带 YAML front matter）
- JSON 索引文件（快速查找）
- 文件系统组织（按领域分类）
- 无需向量化或全文索引

**核心优势：**
- 实现简单，维护成本低
- 完整上下文（不切断文档）
- 适合 Claude 200K context 窗口
- 文档更新即时生效

## 实现步骤

### 1. 设计 Skill 目录结构

规划文件系统组织方式：
```
knowledge_base/
├── skills/
│   ├── federal/                         # 联邦级主题
│   │   ├── personal-income-tax.md
│   │   ├── rrsp.md
│   │   └── tfsa.md
│   ├── provincial/                      # 省级主题
│   │   ├── ontario-personal-tax.md
│   │   ├── saskatchewan-personal-tax.md
│   │   └── bc-personal-tax.md
│   ├── business/                        # 商业税务
│   │   ├── corporate-tax.md
│   │   └── gst-hst.md
│   └── skills-index.json                # 自动生成的索引
└── config/
    └── domains.yaml                     # 领域配置
```

### 2. 定义 Skill 元数据结构

每个 Skill 使用 YAML front matter 定义元数据：

```yaml
---
skill_id: sk-personal-tax
title: 萨斯喀彻温省个人所得税指南 (2024)
version: "1.0"
last_updated: "2024-01-01"

# 分类
domain: provincial_tax
province: Saskatchewan
tax_year: 2024

# 适用对象
applicable_to:
  - 个人纳税人
  - 萨省居民

# 主题标签
topics:
  - 省税税率
  - 税收抵免
  - 萨省特有减免

# 触发关键词（用于路由）
triggers:
  - 萨省
  - Saskatchewan
  - SK省
  - Regina
  - Saskatoon

keywords:
  - 个人所得税
  - provincial tax
  - 税率

# 相关 Skills（自动组合）
related_skills:
  - id: federal-personal-tax
    reason: 省税计算需要结合联邦税
    priority: high
  - id: tax-credits
    reason: 可能涉及税收抵免
    priority: medium

# 内容统计
content_size_kb: 25
estimated_tokens: 6500
---
```

### 3. 实现 Skill 管理器

开发轻量级 Skill 管理系统：
- 扫描 Skill 文件并构建索引
- 解析 YAML front matter
- 提供 Skill 查询和加载接口
- 无需向量化或复杂索引

### 4. 集成 Open WebUI

将 Skill 系统注册到 Open WebUI：
- 作为 Function 或 Pipeline 集成
- 提供 Skill 管理界面
- 支持 Skill 的增删改查

## 关键代码提示

**领域配置定义（domains.yaml）：**

```yaml
domains:
  - id: federal
    name: 联邦税务
    description: 加拿大联邦税务相关主题
    icon: 🇨🇦

  - id: provincial
    name: 省级税务
    description: 各省份税务政策和规定
    icon: 🏛️
    provinces:
      - Ontario
      - Saskatchewan
      - British Columbia
      - Quebec

  - id: business
    name: 商业税务
    description: 公司税、销售税等商业税务
    icon: 💼

  - id: specialized
    name: 专项税务
    description: 特殊情况的税务处理
    icon: 📋
```

**Skill 文件示例：**

```markdown
# knowledge_base/skills/provincial/saskatchewan-personal-tax.md

---
skill_id: sk-personal-tax
title: 萨斯喀彻温省个人所得税指南 (2024)
version: "1.0"
last_updated: "2024-01-01"
domain: provincial_tax
province: Saskatchewan
tax_year: 2024

applicable_to:
  - 个人纳税人
  - 萨省居民

topics:
  - 省税税率
  - 税收抵免

triggers:
  - 萨省
  - Saskatchewan
  - SK省

keywords:
  - 个人所得税
  - provincial tax

related_skills:
  - id: federal-personal-tax
    reason: 省税计算需要结合联邦税
    priority: high

content_size_kb: 25
estimated_tokens: 6500
---

# 萨斯喀彻温省个人所得税指南 (2024)

## 概述

萨斯喀彻温省的个人所得税基于联邦应税收入计算。省税是在联邦税基础上额外征收的。

## 税率档次 (2024年)

2024年萨省个人所得税税率如下：

| 应税收入范围 | 税率 |
|------------|------|
| $0 - $49,720 | 10.5% |
| $49,720 - $142,058 | 12.5% |
| $142,058 以上 | 14.5% |

## 基本个人免税额

2024年萨省基本个人免税额为 $17,661。

## 计算示例

假设您的联邦应税收入为 $50,000：

1. 前 $49,720 按 10.5% 计税：$49,720 × 10.5% = $5,220.60
2. 剩余 $280 按 12.5% 计税：$280 × 12.5% = $35.00
3. 省税总额：$5,220.60 + $35.00 = $5,255.60

## 税收抵免

萨省提供以下主要税收抵免：
- 基本个人免税额抵免
- 配偶/同居伴侣免税额
- 适龄工作者福利
- 萨省低收入税收抵免

## 注意事项

1. 省税基于联邦应税收入，而非总收入
2. 需要同时计算联邦税和省税
3. 建议使用官方税务软件或咨询专业税务师

---

**免责声明：** 此信息仅供参考，具体税务情况请咨询专业税务师或访问 CRA 官方网站。
```

**Skill 管理器实现：**

```python
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class SkillMetadata:
    """Skill 元数据"""
    skill_id: str
    title: str
    domain: str
    topics: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    related_skills: List[Dict] = field(default_factory=list)
    content_size_kb: float = 0
    estimated_tokens: int = 0
    version: str = "1.0"
    last_updated: str = ""

    def to_dict(self) -> Dict:
        return {
            "skill_id": self.skill_id,
            "title": self.title,
            "domain": self.domain,
            "topics": self.topics,
            "triggers": self.triggers,
            "keywords": self.keywords,
            "related_skills": self.related_skills,
            "content_size_kb": self.content_size_kb,
            "estimated_tokens": self.estimated_tokens,
            "version": self.version,
            "last_updated": self.last_updated
        }


class SkillManager:
    """轻量级 Skill 管理器"""

    def __init__(self, skills_dir: str = "knowledge_base/skills"):
        self.skills_dir = Path(skills_dir)
        self.skills_index: Dict[str, Dict] = {}

        # 初始化
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self._build_index()

    def _build_index(self):
        """扫描并构建 Skill 索引"""
        self.skills_index = {}

        # 扫描所有 .md 文件
        for md_file in self.skills_dir.rglob("*.md"):
            metadata = self._parse_skill_metadata(md_file)

            if metadata:
                skill_id = metadata.get("skill_id", md_file.stem)
                self.skills_index[skill_id] = {
                    "path": str(md_file.relative_to(self.skills_dir)),
                    "metadata": metadata
                }

        # 保存索引文件
        self._save_index()

    def _parse_skill_metadata(self, md_file: Path) -> Optional[Dict]:
        """解析 Skill 的 YAML front matter"""
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查是否有 front matter
            if not content.startswith("---"):
                return None

            # 提取 YAML 部分
            parts = content.split("---", 2)
            if len(parts) < 3:
                return None

            yaml_content = parts[1]
            metadata = yaml.safe_load(yaml_content)

            # 计算文件大小
            file_size_kb = md_file.stat().st_size / 1024
            metadata["content_size_kb"] = round(file_size_kb, 2)

            return metadata

        except Exception as e:
            print(f"解析 {md_file} 失败: {e}")
            return None

    def _save_index(self):
        """保存索引到 JSON 文件"""
        index_file = self.skills_dir / "skills-index.json"

        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(self.skills_index, f, ensure_ascii=False, indent=2)

    def get_skill(self, skill_id: str) -> Optional[Dict]:
        """获取指定 Skill 的完整信息"""
        if skill_id not in self.skills_index:
            return None

        skill_info = self.skills_index[skill_id]
        skill_path = self.skills_dir / skill_info["path"]

        # 读取完整内容
        with open(skill_path, "r", encoding="utf-8") as f:
            full_content = f.read()

        # 移除 front matter，只保留正文
        if full_content.startswith("---"):
            parts = full_content.split("---", 2)
            content = parts[2].strip() if len(parts) >= 3 else full_content
        else:
            content = full_content

        return {
            "skill_id": skill_id,
            "metadata": skill_info["metadata"],
            "content": content,
            "path": str(skill_path)
        }

    def search_skills(
        self,
        domain: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> List[str]:
        """搜索 Skills（简单的关键词匹配）"""
        results = []

        for skill_id, skill_info in self.skills_index.items():
            metadata = skill_info["metadata"]

            # 领域过滤
            if domain and metadata.get("domain") != domain:
                continue

            # 关键词匹配
            if keywords:
                skill_keywords = metadata.get("keywords", [])
                skill_triggers = metadata.get("triggers", [])
                all_keywords = skill_keywords + skill_triggers

                if any(kw.lower() in " ".join(all_keywords).lower() for kw in keywords):
                    results.append(skill_id)
            else:
                results.append(skill_id)

        return results

    def get_related_skills(self, skill_id: str, priority: str = "high") -> List[str]:
        """获取相关 Skills"""
        if skill_id not in self.skills_index:
            return []

        metadata = self.skills_index[skill_id]["metadata"]
        related = metadata.get("related_skills", [])

        # 按优先级过滤
        return [
            r["id"] for r in related
            if r.get("priority") == priority or priority == "all"
        ]

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        domains = {}
        total_size = 0
        total_tokens = 0

        for skill_info in self.skills_index.values():
            metadata = skill_info["metadata"]
            domain = metadata.get("domain", "unknown")

            domains[domain] = domains.get(domain, 0) + 1
            total_size += metadata.get("content_size_kb", 0)
            total_tokens += metadata.get("estimated_tokens", 0)

        return {
            "total_skills": len(self.skills_index),
            "domains": domains,
            "total_size_kb": round(total_size, 2),
            "total_estimated_tokens": total_tokens
        }
```

## 测试验证

```python
# 初始化管理器
manager = SkillManager("knowledge_base/skills")

# 查看索引
print(f"总共 {len(manager.skills_index)} 个 Skills")

# 获取特定 Skill
skill = manager.get_skill("sk-personal-tax")
print(f"Skill: {skill['metadata']['title']}")
print(f"内容大小: {skill['metadata']['content_size_kb']} KB")

# 搜索 Skills
results = manager.search_skills(domain="provincial_tax", keywords=["萨省"])
print(f"找到 {len(results)} 个相关 Skills")

# 获取相关 Skills
related = manager.get_related_skills("sk-personal-tax", priority="high")
print(f"高优先级相关 Skills: {related}")

# 统计信息
stats = manager.get_statistics()
print(f"统计: {stats}")
```

## 注意事项

**Skill 设计原则：**
- 每个 Skill 专注一个主题（单一职责）
- Skill 大小控制在 20-80KB（适合完整加载）
- 使用清晰的 triggers 便于路由
- 合理设置 related_skills 实现自动组合

**元数据完整性：**
- skill_id 必须唯一
- triggers 要覆盖主要查询方式
- related_skills 设置高优先级的必要关联
- 定期更新 last_updated 和 version

**性能优化：**
- 索引文件缓存在内存中
- 延迟加载 Skill 内容（按需读取）
- 合理控制单次加载的 Skill 数量（≤3个）

**与 Claude Code Skill 的类比：**
- Skill 文件 ≈ Claude Code 的 .claude/skills/*.md
- YAML front matter ≈ Skill 配置
- 触发词 ≈ Skill 激活条件
- 相关 Skills ≈ 自动加载的依赖

## 依赖关系

**前置任务：**
- 任务09：Markdown 生成优化

**后置任务：**
- 任务11：轻量级 Skill 索引系统
- 任务13：Claude 辅助的 Skill 路由器
