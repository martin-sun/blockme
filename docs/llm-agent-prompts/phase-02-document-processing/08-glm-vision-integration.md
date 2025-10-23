# 任务08：GLM-4V API 集成

## 任务目标

集成智谱 AI GLM-4V 视觉模型，专门处理中文文档的图像识别和 Markdown 转换。利用 GLM-4V 的 99.3% 中文识别准确率和免费 API（GLM-4V-Flash），实现低成本、高质量的中文文档处理。

## 技术要求

**API 配置：**
- 智谱 API Key（任务03已配置）
- 推荐模型：
  - `glm-4v-flash`：免费，中文优秀
  - `glm-4v-plus`：付费，准确率更高

**输入要求：**
- 图像格式：JPEG/PNG/WebP
- 单张大小：< 20MB
- 分辨率：建议 300 DPI

**输出要求：**
- Markdown 格式
- 中文排版优化
- 保留表格和公式

## 实现步骤

### 1. 安装智谱 SDK

```bash
uv add zhipuai
```

### 2. 创建 GLM Vision 封装类

设计 `GLMVisionExtractor` 类：
- 与 ClaudeVisionExtractor 接口一致
- 针对中文文档优化
- 支持 GLM-4V-Flash 免费模型
- 自动降级策略

### 3. 优化中文提示词

设计专门的中文提示词：
- 识别中文排版特点
- 保留中文标点符号
- 处理繁简体混合
- 识别中文表格

### 4. 实现智能模型路由

根据文档特征选择模型：
- 简单中文文档 → GLM-4V-Flash（免费）
- 复杂排版 → GLM-4V-Plus
- 混合语言 → Claude Vision

## 关键代码提示

**GLM Vision 提取器实现：**

```python
from zhipuai import ZhipuAI
import base64
from pathlib import Path
from typing import List, Optional
import time

class GLMVisionExtractor:
    """GLM-4V 文档提取器"""

    def __init__(
        self,
        api_key: str,
        model: str = "glm-4v-flash",
        max_tokens: int = 4096
    ):
        self.client = ZhipuAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

        # 成本追踪（GLM-4V-Flash 免费）
        self.total_images_processed = 0
        self.total_tokens = 0

    def extract_from_images(
        self,
        image_paths: List[str],
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        从图像序列提取 Markdown 内容

        Args:
            image_paths: 图像文件路径列表
            custom_prompt: 自定义提示词

        Returns:
            合并后的 Markdown 文本
        """
        markdown_pages = []

        for idx, image_path in enumerate(image_paths, 1):
            print(f"处理第 {idx}/{len(image_paths)} 页...")

            try:
                markdown = self._extract_single_image(image_path, custom_prompt, page_num=idx)
                markdown_pages.append(markdown)

                # API 速率控制
                if idx < len(image_paths):
                    time.sleep(0.3)

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
        # 编码图像为 base64
        image_data = self._encode_image(image_path)

        # 构建提示词
        prompt = custom_prompt or self._get_default_chinese_prompt()

        # 调用 GLM-4V API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=self.max_tokens,
        )

        # 更新统计
        self.total_images_processed += 1
        self.total_tokens += response.usage.total_tokens

        # 提取响应
        markdown = response.choices[0].message.content

        # 添加页码标注
        markdown = f"<!-- 第 {page_num} 页 -->\n\n{markdown}"

        return markdown

    def _encode_image(self, image_path: str) -> str:
        """图像编码为 base64"""
        with open(image_path, "rb") as image_file:
            return base64.standard_b64encode(image_file.read()).decode("utf-8")

    def _get_default_chinese_prompt(self) -> str:
        """获取中文文档提取提示词"""
        return """请将这张文档图片中的内容转换为 Markdown 格式。要求：

1. **文字提取**：准确识别所有中文文字，保持原有段落结构和标点符号
2. **标题层级**：识别标题，使用 #, ##, ### 等标记
3. **表格**：将表格转换为 Markdown 表格格式，保持对齐
4. **列表**：识别编号列表（一、1.、①等）和无序列表
5. **代码**：代码块使用 ```语言 格式包裹
6. **公式**：数学公式使用 LaTeX 格式（$ 或 $$）
7. **图表**：对图表、图片提供简洁的中文描述，格式为 `![描述](placeholder)`
8. **格式**：粗体 **文字**，斜体 *文字*

特别注意：
- 保留中文标点符号（。，、；：""''等）
- 识别繁简体混合内容
- 保持专业术语的准确性

请直接输出 Markdown 内容，不要添加任何额外说明。"""

    def get_cost_report(self) -> dict:
        """获取成本报告"""
        # GLM-4V-Flash 免费，GLM-4V-Plus 约 ¥0.01/1K tokens
        is_free = "flash" in self.model.lower()

        if is_free:
            cost_cny = 0.0
        else:
            cost_cny = (self.total_tokens / 1000) * 0.01

        return {
            "images_processed": self.total_images_processed,
            "total_tokens": self.total_tokens,
            "model": self.model,
            "is_free": is_free,
            "estimated_cost_cny": round(cost_cny, 4),
            "estimated_cost_usd": round(cost_cny / 7.2, 4)  # 汇率估算
        }
```

**智能模型路由器：**

```python
class DocumentVisionRouter:
    """文档视觉处理路由器"""

    def __init__(self, claude_api_key: str, glm_api_key: str):
        self.claude_extractor = ClaudeVisionExtractor(claude_api_key)
        self.glm_extractor = GLMVisionExtractor(glm_api_key)

    def extract_smart(
        self,
        image_paths: List[str],
        language_hint: str = "auto"
    ) -> dict:
        """
        智能选择模型提取文档

        Args:
            language_hint: "chinese", "english", "auto"

        Returns:
            {
                "markdown": str,
                "model_used": str,
                "cost": dict
            }
        """
        # 语言检测（简单实现）
        if language_hint == "auto":
            language_hint = self._detect_language(image_paths[0])

        # 路由决策
        if language_hint == "chinese":
            # 中文文档优先使用 GLM-4V-Flash（免费）
            print("🚀 使用 GLM-4V-Flash（免费）处理中文文档")
            markdown = self.glm_extractor.extract_from_images(image_paths)
            model_used = "glm-4v-flash"
            cost = self.glm_extractor.get_cost_report()
        else:
            # 英文文档使用 Claude Vision
            print("🚀 使用 Claude Vision 处理英文文档")
            markdown = self.claude_extractor.extract_from_images(image_paths)
            model_used = "claude-3.5-sonnet"
            cost = self.claude_extractor.get_cost_report()

        return {
            "markdown": markdown,
            "model_used": model_used,
            "cost": cost
        }

    def _detect_language(self, image_path: str) -> str:
        """
        简单语言检测（基于快速采样）

        实际项目中可以：
        1. 使用 tesseract OCR 快速识别部分文字
        2. 统计中文字符比例
        3. 使用语言检测库
        """
        # 这里简化实现，实际应该做文字检测
        # 可以使用免费的 GLM 快速识别第一页判断语言
        try:
            # 用 GLM-4V-Flash 快速识别
            response = self.glm_extractor.client.chat.completions.create(
                model="glm-4v-flash",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "这张图片的主要语言是中文还是英文？只回答'中文'或'英文'"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{self.glm_extractor._encode_image(image_path)}"}}
                        ]
                    }
                ],
                max_tokens=10
            )

            answer = response.choices[0].message.content
            return "chinese" if "中文" in answer else "english"

        except:
            # 默认中文（根据实际情况调整）
            return "chinese"

    def extract_with_fallback(
        self,
        image_paths: List[str],
        primary_model: str = "glm"
    ) -> str:
        """
        带降级策略的提取

        主模型失败时自动切换备用模型
        """
        try:
            if primary_model == "glm":
                print("使用 GLM-4V 提取...")
                return self.glm_extractor.extract_from_images(image_paths)
            else:
                print("使用 Claude Vision 提取...")
                return self.claude_extractor.extract_from_images(image_paths)

        except Exception as e:
            print(f"⚠️  主模型失败: {e}")
            print("切换到备用模型...")

            # 切换备用模型
            if primary_model == "glm":
                return self.claude_extractor.extract_from_images(image_paths)
            else:
                return self.glm_extractor.extract_from_images(image_paths)
```

**使用示例：**

```python
import os

# 单一模型使用
glm_extractor = GLMVisionExtractor(
    api_key=os.getenv("GLM_API_KEY"),
    model="glm-4v-flash"  # 免费模型
)

markdown = glm_extractor.extract_from_images(["page1.jpg", "page2.jpg"])
cost = glm_extractor.get_cost_report()
print(f"完全免费！处理了 {cost['images_processed']} 张图像")

# 智能路由使用
router = DocumentVisionRouter(
    claude_api_key=os.getenv("CLAUDE_API_KEY"),
    glm_api_key=os.getenv("GLM_API_KEY")
)

result = router.extract_smart(image_paths, language_hint="chinese")
print(f"使用模型: {result['model_used']}")
print(f"成本: {result['cost']}")
```

## 测试验证

### 1. 中文识别准确率测试

```python
# 准备包含复杂中文排版的测试图像
test_image = "chinese_contract.jpg"
markdown = glm_extractor._extract_single_image(test_image, None, 1)

# 验证中文标点
assert "。" in markdown or "，" in markdown
# 验证内容完整性
assert len(markdown) > 100
```

### 2. 繁简体混合测试

```python
# 测试繁体字识别
markdown = glm_extractor.extract_from_images(["traditional_chinese.jpg"])
assert "繁體" in markdown or len(markdown) > 0
```

### 3. 智能路由测试

```python
router = DocumentVisionRouter(CLAUDE_KEY, GLM_KEY)

# 中文文档应使用 GLM
result = router.extract_smart(["chinese_doc.jpg"], "chinese")
assert result["model_used"] == "glm-4v-flash"
assert result["cost"]["is_free"] == True

# 英文文档应使用 Claude
result = router.extract_smart(["english_doc.jpg"], "english")
assert "claude" in result["model_used"]
```

### 4. 成本对比测试

```python
# 同一文档分别用两个模型处理
glm_cost = glm_extractor.get_cost_report()
claude_cost = claude_extractor.get_cost_report()

print(f"GLM 成本: ¥{glm_cost['estimated_cost_cny']}")
print(f"Claude 成本: ${claude_cost['estimated_cost_usd']}")
```

## 注意事项

**免费额度优化：**
- GLM-4V-Flash 完全免费，优先使用
- 大量文档建议全部用 GLM-4V-Flash
- 只有识别失败时才切换付费模型

**中文特性优化：**
- 保留中文标点符号
- 识别中文编号（一、二、三 / 甲、乙、丙）
- 处理中文表格对齐问题

**API 速率限制：**
- 免费用户 QPM（每分钟查询数）较低
- 实现队列处理，避免超限
- 重试机制使用指数退避

**质量对比：**
| 文档类型 | GLM-4V-Flash | Claude Vision |
|---------|-------------|---------------|
| 中文合同 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 英文论文 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 中文表格 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 复杂公式 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 成本 | 免费 | 付费 |

## 依赖关系

**前置任务：**
- 任务03：配置 GLM API
- 任务04：安装 Python 依赖
- 任务05：PDF 转图像模块

**后置任务：**
- 任务09：Markdown 生成优化
- 任务13：意图识别模块（智能路由）
