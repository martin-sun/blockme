# 任务12：Skill 元数据管理器

## 任务目标

开发一个完整的 Skill 元数据管理系统，管理每个 Skill 的 YAML front matter 元数据。系统需要支持元数据验证、自动生成默认元数据、批量更新和一致性检查，为 Skill 路由和加载提供可靠的元数据支持。

**为什么需要元数据管理：**
- Skill 路由依赖准确的 triggers 和 domain 信息
- related_skills 影响关联 Skills 的加载优先级
- 元数据质量直接影响路由准确性和用户体验

## 技术要求

**核心元数据字段（YAML front matter）：**
- **必需字段：**
  - skill_id：唯一标识符（影响加载和缓存）
  - title：显示标题
  - domain：领域分类（影响路由分组）
  - triggers：路由触发词列表（**最关键**，直接影响路由准确性）

- **推荐字段：**
  - keywords：关键词列表（辅助路由）
  - topics：主题标签（辅助分类）
  - related_skills：关联 Skills 及优先级
  - version：版本号
  - last_updated：最后更新时间

**功能要求：**
- YAML front matter 验证器
- 元数据提取和更新工具
- 自动生成默认元数据
- 元数据一致性检查
- 批量验证所有 Skills

## 实现步骤

### 1. 设计 YAML Front Matter 验证器

创建 Skill 元数据验证模型：
```bash
touch src/knowledge_manager/skill_metadata_validator.py
```

**核心功能：**
- 验证必填字段（skill_id, title, domain, triggers）
- 验证 skill_id 格式（有效标识符）
- 验证 triggers 非空（至少 1 个触发词）
- 验证 related_skills 结构

### 2. 实现元数据提取和更新工具

开发 YAML front matter 操作工具：
- 从 Skill 文件提取 YAML front matter
- 更新元数据（保持内容不变）
- 验证更新后的元数据
- 支持部分更新

### 3. 实现默认元数据生成器

为新 Skill 自动生成元数据：
- 从 skill_id 和 title 生成默认 triggers
- 从内容提取关键词（简单词频或 TF-IDF）
- 自动设置创建时间和版本号
- 生成初始 related_skills 为空列表

### 4. 实现元数据一致性检查

批量验证所有 Skills：
- 检查重复 skill_id
- 验证 related_skills 引用的有效性
- 检查 triggers 的覆盖度
- 报告验证错误和警告

## 关键代码提示

**Skill 元数据验证器：**

```python
from typing import Dict, List, Optional
from pydantic import BaseModel, validator
import yaml
from pathlib import Path

class SkillMetadataValidator(BaseModel):
    """Skill 元数据验证模型"""
    skill_id: str
    title: str
    domain: str
    triggers: List[str] = []
    keywords: List[str] = []
    topics: List[str] = []
    related_skills: List[Dict] = []
    version: str = "1.0"
    last_updated: str = ""

    @validator('skill_id')
    def validate_skill_id(cls, v):
        # skill_id 必须是有效的标识符
        if not v or not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('skill_id 必须是有效标识符')
        return v

    @validator('triggers')
    def validate_triggers(cls, v):
        # 至少需要 1 个触发词
        if not v or len(v) == 0:
            raise ValueError('triggers 不能为空，至少需要 1 个触发词')
        return v

class SkillMetadataManager:
    """Skill 元数据管理器"""

    def __init__(self, skills_dir: str = "knowledge_base/skills"):
        self.skills_dir = Path(skills_dir)

    def validate_skill_file(self, skill_path: Path) -> tuple[bool, Optional[str]]:
        """验证 Skill 文件的元数据"""
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取 YAML front matter
            if not content.startswith('---'):
                return False, "缺少 YAML front matter"

            parts = content.split('---', 2)
            if len(parts) < 3:
                return False, "YAML front matter 格式错误"

            yaml_content = parts[1]
            metadata = yaml.safe_load(yaml_content)

            # 验证元数据
            SkillMetadataValidator(**metadata)

            return True, None

        except Exception as e:
            return False, str(e)

    def update_metadata(
        self,
        skill_path: Path,
        updates: Dict
    ) -> bool:
        """更新 Skill 的元数据"""
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()

            parts = content.split('---', 2)
            if len(parts) < 3:
                return False

            # 解析现有元数据
            metadata = yaml.safe_load(parts[1])

            # 应用更新
            metadata.update(updates)

            # 验证更新后的元数据
            SkillMetadataValidator(**metadata)

            # 重新构建文件
            new_content = f"---\n{yaml.dump(metadata, allow_unicode=True)}---\n{parts[2]}"

            with open(skill_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return True

        except Exception as e:
            print(f"更新失败: {e}")
            return False

    def generate_default_metadata(
        self,
        skill_id: str,
        title: str,
        domain: str,
        content: str
    ) -> Dict:
        """为新 Skill 生成默认元数据"""
        from datetime import datetime

        # 从内容中提取关键词（简单实现）
        keywords = self._extract_keywords(content)

        return {
            "skill_id": skill_id,
            "title": title,
            "domain": domain,
            "triggers": [skill_id.replace('-', ' '), title],
            "keywords": keywords[:10],
            "topics": [],
            "related_skills": [],
            "version": "1.0",
            "last_updated": datetime.now().isoformat()
        }

    def _extract_keywords(self, content: str) -> List[str]:
        """简单的关键词提取（可使用 TF-IDF 或其他方法）"""
        # 简化实现：提取常见词
        words = content.lower().split()
        # 移除停用词、标点等
        # 返回前 N 个高频词
        from collections import Counter
        word_freq = Counter(words)
        return [word for word, _ in word_freq.most_common(10)]

    def validate_all_skills(self) -> Dict[str, List[str]]:
        """批量验证所有 Skills"""
        results = {
            "valid": [],
            "invalid": [],
            "errors": {}
        }

        for skill_file in self.skills_dir.rglob("*.md"):
            is_valid, error_msg = self.validate_skill_file(skill_file)

            if is_valid:
                results["valid"].append(str(skill_file))
            else:
                results["invalid"].append(str(skill_file))
                results["errors"][str(skill_file)] = error_msg

        return results

    def check_related_skills_validity(self) -> Dict[str, List[str]]:
        """检查 related_skills 引用的有效性"""
        # 加载所有 skill_id
        all_skill_ids = set()
        skill_references = {}

        for skill_file in self.skills_dir.rglob("*.md"):
            try:
                with open(skill_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        metadata = yaml.safe_load(parts[1])
                        skill_id = metadata.get('skill_id')
                        all_skill_ids.add(skill_id)
                        skill_references[skill_id] = metadata.get('related_skills', [])
            except:
                pass

        # 检查引用
        invalid_refs = {}
        for skill_id, related in skill_references.items():
            for ref in related:
                ref_id = ref.get('skill_id') if isinstance(ref, dict) else ref
                if ref_id not in all_skill_ids:
                    if skill_id not in invalid_refs:
                        invalid_refs[skill_id] = []
                    invalid_refs[skill_id].append(ref_id)

        return invalid_refs
```

## 测试验证

```python
from pathlib import Path

# 1. 验证 Skill 文件的元数据
manager = SkillMetadataManager(skills_dir="knowledge_base/skills")

skill_path = Path("knowledge_base/skills/tax/sk-rate.md")
is_valid, error = manager.validate_skill_file(skill_path)

if is_valid:
    print("✅ 元数据验证通过")
else:
    print(f"❌ 元数据验证失败: {error}")

# 2. 更新元数据
updates = {
    "triggers": ["萨省税率", "saskatchewan tax rate", "萨省 PST GST"],
    "keywords": ["税率", "PST", "GST", "萨省"],
    "last_updated": "2024-01-20T10:30:00"
}

success = manager.update_metadata(skill_path, updates)
assert success, "元数据更新失败"

# 3. 生成默认元数据
content = """
# 萨省税率说明

萨省的销售税包括 PST 和 GST...
"""

default_meta = manager.generate_default_metadata(
    skill_id="sk-rate",
    title="萨省税率",
    domain="tax",
    content=content
)

print("生成的默认元数据:", default_meta)

# 4. 批量验证所有 Skills
results = manager.validate_all_skills()

print(f"✅ 有效 Skills: {len(results['valid'])}")
print(f"❌ 无效 Skills: {len(results['invalid'])}")

if results['invalid']:
    print("\n无效 Skills 详情:")
    for skill_file, error in results['errors'].items():
        print(f"  - {skill_file}: {error}")

# 5. 检查 related_skills 引用
invalid_refs = manager.check_related_skills_validity()

if invalid_refs:
    print("\n⚠️  发现无效的 related_skills 引用:")
    for skill_id, invalid_ids in invalid_refs.items():
        print(f"  - {skill_id} 引用了不存在的: {invalid_ids}")
else:
    print("✅ 所有 related_skills 引用有效")
```

**预期输出：**
```
✅ 元数据验证通过
生成的默认元数据: {
  'skill_id': 'sk-rate',
  'title': '萨省税率',
  'domain': 'tax',
  'triggers': ['sk rate', '萨省税率'],
  'keywords': ['萨省', '税率', 'pst', 'gst', '销售税'],
  'topics': [],
  'related_skills': [],
  'version': '1.0',
  'last_updated': '2024-01-20T10:30:00'
}
✅ 有效 Skills: 15
❌ 无效 Skills: 2

无效 Skills 详情:
  - knowledge_base/skills/tax/old-doc.md: 缺少 YAML front matter
  - knowledge_base/skills/general/draft.md: triggers 不能为空，至少需要 1 个触发词

✅ 所有 related_skills 引用有效
```

## 注意事项

**1. triggers 的重要性**
- triggers 是路由最关键的字段，直接影响 Claude 路由的准确性
- 建议每个 Skill 至少包含 3-5 个 triggers
- triggers 应覆盖：
  - 中文名称（如 "萨省税率"）
  - 英文名称（如 "Saskatchewan tax rate"）
  - 常见问法（如 "萨省 PST 是多少"）
  - 缩写（如 "SK tax"）

**2. related_skills 的优先级设置**
```yaml
related_skills:
  - skill_id: "pst-exemptions"
    priority: "high"     # 强相关，优先加载
  - skill_id: "gst-basics"
    priority: "medium"   # 中等相关
  - skill_id: "tax-filing"
    priority: "low"      # 弱相关，仅在需要时加载
```

**3. 版本管理最佳实践**
- 每次内容更新都应更新 `last_updated` 字段
- 重大修改（如添加新章节）应递增 `version`
- 保持 version 格式为 "major.minor"（如 "1.0", "1.1", "2.0"）

**4. 元数据一致性**
- 定期运行 `validate_all_skills()` 检查所有 Skills
- 在 CI/CD 流程中集成元数据验证
- 发现无效引用时及时修复

**5. 性能优化**
- 元数据提取和验证在启动时完成，不影响运行时性能
- 考虑缓存验证结果（如写入 JSON 索引）

## 依赖关系

**前置任务：**
- 任务10：Skill 架构设计（定义 YAML front matter 规范）
- 任务11：Skill 索引系统（SkillLoader 加载元数据）

**后置任务：**
- 任务13：ClaudeSkillRouter（使用 triggers 进行路由）
- 任务14：SkillEngine（加载 related_skills）
- 任务15：Filter 集成（需要有效的元数据）
