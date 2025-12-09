"""
自动化测试脚本 - T2 Corporate Tax 问答测试 (GLM 路由版本)

使用 GLM API 作为路由器，与 Claude Haiku 版本进行对比。
"""
import os
from datetime import datetime
from pathlib import Path
from skill_loader import SkillLoader
from skill_router_glm import SkillRouterGLM
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


def save_results_to_file(results: list, output_path: Path, router_name: str):
    """保存测试结果到 Markdown 文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# T2 Corporate Tax 问答测试结果 ({router_name} 路由)\n\n")
        f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**路由器**: {router_name}\n\n")
        f.write("---\n\n")

        for i, result in enumerate(results, 1):
            f.write(f"## 问题 {i}: {result['description']}\n\n")
            f.write(f"**问题**: {result['query']}\n\n")
            f.write(f"**匹配的 Skills**: {', '.join(result.get('matched_skills', ['无']))}\n\n")
            f.write(f"**置信度**: {result.get('confidence', 'N/A')}\n\n")
            f.write(f"**推理过程**: {result.get('reasoning', 'N/A')}\n\n")
            f.write("### 回答\n\n")
            f.write(f"{result.get('answer', '无回答')}\n\n")
            f.write("---\n\n")

        # 总结
        total = len(results)
        passed = sum(1 for r in results if r.get("success", False))
        f.write(f"## 测试总结\n\n")
        f.write(f"- **总测试数**: {total}\n")
        f.write(f"- **成功匹配**: {passed}\n")
        f.write(f"- **成功率**: {passed/total*100:.1f}%\n")


def test_complete_flow():
    """测试完整流程 - T2 Corporate Tax 问答 (GLM 路由版本)"""
    print("\n" + "="*60)
    print("  🧪 T2 Corporate Tax 问答测试 (GLM 路由)")
    print("="*60 + "\n")

    # 加载 .env 文件
    load_env()

    # 检查 API Keys
    if not os.getenv("GLM_API_KEY"):
        print("❌ 未找到 GLM_API_KEY")
        return False

    print("✅ API Keys 已配置\n")

    # 初始化组件
    print("🚀 初始化组件...")
    skill_loader = SkillLoader("skills")
    skill_router = SkillRouterGLM()  # 使用 GLM 路由器
    chat_service = ChatService()
    print()

    # T2 Corporate Tax 测试问题
    test_cases = [
        {"query": "What is the T2 Corporation Income Tax Return and who must file it?", "description": "基础概念"},
        {"query": "What is the filing deadline for T2 corporate tax return?", "description": "截止日期"},
        {"query": "What is the small business deduction and how does it reduce corporate tax?", "description": "税务优惠"},
        {"query": "What are the electronic filing requirements for T2 returns starting 2024?", "description": "申报要求"},
        {"query": "How do I complete Schedule 500 for Ontario Corporation Tax?", "description": "省级税务 (Ontario)"},
        {"query": "What is the Carbon Capture, Utilization, and Storage (CCUS) Investment Tax Credit?", "description": "联邦税收抵免"},
        {"query": "What are the penalties for late filing of T2 returns?", "description": "罚款规定"},
        {"query": "How do associated corporations share the business limit for small business deduction?", "description": "关联公司"},
        {"query": "What is Schedule 13 Continuity of Reserves used for?", "description": "具体表格"},
        {"query": "What documents are needed to file a T2 corporate tax return?", "description": "申报材料"},
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"  问题 {i}/10: {test_case['description']}")
        print(f"{'='*60}\n")

        query = test_case["query"]
        print(f"❓ 问题: {query}\n")

        try:
            # Step 1: 路由 (使用 GLM)
            print("📍 Step 1: 路由相关 Skills (GLM)...")
            routing_result = skill_router.route(
                query,
                skill_loader.get_all_skills_metadata()
            )

            matched_skills = routing_result.get("matched_skills", [])
            confidence = routing_result.get("confidence", "N/A")
            reasoning = routing_result.get("reasoning", "N/A")

            print(f"   匹配: {matched_skills}")
            print(f"   置信度: {confidence}")

            # Step 2: 加载 Skills
            print("\n📚 Step 2: 加载 Skills 内容...")
            loaded_skills = []
            for skill_id in matched_skills:
                skill = skill_loader.get_skill(skill_id)
                if skill:
                    loaded_skills.append(skill)
                    print(f"  ✓ {skill.title}")

            # Step 3: 生成回答
            print("\n🤖 Step 3: 生成回答...")
            answer = chat_service.generate_answer(
                user_query=query,
                loaded_skills=loaded_skills
            )

            # 显示回答预览
            preview = answer[:300] + "..." if len(answer) > 300 else answer
            print(f"\n📝 回答预览:\n{preview}\n")

            # 验证结果
            success = len(matched_skills) > 0
            results.append({
                "description": test_case['description'],
                "query": query,
                "matched_skills": matched_skills,
                "confidence": confidence,
                "reasoning": reasoning,
                "answer": answer,
                "answer_length": len(answer),
                "success": success
            })

            if success:
                print(f"✅ 成功: 匹配到 {len(matched_skills)} 个 Skills, 回答 {len(answer)} 字符")
            else:
                print(f"⚠️  警告: 未匹配到 Skills")

        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            results.append({
                "description": test_case['description'],
                "query": query,
                "success": False,
                "error": str(e),
                "answer": f"错误: {str(e)}"
            })

    # 保存结果到文件 (GLM 版本)
    output_path = Path(__file__).parent / "test_results_glm.md"
    save_results_to_file(results, output_path, "GLM-4-Flash")
    print(f"\n💾 测试结果已保存到: {output_path}")

    # 总结
    print(f"\n\n{'='*60}")
    print("  📊 测试结果总结 (GLM 路由)")
    print(f"{'='*60}\n")

    total = len(results)
    passed = sum(1 for r in results if r.get("success", False))

    for i, result in enumerate(results, 1):
        status = "✅" if result.get("success", False) else "❌"
        print(f"{status} 问题 {i}: {result['description']}")
        print(f"   {result['query'][:50]}...")
        if result.get("success", False):
            print(f"   匹配: {', '.join(result.get('matched_skills', []))}")
            print(f"   回答长度: {result.get('answer_length', 0)} 字符")
        else:
            print(f"   错误: {result.get('error', '未知错误')}")
        print()

    print(f"{'='*60}")
    print(f"  总计: {passed}/{total} 成功匹配 ({passed/total*100:.1f}%)")
    print(f"{'='*60}\n")

    if passed == total:
        print("🎉 所有问题都成功匹配到 Skills！")
        return True
    else:
        print("⚠️  部分问题未匹配到 Skills，请检查日志")
        return False


if __name__ == "__main__":
    test_complete_flow()
