"""
MVP CLI - 验证 Skill 路由 + LLM 回答流程

流程:
1. 用户输入问题
2. Claude Haiku 4.5 路由相关 Skills
3. 加载 Skills 内容
4. GLM-4.6 基于 Skills 生成回答
"""
import os
from pathlib import Path
from skill_loader import SkillLoader
from skill_router import SkillRouter
from chat_service import ChatService


def load_env():
    """加载 .env 文件"""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()


class KnowledgeAssistant:
    """知识库助手 (MVP)"""

    def __init__(self, skills_dir: str = "skills"):
        print("\n🚀 初始化知识库助手...\n")

        # 加载 Skills
        self.skill_loader = SkillLoader(skills_dir)

        # 初始化路由器 (Claude Haiku 4.5)
        self.skill_router = SkillRouter()

        # 初始化聊天服务 (GLM-4.6)
        self.chat_service = ChatService()

        print("✅ 初始化完成!\n")

    def answer_question(self, user_query: str) -> str:
        """
        回答用户问题

        流程:
        1. 路由 Skills (Claude Haiku 4.5)
        2. 加载相关 Skills
        3. 生成回答 (GLM-4.6)
        """
        print(f"\n{'='*60}")
        print(f"❓ 问题: {user_query}")
        print(f"{'='*60}\n")

        # Step 1: 路由 Skills
        print("📍 Step 1: 路由相关知识...")
        routing_result = self.skill_router.route(
            user_query,
            self.skill_loader.get_all_skills_metadata()
        )

        matched_skill_ids = routing_result.get("matched_skills", [])

        if not matched_skill_ids:
            print("⚠️  未找到相关 Skills，将使用通用知识回答\n")
            loaded_skills = []
        else:
            # Step 2: 加载 Skills
            print("📚 Step 2: 加载 Skills 内容...")
            loaded_skills = []
            for skill_id in matched_skill_ids:
                skill = self.skill_loader.get_skill(skill_id)
                if skill:
                    loaded_skills.append(skill)
                    print(f"  ✓ {skill.title}")
            print()

        # Step 3: 生成回答
        print("🤖 Step 3: 生成回答 (GLM-4.6)...")
        answer = self.chat_service.generate_answer(
            user_query=user_query,
            loaded_skills=loaded_skills
        )

        print(f"{'='*60}\n")

        return answer

    def run_cli(self):
        """运行 CLI 交互循环"""
        print("="*60)
        print("  BlockMe 知识库助手 MVP")
        print("="*60)
        print("\n提示:")
        print("  - 输入问题并按回车")
        print("  - 输入 'quit' 或 'exit' 退出")
        print("  - 输入 'skills' 查看所有 Skills")
        print()

        while True:
            try:
                user_input = input("💬 你的问题: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 再见!")
                    break

                if user_input.lower() == 'skills':
                    self._show_all_skills()
                    continue

                # 回答问题
                self.answer_question(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 再见!")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}\n")

    def _show_all_skills(self):
        """显示所有可用的 Skills"""
        print("\n📚 可用的 Skills:")
        for meta in self.skill_loader.get_all_skills_metadata():
            print(f"\n  ID: {meta['id']}")
            print(f"  标题: {meta['title']}")
            print(f"  描述: {meta['description']}")
            print(f"  标签: {', '.join(meta.get('tags', []))}")
        print()


def main():
    """主函数"""
    # 加载 .env 文件
    load_env()

    # 检查环境变量
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ 错误: 未找到 ANTHROPIC_API_KEY 环境变量")
        print("请在 .env 文件中设置或运行: export ANTHROPIC_API_KEY=your-key")
        return

    if not os.getenv("GLM_API_KEY"):
        print("❌ 错误: 未找到 GLM_API_KEY 环境变量")
        print("请在 .env 文件中设置或运行: export GLM_API_KEY=your-key")
        return

    # 启动助手
    assistant = KnowledgeAssistant(skills_dir="skills")
    assistant.run_cli()


if __name__ == "__main__":
    main()
