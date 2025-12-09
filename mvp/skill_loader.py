"""
Skill Loader - 加载和解析 Skill markdown 文件
"""
import os
from pathlib import Path
from typing import Dict, List
import yaml


class Skill:
    """Skill 数据模型"""
    def __init__(self, skill_id: str, title: str, content: str, metadata: dict):
        self.skill_id = skill_id
        self.title = title
        self.content = content
        self.metadata = metadata

    def __repr__(self):
        return f"Skill(id={self.skill_id}, title={self.title})"


class SkillLoader:
    """加载和管理 Skills"""

    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Skill] = {}
        self.load_all_skills()

    def load_all_skills(self):
        """加载所有 Skill 文件（支持扁平文件和目录结构）"""
        if not self.skills_dir.exists():
            print(f"⚠️  Skills 目录不存在: {self.skills_dir}")
            return

        # 1. 加载扁平的 .md 文件（旧格式）
        for file_path in self.skills_dir.glob("*.md"):
            try:
                skill = self._load_skill_file(file_path)
                self.skills[skill.skill_id] = skill
                print(f"✅ 加载 Skill: {skill.skill_id}")
            except Exception as e:
                print(f"❌ 加载失败 {file_path.name}: {e}")

        # 2. 加载目录结构的 Skills（新格式：skill_id/SKILL.md）
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    try:
                        skill = self._load_skill_file(skill_file)
                        self.skills[skill.skill_id] = skill
                        print(f"✅ 加载 Skill: {skill.skill_id} (目录结构)")
                    except Exception as e:
                        print(f"❌ 加载失败 {skill_dir.name}/SKILL.md: {e}")

        print(f"\n📚 共加载 {len(self.skills)} 个 Skills\n")

    def _load_skill_file(self, file_path: Path) -> Skill:
        """加载单个 Skill 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 分离 YAML front matter 和 markdown 内容
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                markdown_content = parts[2].strip()
            else:
                raise ValueError("无效的 YAML front matter 格式")
        else:
            raise ValueError("缺少 YAML front matter")

        # 解析 YAML
        metadata = yaml.safe_load(yaml_content)

        # 创建 Skill 对象
        skill = Skill(
            skill_id=metadata.get('id', file_path.stem),
            title=metadata.get('title', ''),
            content=markdown_content,
            metadata=metadata
        )

        return skill

    def get_skill(self, skill_id: str) -> Skill | None:
        """根据 ID 获取 Skill"""
        return self.skills.get(skill_id)

    def get_all_skills_metadata(self) -> List[dict]:
        """获取所有 Skills 的元数据（用于路由）"""
        return [
            {
                'id': skill.skill_id,
                'title': skill.title,
                'tags': skill.metadata.get('tags', []),
                'description': skill.metadata.get('description', ''),
                'domain': skill.metadata.get('domain', ''),
            }
            for skill in self.skills.values()
        ]


if __name__ == "__main__":
    # 测试
    loader = SkillLoader("skills")

    print("所有 Skills 元数据:")
    for meta in loader.get_all_skills_metadata():
        print(f"  - {meta['id']}: {meta['title']}")

    print("\n测试获取单个 Skill:")
    skill = loader.get_skill("saskatchewan-pst")
    if skill:
        print(f"  ID: {skill.skill_id}")
        print(f"  标题: {skill.title}")
        print(f"  内容长度: {len(skill.content)} 字符")
