<script lang="ts">
	import type { Message } from '$lib/types';

	let messages: Message[] = $state([]);
	let inputMessage = $state('');
	let isLoading = $state(false);

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
							<div
								class="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
								style="animation-delay: 0.2s"
							></div>
							<div
								class="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
								style="animation-delay: 0.4s"
							></div>
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
					onkeypress={handleKeyPress}
					placeholder="输入你的问题..."
					class="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
					rows="2"
					disabled={isLoading}
				/>
				<button
					onclick={sendMessage}
					disabled={isLoading || !inputMessage.trim()}
					class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
				>
					发送
				</button>
			</div>
		</div>
	</div>
</div>
