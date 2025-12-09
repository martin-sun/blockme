"""
Skill Router - Route relevant Skills using Claude Haiku 4.5
"""
import os
import json
from typing import List, Dict
from anthropic import Anthropic


class SkillRouter:
    """Route Skills using Claude Haiku 4.5"""

    def __init__(self, api_key: str = None, enable_prefilter: bool = False):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")

        self.client = Anthropic(api_key=self.api_key)
        # Claude Haiku 4.5 - latest Haiku model
        self.model = "claude-haiku-4-5-20251001"

        # Prefilter switch (recommended when Skills > 50)
        self.enable_prefilter = enable_prefilter

    def route(self, user_query: str, available_skills: List[dict]) -> Dict:
        """
        Route user query to relevant Skills.

        Args:
            user_query: User's question
            available_skills: List of available Skills metadata

        Returns:
            {
                "matched_skills": ["skill-id-1", "skill-id-2"],
                "confidence": "high" | "medium" | "low",
                "reasoning": "Reasoning for selecting these Skills"
            }
        """
        # Optional first layer: metadata prefilter (only when Skills > 50 and enabled)
        if self.enable_prefilter and len(available_skills) > 50:
            original_count = len(available_skills)
            available_skills = self._prefilter_skills(user_query, available_skills)
            print(f"✂️  Prefilter: {original_count} → {len(available_skills)} candidate Skills")

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

            print(f"\n🎯 Routing Result:")
            print(f"  - Matched Skills: {result['matched_skills']}")
            print(f"  - Confidence: {result['confidence']}")
            print(f"  - Reasoning: {result['reasoning']}\n")

            return result

        except Exception as e:
            print(f"❌ Routing failed: {e}")
            return {
                "matched_skills": [],
                "confidence": "low",
                "reasoning": f"Routing failed: {str(e)}"
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
        """Parse routing result from Claude."""
        try:
            # Extract JSON (may be wrapped in ```json ... ```)
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

            # Validate required fields
            if "matched_skills" not in result:
                result["matched_skills"] = []
            if "confidence" not in result:
                result["confidence"] = "medium"
            if "reasoning" not in result:
                result["reasoning"] = "No reasoning provided"

            return result

        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parse failed: {e}")
            print(f"Raw output: {result_text}")
            return {
                "matched_skills": [],
                "confidence": "low",
                "reasoning": "Parse failed"
            }

    def _prefilter_skills(
        self,
        user_query: str,
        all_skills: List[dict],
        keep_ratio: float = 0.3  # Keep top 30%
    ) -> List[dict]:
        """
        First layer coarse filter: quick filtering with simple rules.

        Only enabled when Skills > 50, reduces Claude API token consumption.

        Args:
            user_query: User's question
            all_skills: All available Skills
            keep_ratio: Minimum ratio to keep (default 30%)

        Returns:
            Filtered Skills list
        """
        scored_skills = []
        query_lower = user_query.lower()

        for skill in all_skills:
            score = 0

            # 1. Check triggers - highest weight
            triggers = skill.get('triggers', [])
            for trigger in triggers:
                if trigger.lower() in query_lower:
                    score += 10

            # 2. Check keywords - high weight
            keywords = skill.get('keywords', [])
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    score += 5

            # 3. Check domain - medium weight
            domain = skill.get('domain', '')
            if domain and domain.lower() in query_lower:
                score += 3

            # 4. Check tags - low weight
            tags = skill.get('tags', [])
            for tag in tags:
                if tag.lower() in query_lower:
                    score += 2

            scored_skills.append((score, skill))

        # Sort by score
        scored_skills.sort(reverse=True, key=lambda x: x[0])

        # Keep strategy: all scored + at least keep_ratio
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
