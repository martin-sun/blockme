# 任务11：轻量级 Skill 索引系统

## 任务目标

实现轻量级的 Skill 索引和加载系统，支持快速查找、加载和管理 Skills。系统采用简单的文件系统 + JSON 索引方案，无需向量数据库或全文检索引擎，充分利用 Claude 200K context 窗口的优势。

## 技术要求

**存储方案：**
- 文件系统：Markdown 文件存储（带 YAML front matter）
- JSON 索引：轻量级元数据索引
- 无需向量数据库（ChromaDB、Qdrant 等）
- 无需全文检索引擎（SQLite FTS5、Elasticsearch 等）

**核心功能：**
- YAML front matter 解析
- 自动索引构建和更新
- Skill 快速查找和加载
- 元数据查询和过滤

**性能要求：**
- 索引构建时间 < 1秒（100个 Skills）
- Skill 加载时间 < 50ms
- 内存占用 < 10MB（索引）
- 支持热更新（文件变化自动重建索引）

## 实现步骤

### 1. 设计索引结构

定义轻量级 JSON 索引格式：
```json
{
  "skill_id_1": {
    "path": "federal/personal-income-tax.md",
    "metadata": {
      "skill_id": "skill_id_1",
      "title": "...",
      "domain": "...",
      "triggers": [...],
      "keywords": [...],
      "related_skills": [...],
      "content_size_kb": 25.5,
      "estimated_tokens": 6500
    }
  }
}
```

### 2. 实现 YAML Parser

开发 YAML front matter 解析器：
- 读取 Markdown 文件
- 提取 `---` 分隔的 YAML 部分
- 解析为 Python 字典
- 验证必需字段

### 3. 实现索引构建器

开发自动索引构建系统：
- 扫描 skills 目录
- 解析所有 .md 文件
- 构建内存索引
- 保存到 JSON 文件

### 4. 实现 Skill 加载器

开发 Skill 内容加载系统：
- 根据 skill_id 快速定位文件
- 读取文件内容
- 移除 front matter 返回纯内容
- 支持批量加载

## 关键代码提示

**Skill Loader 核心实现：**

```python
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import hashlib
import time

@dataclass
class SkillMetadata:
    """Skill 元数据"""
    skill_id: str
    title: str
    domain: str
    path: str  # 相对路径
    topics: List[str]
    triggers: List[str]
    keywords: List[str]
    related_skills: List[Dict]
    content_size_kb: float
    estimated_tokens: int
    version: str = "1.0"
    last_updated: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


class SkillIndexBuilder:
    """Skill 索引构建器"""

    def __init__(self, skills_dir: str = "knowledge_base/skills"):
        self.skills_dir = Path(skills_dir)
        self.index: Dict[str, SkillMetadata] = {}

    def build(self) -> Dict[str, Dict]:
        """
        扫描并构建索引

        Returns:
            {skill_id: {path, metadata}}
        """
        start_time = time.time()
        self.index = {}

        # 扫描所有 .md 文件
        md_files = list(self.skills_dir.rglob("*.md"))

        for md_file in md_files:
            # 跳过索引文件
            if md_file.name == "skills-index.json":
                continue

            try:
                metadata = self._parse_skill_file(md_file)
                if metadata:
                    self.index[metadata.skill_id] = {
                        "path": str(md_file.relative_to(self.skills_dir)),
                        "metadata": metadata.to_dict()
                    }
            except Exception as e:
                print(f"⚠️  解析 {md_file.name} 失败: {e}")

        duration = time.time() - start_time
        print(f"✅ 索引构建完成：{len(self.index)} 个 Skills，耗时 {duration:.2f}s")

        return self.index

    def _parse_skill_file(self, md_file: Path) -> Optional[SkillMetadata]:
        """解析单个 Skill 文件"""
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查 front matter
        if not content.startswith("---"):
            print(f"⚠️  {md_file.name} 缺少 YAML front matter")
            return None

        # 分割内容
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        yaml_content = parts[1]
        markdown_content = parts[2].strip()

        # 解析 YAML
        yaml_data = yaml.safe_load(yaml_content)

        # 验证必需字段
        required_fields = ["skill_id", "title", "domain"]
        for field in required_fields:
            if field not in yaml_data:
                print(f"⚠️  {md_file.name} 缺少必需字段: {field}")
                return None

        # 计算文件大小
        file_size_kb = md_file.stat().st_size / 1024

        # 估算 token 数（粗略：中文 2字符/token，英文 4字符/token）
        estimated_tokens = int(len(markdown_content) * 0.5)

        # 构建元数据
        return SkillMetadata(
            skill_id=yaml_data["skill_id"],
            title=yaml_data["title"],
            domain=yaml_data["domain"],
            path=str(md_file.relative_to(self.skills_dir)),
            topics=yaml_data.get("topics", []),
            triggers=yaml_data.get("triggers", []),
            keywords=yaml_data.get("keywords", []),
            related_skills=yaml_data.get("related_skills", []),
            content_size_kb=round(file_size_kb, 2),
            estimated_tokens=estimated_tokens,
            version=yaml_data.get("version", "1.0"),
            last_updated=yaml_data.get("last_updated", "")
        )

    def save(self, output_path: Optional[Path] = None):
        """保存索引到 JSON 文件"""
        if output_path is None:
            output_path = self.skills_dir / "skills-index.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

        print(f"💾 索引已保存: {output_path}")


class SkillLoader:
    """Skill 加载器"""

    def __init__(self, skills_dir: str = "knowledge_base/skills"):
        self.skills_dir = Path(skills_dir)
        self.index: Dict[str, Dict] = {}
        self._load_index()

    def _load_index(self):
        """加载索引文件"""
        index_file = self.skills_dir / "skills-index.json"

        if not index_file.exists():
            print("⚠️  索引文件不存在，正在构建...")
            self.rebuild_index()
            return

        with open(index_file, "r", encoding="utf-8") as f:
            self.index = json.load(f)

        print(f"📚 已加载 {len(self.index)} 个 Skills 索引")

    def rebuild_index(self):
        """重建索引"""
        builder = SkillIndexBuilder(str(self.skills_dir))
        self.index = builder.build()
        builder.save()

    def get_skill(self, skill_id: str) -> Optional[Dict]:
        """
        获取指定 Skill 的完整内容

        Returns:
            {
                "skill_id": "...",
                "metadata": {...},
                "content": "...",  # 纯 Markdown 内容（无 front matter）
                "path": "..."
            }
        """
        if skill_id not in self.index:
            return None

        skill_info = self.index[skill_id]
        skill_path = self.skills_dir / skill_info["path"]

        # 读取文件
        with open(skill_path, "r", encoding="utf-8") as f:
            full_content = f.read()

        # 移除 front matter
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

    def load_skills(self, skill_ids: List[str]) -> List[Dict]:
        """批量加载 Skills"""
        loaded = []

        for skill_id in skill_ids:
            skill = self.get_skill(skill_id)
            if skill:
                loaded.append(skill)
            else:
                print(f"⚠️  Skill '{skill_id}' 不存在")

        return loaded

    def search(
        self,
        domain: Optional[str] = None,
        triggers: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> List[str]:
        """
        搜索 Skills（简单的元数据匹配）

        Returns:
            List of skill_ids
        """
        results = []

        for skill_id, skill_info in self.index.items():
            metadata = skill_info["metadata"]

            # 领域过滤
            if domain and metadata.get("domain") != domain:
                continue

            # 触发词匹配
            if triggers:
                skill_triggers = metadata.get("triggers", [])
                if not any(t.lower() in [st.lower() for st in skill_triggers] for t in triggers):
                    continue

            # 关键词匹配
            if keywords:
                skill_keywords = metadata.get("keywords", [])
                if not any(kw.lower() in " ".join(skill_keywords).lower() for kw in keywords):
                    continue

            results.append(skill_id)

        return results

    def get_related_skills(
        self,
        skill_id: str,
        priority: Optional[str] = None
    ) -> List[str]:
        """
        获取相关 Skills

        Args:
            skill_id: 主 Skill ID
            priority: 优先级过滤（high/medium/low），None 返回全部

        Returns:
            List of related skill_ids
        """
        if skill_id not in self.index:
            return []

        metadata = self.index[skill_id]["metadata"]
        related = metadata.get("related_skills", [])

        if priority:
            related = [r for r in related if r.get("priority") == priority]

        return [r["id"] for r in related]

    def get_all_skill_ids(self) -> List[str]:
        """获取所有 Skill IDs"""
        return list(self.index.keys())

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        domains = {}
        total_size = 0
        total_tokens = 0

        for skill_info in self.index.values():
            metadata = skill_info["metadata"]
            domain = metadata.get("domain", "unknown")

            domains[domain] = domains.get(domain, 0) + 1
            total_size += metadata.get("content_size_kb", 0)
            total_tokens += metadata.get("estimated_tokens", 0)

        return {
            "total_skills": len(self.index),
            "domains": domains,
            "total_size_kb": round(total_size, 2),
            "total_estimated_tokens": total_tokens,
            "avg_skill_size_kb": round(total_size / len(self.index), 2) if self.index else 0
        }


class SkillCache:
    """Skill 内容缓存（可选优化）"""

    def __init__(self, max_size: int = 20):
        self.max_size = max_size
        self.cache: Dict[str, Dict] = {}
        self.access_order: List[str] = []

    def get(self, skill_id: str) -> Optional[Dict]:
        """从缓存获取"""
        if skill_id in self.cache:
            # 更新访问顺序（LRU）
            self.access_order.remove(skill_id)
            self.access_order.append(skill_id)
            return self.cache[skill_id]
        return None

    def put(self, skill_id: str, skill_data: Dict):
        """添加到缓存"""
        if skill_id in self.cache:
            # 已存在，更新访问顺序
            self.access_order.remove(skill_id)
        elif len(self.cache) >= self.max_size:
            # 缓存满，移除最旧的
            oldest = self.access_order.pop(0)
            del self.cache[oldest]

        self.cache[skill_id] = skill_data
        self.access_order.append(skill_id)

    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_order.clear()


class CachedSkillLoader(SkillLoader):
    """带缓存的 Skill 加载器"""

    def __init__(self, skills_dir: str = "knowledge_base/skills", cache_size: int = 20):
        super().__init__(skills_dir)
        self.cache = SkillCache(max_size=cache_size)

    def get_skill(self, skill_id: str) -> Optional[Dict]:
        """获取 Skill（优先从缓存）"""
        # 检查缓存
        cached = self.cache.get(skill_id)
        if cached:
            return cached

        # 缓存未命中，加载文件
        skill_data = super().get_skill(skill_id)

        if skill_data:
            self.cache.put(skill_id, skill_data)

        return skill_data
```

## 测试验证

### 1. 构建索引测试

```python
from skill_loader import SkillIndexBuilder

# 构建索引
builder = SkillIndexBuilder("knowledge_base/skills")
index = builder.build()

# 保存索引
builder.save()

# 验证
assert len(index) > 0
print(f"✅ 索引包含 {len(index)} 个 Skills")
```

### 2. Skill 加载测试

```python
from skill_loader import SkillLoader

# 初始化加载器
loader = SkillLoader("knowledge_base/skills")

# 加载单个 Skill
skill = loader.get_skill("sk-personal-tax")
assert skill is not None
assert "content" in skill
assert "metadata" in skill

print(f"✅ Skill: {skill['metadata']['title']}")
print(f"✅ 内容长度: {len(skill['content'])} 字符")

# 批量加载
skills = loader.load_skills(["sk-personal-tax", "federal-personal-tax"])
assert len(skills) == 2

print(f"✅ 批量加载 {len(skills)} 个 Skills")
```

### 3. 搜索测试

```python
# 按领域搜索
provincial_skills = loader.search(domain="provincial_tax")
print(f"✅ 省级税务 Skills: {provincial_skills}")

# 按触发词搜索
sk_skills = loader.search(triggers=["Saskatchewan", "萨省"])
print(f"✅ 萨省相关 Skills: {sk_skills}")

# 获取相关 Skills
related = loader.get_related_skills("sk-personal-tax", priority="high")
print(f"✅ 相关 Skills: {related}")
```

### 4. 性能测试

```python
import time

# 测试加载速度
start = time.time()
skill = loader.get_skill("sk-personal-tax")
duration = (time.time() - start) * 1000

print(f"✅ 加载耗时: {duration:.2f} ms")
assert duration < 50  # 应小于 50ms

# 测试批量加载
start = time.time()
skills = loader.load_skills([f"skill_{i}" for i in range(10)])
duration = time.time() - start

print(f"✅ 批量加载 10 个 Skills 耗时: {duration:.2f} s")
```

### 5. 缓存测试

```python
from skill_loader import CachedSkillLoader

# 使用缓存加载器
cached_loader = CachedSkillLoader("knowledge_base/skills", cache_size=10)

# 首次加载（慢）
start = time.time()
skill1 = cached_loader.get_skill("sk-personal-tax")
first_load_time = (time.time() - start) * 1000

# 第二次加载（快，从缓存）
start = time.time()
skill2 = cached_loader.get_skill("sk-personal-tax")
cached_load_time = (time.time() - start) * 1000

print(f"✅ 首次加载: {first_load_time:.2f} ms")
print(f"✅ 缓存加载: {cached_load_time:.2f} ms")
assert cached_load_time < first_load_time
```

## 注意事项

**索引更新策略：**
- 开发阶段：手动重建索引（`loader.rebuild_index()`）
- 生产环境：可选实现文件监控自动重建
- 简单方案：每次启动时检查索引是否存在

**元数据验证：**
- 必需字段：skill_id, title, domain
- 推荐字段：triggers, keywords, related_skills
- 自动计算：content_size_kb, estimated_tokens

**性能优化建议：**
- 索引文件缓存在内存中（启动时加载一次）
- Skill 内容按需加载（不预加载全部）
- 可选使用 LRU 缓存热门 Skills
- 单个索引文件大小控制在 < 1MB

**与向量检索方案对比：**

| 特性 | 轻量级索引 | 向量检索 |
|------|----------|---------|
| 实现复杂度 | ⭐ 简单 | ⭐⭐⭐ 复杂 |
| 依赖项 | PyYAML | ChromaDB + Sentence Transformers |
| 内存占用 | < 10MB | > 500MB |
| 索引构建 | < 1s | > 30s（需要 embedding） |
| 适用场景 | < 1000 Skills | 无限制 |
| 检索方式 | 元数据匹配 | 语义相似度 |

**什么时候需要升级到向量检索：**
- Skills 数量 > 1000
- 需要跨文档的语义检索
- 需要处理模糊查询
- 文档内容高度相似，难以用元数据区分

## 依赖关系

**前置任务：**
- 任务09：Markdown 生成优化
- 任务10：Skill 架构设计

**后置任务：**
- 任务13：Claude 辅助的 Skill 路由器
- 任务14：Skill 加载和上下文构建引擎
