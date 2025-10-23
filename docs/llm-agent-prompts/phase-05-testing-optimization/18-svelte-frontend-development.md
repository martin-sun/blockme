# 任务18：Svelte 前端完整功能开发

## 任务目标

完成 Svelte 前端的所有核心功能开发，包括对话界面、文档上传、知识库管理、成本监控等。实现流畅的用户体验，集成后端 API，提供直观的界面让用户能够轻松管理专业领域知识库。

## 技术要求

**核心功能：**
- 实时对话界面（支持流式响应）
- 文档批量上传
- 知识库可视化管理
- 成本监控面板
- 响应式设计

**技术栈：**
- SvelteKit + TypeScript
- Tailwind CSS
- EventSource（SSE）
- Axios（HTTP 客户端）

**用户体验：**
- 响应时间 < 200ms（UI 交互）
- 流式响应首字 < 3秒
- 操作反馈及时
- 错误提示友好

## 实现步骤

### 1. 完善对话界面（支持流式）

实现流式对话，实时显示 LLM 回复。

### 2. 实现文档上传功能

支持拖拽上传、进度显示、批量处理。

### 3. 开发知识库管理界面

可视化展示 Skills，支持搜索和过滤。

### 4. 实现成本监控面板

显示 API 使用统计和成本。

### 5. 优化响应式布局

适配移动端和平板设备。

## 关键代码提示

### 项目结构

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatMessage.svelte
│   │   │   │   ├── ChatInput.svelte
│   │   │   │   └── SkillTag.svelte
│   │   │   ├── document/
│   │   │   │   ├── DocumentUploader.svelte
│   │   │   │   └── DocumentCard.svelte
│   │   │   └── knowledge/
│   │   │       ├── CollectionCard.svelte
│   │   │       └── SkillBrowser.svelte
│   │   ├── stores/
│   │   │   ├── chat.ts
│   │   │   └── documents.ts
│   │   └── api/
│   │       ├── client.ts
│   │       ├── chat.ts
│   │       └── documents.ts
│   └── routes/
│       ├── +layout.svelte
│       ├── +page.svelte          # 对话页面
│       ├── documents/
│       │   └── +page.svelte      # 文档管理
│       └── knowledge/
│           └── +page.svelte      # 知识库浏览
```

### 流式对话组件

**src/lib/components/chat/ChatWindow.svelte：**
```svelte
<script lang="ts">
  import { onMount, afterUpdate } from 'svelte';
  import type { Message } from '$lib/types';
  import { sendMessageStream } from '$lib/api/chat';
  import ChatMessage from './ChatMessage.svelte';
  import ChatInput from './ChatInput.svelte';

  let messages: Message[] = [];
  let isStreaming = false;
  let currentStreamingMessage = '';
  let currentSkills: string[] = [];
  let chatContainer: HTMLDivElement;

  async function handleSendMessage(content: string) {
    // 添加用户消息
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date()
    };
    messages = [...messages, userMessage];

    // 开始流式响应
    isStreaming = true;
    currentStreamingMessage = '';
    currentSkills = [];

    try {
      await sendMessageStream(
        {
          message: content,
          conversationHistory: messages.slice(0, -1)
        },
        (chunk) => {
          if (chunk.type === 'skill') {
            currentSkills = chunk.skills.map((s: any) => s.skill_id);
          } else if (chunk.type === 'text') {
            currentStreamingMessage += chunk.content;
          } else if (chunk.type === 'done') {
            // 流式完成，添加到消息列表
            const assistantMessage: Message = {
              id: crypto.randomUUID(),
              role: 'assistant',
              content: currentStreamingMessage,
              timestamp: new Date(),
              loadedSkills: currentSkills
            };
            messages = [...messages, assistantMessage];
            isStreaming = false;
            currentStreamingMessage = '';
            currentSkills = [];
          } else if (chunk.type === 'error') {
            console.error('流式错误:', chunk.error);
            isStreaming = false;
          }
        }
      );
    } catch (error) {
      console.error('发送消息失败:', error);
      isStreaming = false;
    }
  }

  afterUpdate(() => {
    // 自动滚动到底部
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  });
</script>

<div class="flex flex-col h-full bg-white rounded-lg shadow-sm">
  <!-- 消息列表 -->
  <div
    bind:this={chatContainer}
    class="flex-1 overflow-y-auto p-6 space-y-4"
  >
    {#each messages as message (message.id)}
      <ChatMessage {message} />
    {/each}

    <!-- 流式消息 -->
    {#if isStreaming}
      <div class="flex justify-start">
        <div class="bg-gray-100 text-gray-900 rounded-lg px-4 py-2 max-w-[80%]">
          <p class="whitespace-pre-wrap">{currentStreamingMessage}</p>
          {#if currentSkills.length > 0}
            <div class="mt-2 flex flex-wrap gap-1">
              {#each currentSkills as skill}
                <span class="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                  📚 {skill}
                </span>
              {/each}
            </div>
          {/if}
          <div class="mt-2 flex space-x-1">
            <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
          </div>
        </div>
      </div>
    {/if}
  </div>

  <!-- 输入框 -->
  <ChatInput
    on:send={(e) => handleSendMessage(e.detail)}
    disabled={isStreaming}
  />
</div>
```

**src/lib/components/chat/ChatMessage.svelte：**
```svelte
<script lang="ts">
  import type { Message } from '$lib/types';
  import SkillTag from './SkillTag.svelte';

  export let message: Message;

  $: isUser = message.role === 'user';
</script>

<div class={isUser ? 'flex justify-end' : 'flex justify-start'}>
  <div
    class={isUser
      ? 'bg-blue-600 text-white rounded-lg px-4 py-2 max-w-[80%]'
      : 'bg-gray-100 text-gray-900 rounded-lg px-4 py-2 max-w-[80%]'}
  >
    <p class="whitespace-pre-wrap">{message.content}</p>

    {#if message.loadedSkills && message.loadedSkills.length > 0}
      <div class="mt-2 flex flex-wrap gap-1">
        {#each message.loadedSkills as skill}
          <SkillTag {skill} />
        {/each}
      </div>
    {/if}

    <div class="mt-1 text-xs opacity-75">
      {new Date(message.timestamp).toLocaleTimeString()}
    </div>
  </div>
</div>
```

**src/lib/components/chat/ChatInput.svelte：**
```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let disabled = false;

  let inputValue = '';
  const dispatch = createEventDispatcher();

  function handleSend() {
    if (!inputValue.trim() || disabled) return;

    dispatch('send', inputValue);
    inputValue = '';
  }

  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  }
</script>

<div class="border-t p-4">
  <div class="flex space-x-2">
    <textarea
      bind:value={inputValue}
      on:keypress={handleKeyPress}
      placeholder="输入你的问题..."
      class="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
      rows="2"
      {disabled}
    />
    <button
      on:click={handleSend}
      disabled={disabled || !inputValue.trim()}
      class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
      发送
    </button>
  </div>
</div>
```

### 文档上传组件

**src/lib/components/document/DocumentUploader.svelte：**
```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { uploadDocuments } from '$lib/api/documents';
  import type { Document } from '$lib/types';

  const dispatch = createEventDispatcher();

  let files: FileList | null = null;
  let isDragging = false;
  let uploadProgress: Map<string, number> = new Map();
  let selectedDomain = 'general';

  const domains = [
    { value: 'programming', label: '编程技术' },
    { value: 'data_science', label: '数据科学' },
    { value: 'business', label: '商业管理' },
    { value: 'general', label: '通用知识' }
  ];

  function handleDragOver(event: DragEvent) {
    event.preventDefault();
    isDragging = true;
  }

  function handleDragLeave() {
    isDragging = false;
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    isDragging = false;
    files = event.dataTransfer?.files || null;
  }

  async function handleUpload() {
    if (!files || files.length === 0) return;

    const formData = new FormData();
    for (const file of Array.from(files)) {
      formData.append('files', file);
    }
    formData.append('domain', selectedDomain);

    try {
      const response = await uploadDocuments(formData);
      dispatch('uploaded', response);
      files = null;
    } catch (error) {
      console.error('上传失败:', error);
    }
  }
</script>

<div class="bg-white rounded-lg shadow-sm p-6">
  <h2 class="text-xl font-bold mb-4">上传文档</h2>

  <!-- 拖拽区域 -->
  <div
    on:dragover={handleDragOver}
    on:dragleave={handleDragLeave}
    on:drop={handleDrop}
    class="border-2 border-dashed rounded-lg p-8 text-center transition-colors {isDragging
      ? 'border-blue-500 bg-blue-50'
      : 'border-gray-300 hover:border-gray-400'}"
  >
    <input
      type="file"
      bind:files
      multiple
      accept=".pdf,.docx,.xlsx,.pptx"
      class="hidden"
      id="fileInput"
    />
    <label for="fileInput" class="cursor-pointer">
      <div class="text-gray-600">
        <svg class="mx-auto h-12 w-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 48 48">
          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <p class="text-lg">拖拽文件到这里，或点击选择文件</p>
        <p class="text-sm text-gray-500 mt-2">支持 PDF, Word, Excel, PowerPoint</p>
      </div>
    </label>
  </div>

  {#if files && files.length > 0}
    <div class="mt-4">
      <p class="text-sm text-gray-600 mb-2">已选择 {files.length} 个文件</p>
      <ul class="space-y-1 text-sm">
        {#each Array.from(files) as file}
          <li class="text-gray-700">📄 {file.name}</li>
        {/each}
      </ul>
    </div>
  {/if}

  <!-- 领域选择 -->
  <div class="mt-4">
    <label class="block text-sm font-medium text-gray-700 mb-2">知识域</label>
    <select
      bind:value={selectedDomain}
      class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      {#each domains as domain}
        <option value={domain.value}>{domain.label}</option>
      {/each}
    </select>
  </div>

  <!-- 上传按钮 -->
  <button
    on:click={handleUpload}
    disabled={!files || files.length === 0}
    class="mt-4 w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
  >
    开始处理
  </button>
</div>
```

### API 客户端

**src/lib/api/chat.ts：**
```typescript
import type { ChatRequest, ChatResponse } from '$lib/types';

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

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('无法读取响应流');
  }

  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            onChunk(data);
          } catch (e) {
            console.error('解析 SSE 数据失败:', e);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
```

**src/lib/api/documents.ts：**
```typescript
import { apiClient } from './client';

export async function uploadDocuments(formData: FormData) {
  const response = await apiClient.post('/api/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}

export async function getDocuments() {
  const response = await apiClient.get('/api/documents');
  return response.data;
}
```

### 主页面

**src/routes/+page.svelte：**
```svelte
<script lang="ts">
  import ChatWindow from '$lib/components/chat/ChatWindow.svelte';
</script>

<svelte:head>
  <title>BlockMe 知识库 - 对话</title>
</svelte:head>

<div class="max-w-6xl mx-auto">
  <div class="mb-6">
    <h1 class="text-3xl font-bold text-gray-900">智能对话</h1>
    <p class="text-gray-600 mt-2">与专业知识库对话，获取准确答案</p>
  </div>

  <ChatWindow />
</div>
```

**src/routes/documents/+page.svelte：**
```svelte
<script lang="ts">
  import DocumentUploader from '$lib/components/document/DocumentUploader.svelte';
</script>

<svelte:head>
  <title>文档管理 - BlockMe 知识库</title>
</svelte:head>

<div class="max-w-4xl mx-auto">
  <div class="mb-6">
    <h1 class="text-3xl font-bold text-gray-900">文档管理</h1>
    <p class="text-gray-600 mt-2">上传和管理你的专业领域文档</p>
  </div>

  <DocumentUploader on:uploaded={() => console.log('上传完成')} />
</div>
```

## 测试验证

### 1. 启动开发服务器

```bash
cd frontend
npm run dev
```

### 2. 功能测试清单

- ✅ 对话功能正常
- ✅ 流式响应实时显示
- ✅ Skill 标签正确显示
- ✅ 文档上传功能正常
- ✅ 拖拽上传可用
- ✅ 进度显示准确
- ✅ 响应式布局正常

### 3. 用户体验测试

- UI 响应速度
- 动画流畅度
- 错误提示友好度
- 移动端适配

### 4. 浏览器兼容性

- Chrome/Edge
- Firefox
- Safari

## 注意事项

**用户体验原则：**
1. 即时反馈（加载状态、进度条）
2. 清晰错误提示（友好的错误信息）
3. 流畅动画（transition 和 animation）
4. 响应式设计（移动端优先）

**性能优化：**
1. 懒加载组件
2. 虚拟滚动（长消息列表）
3. 防抖节流（搜索输入）
4. 图片优化

**可访问性：**
1. 语义化 HTML
2. 键盘导航支持
3. ARIA 标签
4. 颜色对比度

**参考 BeanFlow-LLM：**
- 复用对话组件设计
- 参考文档上传实现
- 借鉴状态管理方式

## 依赖关系

**前置任务：**
- 任务01：Svelte 前端环境搭建
- 任务15：FastAPI 聊天接口集成
- 所有后端功能（02-14）

**完成标志：**
- 用户可通过界面完成所有操作
- 对话流畅，响应及时
- 文档上传和管理简单直观
- 移动端和桌面端都可用
