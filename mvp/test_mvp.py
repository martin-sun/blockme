"""
自动化测试脚本 - 验证完整的 MVP 流程
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


def test_complete_flow():
    """测试完整流程"""
    print("\n" + "="*60)
    print("  🧪 MVP 自动化测试")
    print("="*60 + "\n")

    # 加载 .env 文件
    load_env()

    # 检查 API Keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ 未找到 ANTHROPIC_API_KEY")
        return False

    if not os.getenv("GLM_API_KEY"):
        print("❌ 未找到 GLM_API_KEY")
        return False

    print("✅ API Keys 已配置\n")

    # 初始化组件
    print("🚀 初始化组件...")
    skill_loader = SkillLoader("skills")
    skill_router = SkillRouter()
    chat_service = ChatService()
    print()

    # 测试用例
    test_cases = [
        {
            "query": "萨省的 PST 税率是多少？",
            "expected_skills": ["saskatchewan-pst"],
            "description": "测试1: 单个 Skill 匹配"
        },
        {
            "query": "GST 和 PST 有什么区别？",
            "expected_skills": ["canada-gst", "saskatchewan-pst"],
            "description": "测试2: 多个 Skills 匹配"
        },
        {
            "query": "如何报税？",
            "expected_skills": ["tax-filing-basics"],
            "description": "测试3: 报税相关 Skill"
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"  {test_case['description']}")
        print(f"{'='*60}\n")

        query = test_case["query"]
        print(f"❓ 问题: {query}\n")

        try:
            # Step 1: 路由
            print("📍 Step 1: 路由相关 Skills...")
            routing_result = skill_router.route(
                query,
                skill_loader.get_all_skills_metadata()
            )

            matched_skills = routing_result.get("matched_skills", [])

            # Step 2: 加载 Skills
            print("📚 Step 2: 加载 Skills 内容...")
            loaded_skills = []
            for skill_id in matched_skills:
                skill = skill_loader.get_skill(skill_id)
                if skill:
                    loaded_skills.append(skill)
                    print(f"  ✓ {skill.title}")
            print()

            # Step 3: 生成回答
            print("🤖 Step 3: 生成回答...")
            answer = chat_service.generate_answer(
                user_query=query,
                loaded_skills=loaded_skills
            )

            # 验证结果
            success = len(matched_skills) > 0
            results.append({
                "test": test_case['description'],
                "query": query,
                "matched_skills": matched_skills,
                "answer_length": len(answer),
                "success": success
            })

            if success:
                print(f"\n✅ 测试通过: 匹配到 {len(matched_skills)} 个 Skills")
            else:
                print(f"\n⚠️  警告: 未匹配到 Skills")

        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            results.append({
                "test": test_case['description'],
                "query": query,
                "success": False,
                "error": str(e)
            })

    # 总结
    print(f"\n\n{'='*60}")
    print("  📊 测试结果总结")
    print(f"{'='*60}\n")

    total = len(results)
    passed = sum(1 for r in results if r.get("success", False))

    for i, result in enumerate(results, 1):
        status = "✅" if result.get("success", False) else "❌"
        print(f"{status} 测试 {i}: {result['test']}")
        print(f"   问题: {result['query']}")
        if result.get("success", False):
            print(f"   匹配: {', '.join(result.get('matched_skills', []))}")
            print(f"   回答长度: {result.get('answer_length', 0)} 字符")
        else:
            print(f"   错误: {result.get('error', '未知错误')}")
        print()

    print(f"{'='*60}")
    print(f"  总计: {passed}/{total} 通过")
    print(f"{'='*60}\n")

    if passed == total:
        print("🎉 所有测试通过！MVP 验证成功！")
        return True
    else:
        print("⚠️  部分测试未通过，请检查日志")
        return False


if __name__ == "__main__":
    test_complete_flow()
