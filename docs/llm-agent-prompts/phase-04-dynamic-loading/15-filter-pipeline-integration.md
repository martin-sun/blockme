# 任务15：Skill Filter Pipeline 集成

## 任务目标

将 Skill 引擎集成为 Open WebUI Filter/Function，实现动态 Skill 加载机制。Filter 拦截用户请求，使用 Claude 路由相关 Skills，将完整 Skill 内容注入到 LLM 上下文中，替换原有的 RAG 检索逻辑。

**核心思路：**
- 使用 SkillEngine（任务14）处理用户问题
- 在 Filter 的 inlet 方法中注入 Skills
- 支持对话历史传递
- 错误处理不影响正常对话

## 技术要求

**集成方式：**
- 方式1：Open WebUI Filter（推荐）- 自动注入 Skills
- 方式2：Open WebUI Function - 手动调用查询

**核心组件：**
- SkillEngine（任务14）：端到端问答引擎
- ClaudeSkillRouter（任务13）：智能路由
- SkillLoader（任务11）：加载 Skills
- SkillContextBuilder（任务14）：构建上下文

**功能要求：**
- 提取用户最新消息
- 传递对话历史给 SkillEngine
- 根据置信度过滤路由结果
- 将 Skills 作为系统消息注入
- 在响应中添加来源标注（可选）

**性能要求：**
- 路由时间 < 2秒（可缓存）
- 错误时自动降级（返回原始请求）
- 支持配置参数（Valves）

## 实现步骤

### 1. 创建 Open WebUI Filter

Open WebUI Filter 是 Python 文件，放在 Open WebUI 的 `filters/` 目录：

```bash
# 在 Open WebUI 项目中
mkdir -p filters
touch filters/skill_knowledge_filter.py
```

### 2. 复制 Skill 引擎到 filters 目录

将 SkillEngine 相关代码复制到 filters 目录（或通过 import 引用）：

```bash
cp -r src/knowledge_manager/skill_engine.py filters/
cp -r src/knowledge_manager/skill_loader.py filters/
cp -r src/knowledge_manager/skill_router.py filters/
```

### 3. 实现 Filter 类

遵循 Open WebUI Filter API：
- 定义 `Filter` 类
- 定义 `Valves` 内部类（配置参数）
- 实现 `inlet()` 方法（请求前处理）
- 实现 `outlet()` 方法（响应后处理，可选）

### 4. （可选）创建 Open WebUI Function

如果需要手动调用查询功能：

```bash
mkdir -p functions
touch functions/skill_qa_function.py
```

### 5. 配置和部署

- 在 Open WebUI Admin Panel 启用 Filter
- 配置 Claude API Key
- 设置 Skills 目录路径

## 关键代码提示

### 方式1：Open WebUI Filter（推荐）

**filters/skill_knowledge_filter.py：**

```python
"""
title: Skill Knowledge Filter
description: 动态加载相关 Skills 到对话上下文
author: Your Name
version: 1.0.0
"""

from typing import Optional, Dict, List
from pydantic import BaseModel, Field
import os

# 导入 Skill 引擎（需要将实现放在 filters 目录）
from .skill_engine import SkillEngine


class Filter:
    """Open WebUI Filter for Skill-based Knowledge Loading"""

    class Valves(BaseModel):
        """配置参数"""
        SKILLS_DIR: str = Field(
            default="knowledge_base/skills",
            description="Skills 目录路径"
        )
        CLAUDE_API_KEY: str = Field(
            default="",
            description="Claude API Key"
        )
        ENABLE_SKILL_LOADING: bool = Field(
            default=True,
            description="是否启用 Skill 自动加载"
        )
        MIN_CONFIDENCE: str = Field(
            default="medium",
            description="最低路由置信度 (low/medium/high)"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.engine: Optional[SkillEngine] = None

    def _init_engine(self):
        """懒加载 Skill 引擎"""
        if self.engine is None and self.valves.ENABLE_SKILL_LOADING:
            api_key = self.valves.CLAUDE_API_KEY or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("⚠️  未配置 Claude API Key，Skill 加载功能已禁用")
                return False

            try:
                self.engine = SkillEngine(
                    skills_dir=self.valves.SKILLS_DIR,
                    api_key=api_key
                )
                print(f"✅ Skill 引擎初始化成功")
                return True
            except Exception as e:
                print(f"❌ Skill 引擎初始化失败: {e}")
                return False

        return self.engine is not None

    def inlet(self, body: Dict, __user__: Optional[Dict] = None) -> Dict:
        """
        在消息发送到 LLM 前处理（注入 Skills）

        Args:
            body: 请求体，包含 messages
            __user__: 用户信息

        Returns:
            修改后的 body
        """
        if not self.valves.ENABLE_SKILL_LOADING:
            return body

        if not self._init_engine():
            return body

        try:
            # 提取用户最新消息
            messages = body.get("messages", [])
            if not messages:
                return body

            last_message = messages[-1]
            if last_message.get("role") != "user":
                return body

            user_query = last_message.get("content", "")
            if not user_query:
                return body

            # 提取对话历史（排除最新消息）
            conversation_history = messages[:-1] if len(messages) > 1 else None

            # 使用 Skill 引擎路由和加载
            result = self.engine.answer_question(
                user_query=user_query,
                conversation_history=conversation_history
            )

            if not result.success or not result.loaded_skills:
                print(f"⚠️  未找到相关 Skills 或执行失败")
                return body

            # 检查置信度
            confidence = result.routing_info.get("confidence", "low")
            if confidence == "low" and self.valves.MIN_CONFIDENCE in ["medium", "high"]:
                print(f"⚠️  路由置信度过低 ({confidence})，跳过 Skill 注入")
                return body

            # 构建知识上下文
            knowledge_context = self._build_knowledge_context(result)

            # 将知识注入到用户消息前
            # 方式1：作为系统消息注入
            skill_message = {
                "role": "system",
                "content": knowledge_context
            }

            # 插入到最新消息之前
            messages.insert(-1, skill_message)

            # 更新 body
            body["messages"] = messages

            # 添加元数据（供 outlet 使用）
            body["__skill_metadata__"] = {
                "loaded_skills": [s["skill_id"] for s in result.loaded_skills],
                "routing_info": result.routing_info,
                "tokens_used": result.tokens_used
            }

            print(f"✅ 已注入 {len(result.loaded_skills)} 个 Skills")

        except Exception as e:
            print(f"❌ Skill 加载失败: {e}")
            # 失败时返回原始 body，不影响正常对话

        return body

    def outlet(self, body: Dict, __user__: Optional[Dict] = None) -> Dict:
        """
        在 LLM 响应返回给用户后处理（可选：添加元数据）

        Args:
            body: 响应体
            __user__: 用户信息

        Returns:
            修改后的 body
        """
        # 可以在这里添加 Skills 使用信息到响应中
        skill_metadata = body.get("__skill_metadata__")

        if skill_metadata:
            # 示例：在响应末尾添加来源标注
            messages = body.get("messages", [])
            if messages and messages[-1].get("role") == "assistant":
                loaded_skills = skill_metadata.get("loaded_skills", [])
                if loaded_skills:
                    citation = f"\n\n---\n*📚 参考知识: {', '.join(loaded_skills)}*"
                    messages[-1]["content"] += citation

        return body

    def _build_knowledge_context(self, result) -> str:
        """构建知识上下文"""
        from .skill_engine import SkillContextBuilder

        builder = SkillContextBuilder()
        context = builder.build_context(
            loaded_skills=[
                self.engine.skill_loader.get_skill(s["skill_id"])
                for s in result.loaded_skills
            ],
            routing_info=result.routing_info
        )

        return context
```

### 方式2：Open WebUI Function（可选）

**functions/skill_qa_function.py：**

```python
"""
title: Skill Q&A Function
description: 基于 Skills 的问答功能
author: Your Name
version: 1.0.0
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class Tools:
    """Open WebUI Function for Skill-based Q&A"""

    class Valves(BaseModel):
        SKILLS_DIR: str = Field(default="knowledge_base/skills")
        CLAUDE_API_KEY: str = Field(default="")

    def __init__(self):
        self.valves = self.Valves()

    def ask_knowledge_base(
        self,
        question: str,
        __user__: Optional[Dict] = None
    ) -> str:
        """
        查询知识库

        Args:
            question: 用户问题

        Returns:
            答案
        """
        from .skill_engine import SkillEngine
        import os

        api_key = self.valves.CLAUDE_API_KEY or os.getenv("ANTHROPIC_API_KEY")

        engine = SkillEngine(
            skills_dir=self.valves.SKILLS_DIR,
            api_key=api_key
        )

        result = engine.answer_question(question)

        if result.success:
            return result.answer
        else:
            return f"抱歉，查询失败: {result.error}"
```

### 依赖和配置

**requirements.txt（如果需要独立安装）：**

```txt
pydantic>=2.9.0
anthropic>=0.40.0
pyyaml>=6.0
```

**注意：** Open WebUI Filters 和 Functions 通常不需要独立部署，它们直接运行在 Open WebUI 进程中。

### 启用 Filter

1. **将文件放到 Open WebUI 目录：**
   ```bash
   cp filters/skill_knowledge_filter.py /path/to/open-webui/backend/open_webui/apps/webui/routers/filters/
   ```

2. **在 Admin Panel 中启用：**
   - 进入 Settings → Filters
   - 找到 "Skill Knowledge Filter"
   - 配置参数（Claude API Key, Skills 目录）
   - 启用 Filter

3. **配置环境变量：**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key"
   ```

## 测试验证

### 1. Filter 注入测试

```python
# 模拟 Open WebUI 请求
filter = Filter()

test_body = {
    "messages": [
        {"role": "user", "content": "萨省的 PST 税率是多少？"}
    ]
}

# 调用 inlet
result = filter.inlet(test_body)

# 验证
assert len(result["messages"]) == 2  # 用户消息 + 系统消息（Skills）
assert result["messages"][0]["role"] == "system"  # Skills 作为系统消息
assert "skill_id" in str(result["messages"][0]["content"])  # 包含 Skill 内容

print("✅ Filter 注入测试通过")
```

### 2. 对话历史处理测试

```python
test_body = {
    "messages": [
        {"role": "user", "content": "萨省的税率是多少？"},
        {"role": "assistant", "content": "萨省的 PST 是 6%"},
        {"role": "user", "content": "那 GST 呢？"}  # 跟进问题
    ]
}

result = filter.inlet(test_body)

# SkillEngine 应该能理解这是关于萨省税率的跟进问题
assert "__skill_metadata__" in result
print("✅ 对话历史处理测试通过")
```

### 3. 置信度过滤测试

```python
# 设置最低置信度为 high
filter.valves.MIN_CONFIDENCE = "high"

# 发送模糊问题
test_body = {
    "messages": [
        {"role": "user", "content": "今天天气怎么样？"}  # 与知识库无关
    ]
}

result = filter.inlet(test_body)

# 应该不注入 Skills（置信度过低或无匹配）
assert len(result["messages"]) == 1  # 只有原始用户消息
print("✅ 置信度过滤测试通过")
```

### 4. 端到端测试（在 Open WebUI 中）

1. **启用 Filter**
2. **发送测试问题：** "萨省的税率是多少？"
3. **检查日志：**
   ```
   ✅ Skill 引擎初始化成功
   ✅ 已注入 1 个 Skills
   ```
4. **验证回复：** 应包含准确的税率信息，并引用 Skill 来源

### 5. 元数据传递测试

```python
result = filter.inlet(test_body)

# 调用 outlet
result = filter.outlet(result)

# 验证响应中包含来源标注
messages = result.get("messages", [])
if messages and messages[-1].get("role") == "assistant":
    content = messages[-1].get("content", "")
    assert "📚 参考知识:" in content  # 来源标注

print("✅ 元数据传递测试通过")
```

## 注意事项

**1. Open WebUI Filter API 兼容性**
- 确保使用正确的 Filter 类结构
- `inlet()` 和 `outlet()` 方法签名必须匹配
- 使用 `Valves` 内部类定义配置参数
- 参数名使用 `__user__` 而非 `user`

**2. 错误处理不能影响正常对话**
- **关键原则：** 任何错误都应该降级，返回原始 body
- 用户不应因为 Filter 错误而无法使用 LLM
- 记录详细错误日志便于调试
- 示例：
  ```python
  try:
      # Skill 加载逻辑
      ...
  except Exception as e:
      print(f"❌ Skill 加载失败: {e}")
      return body  # 返回原始请求
  ```

**3. 性能优化**
- **路由缓存：** ClaudeSkillRouter 应实现缓存（参考任务13）
- **懒加载：** 只在第一次请求时初始化 SkillEngine
- **异步处理（可选）：** 如果 Open WebUI 支持异步 Filter
- **监控指标：**
  - 路由时间
  - Skills 加载时间
  - 缓存命中率

**4. 调试技巧**
- 使用 `print()` 输出日志（Open WebUI 会显示在控制台）
- 在 `__skill_metadata__` 中保存调试信息
- 测试时可以临时禁用 MIN_CONFIDENCE 过滤

**5. 多 LLM 模型兼容性**
- 当前实现支持任何支持 system 消息的 LLM
- 如果目标 LLM 不支持 system 角色，修改注入方式：
  ```python
  # 替代方案：注入到用户消息中
  user_message = f"{knowledge_context}\n\n---\n\n{user_query}"
  messages[-1]["content"] = user_message
  ```

## 依赖关系

**前置任务：**
- 任务11：SkillLoader（加载 Skills）
- 任务13：ClaudeSkillRouter（路由 Skills）
- 任务14：SkillEngine（端到端引擎）
- 任务12：SkillMetadataManager（元数据验证，可选）

**后置任务：**
- 任务16：集成测试
- 任务17：成本优化（路由缓存）
