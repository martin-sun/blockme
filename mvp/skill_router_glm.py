"""
Skill Router - 使用 GLM API 路由相关 Skills
"""
import os
import json
from typing import List, Dict
from zhipuai import ZhipuAI


class SkillRouterGLM:
    """使用 GLM API 路由 Skills"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GLM_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 GLM_API_KEY")

        self.client = ZhipuAI(api_key=self.api_key)
        # GLM-4-Flash 免费版
        self.model = "glm-4-flash"

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
        prompt = self._build_routing_prompt(user_query, available_skills)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024,
                temperature=0.1  # 低温度以获得更一致的结果
            )

            result_text = response.choices[0].message.content
            result = self._parse_routing_result(result_text)

            print(f"\n🎯 路由结果 (GLM):")
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
        """Build routing prompt."""
        skills_info = "\n".join([
            f"- ID: {skill['id']}\n"
            f"  Title: {skill['title']}\n"
            f"  Description: {skill['description']}\n"
            f"  Tags: {', '.join(skill.get('tags', []))}"
            for skill in available_skills
        ])

        prompt = f"""You are a professional knowledge routing assistant. A user has asked a question, and you need to select the most relevant 1-3 Skills from the available knowledge base.

**User Question:**
{user_query}

**Available Skills:**
{skills_info}

**Task:**
1. Analyze the user's question intent
2. Select the most relevant Skills (up to 3)
3. Evaluate the matching confidence (high/medium/low)
4. Explain your reasoning

**Output Format (strictly use JSON):**
```json
{{
    "matched_skills": ["skill-id-1", "skill-id-2"],
    "confidence": "high",
    "reasoning": "Explain why these Skills were selected"
}}
```

Return only JSON, no other content."""

        return prompt

    def _parse_routing_result(self, result_text: str) -> Dict:
        """解析 GLM 返回的路由结果"""
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


if __name__ == "__main__":
    # 测试
    from skill_loader import SkillLoader

    loader = SkillLoader("skills")
    router = SkillRouterGLM()

    test_queries = [
        "What is the T2 Corporation Income Tax Return?",
        "How do I complete Schedule 500 for Ontario?",
        "What is the CCUS Investment Tax Credit?"
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"问题: {query}")
        result = router.route(query, loader.get_all_skills_metadata())
