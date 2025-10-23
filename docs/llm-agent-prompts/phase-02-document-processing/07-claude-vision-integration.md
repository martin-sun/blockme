# 任务07：Claude Vision API 集成

## 任务目标

集成 Anthropic Claude Vision API，将 PDF/Office 文档生成的图像转换为结构化 Markdown 文本。利用 Claude 3.5 Sonnet 的强大视觉理解能力，准确提取文档中的文字、表格、公式和图表描述。

## 技术要求

**API 配置：**
- Anthropic API Key（任务02已配置）
- 推荐模型：`claude-3-5-sonnet-20241022`
- 支持 Vision 的模型版本

**输入要求：**
- 图像格式：JPEG/PNG/WebP
- 单张大小：< 32MB
- 分辨率：建议 300 DPI

**输出要求：**
- Markdown 格式
- 保留表格结构
- 提取代码块
- 描述图表和公式

## 实现步骤

### 1. 安装 Anthropic SDK

```bash
uv add anthropic
```

### 2. 创建 Vision API 封装类

设计一个 `ClaudeVisionExtractor` 类：
- 图像批量处理
- 自动合并多页内容
- 错误重试机制
- 成本追踪

### 3. 优化提示词

设计专门的提示词模板，指导 Claude：
- 提取所有文字
- 保留 Markdown 格式
- 表格转换为 Markdown 表格
- 公式转换为 LaTeX
- 图表生成文字描述

### 4. 实现批处理逻辑

处理多页文档：
- 逐页发送到 API
- 合并各页 Markdown
- 添加页码标注
- 去重和清理

### 5. 成本控制

实现成本优化策略：
- 图像压缩（保持可读性）
- 缓存已处理图像
- 批量处理减少请求

## 关键代码提示

**Claude Vision 提取器实现：**

```python
import anthropic
import base64
from pathlib import Path
from typing import List, Optional
import time

class ClaudeVisionExtractor:
    """Claude Vision API 文档提取器"""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

        # 成本追踪
        self.total_images_processed = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def extract_from_images(
        self,
        image_paths: List[str],
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        从图像序列提取 Markdown 内容

        Args:
            image_paths: 图像文件路径列表
            custom_prompt: 自定义提示词（None 则使用默认）

        Returns:
            合并后的 Markdown 文本
        """
        markdown_pages = []

        for idx, image_path in enumerate(image_paths, 1):
            print(f"处理第 {idx}/{len(image_paths)} 页...")

            try:
                markdown = self._extract_single_image(image_path, custom_prompt, page_num=idx)
                markdown_pages.append(markdown)

                # API 速率限制：避免过快请求
                if idx < len(image_paths):
                    time.sleep(0.5)

            except Exception as e:
                print(f"⚠️  第 {idx} 页处理失败: {e}")
                markdown_pages.append(f"<!-- 第 {idx} 页提取失败 -->")

        # 合并所有页面
        full_markdown = "\n\n---\n\n".join(markdown_pages)
        return full_markdown

    def _extract_single_image(
        self,
        image_path: str,
        custom_prompt: Optional[str],
        page_num: int
    ) -> str:
        """提取单张图像"""
        # 读取图像并编码
        image_data = self._encode_image(image_path)

        # 构建提示词
        prompt = custom_prompt or self._get_default_prompt()

        # 调用 Claude Vision API
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": self._get_media_type(image_path),
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )

        # 更新成本追踪
        self.total_images_processed += 1
        self.total_input_tokens += message.usage.input_tokens
        self.total_output_tokens += message.usage.output_tokens

        # 提取响应文本
        markdown = message.content[0].text

        # 添加页码标注
        markdown = f"<!-- Page {page_num} -->\n\n{markdown}"

        return markdown

    def _encode_image(self, image_path: str) -> str:
        """将图像编码为 base64"""
        with open(image_path, "rb") as image_file:
            return base64.standard_b64encode(image_file.read()).decode("utf-8")

    def _get_media_type(self, image_path: str) -> str:
        """获取图像 MIME 类型"""
        ext = Path(image_path).suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif"
        }
        return mime_types.get(ext, "image/jpeg")

    def _get_default_prompt(self) -> str:
        """获取默认提取提示词"""
        return """请将这张文档图片中的内容转换为 Markdown 格式。要求：

1. **文字提取**：准确提取所有可见文字，保持原有段落结构
2. **标题层级**：识别标题层级，使用 #, ##, ### 等标记
3. **表格**：将表格转换为 Markdown 表格格式
4. **列表**：识别有序和无序列表，使用 - 或 1. 标记
5. **代码**：代码块使用 ```语言 格式包裹
6. **公式**：数学公式使用 LaTeX 格式（$ 或 $$）
7. **图表**：对于图表、图片，提供简洁的文字描述，格式为 `![图表描述](placeholder)`
8. **格式保留**：粗体使用 **文字**，斜体使用 *文字*

请直接输出 Markdown 内容，不要添加任何解释说明。"""

    def get_cost_report(self) -> dict:
        """获取成本报告"""
        # Claude 定价（2024年价格）
        input_cost_per_mtok = 3.0  # Sonnet: $3/M tokens
        output_cost_per_mtok = 15.0  # Sonnet: $15/M tokens

        input_cost = (self.total_input_tokens / 1_000_000) * input_cost_per_mtok
        output_cost = (self.total_output_tokens / 1_000_000) * output_cost_per_mtok
        total_cost = input_cost + output_cost

        return {
            "images_processed": self.total_images_processed,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "estimated_cost_usd": round(total_cost, 4),
            "cost_breakdown": {
                "input": round(input_cost, 4),
                "output": round(output_cost, 4)
            }
        }
```

**高级功能：分类提取**

```python
def extract_with_context(
    self,
    image_paths: List[str],
    document_type: str = "generic"
) -> str:
    """
    根据文档类型使用优化的提示词

    Args:
        document_type: "academic", "financial", "technical", "contract", "generic"
    """
    prompts = {
        "academic": """这是一篇学术论文的页面，请提取：
- 标题、作者、摘要
- 正文内容（保留章节结构）
- 图表和公式（使用 LaTeX）
- 参考文献（如果有）""",

        "financial": """这是一份财务文档，请提取：
- 所有数字、金额（保持精确）
- 表格数据（完整转换为 Markdown 表格）
- 日期、账户信息
- 备注说明""",

        "technical": """这是一份技术文档，请提取：
- 代码片段（使用 ``` 代码块）
- 技术参数和配置
- 架构图和流程图（文字描述）
- API 接口说明""",

        "contract": """这是一份合同文档，请提取：
- 合同标题和日期
- 甲乙方信息
- 条款内容（保留编号）
- 重要数字和金额（标注）
- 签字栏信息""",
    }

    prompt = prompts.get(document_type, self._get_default_prompt())
    return self.extract_from_images(image_paths, custom_prompt=prompt)
```

**使用示例：**

```python
import os

# 初始化提取器
extractor = ClaudeVisionExtractor(
    api_key=os.getenv("CLAUDE_API_KEY"),
    model="claude-3-5-sonnet-20241022"
)

# 提取文档
image_paths = ["page_0001.jpg", "page_0002.jpg", "page_0003.jpg"]
markdown = extractor.extract_from_images(image_paths)

# 保存结果
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown)

# 查看成本
cost_report = extractor.get_cost_report()
print(f"处理 {cost_report['images_processed']} 张图像")
print(f"预估成本: ${cost_report['estimated_cost_usd']}")
```

## 测试验证

### 1. 单页提取测试

```python
extractor = ClaudeVisionExtractor(api_key=API_KEY)
markdown = extractor._extract_single_image("test_page.jpg", None, 1)

assert len(markdown) > 0
assert "<!--" in markdown  # 包含页码标注
```

### 2. 多页合并测试

```python
markdown = extractor.extract_from_images(["p1.jpg", "p2.jpg", "p3.jpg"])
assert markdown.count("---") == 2  # 3页应有2个分隔符
assert markdown.count("<!-- Page") == 3
```

### 3. 表格提取测试

准备一张包含表格的图像，验证输出包含 Markdown 表格：
```python
assert "|" in markdown  # Markdown 表格分隔符
assert "---" in markdown  # 表头分隔行
```

### 4. 成本计算测试

```python
extractor.extract_from_images(["test.jpg"])
cost = extractor.get_cost_report()
assert cost["images_processed"] == 1
assert cost["estimated_cost_usd"] > 0
```

## 注意事项

**API 速率限制：**
- 免费层：较低的 RPM
- 实现指数退避重试
- 批量处理时添加延迟

**图像质量要求：**
- 模糊图像会影响准确率
- 建议使用 300 DPI
- 过度压缩会降低识别质量

**成本优化策略：**
1. **缓存机制**：相同文档不重复处理
2. **智能路由**：简单页面用 GLM-4V-Flash（免费）
3. **分辨率优化**：降低到刚好能识别的最低分辨率

**提示词优化：**
- 针对不同文档类型定制提示词
- 明确输出格式要求
- 提供少量示例（few-shot）提升准确率

**错误处理：**
```python
from anthropic import APIError, RateLimitError

try:
    markdown = extractor.extract_from_images(images)
except RateLimitError:
    print("速率限制，等待后重试")
    time.sleep(60)
except APIError as e:
    print(f"API 错误: {e}")
```

## 依赖关系

**前置任务：**
- 任务02：配置 Claude API
- 任务04：安装 Python 依赖
- 任务05：PDF 转图像模块

**后置任务：**
- 任务09：Markdown 生成优化
- 任务11：Markdown 存储索引系统
