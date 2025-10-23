"""
Chat Service - 使用 GLM-4.6 生成回答
"""
import os
from typing import List
from zhipuai import ZhipuAI
from skill_loader import Skill


class ChatService:
    """聊天服务，使用 GLM-4.6 生成回答"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GLM_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 GLM_API_KEY")

        self.client = ZhipuAI(api_key=self.api_key)
        # GLM-4.6 可选模型：glm-4-flash (免费), glm-4-plus (更强)
        self.model = "glm-4-flash"

    def generate_answer(
        self,
        user_query: str,
        loaded_skills: List[Skill] = None
    ) -> str:
        """
        生成回答

        Args:
            user_query: 用户问题
            loaded_skills: 加载的 Skills（提供知识上下文）

        Returns:
            LLM 生成的回答
        """
        # 构建知识上下文
        knowledge_context = self._build_knowledge_context(loaded_skills)

        # 构建消息
        messages = []

        if knowledge_context:
            messages.append({
                "role": "system",
                "content": "你是一个专业的税务知识助手。请基于提供的知识内容准确回答用户问题。"
            })
            messages.append({
                "role": "user",
                "content": f"{knowledge_context}\n\n---\n\n用户问题：{user_query}"
            })
        else:
            messages.append({
                "role": "system",
                "content": "你是一个专业的税务知识助手。"
            })
            messages.append({
                "role": "user",
                "content": user_query
            })

        # 调用 GLM API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1024,
                temperature=0.7
            )

            answer = response.choices[0].message.content

            print(f"\n💬 GLM-4.6 回答:")
            print(f"{answer}\n")

            return answer

        except Exception as e:
            error_msg = f"❌ 生成回答失败: {e}"
            print(error_msg)
            return error_msg

    def _build_knowledge_context(self, loaded_skills: List[Skill]) -> str:
        """构建知识上下文"""
        if not loaded_skills:
            return ""

        context_parts = ["# 相关知识\n"]

        for skill in loaded_skills:
            context_parts.append(f"## {skill.title}\n")
            context_parts.append(skill.content)
            context_parts.append("\n---\n")

        context_parts.append("\n请基于以上知识回答用户问题。如果知识库中没有相关信息，请诚实说明。")

        return "\n".join(context_parts)


if __name__ == "__main__":
    # 测试
    from skill_loader import SkillLoader

    loader = SkillLoader("skills")
    chat_service = ChatService()

    # 测试1: 使用知识库
    print("="*60)
    print("测试1: 使用知识库回答")
    skill = loader.get_skill("saskatchewan-pst")
    answer = chat_service.generate_answer(
        user_query="萨省的 PST 税率是多少？",
        loaded_skills=[skill] if skill else []
    )

    # 测试2: 不使用知识库
    print("\n" + "="*60)
    print("测试2: 不使用知识库回答")
    answer = chat_service.generate_answer(
        user_query="今天天气怎么样？",
        loaded_skills=[]
    )
