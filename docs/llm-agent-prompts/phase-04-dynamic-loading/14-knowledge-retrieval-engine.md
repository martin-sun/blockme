# 任务14：Skill 引擎（使用 GLM-4.6 问答）

## 任务目标

实现完整的 Skill 加载和问答引擎，整合路由、加载、上下文构建和 **GLM-4.6 问答**的完整流程。该引擎是 Skill-like 知识库系统的核心，负责将用户问题转换为知识增强的回答。

**架构流程：**
```
用户问题
  ↓
Claude Haiku 4.5 路由 → 匹配 Skills
  ↓
加载完整 Skills → 构建上下文
  ↓
GLM-4.6 问答 → 生成答案
```

**为什么使用 GLM-4.6 进行问答：**
- ✅ **中英文能力强**：MMLU 81.2%（优于 Gemini Flash）
- ✅ **推理能力优秀**：GSM8K 89.5%（优于 Gemini Flash）
- ✅ **技术领域表现好**：编程、数学、科学
- ✅ **成本适中**：$0.50/M tokens（比 Claude 便宜 83%）
- ✅ **架构简单**：统一使用 GLM，无需语言检测

## 技术要求

**核心功能：**
- 集成 Skill 路由器（Claude Haiku）和加载器
- 构建知识上下文（完整文档注入）
- 调用 **GLM-4.6 API** 回答问题
- 返回结构化结果（答案 + 元数据）

**性能要求：**
- 端到端响应时间 < 5秒
  - 路由：1-2秒（Haiku）
  - 问答：2-3秒（GLM）
- 支持批量 Skill 加载（1-3个）
- Token 使用优化（GLM 128K context）
- 提供详细的调试信息

**输出要求：**
- 回答内容
- 使用的 Skills 列表
- Token 消耗统计
- 路由信息和置信度

**成本对比：**
| 问答模型 | 成本/M tokens | 单次问答成本 | vs Claude Sonnet |
|---------|--------------|-------------|------------------|
| **GLM-4.6** | **$0.50** | **$0.0085** | **节省 89%** |
| Claude Haiku | $0.80-4.0 | $0.004 | 节省 95% |
| Claude Sonnet | $3.0-15.0 | $0.075 | - |
| Gemini Flash | $0.075-0.30 | $0.0018 | 节省 98% |

## 实现步骤

### 1. 设计核心引擎架构

整合各个组件：
- SkillLoader（任务11）
- ClaudeSkillRouter（任务13）
- 上下文构建器（新增）
- Claude API 客户端

### 2. 实现上下文构建器

将 Skills 格式化为 Claude 上下文：
- 添加结构化标记
- 来源标注
- Token 估算和控制
- Markdown 格式化

### 3. 实现完整问答流程

开发端到端问答系统：
- 路由 → 加载 → 构建上下文 → Claude 回答
- 错误处理和降级方案
- 结果格式化

### 4. 实现监控和统计

提供系统可观测性：
- Token 使用统计
- 路由准确性跟踪
- 性能指标记录

## 关键代码提示

**Skill 引擎核心实现：**

```python
from zhipuai import ZhipuAI
from typing import Dict, List, Optional
from dataclasses import dataclass
import time

# 假设已经实现了这些模块
from skill_loader import SkillLoader
from skill_router import ClaudeSkillRouter


@dataclass
class SkillEngineResult:
    """引擎执行结果"""
    answer: str
    loaded_skills: List[Dict]
    routing_info: Dict
    tokens_used: Dict
    execution_time: float
    success: bool
    error: Optional[str] = None


class SkillContextBuilder:
    """Skill 上下文构建器"""

    def __init__(self, max_tokens: int = 150000):
        """
        Args:
            max_tokens: GLM/Claude 200K context 中预留给知识的最大 tokens
        """
        self.max_tokens = max_tokens

    def build_context(
        self,
        loaded_skills: List[Dict],
        routing_info: Dict
    ) -> str:
        """
        构建知识上下文（带 token 预算控制）

        Args:
            loaded_skills: 已加载的 Skills 列表
            routing_info: 路由信息

        Returns:
            格式化的 Markdown 上下文
        """
        context_parts = ["# 知识库参考资料\n\n"]

        # 添加路由说明
        if routing_info.get("reasoning"):
            context_parts.append(f"> **选择原因**: {routing_info['reasoning']}\n\n")

        # 分离主要和相关 Skills
        primary_ids = {s["skill_id"] for s in routing_info.get("primary_skills", [])}

        # 按优先级排序：主要 Skills > 相关 Skills
        primary_skills = [s for s in loaded_skills if s["skill_id"] in primary_ids]
        related_skills = [s for s in loaded_skills if s["skill_id"] not in primary_ids]

        # Token 预算控制：优先保留主要 Skills
        current_tokens = self.estimate_tokens("".join(context_parts))
        final_primary = []
        final_related = []

        # 添加主要 Skills（优先级最高）
        for skill in primary_skills:
            skill_tokens = skill["metadata"].get("estimated_tokens", 5000)
            if current_tokens + skill_tokens <= self.max_tokens:
                final_primary.append(skill)
                current_tokens += skill_tokens
            else:
                print(f"⚠️  Token 预算不足，跳过主 Skill: {skill['skill_id']}")

        # 添加相关 Skills（如有剩余预算）
        for skill in related_skills:
            skill_tokens = skill["metadata"].get("estimated_tokens", 5000)
            if current_tokens + skill_tokens <= self.max_tokens:
                final_related.append(skill)
                current_tokens += skill_tokens
            else:
                print(f"⚠️  Token 预算不足，跳过相关 Skill: {skill['skill_id']}")
                break

        # 构建最终上下文
        if final_primary:
            context_parts.append("## 主要参考资料\n\n")
            for skill in final_primary:
                self._add_skill_content(context_parts, skill)

        if final_related:
            context_parts.append("## 补充参考资料\n\n")
            for skill in final_related:
                self._add_skill_content(context_parts, skill)

        # 添加 token 使用提示
        final_context = "".join(context_parts)
        final_tokens = self.estimate_tokens(final_context)
        print(f"✓ 上下文构建完成：{len(final_primary)} 主要 + {len(final_related)} 相关，约 {final_tokens} tokens")

        return final_context

    def _add_skill_content(self, context_parts: List[str], skill: Dict):
        """添加单个 Skill 的内容"""
        metadata = skill["metadata"]

        context_parts.append(f"### 📄 {metadata['title']}\n\n")
        context_parts.append(f"> 来源: {skill['skill_id']}\n\n")
        context_parts.append(skill["content"])
        context_parts.append("\n\n---\n\n")

    def estimate_tokens(self, context: str) -> int:
        """
        粗略估算 token 数

        中文：约 2 字符 = 1 token
        英文：约 4 字符 = 1 token
        """
        return int(len(context) * 0.5)


class SkillEngine:
    """完整的 Skill 引擎"""

    def __init__(
        self,
        skills_dir: str,
        claude_api_key: str,
        glm_api_key: str,
        cache_routing: bool = True
    ):
        # 初始化组件
        self.skill_loader = SkillLoader(skills_dir)
        self.skill_router = ClaudeSkillRouter(
            skills_index=self.skill_loader.index,
            api_key=claude_api_key
        )
        self.context_builder = SkillContextBuilder()
        self.glm_client = ZhipuAI(api_key=glm_api_key)

        # 统计
        self.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_tokens": 0
        }

    def answer_question(
        self,
        user_query: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> SkillEngineResult:
        """
        回答用户问题（完整流程）

        Args:
            user_query: 用户问题
            system_prompt: 自定义系统提示（可选）
            conversation_history: 对话历史（可选）

        Returns:
            SkillEngineResult
        """
        start_time = time.time()
        self.stats["total_queries"] += 1

        try:
            # 1. 路由到 Skills
            routing_result = self.skill_router.route(user_query)

            if not routing_result["primary_skills"]:
                # 没有匹配的 Skills
                return self._no_skill_response(user_query, start_time)

            # 2. 加载 Skills
            all_skill_ids = [
                s["skill_id"] for s in routing_result["primary_skills"]
            ] + [
                s["skill_id"] for s in routing_result.get("related_skills", [])
            ]

            loaded_skills = self.skill_loader.load_skills(all_skill_ids)

            # 3. 构建上下文
            knowledge_context = self.context_builder.build_context(
                loaded_skills,
                routing_result
            )

            # 4. 调用 GLM-4.6 回答
            answer, tokens_used = self._query_glm(
                user_query,
                knowledge_context,
                system_prompt,
                conversation_history
            )

            # 5. 构建结果
            execution_time = time.time() - start_time
            self.stats["successful_queries"] += 1
            self.stats["total_tokens"] += tokens_used["total"]

            return SkillEngineResult(
                answer=answer,
                loaded_skills=[
                    {
                        "skill_id": s["skill_id"],
                        "title": s["metadata"]["title"],
                        "type": "primary" if s["skill_id"] in [p["skill_id"] for p in routing_result["primary_skills"]] else "related"
                    }
                    for s in loaded_skills
                ],
                routing_info={
                    "reasoning": routing_result.get("reasoning", ""),
                    "confidence": routing_result.get("confidence", "medium"),
                    "from_cache": routing_result.get("from_cache", False)
                },
                tokens_used=tokens_used,
                execution_time=execution_time,
                success=True
            )

        except Exception as e:
            self.stats["failed_queries"] += 1
            execution_time = time.time() - start_time

            return SkillEngineResult(
                answer="",
                loaded_skills=[],
                routing_info={},
                tokens_used={"input": 0, "output": 0, "total": 0},
                execution_time=execution_time,
                success=False,
                error=str(e)
            )

    def _query_glm(
        self,
        user_query: str,
        knowledge_context: str,
        system_prompt: Optional[str],
        conversation_history: Optional[List[Dict]]
    ) -> tuple[str, Dict]:
        """调用 GLM-4.6 API"""

        # 默认系统提示
        if not system_prompt:
            system_prompt = """你是一个专业的问答助手。

重要指引：
1. 基于提供的知识库资料回答问题
2. 如果知识库中没有相关信息，明确说明
3. 提供准确、详细、易懂的回答
4. 使用 Markdown 格式组织答案
5. 引用具体的知识来源

回答风格：
- 清晰、专业、有条理
- 使用列表、表格等格式
- 提供实际例子说明
- 必要时添加免责声明
"""

        # 构建完整 prompt
        user_prompt = f"""
{knowledge_context}

---

用户问题：{user_query}

请基于以上知识库资料回答用户问题。
"""

        # 构建消息列表
        messages = []

        # 添加系统提示（GLM 使用 system role）
        messages.append({"role": "system", "content": system_prompt})

        # 添加对话历史
        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": user_prompt})

        # 调用 GLM-4.6
        response = self.glm_client.chat.completions.create(
            model="glm-4.6",
            max_tokens=4000,
            temperature=0.7,
            messages=messages
        )

        answer = response.choices[0].message.content

        # GLM API 返回的 token 使用情况
        tokens_used = {
            "input": response.usage.prompt_tokens,
            "output": response.usage.completion_tokens,
            "total": response.usage.total_tokens
        }

        return answer, tokens_used

    def _no_skill_response(self, user_query: str, start_time: float) -> SkillEngineResult:
        """没有匹配 Skills 时的响应"""
        answer = """抱歉，我没有找到与您问题相关的知识库资料。

可能的原因：
1. 您的问题超出了当前知识库的范围
2. 问题表述不够清晰，请尝试重新描述

建议：
- 尝试使用更具体的关键词
- 查看可用的知识库主题列表
"""

        return SkillEngineResult(
            answer=answer,
            loaded_skills=[],
            routing_info={"reasoning": "未找到相关 Skills", "confidence": "low"},
            tokens_used={"input": 0, "output": 0, "total": 0},
            execution_time=time.time() - start_time,
            success=True
        )

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "success_rate": (
                self.stats["successful_queries"] / self.stats["total_queries"]
                if self.stats["total_queries"] > 0
                else 0
            ),
            "avg_tokens_per_query": (
                self.stats["total_tokens"] / self.stats["successful_queries"]
                if self.stats["successful_queries"] > 0
                else 0
            ),
            "skill_stats": self.skill_loader.get_statistics()
        }


class BatchSkillEngine(SkillEngine):
    """支持批量问答的引擎"""

    def answer_batch(
        self,
        queries: List[str],
        max_concurrent: int = 3
    ) -> List[SkillEngineResult]:
        """
        批量回答问题

        Args:
            queries: 问题列表
            max_concurrent: 最大并发数

        Returns:
            结果列表
        """
        results = []

        # 简化实现：串行处理（生产环境可使用异步）
        for query in queries:
            result = self.answer_question(query)
            results.append(result)

        return results
```

## 测试验证

### 1. 基础问答测试

```python
from skill_engine import SkillEngine

# 初始化引擎
engine = SkillEngine(
    skills_dir="knowledge_base/skills",
    claude_api_key="your-claude-api-key",
    glm_api_key="your-glm-api-key"
)

# 测试问答
result = engine.answer_question("我在萨省，年收入5万，要交多少税？")

print(f"回答:\n{result.answer}\n")
print(f"使用的 Skills: {[s['skill_id'] for s in result.loaded_skills]}")
print(f"路由信息: {result.routing_info}")
print(f"Token 使用: {result.tokens_used}")
print(f"执行时间: {result.execution_time:.2f}s")
```

### 2. 多 Skill 组合测试

```python
result = engine.answer_question("RRSP 和 TFSA 的区别是什么？")

print(f"使用的 Skills: {[s['skill_id'] for s in result.loaded_skills]}")
# 预期: ['rrsp', 'tfsa']
```

### 3. 对话历史测试

```python
# 带对话历史
history = [
    {"role": "user", "content": "什么是 TFSA？"},
    {"role": "assistant", "content": "TFSA 是免税储蓄账户..."}
]

result = engine.answer_question(
    "那每年的限额是多少？",
    conversation_history=history
)

print(result.answer)
```

### 4. 统计信息测试

```python
# 回答多个问题
questions = [
    "萨省税率是多少？",
    "RRSP 限额",
    "如何申报租金收入？"
]

for q in questions:
    engine.answer_question(q)

# 查看统计
stats = engine.get_statistics()
print(f"总查询: {stats['total_queries']}")
print(f"成功率: {stats['success_rate']:.2%}")
print(f"平均 tokens: {stats['avg_tokens_per_query']:.0f}")
```

## 注意事项

**Token 管理：**
- Claude 200K context 可容纳约 5-10 个中等 Skills
- 单个 Skill 通常 5K-10K tokens
- 预留 50K tokens 给对话历史和回答
- 超出限制时优先保留主 Skills

**性能优化：**
- 路由缓存可节省 1-2 秒
- 异步加载 Skills 可并行化
- 对话历史压缩（保留摘要）
- 预加载热门 Skills

**错误处理：**
- Claude API 失败：返回友好错误消息
- Skill 加载失败：跳过并记录
- 路由失败：使用降级方案
- 超时处理：设置合理的超时时间

**成本估算：**

| 操作 | Token 消耗 | 成本 |
|------|----------|------|
| 路由（Haiku 4.5） | ~1K input + 0.2K output | $0.001125 |
| 2个 Skills 上下文 | ~12K | - |
| GLM-4.6 问答 | ~15K input + 2K output | $0.0085 |
| **单次问答总计** | **~30K** | **~$0.0096** |

**vs 原方案（全 Sonnet）：**
- 原成本：~$0.078/次
- 新成本：~$0.0096/次
- **节省：88%**

**与 RAG 方案对比：**

| 特性 | Skill-like | RAG |
|------|-----------|-----|
| 实现复杂度 | ⭐ 低 | ⭐⭐⭐ 高 |
| Token 消耗 | ⭐⭐ 中（完整文档） | ⭐⭐⭐ 低（片段） |
| 回答质量 | ⭐⭐⭐ 高（完整上下文） | ⭐⭐ 中（可能断章） |
| 适用规模 | < 1000 Skills | 无限制 |
| 维护成本 | ⭐ 低 | ⭐⭐⭐ 高 |

**最佳实践：**
- 生产环境启用所有缓存
- 监控 token 使用和成本
- 定期分析失败案例
- 优化 Skills 大小（20-50KB）
- 设置合理的超时和重试

## 依赖关系

**前置任务：**
- 任务11：轻量级 Skill 索引系统
- 任务13：Claude 辅助的 Skill 路由器

**后置任务：**
- 任务15：Filter Pipeline 集成
- 任务18：UI 工作流优化
