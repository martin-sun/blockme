<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

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
		{@render children?.()}
	</main>
</div>
