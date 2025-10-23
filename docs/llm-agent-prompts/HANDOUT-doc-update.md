# 文档更新任务 Handout

> 本文档用于指导新的 LLM Agent 完成剩余的文档更新工作

## 📋 任务背景

**项目**：Open WebUI + Claude Skill-like 知识库系统
**任务**：将原 RAG 方案的文档更新为 Skill-like 方案
**进度**：已完成 6/9 个文档，剩余 3 个待更新

## ✅ 已完成的工作

### 核心架构文档（已全部更新）

1. **10-knowledge-collection-design.md** - Skill 架构设计
   - 从 Collection 改为 Skill 化组织
   - 添加 YAML front matter 设计
   - 实现 SkillManager 类
   - 无需向量数据库

2. **11-markdown-storage-indexing.md** - 轻量级 Skill 索引系统
   - 移除 ChromaDB 向量存储
   - 移除 SQLite FTS5 全文检索
   - 实现 SkillLoader 和 SkillIndexBuilder
   - JSON 索引 + 文件系统

3. **13-intent-recognition-module.md** - Claude 辅助的 Skill 路由器
   - 移除传统意图识别
   - 实现 ClaudeSkillRouter
   - Claude API 智能路由
   - 路由缓存机制

4. **14-knowledge-retrieval-engine.md** - Skill 加载和上下文构建引擎
   - 移除向量检索和 BM25
   - 实现 SkillEngine
   - 完整文档注入（不分块）
   - 端到端问答流程

5. **README.md** - 项目概述
   - 更新核心特性
   - 更新技术栈（移除 ChromaDB、Sentence Transformers、SQLite FTS5、BM25）
   - 更新创新点

6. **01-docker-deploy-openwebui.md** - 环境配置
   - 移除 `RAG_EMBEDDING_MODEL` 环境变量

## 🎯 待完成的任务（剩余 3 个文档）

### 任务 1: 更新 12-document-metadata-manager.md

**文件路径**: `docs/llm-agent-prompts/phase-03-knowledge-management/12-document-metadata-manager.md`

**修改要求**：

1. **标题**：保持不变或改为 "Skill 元数据管理器"

2. **任务目标**：
   - 强调管理 Skill 的 YAML front matter 元数据
   - 说明元数据对 Skill 路由的重要性

3. **技术要求**：
   - 移除向量相关字段
   - 保留并增强：
     - skill_id（必需，唯一标识）
     - title（必需，显示标题）
     - domain（必需，领域分类）
     - triggers（必需，路由触发词）
     - keywords（推荐，关键词）
     - related_skills（推荐，关联 Skills）
     - topics（推荐，主题标签）
     - version, last_updated（推荐，版本管理）

4. **实现步骤**：
   - 设计 YAML front matter 验证器
   - 实现元数据提取和更新工具
   - 自动生成默认元数据
   - 元数据一致性检查

5. **关键代码提示**：

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
```

6. **测试验证**：
   - 验证元数据合法性测试
   - 更新元数据测试
   - 生成默认元数据测试
   - 批量验证所有 Skills 测试

7. **注意事项**：
   - 强调 triggers 的重要性（影响路由准确性）
   - 说明 related_skills 的优先级设置
   - 版本管理最佳实践

---

### 任务 2: 更新 15-filter-pipeline-integration.md

**文件路径**: `docs/llm-agent-prompts/phase-04-dynamic-loading/15-filter-pipeline-integration.md`

**修改要求**：

1. **任务目标**：
   - 将 Skill 引擎集成为 Open WebUI Filter/Function
   - 替换原有的 RAG 检索逻辑

2. **技术要求**：
   - 集成 SkillEngine（任务14）
   - 支持 Open WebUI Filter API
   - 实现为 Python Function
   - 处理对话历史

3. **实现步骤**：

**步骤 1**: 创建 Open WebUI Filter

```python
# filters/skill_knowledge_filter.py

"""
title: Skill Knowledge Filter
description: 动态加载相关 Skills 到对话上下文
author: Your Name
version: 1.0.0
"""

from typing import Optional, Dict, List
from pydantic import BaseModel, Field
import os

# 导入 Skill 引擎（需要将实现放在 filters 目录）
from .skill_engine import SkillEngine


class Filter:
    """Open WebUI Filter for Skill-based Knowledge Loading"""

    class Valves(BaseModel):
        """配置参数"""
        SKILLS_DIR: str = Field(
            default="knowledge_base/skills",
            description="Skills 目录路径"
        )
        CLAUDE_API_KEY: str = Field(
            default="",
            description="Claude API Key"
        )
        ENABLE_SKILL_LOADING: bool = Field(
            default=True,
            description="是否启用 Skill 自动加载"
        )
        MIN_CONFIDENCE: str = Field(
            default="medium",
            description="最低路由置信度 (low/medium/high)"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.engine: Optional[SkillEngine] = None

    def _init_engine(self):
        """懒加载 Skill 引擎"""
        if self.engine is None and self.valves.ENABLE_SKILL_LOADING:
            api_key = self.valves.CLAUDE_API_KEY or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("⚠️  未配置 Claude API Key，Skill 加载功能已禁用")
                return False

            try:
                self.engine = SkillEngine(
                    skills_dir=self.valves.SKILLS_DIR,
                    api_key=api_key
                )
                print(f"✅ Skill 引擎初始化成功")
                return True
            except Exception as e:
                print(f"❌ Skill 引擎初始化失败: {e}")
                return False

        return self.engine is not None

    def inlet(self, body: Dict, __user__: Optional[Dict] = None) -> Dict:
        """
        在消息发送到 LLM 前处理（注入 Skills）

        Args:
            body: 请求体，包含 messages
            __user__: 用户信息

        Returns:
            修改后的 body
        """
        if not self.valves.ENABLE_SKILL_LOADING:
            return body

        if not self._init_engine():
            return body

        try:
            # 提取用户最新消息
            messages = body.get("messages", [])
            if not messages:
                return body

            last_message = messages[-1]
            if last_message.get("role") != "user":
                return body

            user_query = last_message.get("content", "")
            if not user_query:
                return body

            # 提取对话历史（排除最新消息）
            conversation_history = messages[:-1] if len(messages) > 1 else None

            # 使用 Skill 引擎路由和加载
            result = self.engine.answer_question(
                user_query=user_query,
                conversation_history=conversation_history
            )

            if not result.success or not result.loaded_skills:
                print(f"⚠️  未找到相关 Skills 或执行失败")
                return body

            # 检查置信度
            confidence = result.routing_info.get("confidence", "low")
            if confidence == "low" and self.valves.MIN_CONFIDENCE in ["medium", "high"]:
                print(f"⚠️  路由置信度过低 ({confidence})，跳过 Skill 注入")
                return body

            # 构建知识上下文
            knowledge_context = self._build_knowledge_context(result)

            # 将知识注入到用户消息前
            # 方式1：作为系统消息注入
            skill_message = {
                "role": "system",
                "content": knowledge_context
            }

            # 插入到最新消息之前
            messages.insert(-1, skill_message)

            # 更新 body
            body["messages"] = messages

            # 添加元数据（供 outlet 使用）
            body["__skill_metadata__"] = {
                "loaded_skills": [s["skill_id"] for s in result.loaded_skills],
                "routing_info": result.routing_info,
                "tokens_used": result.tokens_used
            }

            print(f"✅ 已注入 {len(result.loaded_skills)} 个 Skills")

        except Exception as e:
            print(f"❌ Skill 加载失败: {e}")
            # 失败时返回原始 body，不影响正常对话

        return body

    def outlet(self, body: Dict, __user__: Optional[Dict] = None) -> Dict:
        """
        在 LLM 响应返回给用户后处理（可选：添加元数据）

        Args:
            body: 响应体
            __user__: 用户信息

        Returns:
            修改后的 body
        """
        # 可以在这里添加 Skills 使用信息到响应中
        skill_metadata = body.get("__skill_metadata__")

        if skill_metadata:
            # 示例：在响应末尾添加来源标注
            messages = body.get("messages", [])
            if messages and messages[-1].get("role") == "assistant":
                loaded_skills = skill_metadata.get("loaded_skills", [])
                if loaded_skills:
                    citation = f"\n\n---\n*📚 参考知识: {', '.join(loaded_skills)}*"
                    messages[-1]["content"] += citation

        return body

    def _build_knowledge_context(self, result) -> str:
        """构建知识上下文"""
        from .skill_engine import SkillContextBuilder

        builder = SkillContextBuilder()
        context = builder.build_context(
            loaded_skills=[
                self.engine.skill_loader.get_skill(s["skill_id"])
                for s in result.loaded_skills
            ],
            routing_info=result.routing_info
        )

        return context
```

**步骤 2**: 创建 Open WebUI Function（可选，功能类似）

```python
# functions/skill_qa_function.py

"""
title: Skill Q&A Function
description: 基于 Skills 的问答功能
author: Your Name
version: 1.0.0
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class Tools:
    """Open WebUI Function for Skill-based Q&A"""

    class Valves(BaseModel):
        SKILLS_DIR: str = Field(default="knowledge_base/skills")
        CLAUDE_API_KEY: str = Field(default="")

    def __init__(self):
        self.valves = self.Valves()

    def ask_knowledge_base(
        self,
        question: str,
        __user__: Optional[Dict] = None
    ) -> str:
        """
        查询知识库

        Args:
            question: 用户问题

        Returns:
            答案
        """
        from .skill_engine import SkillEngine
        import os

        api_key = self.valves.CLAUDE_API_KEY or os.getenv("ANTHROPIC_API_KEY")

        engine = SkillEngine(
            skills_dir=self.valves.SKILLS_DIR,
            api_key=api_key
        )

        result = engine.answer_question(question)

        if result.success:
            return result.answer
        else:
            return f"抱歉，查询失败: {result.error}"
```

4. **测试验证**：
   - Filter 注入测试
   - 对话历史处理测试
   - 置信度过滤测试
   - 元数据传递测试

5. **注意事项**：
   - Open WebUI Filter API 兼容性
   - 错误处理不能影响正常对话
   - 性能优化（缓存、异步）

---

### 任务 3: 更新 17-cost-optimization-strategies.md

**文件路径**: `docs/llm-agent-prompts/phase-05-testing-optimization/17-cost-optimization-strategies.md`

**修改要求**：

1. **移除的内容**：
   - 所有关于 embedding 模型成本的内容
   - 向量数据库（ChromaDB）成本
   - BM25/FTS5 成本
   - 向量检索优化策略

2. **保留并增强的内容**：
   - Claude/GLM Vision API 成本优化（文档处理）
   - 对话缓存策略
   - 批量处理优化

3. **新增内容**：

**3.1 Skill 路由成本优化**

```markdown
### 路由成本优化

**成本分析**：
- 每次路由调用 Claude API：~500-1000 tokens
- 成本：约 $0.001-0.002/次
- 每天 1000 次查询：约 $1-2

**优化策略**：

#### 1. 路由结果缓存

```python
class CachedSkillRouter(ClaudeSkillRouter):
    """带持久化缓存的路由器"""

    def __init__(self, *args, cache_backend="redis", **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_backend = cache_backend

        if cache_backend == "redis":
            import redis
            self.cache = redis.Redis(host='localhost', port=6379, db=0)
        else:
            self.cache = {}  # 内存缓存

    def route(self, user_query: str, use_cache: bool = True) -> Dict:
        if not use_cache:
            return super().route(user_query, use_cache=False)

        cache_key = self._compute_cache_key(user_query)

        # 尝试从 Redis 获取
        if self.cache_backend == "redis":
            cached = self.cache.get(cache_key)
            if cached:
                import json
                result = json.loads(cached)
                result["from_cache"] = True
                return result

        # 缓存未命中，调用 Claude
        result = super().route(user_query, use_cache=False)

        # 保存到 Redis（有效期 24 小时）
        if self.cache_backend == "redis":
            import json
            self.cache.setex(
                cache_key,
                86400,  # 24 hours
                json.dumps(result)
            )

        return result
```

**预期效果**：
- 缓存命中率 50-70%
- 成本节省 50-70%
- 响应时间从 2s 降至 < 10ms

#### 2. 预热常见问题

```python
def preheat_cache(router: CachedSkillRouter, common_questions: List[str]):
    """预热缓存"""
    print(f"预热 {len(common_questions)} 个常见问题...")

    for question in common_questions:
        router.route(question, use_cache=False)

    print("预热完成！")

# 使用示例
common_questions = [
    "萨省税率是多少？",
    "RRSP 和 TFSA 的区别？",
    "如何申报租金收入？",
    # ... 更多常见问题
]

preheat_cache(router, common_questions)
```

#### 3. 语义相似问题去重

```python
from sentence_transformers import SentenceTransformer, util

class SemanticCachedRouter(CachedSkillRouter):
    """语义缓存路由器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 使用小型 embedding 模型做相似度匹配
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.question_embeddings = {}

    def route(self, user_query: str, similarity_threshold: float = 0.85) -> Dict:
        # 计算查询的 embedding
        query_emb = self.embedder.encode(user_query)

        # 查找相似的已缓存问题
        for cached_q, cached_emb in self.question_embeddings.items():
            similarity = util.cos_sim(query_emb, cached_emb).item()

            if similarity > similarity_threshold:
                print(f"找到相似问题: {cached_q} (相似度: {similarity:.2f})")
                # 使用缓存的路由结果
                cache_key = self._compute_cache_key(cached_q)
                return self.get_from_cache(cache_key)

        # 未找到相似问题，正常路由
        result = super().route(user_query)

        # 保存 embedding
        self.question_embeddings[user_query] = query_emb

        return result
```

**成本对比**：
- 小型 embedding（本地）：免费
- Claude 路由：$0.001/次
- 语义缓存命中后：$0（完全免费）
```

**3.2 整体成本估算**

```markdown
### Skill-like 方案成本分析

#### 单次问答成本

| 组件 | Token 消耗 | 成本（Sonnet） | 备注 |
|------|----------|--------------|------|
| 路由 | 1K | $0.001 | 可缓存 |
| Skills 上下文 | 12K (2个 Skills) | $0 | 仅计入 input |
| Claude 问答 | 15K input + 2K output | $0.045 + $0.03 | |
| **总计** | **~30K** | **~$0.08** | 缓存后可降至 $0.07 |

#### 月度成本估算（1000 用户）

| 场景 | 查询/天 | 缓存率 | 月成本 | 年成本 |
|------|---------|-------|--------|--------|
| 低频使用 | 5,000 | 50% | $10,500 | $126,000 |
| 中频使用 | 10,000 | 60% | $19,200 | $230,400 |
| 高频使用 | 20,000 | 70% | $33,600 | $403,200 |

#### 与 RAG 方案对比

| 成本项 | RAG 方案 | Skill-like 方案 | 节省 |
|--------|---------|-----------------|------|
| 向量数据库 | $50-200/月 | $0 | 100% |
| Embedding API | $5-20/月 | $0 | 100% |
| 路由/检索 | ~$0 (本地) | ~$300/月 (缓存后) | -$300/月 |
| Claude 问答 | $2,000/月 | $2,000/月 | 0% |
| **基础设施总计** | $2,055-2,220/月 | $2,300/月 | **-4%** |

**结论**：
- Skill-like 方案虽然增加了路由成本，但：
  - 消除了向量数据库和 embedding 成本
  - 实现更简单，维护成本更低
  - 回答质量更高（完整上下文）
  - 适合 < 1000 Skills 的场景
```

**3.3 极致成本优化方案**

```markdown
### 极致优化：混合路由策略

```python
class HybridRouter:
    """混合路由器：规则 + Claude"""

    def __init__(self, skill_loader, claude_router):
        self.skill_loader = skill_loader
        self.claude_router = claude_router
        self.rule_based_hits = 0
        self.claude_hits = 0

    def route(self, user_query: str) -> Dict:
        # 第一步：尝试规则匹配（免费）
        rule_result = self._rule_based_route(user_query)

        if rule_result and rule_result.get("confidence") == "high":
            self.rule_based_hits += 1
            print(f"✅ 规则路由命中 (节省 $0.001)")
            return rule_result

        # 第二步：使用 Claude 路由
        self.claude_hits += 1
        return self.claude_router.route(user_query)

    def _rule_based_route(self, query: str) -> Optional[Dict]:
        """基于规则的快速路由"""
        query_lower = query.lower()

        # 强规则匹配
        for skill_id, skill_info in self.skill_loader.index.items():
            triggers = skill_info["metadata"].get("triggers", [])

            # 完全匹配触发词
            for trigger in triggers:
                if trigger.lower() in query_lower:
                    return {
                        "primary_skills": [{
                            "skill_id": skill_id,
                            "title": skill_info["metadata"]["title"],
                            "path": skill_info["path"],
                            "tokens": skill_info["metadata"].get("estimated_tokens", 5000)
                        }],
                        "related_skills": [],
                        "reasoning": f"规则匹配: '{trigger}'",
                        "confidence": "high",
                        "estimated_tokens": skill_info["metadata"].get("estimated_tokens", 5000),
                        "from_cache": False
                    }

        return None

    def get_stats(self) -> Dict:
        total = self.rule_based_hits + self.claude_hits
        return {
            "rule_based_hits": self.rule_based_hits,
            "claude_hits": self.claude_hits,
            "rule_hit_rate": self.rule_based_hits / total if total > 0 else 0,
            "cost_saved": self.rule_based_hits * 0.001  # 每次节省 $0.001
        }
```

**效果**：
- 规则命中率：20-30%
- 额外成本节省：$60-90/月（基于 1万次/天）
- 规则命中时响应 < 50ms
```

4. **测试验证**：
   - 缓存命中率测试
   - 成本追踪测试
   - 混合路由效果测试

5. **最佳实践**：
   - 生产环境必须启用 Redis 缓存
   - 定期分析高频问题并添加规则
   - 监控缓存命中率和成本
   - 设置成本预警阈值

---

## 🔍 关键设计原则（供参考）

### Skill-like vs RAG 核心差异

| 维度 | RAG 方案 | Skill-like 方案 |
|------|---------|-----------------|
| **检索单位** | 文档片段 (chunks) | 完整文档 (Skills) |
| **索引方式** | 向量 + BM25 | 元数据 + JSON |
| **路由方式** | 向量相似度 | Claude 理解 |
| **上下文** | 片段拼接 | 完整文档 |
| **适用规模** | 无限制 | < 1000 Skills |
| **实现复杂度** | 高 | 低 |

### 术语对照表

| RAG 术语 | Skill-like 术语 |
|---------|----------------|
| Collection | Skill Domain |
| Document | Skill |
| Chunk | - (不分块) |
| Vector Store | Skill Loader |
| Embedding | - (不需要) |
| Retrieval | Routing + Loading |
| Context Window | Skill Context |

## 📚 参考资料

- 已更新的文档位置：
  - `docs/llm-agent-prompts/phase-03-knowledge-management/10-knowledge-collection-design.md`
  - `docs/llm-agent-prompts/phase-03-knowledge-management/11-markdown-storage-indexing.md`
  - `docs/llm-agent-prompts/phase-04-dynamic-loading/13-intent-recognition-module.md`
  - `docs/llm-agent-prompts/phase-04-dynamic-loading/14-knowledge-retrieval-engine.md`

- Skill 示例（参考任务10）
- SkillLoader 实现（参考任务11）
- ClaudeSkillRouter 实现（参考任务13）
- SkillEngine 实现（参考任务14）

## ✅ 验收标准

完成后，确保：

1. **文档 12** 包含完整的 Skill 元数据管理实现和验证逻辑
2. **文档 15** 包含可运行的 Open WebUI Filter/Function 代码
3. **文档 17** 完整的成本分析和优化策略（移除所有 RAG 相关成本）
4. 所有代码示例完整、可运行
5. 测试验证部分详尽
6. 与已更新文档风格一致

## 📝 交接清单

- [x] 已完成 6 个核心文档
- [x] 提供详细的剩余任务指引
- [x] 包含完整代码示例
- [ ] 待完成：12-document-metadata-manager.md
- [ ] 待完成：15-filter-pipeline-integration.md
- [ ] 待完成：17-cost-optimization-strategies.md

---

**预计完成时间**: 2-3 小时
**优先级**: 按顺序完成（12 → 15 → 17）

祝工作顺利！🚀
