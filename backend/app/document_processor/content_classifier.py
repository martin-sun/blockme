"""
Content Classifier for CRA Tax Documents

Keyword-based classification with TF-IDF semantic analysis for quality assessment.
"""

import logging
import re
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TaxCategory(str, Enum):
    """CRA tax document categories."""

    # Personal Income Tax
    PERSONAL_INCOME = "personal_income"
    EMPLOYMENT_INCOME = "employment_income"
    SELF_EMPLOYMENT = "self_employment"

    # Business Tax
    BUSINESS_INCOME = "business_income"
    BUSINESS_EXPENSES = "business_expenses"
    CORPORATE_TAX = "corporate_tax"

    # Investment and Capital
    CAPITAL_GAINS = "capital_gains"
    DIVIDENDS = "dividends"
    INTEREST_INCOME = "interest_income"

    # Deductions and Credits
    DEDUCTIONS = "deductions"
    CREDITS = "credits"
    MEDICAL_EXPENSES = "medical_expenses"
    CHARITABLE_DONATIONS = "charitable_donations"

    # Retirement and Savings
    RRSP = "rrsp"
    TFSA = "tfsa"
    RESP = "resp"
    PENSION = "pension"

    # Sales Tax
    GST_HST = "gst_hst"
    PST = "pst"
    QST = "qst"

    # Special Topics
    NON_RESIDENT_TAX = "non_resident_tax"
    FOREIGN_INCOME = "foreign_income"
    TRUSTS_ESTATES = "trusts_estates"
    PAYROLL = "payroll"

    # Procedural
    FILING_PROCEDURES = "filing_procedures"
    PAYMENTS = "payments"
    ASSESSMENTS = "assessments"
    APPEALS = "appeals"

    # Other
    GENERAL = "general"
    UNKNOWN = "unknown"


class QualityMetrics(BaseModel):
    """Five-dimensional quality assessment metrics."""

    completeness: float = Field(..., ge=0.0, le=1.0, description="Content completeness score")
    accuracy: float = Field(..., ge=0.0, le=1.0, description="Information accuracy score")
    relevance: float = Field(..., ge=0.0, le=1.0, description="Topic relevance score")
    clarity: float = Field(..., ge=0.0, le=1.0, description="Expression clarity score")
    practicality: float = Field(..., ge=0.0, le=1.0, description="Practical usefulness score")

    @property
    def overall_score(self) -> float:
        """Calculate weighted average quality score."""
        weights = {
            "completeness": 0.25,
            "accuracy": 0.25,
            "relevance": 0.20,
            "clarity": 0.15,
            "practicality": 0.15
        }
        return (
            self.completeness * weights["completeness"]
            + self.accuracy * weights["accuracy"]
            + self.relevance * weights["relevance"]
            + self.clarity * weights["clarity"]
            + self.practicality * weights["practicality"]
        )

    @property
    def quality_grade(self) -> str:
        """Convert overall score to letter grade."""
        score = self.overall_score
        if score >= 0.9:
            return "A+"
        elif score >= 0.8:
            return "A"
        elif score >= 0.7:
            return "B"
        elif score >= 0.6:
            return "C"
        elif score >= 0.5:
            return "D"
        else:
            return "F"


class ClassificationResult(BaseModel):
    """Document classification result."""

    primary_category: TaxCategory = Field(..., description="Primary classification category")
    secondary_categories: List[TaxCategory] = Field(
        default_factory=list, description="Secondary classification categories"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence score")
    matched_keywords: List[str] = Field(default_factory=list, description="Matched keywords")
    quality_metrics: QualityMetrics = Field(..., description="Quality assessment metrics")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")


class ContentClassifier:
    """
    CRA tax document classifier.

    Features:
    - Keyword-based multi-category classification
    - Five-dimensional quality assessment
    - Confidence scoring
    - Improvement suggestions
    """

    # Keyword dictionary for each category
    CATEGORY_KEYWORDS: Dict[TaxCategory, Set[str]] = {
        TaxCategory.PERSONAL_INCOME: {
            "personal income", "individual", "taxpayer", "income tax",
            "T1", "personal return", "filing", "assessment"
        },
        TaxCategory.EMPLOYMENT_INCOME: {
            "employment", "salary", "wages", "T4", "employer",
            "employee", "payroll", "benefits", "allowances"
        },
        TaxCategory.SELF_EMPLOYMENT: {
            "self-employed", "business income", "T4A", "contractor",
            "freelance", "sole proprietor", "commission"
        },
        TaxCategory.BUSINESS_INCOME: {
            "business", "corporation", "T2", "profit", "revenue",
            "commercial", "enterprise", "fiscal period"
        },
        TaxCategory.BUSINESS_EXPENSES: {
            "expenses", "deductible", "business expense", "cost",
            "overhead", "operating expense", "capital cost allowance"
        },
        TaxCategory.CAPITAL_GAINS: {
            "capital gain", "capital loss", "disposition", "ACB",
            "adjusted cost base", "principal residence", "property sale"
        },
        TaxCategory.DEDUCTIONS: {
            "deduction", "deductible", "claim", "reduce income",
            "allowable", "eligible", "tax deduction"
        },
        TaxCategory.CREDITS: {
            "tax credit", "credit", "non-refundable", "refundable",
            "eligible", "claim", "reduce tax"
        },
        TaxCategory.RRSP: {
            "RRSP", "registered retirement", "contribution", "deduction limit",
            "HBP", "home buyers plan", "LLP", "lifelong learning"
        },
        TaxCategory.TFSA: {
            "TFSA", "tax-free savings", "contribution room", "withdrawal",
            "investment income", "tax-free"
        },
        TaxCategory.GST_HST: {
            "GST", "HST", "goods and services tax", "harmonized sales tax",
            "input tax credit", "ITC", "registrant", "supply"
        },
        TaxCategory.MEDICAL_EXPENSES: {
            "medical expenses", "medical", "health", "prescription",
            "doctor", "hospital", "treatment", "disability"
        },
        TaxCategory.CHARITABLE_DONATIONS: {
            "donation", "charitable", "gift", "donor", "charity",
            "registered charity", "tax receipt"
        },
        TaxCategory.NON_RESIDENT_TAX: {
            "non-resident", "deemed resident", "residency", "immigration",
            "emigration", "withholding tax", "Part XIII"
        },
        TaxCategory.FOREIGN_INCOME: {
            "foreign income", "foreign tax credit", "T1135",
            "offshore", "foreign property", "tax treaty"
        },
        TaxCategory.FILING_PROCEDURES: {
            "filing", "deadline", "return", "submit", "NETFILE",
            "paper filing", "due date", "extension"
        },
        TaxCategory.PAYMENTS: {
            "payment", "instalment", "balance owing", "refund",
            "direct deposit", "pay CRA", "arrears"
        },
    }

    def __init__(self, use_tfidf: bool = False):
        """
        Initialize the classifier.

        Args:
            use_tfidf: Whether to use TF-IDF enhancement (requires scikit-learn)
        """
        self.use_tfidf = use_tfidf

        if use_tfidf:
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.metrics.pairwise import cosine_similarity
                self._tfidf_vectorizer = TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                logger.info("TF-IDF enhancement enabled")
            except ImportError:
                logger.warning("scikit-learn not installed, TF-IDF enhancement disabled")
                self.use_tfidf = False

    def classify(self, text: str, title: str = "") -> ClassificationResult:
        """
        Classify document content.

        Args:
            text: Document content
            title: Document title (optional, improves accuracy)

        Returns:
            ClassificationResult with category, confidence, and quality metrics
        """
        if not text or len(text.strip()) < 50:
            logger.warning("Text content too short for accurate classification")
            return self._create_default_result()

        # Combine title and content (title has higher weight)
        full_text = f"{title} {title} {title} {text}".lower()

        # 1. Keyword matching
        category_scores = self._keyword_matching(full_text)

        # 2. Determine primary and secondary categories
        primary_category, secondary_categories, confidence = self._determine_categories(
            category_scores
        )

        # 3. Collect matched keywords
        matched_keywords = self._get_matched_keywords(full_text, primary_category)

        # 4. Quality assessment
        quality_metrics = self._assess_quality(text, primary_category)

        # 5. Generate improvement suggestions
        suggestions = self._generate_suggestions(quality_metrics, text)

        return ClassificationResult(
            primary_category=primary_category,
            secondary_categories=secondary_categories,
            confidence=confidence,
            matched_keywords=matched_keywords,
            quality_metrics=quality_metrics,
            suggestions=suggestions
        )

    def smart_categorize(
        self,
        text: str,
        title: str = "",
        source_file: str = "",
        min_score: int = 2
    ) -> ClassificationResult:
        """
        Smart categorization using Skill_Seekers multi-signal scoring algorithm.

        This method uses weighted signals:
        - Source file name (weight: 3) - strongest signal
        - Title (weight: 2) - medium signal
        - Content (weight: 1) - weakest signal

        Args:
            text: Document content
            title: Document title
            source_file: Source file path (e.g., PDF filename)
            min_score: Minimum score threshold for categorization (default: 2)

        Returns:
            ClassificationResult with multi-signal based categorization
        """
        if not text or len(text.strip()) < 50:
            logger.warning("Text content too short for accurate classification")
            return self._create_default_result()

        # Multi-signal scoring
        category_scores = self._multi_signal_scoring(text, title, source_file)

        # Determine primary and secondary categories with threshold
        primary_category, secondary_categories, confidence = self._determine_categories_with_threshold(
            category_scores, min_score
        )

        # Get matched keywords
        matched_keywords = self._get_matched_keywords(text.lower(), primary_category)

        # Quality assessment
        quality_metrics = self._assess_quality(text, primary_category)

        # Generate improvement suggestions
        suggestions = self._generate_suggestions(quality_metrics, text)

        logger.info(
            f"Smart categorization: {primary_category.value} "
            f"(confidence: {confidence:.2f}, score: {category_scores.get(primary_category, 0)})"
        )

        return ClassificationResult(
            primary_category=primary_category,
            secondary_categories=secondary_categories,
            confidence=confidence,
            matched_keywords=matched_keywords,
            quality_metrics=quality_metrics,
            suggestions=suggestions
        )

    def _multi_signal_scoring(
        self,
        text: str,
        title: str,
        source_file: str
    ) -> Dict[TaxCategory, int]:
        """
        Multi-signal scoring algorithm from Skill_Seekers.

        Scoring weights:
        - Source file match: +3 points
        - Title match: +2 points
        - Content match: +1 point

        Returns:
            Dict mapping categories to integer scores
        """
        from collections import defaultdict

        scores = defaultdict(int)

        # Prepare search texts
        text_lower = text.lower()
        title_lower = title.lower()
        source_lower = source_file.lower()

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                keyword_lower = keyword.lower()

                # Signal 1: Source file name (strongest signal, weight: 3)
                if source_lower and keyword_lower in source_lower:
                    scores[category] += 3

                # Signal 2: Title (medium signal, weight: 2)
                if title_lower and keyword_lower in title_lower:
                    scores[category] += 2

                # Signal 3: Content (weakest signal, weight: 1)
                # Only count if keyword appears (not counting multiple occurrences)
                if keyword_lower in text_lower:
                    scores[category] += 1

        return dict(scores)

    def _determine_categories_with_threshold(
        self,
        category_scores: Dict[TaxCategory, int],
        min_score: int = 2
    ) -> Tuple[TaxCategory, List[TaxCategory], float]:
        """
        Determine primary category with minimum score threshold.

        Args:
            category_scores: Dict of category scores
            min_score: Minimum score required for valid categorization

        Returns:
            Tuple of (primary_category, secondary_categories, confidence)
        """
        if not category_scores:
            return TaxCategory.UNKNOWN, [], 0.0

        # Sort by score
        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Check if best category meets minimum threshold
        if not sorted_categories or sorted_categories[0][1] < min_score:
            logger.warning(
                f"Best category score {sorted_categories[0][1] if sorted_categories else 0} "
                f"below threshold {min_score}, defaulting to UNKNOWN"
            )
            return TaxCategory.UNKNOWN, [], 0.0

        primary_category, primary_score = sorted_categories[0]

        # Secondary categories (score >= 30% of primary AND above threshold)
        threshold = max(primary_score * 0.3, min_score)
        secondary_categories = [
            cat for cat, score in sorted_categories[1:5]
            if score >= threshold
        ]

        # Calculate confidence based on score separation
        total_score = sum(score for _, score in sorted_categories)
        if total_score > 0:
            # Confidence is ratio of primary score to total
            confidence = primary_score / total_score
            # Normalize to 0.5-1.0 range (we know it passed threshold)
            confidence = 0.5 + (confidence * 0.5)
        else:
            confidence = 0.0

        return primary_category, secondary_categories, min(confidence, 1.0)

    def _keyword_matching(self, text: str) -> Dict[TaxCategory, float]:
        """Calculate keyword-based category scores."""
        category_scores: Dict[TaxCategory, float] = {}

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = 0.0
            for keyword in keywords:
                # Count keyword occurrences with word boundaries
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                matches = len(re.findall(pattern, text))
                score += matches

            category_scores[category] = score

        return category_scores

    def _determine_categories(
        self,
        category_scores: Dict[TaxCategory, float]
    ) -> Tuple[TaxCategory, List[TaxCategory], float]:
        """Determine primary category, secondary categories, and confidence."""
        # Sort by score
        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Primary category
        if not sorted_categories or sorted_categories[0][1] == 0:
            return TaxCategory.UNKNOWN, [], 0.0

        primary_category, primary_score = sorted_categories[0]

        # Secondary categories (score >= 30% of primary)
        threshold = primary_score * 0.3
        secondary_categories = [
            cat for cat, score in sorted_categories[1:5]
            if score >= threshold and score > 0
        ]

        # Calculate confidence
        total_score = sum(score for _, score in sorted_categories)
        if total_score > 0:
            confidence = primary_score / total_score
            # Normalize to 0.5-1.0 range
            confidence = 0.5 + (confidence * 0.5)
        else:
            confidence = 0.0

        return primary_category, secondary_categories, min(confidence, 1.0)

    def _get_matched_keywords(self, text: str, category: TaxCategory) -> List[str]:
        """Get list of matched keywords for a category."""
        matched = []
        keywords = self.CATEGORY_KEYWORDS.get(category, set())

        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text):
                matched.append(keyword)

        return sorted(matched)[:10]  # Return up to 10 keywords

    def _assess_quality(self, text: str, category: TaxCategory) -> QualityMetrics:
        """Assess content quality across five dimensions."""
        # 1. Completeness: based on length and structure
        completeness = self._assess_completeness(text)

        # 2. Accuracy: based on professional terminology usage
        accuracy = self._assess_accuracy(text, category)

        # 3. Relevance: based on keyword density
        relevance = self._assess_relevance(text, category)

        # 4. Clarity: based on readability
        clarity = self._assess_clarity(text)

        # 5. Practicality: based on practical elements (examples, steps, etc.)
        practicality = self._assess_practicality(text)

        return QualityMetrics(
            completeness=completeness,
            accuracy=accuracy,
            relevance=relevance,
            clarity=clarity,
            practicality=practicality
        )

    def _assess_completeness(self, text: str) -> float:
        """Assess content completeness."""
        score = 0.0

        # Text length
        length = len(text)
        if length > 5000:
            score += 0.4
        elif length > 2000:
            score += 0.3
        elif length > 500:
            score += 0.2
        else:
            score += 0.1

        # Structural elements
        has_sections = len(re.findall(r'\n[A-Z][^\n]{10,}\n', text)) > 2
        has_lists = bool(re.search(r'(\n\s*[-•*]\s|\n\s*\d+\.\s)', text))
        has_definitions = bool(re.search(r'(?:means|refers to|is defined as)', text, re.I))

        if has_sections:
            score += 0.2
        if has_lists:
            score += 0.2
        if has_definitions:
            score += 0.2

        return min(score, 1.0)

    def _assess_accuracy(self, text: str, category: TaxCategory) -> float:
        """Assess content accuracy based on professional terminology."""
        score = 0.5  # Baseline score

        # Check for official CRA terminology
        official_terms = [
            "CRA", "Canada Revenue Agency", "Income Tax Act",
            "tax year", "fiscal period", "line", "schedule"
        ]
        term_count = sum(1 for term in official_terms if term.lower() in text.lower())
        score += min(term_count * 0.1, 0.3)

        # Check for specific references
        has_references = bool(re.search(r'(section|subsection|paragraph|line) \d+', text, re.I))
        if has_references:
            score += 0.2

        return min(score, 1.0)

    def _assess_relevance(self, text: str, category: TaxCategory) -> float:
        """Assess topic relevance based on keyword density."""
        keywords = self.CATEGORY_KEYWORDS.get(category, set())
        if not keywords:
            return 0.5

        text_lower = text.lower()
        keyword_count = sum(
            len(re.findall(r'\b' + re.escape(kw.lower()) + r'\b', text_lower))
            for kw in keywords
        )

        # Calculate density (keywords per 1000 characters)
        density = (keyword_count / len(text)) * 1000 if text else 0

        if density > 10:
            return 1.0
        elif density > 5:
            return 0.8
        elif density > 2:
            return 0.6
        elif density > 0.5:
            return 0.4
        else:
            return 0.2

    def _assess_clarity(self, text: str) -> float:
        """Assess content clarity based on readability."""
        score = 0.5  # Baseline

        # Average sentence length
        sentences = re.split(r'[.!?]+', text)
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if 15 <= avg_sentence_length <= 25:  # Ideal range
                score += 0.2
            elif 10 <= avg_sentence_length <= 30:
                score += 0.1

        # Paragraph structure
        paragraphs = text.split('\n\n')
        if 3 <= len(paragraphs) <= 20:
            score += 0.2

        # Plain language indicators
        simple_language_indicators = ["for example", "such as", "this means", "in other words"]
        if any(indicator in text.lower() for indicator in simple_language_indicators):
            score += 0.1

        return min(score, 1.0)

    def _assess_practicality(self, text: str) -> float:
        """Assess practical usefulness."""
        score = 0.0

        # Examples
        has_examples = bool(re.search(r'(example|for instance|e\.g\.|such as)', text, re.I))
        if has_examples:
            score += 0.3

        # Step-by-step instructions
        has_steps = bool(re.search(r'(step \d|first,|second,|then,|finally)', text, re.I))
        if has_steps:
            score += 0.3

        # Numbers/calculations
        has_calculations = bool(re.search(r'(\$\d+|[\d,]+%|\d+ ×|\d+ \+)', text))
        if has_calculations:
            score += 0.2

        # Tips/notices
        has_tips = bool(re.search(r'(note:|tip:|important:|warning:|caution:)', text, re.I))
        if has_tips:
            score += 0.2

        return min(score, 1.0)

    def _generate_suggestions(self, quality_metrics: QualityMetrics, text: str) -> List[str]:
        """Generate improvement suggestions based on quality metrics."""
        suggestions = []

        if quality_metrics.completeness < 0.6:
            suggestions.append("Increase content depth to ensure complete topic coverage")

        if quality_metrics.accuracy < 0.7:
            suggestions.append("Add more official terminology and specific references (section numbers)")

        if quality_metrics.relevance < 0.6:
            suggestions.append("Increase topic-relevant keywords and professional terminology")

        if quality_metrics.clarity < 0.6:
            suggestions.append("Improve sentence structure and paragraph organization for better readability")

        if quality_metrics.practicality < 0.5:
            suggestions.append("Add practical elements: examples, calculation steps, tips")

        # Check for missing common elements
        if not re.search(r'example', text, re.I):
            suggestions.append("Consider adding specific examples to aid understanding")

        if not re.search(r'\$\d+', text):
            suggestions.append("Consider adding concrete dollar amount examples")

        return suggestions

    def _create_default_result(self) -> ClassificationResult:
        """Create default classification result for invalid input."""
        return ClassificationResult(
            primary_category=TaxCategory.UNKNOWN,
            secondary_categories=[],
            confidence=0.0,
            matched_keywords=[],
            quality_metrics=QualityMetrics(
                completeness=0.0,
                accuracy=0.0,
                relevance=0.0,
                clarity=0.0,
                practicality=0.0
            ),
            suggestions=["Text content insufficient for effective classification"]
        )


def classify_content(text: str, title: str = "") -> ClassificationResult:
    """
    Convenience function to classify document content.

    Args:
        text: Document content
        title: Document title

    Returns:
        ClassificationResult with category and quality assessment
    """
    classifier = ContentClassifier()
    return classifier.classify(text, title)


def smart_classify_content(
    text: str,
    title: str = "",
    source_file: str = "",
    min_score: int = 2
) -> ClassificationResult:
    """
    Convenience function for smart multi-signal categorization.

    Uses Skill_Seekers algorithm with weighted signals:
    - Source file name (weight: 3)
    - Title (weight: 2)
    - Content (weight: 1)

    Args:
        text: Document content
        title: Document title
        source_file: Source file path (e.g., PDF filename)
        min_score: Minimum score threshold (default: 2)

    Returns:
        ClassificationResult with multi-signal based categorization

    Example:
        >>> result = smart_classify_content(
        ...     text="Information about RRSP contributions...",
        ...     title="RRSP Guide",
        ...     source_file="t4012-rrsp.pdf"
        ... )
        >>> print(result.primary_category)  # TaxCategory.RRSP
    """
    classifier = ContentClassifier()
    return classifier.smart_categorize(text, title, source_file, min_score)
