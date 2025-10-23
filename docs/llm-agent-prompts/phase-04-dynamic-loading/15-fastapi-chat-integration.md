# 任务15：FastAPI 聊天接口集成

## 任务目标

实现 FastAPI 后端的聊天接口，集成 SkillEngine 实现动态知识加载。用户通过前端发送消息，后端自动路由相关 Skills，将完整 Skill 内容注入到 LLM 上下文中，返回智能回答。

**核心思路：**
- 使用 SkillEngine（任务14）处理用户问题
- 构建带知识上下文的 prompt
- 调用 Claude/GLM API 生成回答
- 支持流式响应（SSE）
- 返回加载的 Skills 信息

## 技术要求

**后端框架：**
- FastAPI >= 0.100.0
- Python 3.11+
- uvicorn（ASGI 服务器）

**核心组件：**
- SkillEngine（任务14）：端到端问答引擎
- ClaudeSkillRouter（任务13）：智能路由
- SkillLoader（任务11）：加载 Skills
- SkillContextBuilder（任务14）：构建上下文

**功能要求：**
- RESTful API 接口
- 流式响应（SSE）支持
- 对话历史管理
- 错误处理和日志
- CORS 配置

**性能要求：**
- 路由时间 < 2秒
- 首字响应 < 3秒
- 支持并发请求

## 实现步骤

### 1. 创建 FastAPI 项目结构

```bash
cd /Users/woohelps/CascadeProjects/blockme
mkdir -p backend/app/api/routes
mkdir -p backend/app/core
mkdir -p backend/app/models
mkdir -p backend/app/services
```

### 2. 实现聊天 API 路由

创建聊天接口，集成 SkillEngine。

### 3. 实现流式响应

使用 Server-Sent Events (SSE) 实现流式回答。

### 4. 配置 CORS 和中间件

允许前端跨域访问。

### 5. 部署和测试

使用 uvicorn 启动服务。

## 关键代码提示

### 项目结构

```
backend/
├── app/
│   ├── main.py                 # FastAPI 应用入口
│   ├── api/
│   │   └── routes/
│   │       ├── chat.py         # 聊天接口
│   │       ├── documents.py    # 文档上传接口
│   │       └── knowledge.py    # 知识库管理接口
│   ├── models/
│   │   └── schemas.py          # Pydantic 模型
│   ├── services/
│   │   └── chat_service.py     # 聊天服务
│   └── core/
│       └── config.py           # 配置管理
├── knowledge_base/             # 知识库存储
│   └── skills/
├── pyproject.toml              # uv 项目配置
└── README.md
```

### 主应用入口

**backend/app/main.py：**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, documents, knowledge

app = FastAPI(
    title="BlockMe Knowledge API",
    description="智能知识库对话系统",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Svelte 开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])

@app.get("/")
async def root():
    return {"message": "BlockMe Knowledge API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### Pydantic 模型

**backend/app/models/schemas.py：**
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class Message(BaseModel):
    """消息模型"""
    id: str
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime
    loaded_skills: Optional[List[str]] = None

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., min_length=1, description="用户消息")
    conversation_history: Optional[List[Message]] = Field(
        default=None,
        description="对话历史"
    )
    stream: bool = Field(default=False, description="是否使用流式响应")

class ChatResponse(BaseModel):
    """聊天响应"""
    answer: str
    loaded_skills: List[str]
    tokens_used: Optional[int] = None
    routing_info: Optional[dict] = None

class SkillInfo(BaseModel):
    """Skill 信息"""
    skill_id: str
    title: str
    confidence: str

class StreamChunk(BaseModel):
    """流式响应数据块"""
    type: Literal["text", "skill", "done", "error"]
    content: Optional[str] = None
    skills: Optional[List[SkillInfo]] = None
    error: Optional[str] = None
```

### 聊天服务

**backend/app/services/chat_service.py：**
```python
import os
from typing import List, AsyncGenerator
from anthropic import Anthropic, AsyncAnthropic
from app.models.schemas import Message, ChatResponse, SkillInfo, StreamChunk

# 导入 SkillEngine（需要将任务14的代码放到合适位置）
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from src.knowledge_manager.skill_engine import SkillEngine

class ChatService:
    """聊天服务"""

    def __init__(self):
        self.skill_engine = SkillEngine(
            skills_dir="knowledge_base/skills",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.async_anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def chat(
        self,
        user_message: str,
        conversation_history: List[Message] | None = None
    ) -> ChatResponse:
        """
        处理聊天请求（非流式）

        Args:
            user_message: 用户消息
            conversation_history: 对话历史

        Returns:
            聊天响应
        """
        # 1. 使用 SkillEngine 路由和加载相关知识
        skill_result = self.skill_engine.answer_question(
            user_query=user_message,
            conversation_history=[
                {"role": msg.role, "content": msg.content}
                for msg in (conversation_history or [])
            ]
        )

        if not skill_result.success:
            return ChatResponse(
                answer=f"抱歉，处理失败：{skill_result.error}",
                loaded_skills=[],
                routing_info={"error": skill_result.error}
            )

        # 2. 构建消息列表
        messages = []

        # 添加知识上下文（如果有）
        if skill_result.loaded_skills:
            knowledge_context = self._build_knowledge_context(skill_result)
            messages.append({
                "role": "user",
                "content": knowledge_context
            })

        # 添加对话历史
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })

        # 3. 调用 Claude API
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                system="你是一个专业的知识库助手。请根据提供的知识内容回答用户问题。",
                messages=messages
            )

            answer = response.content[0].text

            return ChatResponse(
                answer=answer,
                loaded_skills=[s["skill_id"] for s in skill_result.loaded_skills],
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                routing_info=skill_result.routing_info
            )

        except Exception as e:
            return ChatResponse(
                answer=f"抱歉，调用 LLM 失败：{str(e)}",
                loaded_skills=[],
                routing_info={"error": str(e)}
            )

    async def chat_stream(
        self,
        user_message: str,
        conversation_history: List[Message] | None = None
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        处理聊天请求（流式）

        Yields:
            流式响应数据块
        """
        try:
            # 1. 使用 SkillEngine 路由和加载相关知识
            skill_result = self.skill_engine.answer_question(
                user_query=user_message,
                conversation_history=[
                    {"role": msg.role, "content": msg.content}
                    for msg in (conversation_history or [])
                ]
            )

            if not skill_result.success:
                yield StreamChunk(
                    type="error",
                    error=skill_result.error
                )
                return

            # 2. 先返回加载的 Skills 信息
            if skill_result.loaded_skills:
                yield StreamChunk(
                    type="skill",
                    skills=[
                        SkillInfo(
                            skill_id=s["skill_id"],
                            title=s.get("title", s["skill_id"]),
                            confidence=skill_result.routing_info.get("confidence", "medium")
                        )
                        for s in skill_result.loaded_skills
                    ]
                )

            # 3. 构建消息列表
            messages = []

            if skill_result.loaded_skills:
                knowledge_context = self._build_knowledge_context(skill_result)
                messages.append({
                    "role": "user",
                    "content": knowledge_context
                })

            if conversation_history:
                for msg in conversation_history:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })

            messages.append({
                "role": "user",
                "content": user_message
            })

            # 4. 调用 Claude API（流式）
            async with self.async_anthropic_client.messages.stream(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                system="你是一个专业的知识库助手。请根据提供的知识内容回答用户问题。",
                messages=messages
            ) as stream:
                async for text in stream.text_stream:
                    yield StreamChunk(type="text", content=text)

            # 5. 完成
            yield StreamChunk(type="done")

        except Exception as e:
            yield StreamChunk(type="error", error=str(e))

    def _build_knowledge_context(self, skill_result) -> str:
        """构建知识上下文"""
        context_parts = ["# 相关知识\n"]

        for skill in skill_result.loaded_skills:
            context_parts.append(f"## {skill.get('title', skill['skill_id'])}\n")
            context_parts.append(skill.get('content', '') + "\n")

        context_parts.append("\n请基于以上知识回答用户问题。")

        return "\n".join(context_parts)
```

### 聊天路由

**backend/app/api/routes/chat.py：**
```python
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest, ChatResponse, StreamChunk
from app.services.chat_service import ChatService
import json

router = APIRouter()
chat_service = ChatService()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口（非流式）

    Args:
        request: 聊天请求

    Returns:
        聊天响应
    """
    try:
        response = await chat_service.chat(
            user_message=request.message,
            conversation_history=request.conversation_history
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    聊天接口（流式，SSE）

    Args:
        request: 聊天请求

    Returns:
        SSE 流
    """
    async def event_generator():
        try:
            async for chunk in chat_service.chat_stream(
                user_message=request.message,
                conversation_history=request.conversation_history
            ):
                # 转换为 SSE 格式
                data = chunk.model_dump_json()
                yield f"data: {data}\n\n"
        except Exception as e:
            error_chunk = StreamChunk(type="error", error=str(e))
            yield f"data: {error_chunk.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### 配置管理

**backend/app/core/config.py：**
```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""

    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GLM_API_KEY: str = os.getenv("GLM_API_KEY", "")

    # 知识库路径
    SKILLS_DIR: str = "knowledge_base/skills"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS 配置
    CORS_ORIGINS: list = ["http://localhost:5173"]

    class Config:
        env_file = ".env"

settings = Settings()
```

### 依赖配置

**backend/pyproject.toml：**
```toml
[project]
name = "blockme-backend"
version = "1.0.0"
description = "BlockMe Knowledge API"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "anthropic>=0.40.0",
    "python-multipart>=0.0.6",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "httpx>=0.24.0",
]
```

### 启动脚本

**backend/start.sh：**
```bash
#!/bin/bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 测试验证

### 1. 安装依赖

```bash
cd backend
uv sync
```

### 2. 配置环境变量

```bash
# backend/.env
ANTHROPIC_API_KEY=your-api-key-here
GLM_API_KEY=your-glm-key-here
```

### 3. 启动服务

```bash
chmod +x start.sh
./start.sh

# 或直接运行
uv run uvicorn app.main:app --reload
```

### 4. 测试 API

**测试非流式接口：**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "萨省的税率是多少？",
    "conversation_history": []
  }'
```

**测试流式接口：**
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "介绍一下萨省的税务政策",
    "stream": true
  }'
```

### 5. 集成测试

在前端调用 API：
```typescript
// src/lib/api/chat.ts
import { apiClient } from './client';
import type { ChatRequest, ChatResponse } from '$lib/types';

export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>('/api/chat', request);
  return response.data;
}

export async function sendMessageStream(
  request: ChatRequest,
  onChunk: (chunk: any) => void
): Promise<void> {
  const response = await fetch('http://localhost:8000/api/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        onChunk(data);
      }
    }
  }
}
```

## 注意事项

**错误处理：**
1. API 调用失败时返回友好错误信息
2. 记录详细日志便于调试
3. 设置超时和重试机制
4. 验证输入参数

**性能优化：**
1. 使用异步 I/O（FastAPI 原生支持）
2. 实现路由缓存（参考任务17）
3. 限流和并发控制
4. 监控响应时间

**安全考虑：**
1. API Key 不要硬编码，使用环境变量
2. 实现认证和授权（可选）
3. 输入验证和清理
4. CORS 配置限制来源

**流式响应最佳实践：**
1. 使用 SSE 而非 WebSocket（简单场景）
2. 及时发送首字节
3. 错误处理要优雅
4. 前端正确解析 SSE 数据

## 依赖关系

**前置任务：**
- 任务11：SkillLoader（加载 Skills）
- 任务13：ClaudeSkillRouter（路由 Skills）
- 任务14：SkillEngine（端到端引擎）
- 任务01：Svelte 前端环境搭建

**后置任务：**
- 任务16：集成测试
- 任务17：成本优化（路由缓存）
- 任务18：完整前端功能开发
