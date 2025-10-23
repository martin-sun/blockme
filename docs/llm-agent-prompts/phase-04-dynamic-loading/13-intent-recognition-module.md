# 任务13：Claude Haiku 4.5 Skill 路由器

## 任务目标

实现智能的 Skill 路由系统，使用 **Claude Haiku 4.5** 分析用户问题并路由到相关的 Skills。该模块是实现"类似 Claude Skill 的动态知识加载机制"的核心，负责决定从知识库中加载哪些 Skills 注入到最终问答上下文。

**为什么选择 Claude Haiku 4.5：**
- ✅ **准确率高**：接近 Sonnet 水平（> 90%）
- ✅ **速度快**：1-2秒响应，优于 Sonnet
- ✅ **成本低**：$1.0/M input，仅为 Sonnet 的 33%
- ✅ **支持结构化输出**：原生支持 JSON 模式
- ✅ **路由任务简单**：Haiku 完全胜任
- ✅ **更大输出**：64K tokens（vs 3.5 Haiku 8K）

## 技术要求

**路由能力：**
- 理解用户问题意图
- 匹配相关 Skills（主要 + 相关）
- 支持多 Skill 自动组合
- 返回路由原因和置信度

**技术方案：**
- 使用 **Claude Haiku 4.5** 进行智能分析
- 提供 Skills 目录给 Claude
- 结构化 JSON 输出（skill_ids + reasoning）
- 自动扩展高优先级相关 Skills

**性能要求：**
- 路由响应时间 < 2秒（Haiku 通常 1秒内）
- 准确率 > 90%（Haiku 基准测试表现优秀）
- 支持中英文问题
- 返回置信度评分

**成本控制：**
- 使用 **Claude Haiku 4.5**（$1.0/M input, $5.0/M output）
- 简洁的路由 prompt（< 2000 tokens）
- 结合缓存降低重复路由成本（参考任务17）

**成本对比：**
| 模型 | Input | Output | 单次路由成本 | vs Sonnet |
|------|-------|--------|-------------|-----------|
| **Haiku 4.5** | $1.0/M | $5.0/M | **$0.001125** | **节省 62.5%** |
| Sonnet 4 | $3.0/M | $15.0/M | $0.003 | - |

*注：单次路由假设约 1K input + 0.2K output*

## 实现步骤

### 1. 设计 Skill 目录构建器

构建可供 Claude 分析的 Skills 目录：
- 列出所有可用 Skills
- 包含 title, domain, topics 等关键信息
- 格式化为清晰的文本列表

### 2. 实现 Claude 路由引擎

开发基于 Claude 的智能路由：
- 构建路由 prompt
- 调用 Claude API 分析
- 解析 JSON 返回结果
- 处理异常和降级方案

### 3. 实现相关 Skill 扩展

自动添加相关 Skills：
- 读取主 Skill 的 related_skills
- 按优先级过滤（high > medium > low）
- 避免重复添加
- 控制总 token 数量

### 4. 实现路由结果缓存

优化重复路由性能：
- 基于问题的哈希缓存
- LRU 淘汰策略
- 可配置的缓存大小

## 关键代码提示

**Claude Skill 路由器核心实现：**

```python
import anthropic
import json
from typing import Dict, List, Optional
from pathlib import Path
import hashlib
from functools import lru_cache

class SkillCatalogBuilder:
    """Skill 目录构建器"""

    def __init__(self, skills_index: Dict[str, Dict]):
        self.skills_index = skills_index

    def build_catalog(self, format: str = "text") -> str:
        """
        构建 Skills 目录描述

        Args:
            format: 输出格式 (text/markdown)

        Returns:
            格式化的 Skills 目录
        """
        if format == "markdown":
            return self._build_markdown_catalog()
        else:
            return self._build_text_catalog()

    def _build_text_catalog(self) -> str:
        """构建文本格式目录"""
        catalog_lines = ["可用的知识库 Skills：\n"]

        # 按领域分组
        domains = {}
        for skill_id, skill_info in self.skills_index.items():
            metadata = skill_info["metadata"]
            domain = metadata.get("domain", "unknown")

            if domain not in domains:
                domains[domain] = []

            domains[domain].append({
                "skill_id": skill_id,
                "title": metadata.get("title", ""),
                "topics": metadata.get("topics", [])
            })

        # 生成目录
        for domain, skills in domains.items():
            catalog_lines.append(f"\n【{domain}】")

            for skill in skills:
                topics_str = ", ".join(skill["topics"][:3])  # 限制主题数量
                catalog_lines.append(
                    f"  - {skill['skill_id']}: {skill['title']}\n"
                    f"    主题: {topics_str}"
                )

        return "\n".join(catalog_lines)

    def _build_markdown_catalog(self) -> str:
        """构建 Markdown 格式目录"""
        lines = ["# 可用的知识库 Skills\n"]

        domains = {}
        for skill_id, skill_info in self.skills_index.items():
            metadata = skill_info["metadata"]
            domain = metadata.get("domain", "unknown")

            if domain not in domains:
                domains[domain] = []

            domains[domain].append({
                "skill_id": skill_id,
                "title": metadata.get("title", ""),
                "topics": metadata.get("topics", []),
                "keywords": metadata.get("keywords", [])
            })

        for domain, skills in domains.items():
            lines.append(f"\n## {domain}\n")

            for skill in skills:
                topics = ", ".join(skill["topics"][:3])
                lines.append(f"- **{skill['skill_id']}**: {skill['title']}")
                lines.append(f"  - 主题: {topics}")

        return "\n".join(lines)


class ClaudeSkillRouter:
    """Claude 辅助的 Skill 路由器"""

    def __init__(
        self,
        skills_index: Dict[str, Dict],
        api_key: str,
        cache_size: int = 100
    ):
        self.skills_index = skills_index
        self.client = anthropic.Anthropic(api_key=api_key)
        self.catalog_builder = SkillCatalogBuilder(skills_index)
        self.cache: Dict[str, Dict] = {}
        self.cache_size = cache_size

    def route(
        self,
        user_query: str,
        max_primary_skills: int = 2,
        use_cache: bool = True
    ) -> Dict:
        """
        路由用户问题到相关 Skills

        Args:
            user_query: 用户问题
            max_primary_skills: 最多返回主 Skills 数量
            use_cache: 是否使用缓存

        Returns:
            {
                "primary_skills": [
                    {
                        "skill_id": "...",
                        "title": "...",
                        "path": "...",
                        "tokens": 6500
                    },
                    ...
                ],
                "related_skills": [...],  # 自动添加的相关 Skills
                "reasoning": "...",        # 路由原因
                "confidence": "high/medium/low",
                "estimated_tokens": 15000,
                "from_cache": false
            }
        """
        # 检查缓存
        if use_cache:
            cache_key = self._compute_cache_key(user_query)
            if cache_key in self.cache:
                cached_result = self.cache[cache_key].copy()
                cached_result["from_cache"] = True
                return cached_result

        # 构建 Skills 目录
        skills_catalog = self.catalog_builder.build_catalog()

        # 构建路由 prompt
        routing_prompt = self._build_routing_prompt(user_query, skills_catalog)

        # 调用 Claude
        try:
            routing_result = self._call_claude(routing_prompt)

            # 扩展相关 Skills
            expanded_result = self._expand_related_skills(
                routing_result["primary_skills"]
            )

            expanded_result["reasoning"] = routing_result.get("reasoning", "")
            expanded_result["confidence"] = routing_result.get("confidence", "medium")
            expanded_result["from_cache"] = False

            # 缓存结果
            if use_cache:
                self._cache_result(cache_key, expanded_result)

            return expanded_result

        except Exception as e:
            print(f"⚠️  Claude 路由失败: {e}")
            # 降级方案：基于关键词简单匹配
            return self._fallback_routing(user_query)

    def _build_routing_prompt(self, user_query: str, skills_catalog: str) -> str:
        """构建路由 prompt"""
        return f"""你是一个专业的知识库路由系统。

用户问题：
"{user_query}"

{skills_catalog}

任务：
1. 分析用户问题涉及的主题和领域
2. 从上述 Skills 中选择 1-2 个最相关的（primary skills）
3. 返回 JSON 格式的路由结果

返回格式（必须是纯 JSON，不要包含其他文字）：
{{
  "primary_skills": ["skill_id_1", "skill_id_2"],
  "reasoning": "用户问题涉及..., 因此选择...",
  "confidence": "high"
}}

注意：
- primary_skills 数组包含 1-2 个最相关的 skill_id
- reasoning 简要说明选择原因（1-2句话）
- confidence 可选值：high（非常确定）、medium（比较确定）、low（不太确定）
- 如果没有相关 Skills，返回空数组：{{"primary_skills": [], "reasoning": "...", "confidence": "low"}}
"""

    def _call_claude(self, prompt: str, retry_count: int = 2) -> Dict:
        """
        调用 Claude Haiku 4.5 API（带 JSON 解析重试）

        Args:
            prompt: 路由提示词
            retry_count: JSON 解析失败时的重试次数

        Returns:
            路由结果 Dict
        """
        for attempt in range(retry_count + 1):
            try:
                response = self.client.messages.create(
                    model="claude-haiku-4-5",  # Haiku 4.5 (2025-10-01)
                    max_tokens=500,
                    temperature=0.0,  # 低温度，确保稳定输出
                    messages=[{"role": "user", "content": prompt}]
                )

                # 提取返回内容
                result_text = response.content[0].text.strip()

                # 解析 JSON（处理可能的 markdown 包装）
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()

                # 尝试解析 JSON
                result = json.loads(result_text)

                # 验证必需字段
                if "primary_skills" in result and "reasoning" in result:
                    return result
                else:
                    raise ValueError("Missing required fields in JSON response")

            except (json.JSONDecodeError, ValueError) as e:
                if attempt < retry_count:
                    print(f"⚠️  JSON 解析失败（第 {attempt + 1} 次），重试中... 错误: {e}")
                    # 增强提示词，要求更严格的 JSON 输出
                    prompt += "\n\n重要：必须返回纯 JSON 格式，不要包含其他文字！"
                else:
                    # 最后一次尝试失败，抛出异常
                    print(f"❌ JSON 解析失败（已重试 {retry_count} 次）")
                    raise

        # 不应该到达这里
        raise RuntimeError("Unexpected error in _call_claude")

    def _expand_related_skills(self, primary_skill_ids: List[str]) -> Dict:
        """扩展相关 Skills（自动组合）"""
        primary_skills = []
        related_skills = []
        related_ids_set = set()

        # 收集主 Skills
        for skill_id in primary_skill_ids:
            if skill_id in self.skills_index:
                skill_data = self.skills_index[skill_id]
                metadata = skill_data["metadata"]

                primary_skills.append({
                    "skill_id": skill_id,
                    "title": metadata.get("title", ""),
                    "path": skill_data.get("path", ""),
                    "tokens": metadata.get("estimated_tokens", 5000)
                })

                # 收集高优先级相关 Skills
                for related in metadata.get("related_skills", []):
                    if related.get("priority") == "high":
                        related_id = related["id"]

                        if related_id not in related_ids_set and related_id in self.skills_index:
                            related_data = self.skills_index[related_id]
                            related_metadata = related_data["metadata"]

                            related_skills.append({
                                "skill_id": related_id,
                                "title": related_metadata.get("title", ""),
                                "path": related_data.get("path", ""),
                                "tokens": related_metadata.get("estimated_tokens", 5000),
                                "reason": related.get("reason", "")
                            })

                            related_ids_set.add(related_id)

        # 计算总 token 估算
        total_tokens = (
            sum(s["tokens"] for s in primary_skills) +
            sum(s["tokens"] for s in related_skills)
        )

        return {
            "primary_skills": primary_skills,
            "related_skills": related_skills,
            "estimated_tokens": total_tokens
        }

    def _fallback_routing(self, user_query: str) -> Dict:
        """降级路由方案（基于关键词）"""
        print("⚠️  使用降级路由方案")

        query_lower = user_query.lower()
        matched_skills = []

        # 简单的触发词匹配
        for skill_id, skill_info in self.skills_index.items():
            metadata = skill_info["metadata"]
            triggers = metadata.get("triggers", [])

            for trigger in triggers:
                if trigger.lower() in query_lower:
                    matched_skills.append({
                        "skill_id": skill_id,
                        "title": metadata.get("title", ""),
                        "path": skill_info.get("path", ""),
                        "tokens": metadata.get("estimated_tokens", 5000)
                    })
                    break

        # 限制数量
        primary_skills = matched_skills[:2]

        return {
            "primary_skills": primary_skills,
            "related_skills": [],
            "reasoning": "使用关键词匹配（降级方案）",
            "confidence": "low",
            "estimated_tokens": sum(s["tokens"] for s in primary_skills),
            "from_cache": False
        }

    def _compute_cache_key(self, query: str) -> str:
        """计算查询的缓存 key"""
        # 使用查询的哈希值作为 key
        return hashlib.md5(query.lower().encode()).hexdigest()

    def _cache_result(self, key: str, result: Dict):
        """缓存路由结果"""
        if len(self.cache) >= self.cache_size:
            # 简单的 FIFO 策略（可升级为 LRU）
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[key] = result

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()

    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        return {
            "cache_size": len(self.cache),
            "cache_limit": self.cache_size
        }


class RoutingOptimizer:
    """路由优化器（高级功能）"""

    def __init__(self, router: ClaudeSkillRouter):
        self.router = router
        self.routing_history: List[Dict] = []

    def route_with_history(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        基于对话历史优化路由

        Args:
            user_query: 当前问题
            conversation_history: 对话历史 [{"role": "user/assistant", "content": "..."}]

        Returns:
            路由结果
        """
        # 基础路由
        routing_result = self.router.route(user_query)

        # 如果有对话历史，可以优化 Skills 选择
        if conversation_history and len(conversation_history) > 0:
            # 提取之前使用的 Skills
            previous_skills = self._extract_previous_skills(conversation_history)

            # 如果当前问题可能是延续性问题，优先使用之前的 Skills
            if self._is_followup_question(user_query):
                routing_result = self._prefer_previous_skills(
                    routing_result,
                    previous_skills
                )

        # 记录路由历史
        self.routing_history.append({
            "query": user_query,
            "result": routing_result
        })

        return routing_result

    def _extract_previous_skills(self, history: List[Dict]) -> List[str]:
        """从历史中提取使用过的 Skills"""
        # 简化实现：从历史记录中提取
        # 实际需要从对话中解析出使用过的 Skills
        return []

    def _is_followup_question(self, query: str) -> bool:
        """判断是否是延续性问题"""
        followup_keywords = ["那", "这", "刚才", "上面", "继续", "还", "也"]
        return any(kw in query for kw in followup_keywords)

    def _prefer_previous_skills(
        self,
        current_result: Dict,
        previous_skills: List[str]
    ) -> Dict:
        """优先使用之前的 Skills"""
        # 简化实现：如果置信度不高，优先使用历史 Skills
        if current_result.get("confidence") == "low" and previous_skills:
            # 添加历史 Skills 到相关 Skills
            for skill_id in previous_skills[:2]:
                if skill_id in self.router.skills_index:
                    # ... 添加逻辑
                    pass

        return current_result
```

## 测试验证

### 1. 基础路由测试

```python
from skill_router import ClaudeSkillRouter, SkillCatalogBuilder
from skill_loader import SkillLoader

# 初始化
loader = SkillLoader("knowledge_base/skills")
router = ClaudeSkillRouter(
    skills_index=loader.index,
    api_key="your-api-key"
)

# 测试路由
result = router.route("我在萨省，年收入5万，要交多少税？")

print(f"主要 Skills: {[s['skill_id'] for s in result['primary_skills']]}")
print(f"相关 Skills: {[s['skill_id'] for s in result['related_skills']]}")
print(f"路由原因: {result['reasoning']}")
print(f"置信度: {result['confidence']}")
print(f"预估 tokens: {result['estimated_tokens']}")

# 预期输出:
# 主要 Skills: ['sk-personal-tax']
# 相关 Skills: ['federal-personal-tax']  # 自动添加
# 路由原因: 用户询问萨省的个人所得税计算...
# 置信度: high
# 预估 tokens: 13000
```

### 2. 多领域路由测试

```python
# 跨领域问题
result = router.route("RRSP 和 TFSA 有什么区别？")

print(f"主要 Skills: {[s['skill_id'] for s in result['primary_skills']]}")
# 预期: ['rrsp', 'tfsa']
```

### 3. 缓存测试

```python
import time

# 首次路由（慢）
start = time.time()
result1 = router.route("萨省税务问题")
time1 = time.time() - start

# 第二次路由（快，从缓存）
start = time.time()
result2 = router.route("萨省税务问题")
time2 = time.time() - start

print(f"首次路由: {time1:.2f}s")
print(f"缓存路由: {time2:.2f}s")
print(f"result2['from_cache']: {result2['from_cache']}")

assert result2["from_cache"] == True
assert time2 < time1
```

### 4. 降级方案测试

```python
# 模拟 API 失败
router_fail = ClaudeSkillRouter(
    skills_index=loader.index,
    api_key="invalid-key"  # 错误的 key
)

result = router_fail.route("萨省税务")

# 应该使用降级方案
assert result["confidence"] == "low"
print(f"降级路由结果: {result['primary_skills']}")
```

### 5. Skill 目录构建测试

```python
from skill_router import SkillCatalogBuilder

builder = SkillCatalogBuilder(loader.index)

# 文本格式
text_catalog = builder.build_catalog(format="text")
print(text_catalog)

# Markdown 格式
md_catalog = builder.build_catalog(format="markdown")
print(md_catalog)
```

## 注意事项

**API 成本控制：**
- 路由使用小型 Sonnet 模型（成本低）
- 每次路由约 500-1000 tokens（约 $0.001）
- 启用缓存可减少 50%+ 成本
- 对于重复问题，缓存命中率高

**准确性保证：**
- Claude 理解能力强，准确率 > 90%
- 提供完整的 Skills 目录给 Claude 参考
- 使用低温度（0.0）确保稳定输出
- 降级方案确保服务可用性

**性能优化：**
- 路由通常 < 2 秒（Claude API 响应时间）
- 启用缓存后重复问题 < 10ms
- 可以预热常见问题缓存
- 异步路由可进一步优化

**与传统意图识别对比：**

| 特性 | Claude 路由 | 传统意图识别 |
|------|-----------|------------|
| 实现复杂度 | ⭐ 简单 | ⭐⭐⭐ 复杂 |
| 准确率 | ⭐⭐⭐ 高（>90%） | ⭐⭐ 中（70-80%） |
| 响应时间 | ⭐⭐ 慢（~2s） | ⭐⭐⭐ 快（<100ms） |
| 维护成本 | ⭐ 低 | ⭐⭐⭐ 高 |
| 成本 | $0.001/次 | 免费（自托管） |

**最佳实践：**
- 生产环境启用缓存
- 监控路由准确率
- 定期分析失败案例
- 优化 Skills 的 triggers 和 keywords

## 依赖关系

**前置任务：**
- 任务10：Skill 架构设计
- 任务11：轻量级 Skill 索引系统

**后置任务：**
- 任务14：Skill 加载和上下文构建引擎
- 任务15：Filter Pipeline 集成
