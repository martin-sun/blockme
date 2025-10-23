# 任务17：Skill-like 方案成本优化策略

## 任务目标

实现 Skill-like 方案的成本优化策略，主要降低 Claude 路由 API 的使用成本。通过路由结果缓存、预热常见问题、语义相似问题去重、混合路由策略等技术手段，在保证服务质量的前提下最大程度节省 API 费用。

**与 RAG 方案的成本差异：**
- ✅ 消除：Embedding 模型成本（$0）
- ✅ 消除：向量数据库成本（$0）
- ✅ 消除：BM25/FTS5 检索成本（$0）
- ❌ 新增：路由成本（~$0.00113/次，可通过缓存优化）
- ✅ 降低：问答成本（使用 GLM-4.6 代替 Claude Sonnet）

## 🎯 推荐的混合模型架构

基于成本和质量的平衡考虑，本方案采用以下混合模型架构：

```
用户问题
    ↓
┌─────────────────────────────────────────┐
│ Skill 路由层                              │
│ → Claude Haiku 4.5                       │
│   成本：$0.00113/次                       │
│   优势：准确率高、速度快、成本低            │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Skill 加载                                │
│ → 完整 Markdown Skills（无需向量化）      │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 最终问答层                                │
│ → GLM-4.6（中英文统一）                   │
│   成本：$0.0085/次                        │
│   优势：中英文能力强、推理优秀、架构简单     │
└─────────────────────────────────────────┘

辅助任务：
┌─────────────────────────────────────────┐
│ 文档 OCR 处理                             │
│ → Gemini 2.5 Flash                       │
│   成本：$0.0012/次                        │
│   优势：Vision 能力强、OCR 准确            │
└─────────────────────────────────────────┘
```

### 方案选择理由

**1. Claude Haiku 4.5 用于 Skill 路由**
- ✅ 路由准确率 > 90%（接近 Sonnet）
- ✅ 速度快（1-2秒）
- ✅ 成本是 Sonnet 的 1/3
- ✅ 支持结构化 JSON 输出

**2. GLM-4.6 用于最终问答**
- ✅ 英文技术能力强（MMLU 81.2%，优于 Gemini Flash 78.9%）
- ✅ 中文能力顶级（国内模型优势）
- ✅ 推理能力强（GSM8K 89.5%，优于 Gemini Flash 85.7%）
- ✅ 架构简单（无需语言检测和模型切换）
- ✅ 成本适中（$0.50/M tokens vs Claude $3.0/M）

**3. Gemini 2.5 Flash 用于文档 OCR**
- ✅ Vision 能力强
- ✅ OCR 准确率高
- ✅ 成本极低（$0.075/M tokens）

### 成本对比分析

#### 单次问答成本

| 方案 | 路由模型 | 路由成本 | 问答模型 | 问答成本 | 总成本 | vs 原方案 |
|------|---------|---------|---------|---------|--------|-----------|
| **原方案** | Sonnet | $0.003 | Sonnet | $0.075 | **$0.078** | - |
| **推荐方案** | **Haiku 4.5** | **$0.00113** | **GLM-4.6** | **$0.0085** | **$0.00963** | **↓ 88%** |
| 备选方案1 | Haiku 4.5 | $0.00113 | Haiku 4.5 | $0.0048 | $0.00593 | ↓ 92% |
| 备选方案2 | Haiku 4.5 | $0.00113 | Gemini Flash | $0.0018 | $0.00293 | ↓ 96% |

**成本计算说明：**
- Claude Haiku 4.5：$1.0/M input, $5.0/M output
- GLM-4.6：~$0.50/M tokens（input/output 相近）
- Gemini 2.5 Flash：$0.075/M input, $0.30/M output
- 假设路由：1K input + 0.2K output
- 假设问答：15K input + 2K output

#### 月度成本估算（1万次查询/天）

| 方案 | 日成本 | 月成本 | 年成本 | vs 原方案节省 |
|------|--------|--------|--------|---------------|
| 原方案（全 Sonnet） | $780 | $23,400 | $280,800 | - |
| **推荐方案（Haiku + GLM）** | **$96.3** | **$2,889** | **$34,668** | **$246,132/年** |

**投资回报率（ROI）：**
- 年度节省：$246,132
- 节省比例：88%
- 如果用户规模扩大 10 倍，年度节省 > $240 万

## 技术要求

**优化维度：**
- **Skill 路由优化**（最关键）- 缓存、预热、语义去重
- Claude/GLM Vision API 优化（文档处理）
- 对话缓存策略
- 批量处理优化

**成本监控：**
- 路由成本追踪
- 缓存命中率监控
- 预算警报
- 成本分析报告

**优化目标：**
- 路由缓存命中率 > 50%
- 路由成本降低 50-70%
- 不影响用户体验

## 实现步骤

### 1. 实现路由结果缓存（最关键）

使用 Redis 持久化缓存路由结果：
- 计算查询的缓存键（哈希）
- 缓存有效期 24 小时
- 缓存命中后直接返回路由结果（跳过 Claude API）

### 2. 实现常见问题预热

系统启动时预热高频问题：
- 提前路由常见问题
- 缓存结果供后续使用
- 节省高频查询的路由成本

### 3. 实现语义相似问题去重

使用小型 embedding 模型检测相似问题：
- 本地运行 `all-MiniLM-L6-v2`（免费）
- 计算查询相似度
- 相似度 > 0.85 时复用缓存路由结果

### 4. 实现混合路由策略

结合规则匹配和 Claude 路由：
- 第一步：尝试规则匹配（免费，基于 triggers）
- 第二步：Claude 路由（付费，准确性高）
- 规则命中率 20-30%，节省路由成本

### 5. 实现成本监控

追踪路由和问答成本：
- 路由调用统计
- 缓存命中率统计
- 费用计算
- 预算管理
- 告警通知

## 关键代码提示

### 1. 路由成本优化

#### 1.1 路由结果缓存

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

**预期效果：**
- 缓存命中率 50-70%
- 成本节省 50-70%
- 响应时间从 2s 降至 < 10ms

#### 1.2 预热常见问题

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

#### 1.3 语义相似问题去重

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

**成本对比：**
- 小型 embedding（本地）：免费
- Claude Haiku 路由：$0.0009/次
- 语义缓存命中后：$0（完全免费）

### 2. 混合模型方案的成本优势

#### 2.1 推荐方案（Haiku + GLM）详细成本

**单次问答成本：**

| 组件 | 模型 | Token 消耗 | 成本计算 | 成本 |
|------|------|-----------|---------|------|
| 路由 | Haiku 4.5 | 1K in + 0.2K out | (1K × $1.0 + 0.2K × $5.0)/1M | $0.00113 |
| Skills 加载 | - | 12K (2个 Skills) | $0 | $0 |
| 问答 | GLM-4.6 | 15K in + 2K out | (17K × $0.50)/1M | $0.0085 |
| **总计** | - | **~18K** | - | **$0.00963** |

**vs 原方案（全 Sonnet）：**
- 原方案：$0.078/次
- 新方案：$0.00963/次
- **节省：88%**

#### 2.2 月度成本估算（不同规模）

| 用户规模 | 查询/天 | 无缓存月成本 | 50%缓存月成本 | 70%缓存月成本 | 年成本（70%缓存） |
|---------|--------|-------------|--------------|--------------|-----------------|
| 100 用户 | 1,000 | $289 | $172 | $130 | $1,560 |
| 1,000 用户 | 10,000 | $2,889 | $1,734 | $1,300 | $15,600 |
| 10,000 用户 | 100,000 | $28,890 | $17,340 | $13,000 | $156,000 |

**对比原方案（全 Sonnet）：**

| 规模 | 原方案年成本 | 新方案年成本 | 年度节省 | 节省比例 |
|------|-------------|-------------|---------|----------|
| 100 用户 | $12,636 | $1,560 | $11,076 | 88% |
| 1,000 用户 | $126,360 | $15,600 | $110,760 | 88% |
| 10,000 用户 | $1,263,600 | $156,000 | $1,107,600 | 88% |

#### 2.3 与其他方案对比

| 方案 | 路由 | 问答 | 单次成本 | 月成本(1万/天) | 优缺点 |
|------|------|------|---------|---------------|--------|
| **推荐：Haiku + GLM** | Haiku 4.5 | GLM-4.6 | **$0.00963** | **$2,889** | ✅ 成本低、质量好、架构简单 |
| 全 Haiku | Haiku 4.5 | Haiku 4.5 | $0.00593 | $1,779 | ✅ 成本更低 ❌ 英文能力稍弱 |
| Haiku + Gemini | Haiku 4.5 | Gemini Flash | $0.00293 | $879 | ✅ 成本最低 ❌ 推理能力弱 |
| 全 Sonnet | Sonnet | Sonnet | $0.078 | $23,400 | ✅ 质量最高 ❌ 成本极高 |

#### 2.4 方案选择建议

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| **技术知识库（英文为主）** | **Haiku + GLM** | 推理能力强，英文技术内容理解好 |
| 严格预算限制 | Haiku + Gemini Flash | 成本最低（$879/月） |
| 质量优先 | Haiku + Haiku | 接近 Sonnet 质量，成本降低 92% |
| 中文为主 | Haiku + GLM | GLM 中文能力顶级 |

**为什么推荐 Haiku + GLM：**
1. ✅ **成本优势明显**：88% 节省，年省 $11.1 万（1000 用户规模）
2. ✅ **质量有保证**：GLM 在技术领域表现优于 Gemini Flash
3. ✅ **架构最简单**：无需语言检测，统一使用 GLM
4. ✅ **中英文兼顾**：GLM 英文能力足够，中文顶级

### 3. 极致成本优化：混合路由策略

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

**效果：**
- 规则命中率：20-30%
- 额外成本节省：$60-90/月（基于 1万次/天）
- 规则命中时响应 < 50ms

### 4. 成本监控系统

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict
import json

@dataclass
class SkillRoutingRecord:
    """Skill 路由记录"""
    timestamp: str
    user_query: str
    route_type: str  # "cache", "rule", "claude"
    loaded_skills: List[str]
    routing_cost_usd: float
    qa_cost_usd: float
    total_tokens: int
    cache_hit: bool

@dataclass
class SkillCostMonitor:
    """Skill 方案成本监控"""
    budget_limit_usd: float = 100.0
    alert_threshold: float = 0.8

    routing_records: List[SkillRoutingRecord] = field(default_factory=list)
    total_cost_usd: float = 0.0

    def record_routing(
        self,
        user_query: str,
        route_type: str,
        loaded_skills: List[str],
        routing_cost_usd: float,
        qa_cost_usd: float,
        total_tokens: int,
        cache_hit: bool = False
    ):
        """记录路由使用"""
        record = SkillRoutingRecord(
            timestamp=datetime.now().isoformat(),
            user_query=user_query,
            route_type=route_type,
            loaded_skills=loaded_skills,
            routing_cost_usd=routing_cost_usd,
            qa_cost_usd=qa_cost_usd,
            total_tokens=total_tokens,
            cache_hit=cache_hit
        )

        self.routing_records.append(record)
        self.total_cost_usd += (routing_cost_usd + qa_cost_usd)

        # 检查预算
        self._check_budget()

    def _check_budget(self):
        """检查预算"""
        usage_ratio = self.total_cost_usd / self.budget_limit_usd

        if usage_ratio >= 1.0:
            print(f"⚠️  预算已用完！总费用: ${self.total_cost_usd:.2f}")
        elif usage_ratio >= self.alert_threshold:
            print(f"⚠️  预算警告！已使用 {usage_ratio*100:.1f}%，总费用: ${self.total_cost_usd:.2f}")

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        if not self.routing_records:
            return {}

        # 按路由类型统计
        route_type_stats = {}
        for record in self.routing_records:
            rt = record.route_type
            if rt not in route_type_stats:
                route_type_stats[rt] = {"count": 0, "total_cost": 0.0}
            route_type_stats[rt]["count"] += 1
            route_type_stats[rt]["total_cost"] += record.routing_cost_usd + record.qa_cost_usd

        # 缓存命中率
        cache_hits = sum(1 for r in self.routing_records if r.cache_hit)
        cache_hit_rate = cache_hits / len(self.routing_records) if self.routing_records else 0

        # 路由成本
        total_routing_cost = sum(r.routing_cost_usd for r in self.routing_records)
        total_qa_cost = sum(r.qa_cost_usd for r in self.routing_records)

        return {
            "total_requests": len(self.routing_records),
            "total_cost_usd": round(self.total_cost_usd, 4),
            "routing_cost_usd": round(total_routing_cost, 4),
            "qa_cost_usd": round(total_qa_cost, 4),
            "budget_usage_percent": round((self.total_cost_usd / self.budget_limit_usd) * 100, 2),
            "cache_hit_rate": round(cache_hit_rate * 100, 2),
            "route_type_breakdown": route_type_stats,
            "average_cost_per_request": round(self.total_cost_usd / len(self.routing_records), 6) if self.routing_records else 0
        }

    def export_report(self, output_file: str):
        """导出报告"""
        stats = self.get_statistics()

        report = {
            "generated_at": datetime.now().isoformat(),
            "statistics": stats,
            "routing_records": [
                {
                    "timestamp": r.timestamp,
                    "user_query": r.user_query[:50],  # 截断长问题
                    "route_type": r.route_type,
                    "loaded_skills": r.loaded_skills,
                    "routing_cost_usd": r.routing_cost_usd,
                    "qa_cost_usd": r.qa_cost_usd,
                    "cache_hit": r.cache_hit
                }
                for r in self.routing_records
            ]
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
```

## 测试验证

### 1. 缓存命中率测试

```python
# 初始化
from redis import Redis
redis_client = Redis(host='localhost', port=6379, db=0)

router = CachedSkillRouter(
    skill_loader=skill_loader,
    api_key=CLAUDE_API_KEY,
    cache_backend="redis"
)

cost_monitor = SkillCostMonitor(budget_limit_usd=50.0)

# 测试相同问题的缓存
questions = ["萨省税率是多少？"] * 10  # 重复10次

for q in questions:
    result = router.route(q)

    # 记录
    cost_monitor.record_routing(
        user_query=q,
        route_type="cache" if result.get("from_cache") else "claude",
        loaded_skills=[],
        routing_cost_usd=0.0 if result.get("from_cache") else 0.001,
        qa_cost_usd=0.0,
        total_tokens=0,
        cache_hit=result.get("from_cache", False)
    )

# 查看统计
stats = cost_monitor.get_statistics()
print(f"缓存命中率: {stats['cache_hit_rate']}%")  # 应该 > 50%
print(f"路由成本: ${stats['routing_cost_usd']}")  # 应显著降低
```

### 2. 混合路由效果测试

```python
hybrid_router = HybridRouter(skill_loader, cached_router)

test_questions = [
    "萨省税率是多少？",  # 应命中规则（"萨省税率" 在 triggers 中）
    "Saskatchewan PST rate?",  # 应命中规则
    "我想了解税率相关的知识",  # 应使用 Claude 路由
]

for q in test_questions:
    result = hybrid_router.route(q)
    print(f"问题: {q}")
    print(f"路由类型: {result.get('reasoning', 'N/A')}\n")

# 查看统计
stats = hybrid_router.get_stats()
print(f"规则命中率: {stats['rule_hit_rate']*100:.1f}%")
print(f"节省成本: ${stats['cost_saved']:.4f}")
```

### 3. 端到端成本测试

```python
# 模拟一天的查询
daily_questions = ["萨省税率是多少？"] * 50 + ["RRSP 额度"] * 30 + ["其他问题"] * 20

for q in daily_questions:
    # 路由
    result = hybrid_router.route(q)

    # 模拟问答成本（假设每次 $0.075）
    qa_cost = 0.075 if result.get("primary_skills") else 0

    cost_monitor.record_routing(
        user_query=q,
        route_type=result.get("reasoning", "claude").split(":")[0],
        loaded_skills=[s["skill_id"] for s in result.get("primary_skills", [])],
        routing_cost_usd=0.0 if result.get("from_cache") else (0.0 if "规则" in result.get("reasoning", "") else 0.001),
        qa_cost_usd=qa_cost,
        total_tokens=15000,
        cache_hit=result.get("from_cache", False)
    )

# 导出报告
cost_monitor.export_report("daily_cost_report.json")

stats = cost_monitor.get_statistics()
print(f"总请求数: {stats['total_requests']}")
print(f"总成本: ${stats['total_cost_usd']}")
print(f"路由成本: ${stats['routing_cost_usd']}")
print(f"问答成本: ${stats['qa_cost_usd']}")
print(f"缓存命中率: {stats['cache_hit_rate']}%")
print(f"平均每次成本: ${stats['average_cost_per_request']}")
```

**预期结果：**
```
总请求数: 100
总成本: $4.50
路由成本: $0.02 (缓存和规则节省了大部分)
问答成本: $4.48
缓存命中率: 65%
平均每次成本: $0.045
```

## 注意事项

**1. 缓存策略**
- **生产环境必须启用 Redis 缓存**（内存缓存在重启后丢失）
- 设置合理的 TTL（推荐 24 小时）
- 定期清理过期缓存
- 监控 Redis 内存使用

**2. 规则匹配最佳实践**
- 定期分析高频问题，添加到 triggers
- triggers 应包含：
  - 标准名称（如 "萨省税率"）
  - 英文名称（如 "Saskatchewan tax rate"）
  - 常见缩写（如 "SK tax"）
- 避免过于宽泛的 triggers（可能导致误匹配）

**3. 成本控制**
- **设置预算上限和告警阈值**
- 实时监控路由成本和问答成本
- 定期审查成本报告，优化高成本查询
- 考虑按用户/租户设置配额

**4. 性能优化**
- Redis 应与应用服务器在同一数据中心（减少延迟）
- 缓存键计算应高效（MD5 哈希）
- 定期监控缓存命中率，目标 > 50%
- 如果缓存命中率低，考虑：
  - 增加预热问题
  - 调高语义相似度阈值
  - 优化 triggers 覆盖度

**5. 优化效果预期**
| 优化策略 | 成本节省 | 响应时间改善 |
|---------|---------|------------|
| 路由缓存 | 50-70% | 2s → 10ms |
| 预热常见问题 | 额外 10-20% | N/A |
| 语义去重 | 额外 5-10% | N/A |
| 混合路由 | 额外 20-30% | 路由时间 < 50ms |
| **综合效果** | **70-85%** | **显著** |

**6. 监控指标**
必须监控的关键指标：
- 缓存命中率
- 规则路由命中率
- Claude 路由调用次数
- 平均每次路由成本
- 平均每次问答成本
- 总成本趋势

## 依赖关系

**前置任务：**
- 任务11：SkillLoader（提供 triggers 用于规则匹配）
- 任务13：ClaudeSkillRouter（路由引擎）
- 任务14：SkillEngine（端到端问答）

**后置任务：**
- 无（这是最后的优化任务）
