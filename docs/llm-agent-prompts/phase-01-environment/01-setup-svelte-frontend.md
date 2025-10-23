# 任务01：搭建 Svelte 前端环境

## 任务目标

搭建基于 SvelteKit + TypeScript 的现代化前端开发环境，提供对话界面、文档上传、知识库管理等功能的基础框架。前端通过 RESTful API 和 WebSocket 与 FastAPI 后端通信。

## 技术要求

**必需工具：**
- Node.js >= 18.0
- npm >= 9.0 或 pnpm/yarn
- TypeScript >= 5.0

**技术栈：**
- **SvelteKit**: 前端框架
- **TypeScript**: 类型安全
- **Tailwind CSS**: 样式框架
- **Vite**: 构建工具

**功能要求：**
- 响应式布局（桌面和移动端）
- 实时对话界面
- 文档上传和管理
- 知识库可视化

## 实现步骤

### 1. 创建 SvelteKit 项目

```bash
cd /Users/woohelps/CascadeProjects/blockme
npm create svelte@latest frontend

# 选择以下选项：
# - Template: Skeleton project
# - TypeScript: Yes, using TypeScript syntax
# - ESLint: Yes
# - Prettier: Yes
# - Playwright: Yes (for E2E testing)
# - Vitest: Yes (for unit testing)
```

### 2. 安装依赖

```bash
cd frontend
npm install

# 安装额外依赖
npm install -D tailwindcss postcss autoprefixer
npm install axios  # HTTP 客户端
npm install @types/axios -D
```

### 3. 配置 Tailwind CSS

```bash
npx tailwindcss init -p
```

修改 `tailwind.config.js`：
```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

创建 `src/app.css`：
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 4. 创建项目结构

```bash
mkdir -p src/lib/components
mkdir -p src/lib/stores
mkdir -p src/lib/api
mkdir -p src/lib/types
mkdir -p src/routes/api
```

### 5. 配置环境变量

创建 `.env.example`：
```bash
VITE_API_BASE_URL=http://localhost:8000
```

创建 `.env`：
```bash
cp .env.example .env
```

## 关键代码提示

### API 客户端配置

**src/lib/api/client.ts：**
```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证 token
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);
```

### 类型定义

**src/lib/types/index.ts：**
```typescript
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  loadedSkills?: string[];
}

export interface ChatRequest {
  message: string;
  conversationHistory?: Message[];
}

export interface ChatResponse {
  answer: string;
  loadedSkills: string[];
  tokensUsed?: number;
  routingInfo?: {
    confidence: 'low' | 'medium' | 'high';
    reasoning: string;
  };
}

export interface Document {
  id: string;
  filename: string;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  progress?: number;
  error?: string;
  skillId?: string;
}

export interface KnowledgeCollection {
  id: string;
  name: string;
  description: string;
  domain: string;
  documentCount: number;
  icon?: string;
}
```

### 基础布局

**src/routes/+layout.svelte：**
```svelte
<script lang="ts">
  import '../app.css';
</script>

<div class="min-h-screen bg-gray-50">
  <nav class="bg-white shadow-sm border-b">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex items-center">
          <h1 class="text-xl font-bold text-gray-900">BlockMe 知识库</h1>
        </div>
        <div class="flex items-center space-x-4">
          <a href="/" class="text-gray-700 hover:text-gray-900">对话</a>
          <a href="/documents" class="text-gray-700 hover:text-gray-900">文档管理</a>
          <a href="/knowledge" class="text-gray-700 hover:text-gray-900">知识库</a>
        </div>
      </div>
    </div>
  </nav>

  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <slot />
  </main>
</div>
```

### 对话界面（基础版）

**src/routes/+page.svelte：**
```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import type { Message } from '$lib/types';

  let messages: Message[] = [];
  let inputMessage = '';
  let isLoading = false;

  async function sendMessage() {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    messages = [...messages, userMessage];
    const currentInput = inputMessage;
    inputMessage = '';
    isLoading = true;

    try {
      // TODO: 实现 API 调用（任务15）
      // const response = await apiClient.post('/chat', { ... });

      // 临时占位响应
      setTimeout(() => {
        const assistantMessage: Message = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: '这是临时响应。后端 API 将在任务15中集成。',
          timestamp: new Date()
        };
        messages = [...messages, assistantMessage];
        isLoading = false;
      }, 1000);
    } catch (error) {
      console.error('发送消息失败:', error);
      isLoading = false;
    }
  }

  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }
</script>

<div class="max-w-4xl mx-auto">
  <div class="bg-white rounded-lg shadow-sm">
    <!-- 消息列表 -->
    <div class="h-[600px] overflow-y-auto p-6 space-y-4">
      {#each messages as message (message.id)}
        <div class={message.role === 'user' ? 'flex justify-end' : 'flex justify-start'}>
          <div
            class={message.role === 'user'
              ? 'bg-blue-600 text-white rounded-lg px-4 py-2 max-w-[80%]'
              : 'bg-gray-100 text-gray-900 rounded-lg px-4 py-2 max-w-[80%]'}
          >
            <p class="whitespace-pre-wrap">{message.content}</p>
            {#if message.loadedSkills && message.loadedSkills.length > 0}
              <div class="mt-2 text-xs opacity-75">
                📚 参考知识: {message.loadedSkills.join(', ')}
              </div>
            {/if}
          </div>
        </div>
      {/each}

      {#if isLoading}
        <div class="flex justify-start">
          <div class="bg-gray-100 rounded-lg px-4 py-2">
            <div class="flex space-x-2">
              <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
            </div>
          </div>
        </div>
      {/if}
    </div>

    <!-- 输入框 -->
    <div class="border-t p-4">
      <div class="flex space-x-2">
        <textarea
          bind:value={inputMessage}
          on:keypress={handleKeyPress}
          placeholder="输入你的问题..."
          class="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          rows="2"
          disabled={isLoading}
        />
        <button
          on:click={sendMessage}
          disabled={isLoading || !inputMessage.trim()}
          class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          发送
        </button>
      </div>
    </div>
  </div>
</div>
```

### 配置文件

**vite.config.ts：**
```typescript
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

**tsconfig.json：**
```json
{
  "extends": "./.svelte-kit/tsconfig.json",
  "compilerOptions": {
    "allowJs": true,
    "checkJs": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "skipLibCheck": true,
    "sourceMap": true,
    "strict": true
  }
}
```

## 测试验证

### 1. 启动开发服务器

```bash
npm run dev
```

浏览器访问：`http://localhost:5173`

### 2. 验证基础功能

- ✅ 页面正常加载
- ✅ 导航菜单可用
- ✅ 对话界面显示正常
- ✅ 可以输入和发送消息（临时响应）
- ✅ 响应式布局正常

### 3. 检查类型安全

```bash
npm run check
```

应该没有类型错误。

### 4. 运行测试

```bash
npm run test:unit
```

### 5. 构建生产版本

```bash
npm run build
npm run preview
```

## 注意事项

**项目结构最佳实践：**
1. 组件按功能分类（`components/chat/`, `components/document/`, 等）
2. 使用 TypeScript 确保类型安全
3. API 调用统一在 `lib/api/` 中管理
4. 复用 BeanFlow-LLM 的经验和组件

**性能优化：**
1. 使用 Svelte 的响应式特性
2. 懒加载大型组件
3. 虚拟滚动处理长对话历史
4. 图片和文件压缩

**开发体验：**
1. 配置 ESLint 和 Prettier
2. 使用 Git hooks（husky）
3. 添加开发文档
4. 使用 Storybook（可选）

**与 BeanFlow-LLM 的区别：**
- BeanFlow-LLM 专注于财务记账，本项目专注于知识库对话
- 可以复用 BeanFlow-LLM 的对话组件和布局
- API 集成方式相似，但数据结构不同

## 依赖关系

**前置任务：** 无

**后置任务：**
- 任务02：配置 Claude API
- 任务03：配置 GLM API
- 任务15：FastAPI 聊天接口集成
- 任务18：完整前端功能开发

**参考项目：**
- `/Users/woohelps/CascadeProjects/BeanFlow-LLM/frontend`
