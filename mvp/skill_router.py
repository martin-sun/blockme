"""
Skill Router - 使用 Claude Haiku 4.5 路由相关 Skills
"""
import os
import json
from typing import List, Dict
from anthropic import Anthropic


class SkillRouter:
    """使用 Claude Haiku 4.5 路由 Skills"""

    def __init__(self, api_key: str = None, enable_prefilter: bool = False):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 ANTHROPIC_API_KEY")

        self.client = Anthropic(api_key=self.api_key)
        # Claude 3.5 Haiku - 最新的 Haiku 模型
        self.model = "claude-haiku-4-5-20251001"

        # 预过滤开关（当 Skill 数量 > 50 时建议启用）
        self.enable_prefilter = enable_prefilter

    def route(self, user_query: str, available_skills: List[dict]) -> Dict:
        """
        路由用户问题到相关 Skills

        Args:
            user_query: 用户问题
            available_skills: 可用的 Skills 元数据列表

        Returns:
            {
                "matched_skills": ["skill-id-1", "skill-id-2"],
                "confidence": "high" | "medium" | "low",
                "reasoning": "为什么选择这些 Skills 的推理过程"
            }
        """
        # 可选的第一层：元数据预过滤（仅在 Skill 数量 > 50 且启用时生效）
        if self.enable_prefilter and len(available_skills) > 50:
            original_count = len(available_skills)
            available_skills = self._prefilter_skills(user_query, available_skills)
            print(f"✂️  预过滤: {original_count} → {len(available_skills)} 个候选 Skills")

        prompt = self._build_routing_prompt(user_query, available_skills)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            result_text = response.content[0].text
            result = self._parse_routing_result(result_text)

            print(f"\n🎯 路由结果:")
            print(f"  - 匹配 Skills: {result['matched_skills']}")
            print(f"  - 置信度: {result['confidence']}")
            print(f"  - 推理: {result['reasoning']}\n")

            return result

        except Exception as e:
            print(f"❌ 路由失败: {e}")
            return {
                "matched_skills": [],
                "confidence": "low",
                "reasoning": f"路由失败: {str(e)}"
            }

    def _build_routing_prompt(self, user_query: str, available_skills: List[dict]) -> str:
        """构建路由 prompt"""
        skills_info = "\n".join([
            f"- ID: {skill['id']}\n"
            f"  标题: {skill['title']}\n"
            f"  描述: {skill['description']}\n"
            f"  标签: {', '.join(skill.get('tags', []))}"
            for skill in available_skills
        ])

        prompt = f"""你是一个专业的知识路由助手。用户提出了一个问题，你需要从可用的知识库 Skills 中选择最相关的 1-3 个。

**用户问题：**
{user_query}

**可用的 Skills：**
{skills_info}

**任务：**
1. 分析用户问题的意图
2. 从可用 Skills 中选择最相关的（最多3个）
3. 评估匹配的置信度（high/medium/low）
4. 解释你的推理过程

**输出格式（严格使用 JSON）：**
```json
{{
    "matched_skills": ["skill-id-1", "skill-id-2"],
    "confidence": "high",
    "reasoning": "这里解释为什么选择这些 Skills"
}}
```

只返回 JSON，不要有其他内容。"""

        return prompt

    def _parse_routing_result(self, result_text: str) -> Dict:
        """解析 Claude 返回的路由结果"""
        try:
            # 提取 JSON（可能被包裹在 ```json ... ``` 中）
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                json_str = result_text[json_start:json_end].strip()
            elif "```" in result_text:
                json_start = result_text.find("```") + 3
                json_end = result_text.find("```", json_start)
                json_str = result_text[json_start:json_end].strip()
            else:
                json_str = result_text.strip()

            result = json.loads(json_str)

            # 验证必需字段
            if "matched_skills" not in result:
                result["matched_skills"] = []
            if "confidence" not in result:
                result["confidence"] = "medium"
            if "reasoning" not in result:
                result["reasoning"] = "未提供推理"

            return result

        except json.JSONDecodeError as e:
            print(f"⚠️  JSON 解析失败: {e}")
            print(f"原始输出: {result_text}")
            return {
                "matched_skills": [],
                "confidence": "low",
                "reasoning": "解析失败"
            }

    def _prefilter_skills(
        self,
        user_query: str,
        all_skills: List[dict],
        keep_ratio: float = 0.3  # 保留前 30%
    ) -> List[dict]:
        """
        第一层粗筛：用简单规则快速过滤

        只在 Skill 数量 > 50 时启用，减少 Claude API token 消耗

        Args:
            user_query: 用户问题
            all_skills: 所有可用 Skills
            keep_ratio: 至少保留的比例（默认 30%）

        Returns:
            过滤后的 Skills 列表
        """
        scored_skills = []
        query_lower = user_query.lower()

        for skill in all_skills:
            score = 0

            # 1. 检查 triggers（触发词） - 最高权重
            triggers = skill.get('triggers', [])
            for trigger in triggers:
                if trigger.lower() in query_lower:
                    score += 10

            # 2. 检查 keywords - 高权重
            keywords = skill.get('keywords', [])
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    score += 5

            # 3. 检查 domain - 中权重
            domain = skill.get('domain', '')
            if domain and domain.lower() in query_lower:
                score += 3

            # 4. 检查 tags - 低权重
            tags = skill.get('tags', [])
            for tag in tags:
                if tag.lower() in query_lower:
                    score += 2

            scored_skills.append((score, skill))

        # 按分数排序
        scored_skills.sort(reverse=True, key=lambda x: x[0])

        # 保留策略：所有有得分的 + 至少保留 keep_ratio
        scored_count = len([s for s in scored_skills if s[0] > 0])
        min_keep = int(len(all_skills) * keep_ratio)
        keep_count = max(scored_count, min_keep)

        return [skill for score, skill in scored_skills[:keep_count]]


if __name__ == "__main__":
    # 测试
    from skill_loader import SkillLoader

    loader = SkillLoader("skills")
    router = SkillRouter()

    test_queries = [
        "萨省的 PST 税率是多少？",
        "GST 和 PST 有什么区别？",
        "如何报税？"
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"问题: {query}")
        result = router.route(query, loader.get_all_skills_metadata())
