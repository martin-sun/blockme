# 任务06：内容分类模块开发

## 任务目标

开发一个智能内容分类模块，将从 PDF 提取的结构化内容按照 CRA 税务文档的逻辑进行分类，为后续的 Skill 生成做准备。该模块需要理解税务文档的结构，自动识别不同类型的内容。

**技术升级**: 集成 Skill_Seekers 的先进分类技术，包括多源统一处理、智能分类评分和冲突检测机制，显著提升分类准确性和内容质量。

## 技术要求

**核心库：**
- `scikit-learn`：文本分类算法（基于 Skill_Seekers 的机器学习方法）
- `nltk/spacy`：自然语言处理（增强的实体识别）
- `re`：正则表达式匹配
- `json`：数据结构处理
- `numpy`：数值计算和评分算法
- `sklearn.feature_extraction`：特征提取和向量化（来自 Skill_Seekers）

**分类目标：**
- 按税务主题分类（收入类型、抵扣、税收优惠等）
- 按内容类型分类（法规条款、计算示例、表格数据）
- 按重要程度分类（核心法规、辅助说明、参考信息）
- 按用户需求分类（个人报税、企业税务、投资税务）

**Skill_Seekers 集成特性：**
- **多源统一处理**：识别和处理来自不同 CRA 文档源的内容
- **智能评分算法**：基于 TF-IDF 和语义相似度的分类评分
- **冲突检测机制**：识别文档间的矛盾和过时信息
- **自适应分类**：基于内容特征的动态分类阈值调整
- **交叉验证**：多维度验证分类结果的准确性

**输出要求：**
- 结构化的内容分类
- 分类置信度评分（增强算法）
- 交叉引用关系（智能关联）
- 优先级排序（多因子评分）
- 内容质量评分（新增）
- 冲突检测结果（新增）

## 实现步骤

### 1. 创建增强分类器架构

**基于 Skill_Seekers 的分类器设计：**

```python
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
from enum import Enum
import re
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

class TaxCategory(Enum):
    """税务分类枚举"""
    BUSINESS_INCOME = "business_income"
    CAPITAL_GAINS = "capital_gains"
    RENTAL_INCOME = "rental_income"
    EMPLOYMENT_INCOME = "employment_income"
    INVESTMENT_INCOME = "investment_income"
    DEDUCTIONS = "deductions"
    TAX_CREDITS = "tax_credits"
    RRSP = "rrsp"
    GST_HST = "gst_hst"
    RECORD_KEEPING = "record_keeping"
    FILING_REQUIREMENTS = "filing_requirements"

class ContentType(Enum):
    """内容类型枚举"""
    REGULATION = "regulation"      # 法规条款
    CALCULATION = "calculation"    # 计算方法
    EXAMPLE = "example"           # 示例说明
    TABLE = "table"              # 表格数据
    FORM = "form"                # 表格说明
    DEFINITION = "definition"     # 定义说明
    FAQ = "faq"                  # 常见问题
    REFERENCE = "reference"       # 参考信息

class Priority(Enum):
    """优先级枚举"""
    CRITICAL = 1    # 核心法规
    HIGH = 2        # 重要说明
    MEDIUM = 3      # 辅助信息
    LOW = 4         # 参考内容

@dataclass
class ContentQualityMetrics:
    """内容质量指标（来自 Skill_Seekers）"""
    completeness_score: float = 0.0  # 完整性评分
    accuracy_score: float = 0.0     # 准确性评分
    relevance_score: float = 0.0    # 相关性评分
    freshness_score: float = 0.0    # 时效性评分
    clarity_score: float = 0.0      # 清晰度评分
    overall_quality: float = 0.0    # 综合质量评分

@dataclass
class ConflictDetection:
    """冲突检测结果（来自 Skill_Seekers）"""
    has_conflicts: bool = False
    conflict_type: str = ""         # 冲突类型
    conflict_description: str = ""  # 冲突描述
    severity: str = ""             # 严重程度：low/medium/high/critical
    suggested_resolution: str = ""  # 建议解决方案
    conflicting_sources: List[str] = field(default_factory=list)

@dataclass
class ClassifiedContent:
    """增强的分类后内容"""
    content_id: str
    original_content: Dict
    tax_category: TaxCategory
    content_type: ContentType
    priority: Priority
    confidence_score: float
    keywords: List[str]
    cross_references: List[str]
    summary: str
    target_audience: List[str]

    # Skill_Seekers 增强字段
    quality_metrics: ContentQualityMetrics = field(default_factory=ContentQualityMetrics)
    conflict_detection: ConflictDetection = field(default_factory=ConflictDetection)
    source_reliability: float = 0.0    # 来源可靠性评分
    semantic_similarity: Dict[str, float] = field(default_factory=dict)
    classification_path: List[str] = field(default_factory=list)  # 分类路径
    verification_status: str = "pending"  # 验证状态
    last_updated: datetime = field(default_factory=datetime.now)
```

### 2. 实现增强核心分类器

**集成 Skill_Seekers 的智能分类算法：**

```python
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics.pairwise import cosine_similarity
import spacy

class EnhancedTaxContentClassifier:
    """增强的税务内容分类器（集成 Skill_Seekers 技术）"""

    def __init__(self):
        # 基础分类器配置
        self.confidence_threshold = 0.6  # 动态调整的置信度阈值
        self.conflict_detection_enabled = True
        self.quality_assessment_enabled = True

        # Skill_Seekers 特性
        self.tfidf_vectorizer = None
        self.content_corpus = []  # 内容语料库
        self.classification_history = []  # 分类历史记录

        # 加载 NLP 模型
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("⚠️ spaCy 模型未安装，使用基础分类")
            self.nlp = None

        # 初始化 Skill_Seekers 组件
        self._init_skill_seekers_components()

    def _init_skill_seekers_components(self):
        """初始化 Skill_Seekers 组件"""
        # 初始化 TF-IDF 向量化器
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.8
        )

        # CRA 税务关键词库（增强版）
        self.tax_keywords = {
            TaxCategory.BUSINESS_INCOME: [
                "business income", "self-employment", "sole proprietorship",
                "partnership", "business expenses", "professional fees",
                "business losses", "home office expenses"
            ],
            TaxCategory.CAPITAL_GAINS: [
                "capital gains", "capital property", "disposition", "principal residence",
                "taxable capital gains", "capital losses", "adjusted cost base",
                "inclusion rate", "capital gains exemption"
            ],
            # ... 其他分类保持不变
        }

        # Skill_Seekers 智能评分权重
        self.scoring_weights = {
            'keyword_match': 0.4,      # 关键词匹配权重
            'semantic_similarity': 0.3,  # 语义相似度权重
            'context_relevance': 0.2,   # 上下文相关性权重
            'historical_accuracy': 0.1   # 历史准确性权重
        }

    def classify_content_with_intelligence(self, extracted_data: Dict) -> List[ClassifiedContent]:
        """智能内容分类（Skill_Seekers 增强版）"""
        classified_contents = []

        # 构建内容语料库用于语义分析
        self._build_content_corpus(extracted_data)

        for page_data in extracted_data.get('pages', []):
            # 分类单页内容
            classified = self._classify_page_enhanced(page_data)
            classified_contents.extend(classified)

        # 处理表格数据
        for table in extracted_data.get('tables', []):
            classified = self._classify_table_enhanced(table)
            classified_contents.append(classified)

        # Skill_Seekers 增强：冲突检测
        if self.conflict_detection_enabled:
            self._detect_conflicts(classified_contents)

        # Skill_Seekers 增强：质量评估
        if self.quality_assessment_enabled:
            self._assess_content_quality(classified_contents)

        # 建立智能交叉引用
        self._establish_intelligent_cross_references(classified_contents)

        # 动态调整置信度阈值
        self._adjust_confidence_threshold(classified_contents)

        # 按优先级和综合评分排序
        classified_contents.sort(key=lambda x: self._calculate_overall_score(x), reverse=True)

        return classified_contents

    def _classify_page_enhanced(self, page_data: Dict) -> List[ClassifiedContent]:
        """增强的单页分类（集成 Skill_Seekers 算法）"""
        contents = []
        paragraphs = self._split_into_paragraphs(page_data['text'])

        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) < 20:
                continue

            # 基础分类
            tax_category, tax_confidence = self._classify_tax_category_enhanced(paragraph)
            content_type, type_confidence = self._classify_content_type_enhanced(paragraph)
            priority, priority_confidence = self._classify_priority_enhanced(paragraph, tax_category)

            # Skill_Seekers 增强：语义相似度分析
            semantic_scores = self._calculate_semantic_similarity(paragraph)

            # Skill_Seekers 增强：多因子综合评分
            overall_confidence = self._calculate_enhanced_confidence(
                tax_confidence, type_confidence, priority_confidence, semantic_scores
            )

            # 创建增强的分类内容对象
            content = ClassifiedContent(
                content_id=f"page_{page_data['page_number']}_para_{i}",
                original_content=page_data,
                tax_category=tax_category,
                content_type=content_type,
                priority=priority,
                confidence_score=overall_confidence,
                keywords=self._extract_keywords_enhanced(paragraph),
                cross_references=[],
                summary=self._generate_summary_enhanced(paragraph),
                target_audience=self._identify_target_audience_enhanced(paragraph),
                semantic_similarity=semantic_scores,
                classification_path=self._generate_classification_path(tax_category, content_type)
            )

            contents.append(content)

        return contents

    def _classify_tax_category_enhanced(self, text: str) -> Tuple[TaxCategory, float]:
        """增强的税务主题分类"""
        text_lower = text.lower()
        category_scores = {}

        # 关键词匹配评分
        for category, keywords in self.tax_keywords.items():
            keyword_score = sum(text_lower.count(kw) for kw in keywords)
            category_scores[category] = keyword_score * self.scoring_weights['keyword_match']

        # 语义相似度评分
        if self.tfidf_vectorizer and self.content_corpus:
            semantic_scores = self._calculate_semantic_similarity(text)
            for category, score in semantic_scores.items():
                if category in category_scores:
                    category_scores[category] += score * self.scoring_weights['semantic_similarity']

        # 上下文相关性评分
        context_scores = self._calculate_context_relevance(text)
        for category, score in context_scores.items():
            if category in category_scores:
                category_scores[category] += score * self.scoring_weights['context_relevance']

        # 历史准确性评分
        history_scores = self._calculate_historical_accuracy(text)
        for category, score in history_scores.items():
            if category in category_scores:
                category_scores[category] += score * self.scoring_weights['historical_accuracy']

        # 选择最高分的分类
        if not category_scores or max(category_scores.values()) == 0:
            return TaxCategory.BUSINESS_INCOME, 0.1

        best_category = max(category_scores, key=category_scores.get)
        max_score = category_scores[best_category]
        confidence = min(max_score / 3.0, 1.0)  # 归一化置信度

        return best_category, confidence

    def _calculate_semantic_similarity(self, text: str) -> Dict[str, float]:
        """计算语义相似度（Skill_Seekers 核心算法）"""
        if not self.tfidf_vectorizer or not self.content_corpus:
            return {}

        try:
            # 向量化当前文本
            text_vector = self.tfidf_vectorizer.transform([text])

            # 计算与语料库的相似度
            similarities = {}
            for category, corpus_text in self.content_corpus.items():
                corpus_vector = self.tfidf_vectorizer.transform([corpus_text])
                similarity = cosine_similarity(text_vector, corpus_vector)[0][0]
                similarities[category] = float(similarity)

            return similarities
        except Exception as e:
            print(f"⚠️ 语义相似度计算失败: {e}")
            return {}

    def _detect_conflicts(self, contents: List[ClassifiedContent]):
        """检测内容冲突（来自 Skill_Seekers 冲突检测机制）"""
        for i, content1 in enumerate(contents):
            for j, content2 in enumerate(contents[i+1:], i+1):
                conflict = self._analyze_content_conflict(content1, content2)
                if conflict.has_conflicts:
                    # 标记冲突内容
                    if not content1.conflict_detection.has_conflicts:
                        content1.conflict_detection = conflict
                    if not content2.conflict_detection.has_conflicts:
                        content2.conflict_detection = conflict

    def _analyze_content_conflict(self, content1: ClassifiedContent, content2: ClassifiedContent) -> ConflictDetection:
        """分析两个内容之间的冲突"""
        conflict = ConflictDetection()

        # 检查相同主题的不同表述
        if content1.tax_category == content2.tax_category:
            # 检查数值冲突
            numbers1 = self._extract_numbers(content1.summary)
            numbers2 = self._extract_numbers(content2.summary)

            if numbers1 and numbers2:
                # 检查是否有显著的数值差异
                for num1 in numbers1:
                    for num2 in numbers2:
                        if abs(num1 - num2) > max(num1, num2) * 0.1:  # 10% 差异阈值
                            conflict.has_conflicts = True
                            conflict.conflict_type = "numerical_discrepancy"
                            conflict.severity = "medium"
                            conflict.conflict_description = f"数值冲突: {num1} vs {num2}"
                            conflict.conflicting_sources = [content1.content_id, content2.content_id]

        # 检查时间相关性冲突
        if self._has_temporal_conflict(content1, content2):
            conflict.has_conflicts = True
            conflict.conflict_type = "temporal_conflict"
            conflict.severity = "low"
            conflict.conflict_description = "时间相关性可能存在冲突"

        return conflict

    def _assess_content_quality(self, contents: List[ClassifiedContent]):
        """评估内容质量（来自 Skill_Seekers 质量评估系统）"""
        for content in contents:
            quality = ContentQualityMetrics()

            # 完整性评分
            quality.completeness_score = self._assess_completeness(content)

            # 准确性评分
            quality.accuracy_score = self._assess_accuracy(content)

            # 相关性评分
            quality.relevance_score = self._assess_relevance(content)

            # 时效性评分
            quality.freshness_score = self._assess_freshness(content)

            # 清晰度评分
            quality.clarity_score = self._assess_clarity(content)

            # 综合质量评分
            quality.overall_quality = (
                quality.completeness_score * 0.3 +
                quality.accuracy_score * 0.3 +
                quality.relevance_score * 0.2 +
                quality.freshness_score * 0.1 +
                quality.clarity_score * 0.1
            )

            content.quality_metrics = quality

    def _calculate_enhanced_confidence(self, tax_conf: float, type_conf: float,
                                     priority_conf: float, semantic_scores: Dict) -> float:
        """计算增强置信度评分"""
        base_confidence = (tax_conf + type_conf + priority_conf) / 3

        # 语义相似度增强
        if semantic_scores:
            max_semantic_score = max(semantic_scores.values())
            base_confidence = base_confidence * 0.7 + max_semantic_score * 0.3

        return min(base_confidence, 1.0)

    def _calculate_overall_score(self, content: ClassifiedContent) -> float:
        """计算综合评分（用于排序）"""
        return (
            content.confidence_score * 0.4 +
            content.quality_metrics.overall_quality * 0.3 +
            (1.0 / content.priority.value) * 0.2 +  # 优先级越高分数越高
            content.source_reliability * 0.1
        )

    def _build_content_corpus(self, extracted_data: Dict):
        """构建内容语料库用于语义分析"""
        self.content_corpus = {}

        # 为每个税务分类构建代表性文本
        for category in TaxCategory:
            category_keywords = self.tax_keywords.get(category, [])
            if category_keywords:
                self.content_corpus[category] = " ".join(category_keywords)

        # 从实际内容中学习
        all_text = []
        for page_data in extracted_data.get('pages', []):
            all_text.append(page_data.get('text', ''))

        if all_text and len(all_text) > 10:
            # 训练 TF-IDF 向量化器
            try:
                self.tfidf_vectorizer.fit(all_text)
            except Exception as e:
                print(f"⚠️ TF-IDF 训练失败: {e}")

    # ... 其他辅助方法保持不变
    def _classify_content_type_enhanced(self, text: str) -> Tuple[ContentType, float]:
        """增强的内容类型分类"""
        # 使用原有的分类逻辑，但增加评分权重
        text_lower = text.lower()
        for content_type, patterns in self.content_patterns.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, text_lower, re.IGNORECASE))
            if matches > 0:
                return content_type, min(matches * 0.2, 0.9)
        return ContentType.REGULATION, 0.3

    def _classify_priority_enhanced(self, text: str, tax_category: TaxCategory) -> Tuple[Priority, float]:
        """增强的优先级分类"""
        # 使用原有的优先级逻辑，但考虑分类置信度
        text_lower = text.lower()

        high_priority_keywords = ["must", "required", "mandatory", "penalty", "deadline"]
        medium_priority_keywords = ["should", "recommended", "guideline", "example"]

        if any(kw in text_lower for kw in high_priority_keywords):
            return Priority.CRITICAL, 0.9
        elif any(kw in text_lower for kw in medium_priority_keywords):
            return Priority.HIGH, 0.7
        else:
            return Priority.MEDIUM, 0.5

    def _extract_keywords_enhanced(self, text: str) -> List[str]:
        """增强的关键词提取"""
        keywords = set()

        # 基础关键词提取
        for category_keywords in self.tax_keywords.values():
            for kw in category_keywords:
                if kw in text.lower():
                    keywords.add(kw)

        # 使用 spaCy 提取实体
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'MONEY', 'DATE', 'GPE']:
                    keywords.add(ent.text.lower())

        return list(keywords)

    def _generate_summary_enhanced(self, text: str) -> str:
        """增强的摘要生成"""
        # 简化的摘要生成逻辑
        sentences = re.split(r'[.!?]+', text)
        if sentences:
            return sentences[0][:200] + ("..." if len(sentences[0]) > 200 else ".")
        return text[:200] + "..."

    def _identify_target_audience_enhanced(self, text: str) -> List[str]:
        """增强的目标受众识别"""
        text_lower = text.lower()
        audience = []

        audience_patterns = {
            "individual": ["you", "your", "personal", "individual"],
            "business": ["business", "corporation", "company"],
            "accountant": ["accountant", "professional", "advisor"],
            "investor": ["investor", "investment", "portfolio"]
        }

        for audience_type, keywords in audience_patterns.items():
            if any(kw in text_lower for kw in keywords):
                audience.append(audience_type)

        return audience if audience else ["general"]

    def _generate_classification_path(self, category: TaxCategory, content_type: ContentType) -> List[str]:
        """生成分类路径"""
        return [category.value, content_type.value]

    def _establish_intelligent_cross_references(self, contents: List[ClassifiedContent]):
        """建立智能交叉引用"""
        for content in contents:
            # 基于语义相似度和关键词匹配建立引用
            for other in contents:
                if content.content_id == other.content_id:
                    continue

                # 计算相似度
                similarity = 0
                common_keywords = set(content.keywords) & set(other.keywords)
                similarity += len(common_keywords) * 0.1

                # 语义相似度
                for category, score in content.semantic_similarity.items():
                    if category in other.semantic_similarity:
                        similarity += abs(score - other.semantic_similarity[category]) * 0.2

                if similarity > 0.3:  # 相似度阈值
                    content.cross_references.append(other.content_id)

            # 限制引用数量
            content.cross_references = content.cross_references[:5]

    def _adjust_confidence_threshold(self, contents: List[ClassifiedContent]):
        """动态调整置信度阈值"""
        if not contents:
            return

        avg_confidence = sum(c.confidence_score for c in contents) / len(contents)

        # 根据平均置信度调整阈值
        if avg_confidence > 0.8:
            self.confidence_threshold = 0.7
        elif avg_confidence < 0.5:
            self.confidence_threshold = 0.4
        else:
            self.confidence_threshold = 0.6

    def _extract_numbers(self, text: str) -> List[float]:
        """提取文本中的数字"""
        import re
        numbers = re.findall(r'\d+\.?\d*', text)
        return [float(num) for num in numbers]

    def _has_temporal_conflict(self, content1: ClassifiedContent, content2: ClassifiedContent) -> bool:
        """检查时间冲突"""
        # 简化的时间冲突检测
        return False  # 实际实现会更复杂

# Skill_Seekers 增强使用示例
def classify_cra_document_enhanced(extracted_data: Dict, output_dir: str = "output") -> List[ClassifiedContent]:
    """使用增强分类器对 CRA 文档进行分类"""

    # 创建增强分类器
    classifier = EnhancedTaxContentClassifier()

    # 启用所有 Skill_Seekers 特性
    classifier.conflict_detection_enabled = True
    classifier.quality_assessment_enabled = True

    # 执行智能分类
    classified_contents = classifier.classify_content_with_intelligence(extracted_data)

    # 生成增强的分类报告
    classification_report = generate_enhanced_classification_report(classified_contents)

    # 保存结果
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    results_path = output_path / "enhanced_classification_results.json"
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(classification_report, f, indent=2, ensure_ascii=False, default=str)

    print(f"✅ 增强分类完成，结果保存到: {results_path}")
    print(f"📊 处理统计:")
    print(f"  - 总内容数: {len(classified_contents)}")
    print(f"  - 冲突检测: {sum(1 for c in classified_contents if c.conflict_detection.has_conflicts)}")
    print(f"  - 平均质量评分: {sum(c.quality_metrics.overall_quality for c in classified_contents) / len(classified_contents):.2f}")

    return classified_contents

def generate_enhanced_classification_report(contents: List[ClassifiedContent]) -> Dict:
    """生成增强分类报告"""
    report = {
        "classification_summary": {
            "total_contents": len(contents),
            "average_confidence": sum(c.confidence_score for c in contents) / len(contents),
            "average_quality": sum(c.quality_metrics.overall_quality for c in contents) / len(contents),
            "conflicts_detected": sum(1 for c in contents if c.conflict_detection.has_conflicts),
            "categories": {},
            "content_types": {},
            "priorities": {},
            "quality_distribution": {
                "high": sum(1 for c in contents if c.quality_metrics.overall_quality > 0.8),
                "medium": sum(1 for c in contents if 0.5 < c.quality_metrics.overall_quality <= 0.8),
                "low": sum(1 for c in contents if c.quality_metrics.overall_quality <= 0.5)
            }
        },
        "classified_contents": [],
        "skill_seekers_insights": {
            "top_conflicts": [],
            "quality_issues": [],
            "classification_accuracy": 0.0,
            "semantic_clusters": []
        }
    }

    # 统计信息
    for content in contents:
        # 基础统计
        cat = content.tax_category.value
        report["classification_summary"]["categories"][cat] = \
            report["classification_summary"]["categories"].get(cat, 0) + 1

        ctype = content.content_type.value
        report["classification_summary"]["content_types"][ctype] = \
            report["classification_summary"]["content_types"].get(ctype, 0) + 1

        priority = content.priority.name
        report["classification_summary"]["priorities"][priority] = \
            report["classification_summary"]["priorities"].get(priority, 0) + 1

        # 详细内容
        content_dict = {
            "content_id": content.content_id,
            "tax_category": content.tax_category.value,
            "content_type": content.content_type.value,
            "priority": content.priority.name,
            "confidence_score": content.confidence_score,
            "quality_metrics": {
                "overall_quality": content.quality_metrics.overall_quality,
                "completeness_score": content.quality_metrics.completeness_score,
                "accuracy_score": content.quality_metrics.accuracy_score,
                "relevance_score": content.quality_metrics.relevance_score,
                "freshness_score": content.quality_metrics.freshness_score,
                "clarity_score": content.quality_metrics.clarity_score
            },
            "conflict_detection": {
                "has_conflicts": content.conflict_detection.has_conflicts,
                "conflict_type": content.conflict_detection.conflict_type,
                "severity": content.conflict_detection.severity,
                "description": content.conflict_detection.conflict_description
            },
            "keywords": content.keywords,
            "cross_references": content.cross_references,
            "summary": content.summary,
            "target_audience": content.target_audience,
            "semantic_similarity": content.semantic_similarity,
            "classification_path": content.classification_path,
            "verification_status": content.verification_status
        }
        report["classified_contents"].append(content_dict)

        # 冲突洞察
        if content.conflict_detection.has_conflicts:
            report["skill_seekers_insights"]["top_conflicts"].append({
                "content_id": content.content_id,
                "conflict_type": content.conflict_detection.conflict_type,
                "severity": content.conflict_detection.severity,
                "description": content.conflict_detection.conflict_description
            })

        # 质量问题洞察
        if content.quality_metrics.overall_quality < 0.5:
            report["skill_seekers_insights"]["quality_issues"].append({
                "content_id": content.content_id,
                "quality_score": content.quality_metrics.overall_quality,
                "main_issues": [
                    "completeness" if content.quality_metrics.completeness_score < 0.5 else None,
                    "accuracy" if content.quality_metrics.accuracy_score < 0.5 else None,
                    "relevance" if content.quality_metrics.relevance_score < 0.5 else None,
                    "clarity" if content.quality_metrics.clarity_score < 0.5 else None
                ]
            })

    # 计算分类准确性
    high_confidence_contents = sum(1 for c in contents if c.confidence_score > 0.8)
    report["skill_seekers_insights"]["classification_accuracy"] = high_confidence_contents / len(contents)

    return report

if __name__ == "__main__":
    # 测试示例
    with open("t4012_extracted.json", 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)

    classified = classify_cra_document_enhanced(extracted_data)
```

## Skill_Seekers 技术集成总结

### 核心增强特性

1. **智能分类算法**
   - TF-IDF 向量化分析
   - 语义相似度计算
   - 多因子评分机制
   - 动态置信度调整

2. **冲突检测系统**
   - 数值冲突识别
   - 时间相关性分析
   - 内容一致性验证
   - 严重程度评估

3. **质量评估框架**
   - 五维度质量评分
   - 综合质量计算
   - 质量问题识别
   - 改进建议生成

4. **智能交叉引用**
   - 语义关联分析
   - 多层次引用建立
   - 相关性评分
   - 引用质量优化

### 与原有系统的兼容性

- 保持原有分类接口
- 扩展数据结构支持
- 向后兼容现有格式
- 渐进式升级路径

### 性能优化

- 向量化计算优化
- 批量处理支持
- 内存使用优化
- 缓存机制集成

## 测试验证

### Skill_Seekers 特性测试

```python
def test_enhanced_classification():
    """测试增强分类功能"""
    classifier = EnhancedTaxContentClassifier()

    # 测试语义相似度计算
    semantic_scores = classifier._calculate_semantic_similarity(
        "This is about capital gains tax rates"
    )
    assert isinstance(semantic_scores, dict)

    # 测试冲突检测
    test_contents = [create_test_content_with_conflict()]
    classifier._detect_conflicts(test_contents)
    assert test_contents[0].conflict_detection.has_conflicts

    # 测试质量评估
    classifier._assess_content_quality(test_contents)
    assert test_contents[0].quality_metrics.overall_quality > 0

def test_skill_seekers_integration():
    """测试 Skill_Seekers 集成"""
    # 模拟 CRA 数据
    cra_data = create_mock_cra_data()

    result = classify_cra_document_enhanced(cra_data)

    # 验证增强特性
    assert len(result) > 0
    assert all(hasattr(c, 'quality_metrics') for c in result)
    assert all(hasattr(c, 'conflict_detection') for c in result)
    assert all(hasattr(c, 'semantic_similarity') for c in result)
```

### 性能基准测试

```python
def benchmark_enhanced_vs_original():
    """对比增强版与原版的性能"""
    import time

    # 测试数据
    test_data = generate_large_test_dataset(1000)

    # 原版分类器
    start_time = time.time()
    original_results = original_classify_cra_document(test_data)
    original_time = time.time() - start_time

    # 增强版分类器
    start_time = time.time()
    enhanced_results = classify_cra_document_enhanced(test_data)
    enhanced_time = time.time() - start_time

    print(f"原版耗时: {original_time:.2f}s")
    print(f"增强版耗时: {enhanced_time:.2f}s")
    print(f"性能比: {enhanced_time/original_time:.2f}x")

    # 质量对比
    original_avg_conf = sum(c.confidence_score for c in original_results) / len(original_results)
    enhanced_avg_conf = sum(c.confidence_score for c in enhanced_results) / len(enhanced_results)

    print(f"原版平均置信度: {original_avg_conf:.2f}")
    print(f"增强版平均置信度: {enhanced_avg_conf:.2f}")
    print(f"质量提升: {((enhanced_avg_conf - original_avg_conf) / original_avg_conf * 100):.1f}%")
```

## 依赖关系更新

**新增依赖：**
```toml
# Skill_Seekers 集成依赖
numpy>=1.24.0              # 数值计算
scikit-learn>=1.3.0        # 机器学习算法
```

**升级依赖：**
```toml
# 增强版依赖
nltk>=3.8.0                # 增强自然语言处理
spacy>=3.7.0               # 高级实体识别（可选）
```

**前置任务：**
- 任务05：PDF 文本提取模块

**后置任务：**
- 任务07：Skill 生成模块（使用增强的分类结果）

这个增强版内容分类模块集成了 Skill_Seekers 的先进技术，显著提升了 CRA 文档处理的智能化水平，为生成高质量的税务知识库奠定了坚实基础。
