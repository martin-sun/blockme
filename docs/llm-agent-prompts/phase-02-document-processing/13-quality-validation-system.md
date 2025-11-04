# 质量控制和验证系统框架

## 概述

质量控制和验证系统是确保 BlockMe CRA 税务文档处理系统输出高质量内容的关键组件。本系统集成了 Skill_Seekers 的先进质量控制理念，提供多层次、全方位的质量保证机制。

## 系统架构

### 核心组件

```
质量控制系统架构：
┌─────────────────────────────────────────────────────────────┐
│                    质量控制中心                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │ 质量评估器  │ │ 验证引擎    │ │ 改进引擎    │ │ 监控器  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │ 规则检查器  │ │ 数据验证器  │ │ 格式验证器  │ │ 报告器  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │ 冲突检测器  │ │ 一致性检查  │ │ 时效性检查  │ │ 告警器  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 数据流架构

```
输入内容 → 预处理 → 质量评估 → 验证检查 → 质量改进 → 输出验证 → 质量报告
    ↓         ↓         ↓         ↓         ↓         ↓         ↓
原始内容   标准化   多维评分   规则验证   自动改进   最终检查   详细报告
```

## 多维度质量评估

### 五维质量评估模型

```python
@dataclass
class QualityMetrics:
    """质量指标数据模型"""
    completeness: float      # 完整性评分 (0-1)
    accuracy: float         # 准确性评分 (0-1)
    relevance: float        # 相关性评分 (0-1)
    clarity: float          # 清晰度评分 (0-1)
    practicality: float     # 实用性评分 (0-1)

    overall_score: float = field(init=False)
    quality_grade: str = field(init=False)

    def __post_init__(self):
        self.overall_score = self._calculate_overall_score()
        self.quality_grade = self._assign_quality_grade()

    def _calculate_overall_score(self) -> float:
        """计算综合质量评分"""
        weights = {
            'accuracy': 0.30,      # 准确性权重最高
            'completeness': 0.25,  # 完整性次之
            'clarity': 0.20,       # 清晰度
            'relevance': 0.15,     # 相关性
            'practicality': 0.10   # 实用性
        }

        return sum(
            getattr(self, metric) * weight
            for metric, weight in weights.items()
        )

    def _assign_quality_grade(self) -> str:
        """分配质量等级"""
        score = self.overall_score
        if score >= 0.95:
            return "A+"
        elif score >= 0.90:
            return "A"
        elif score >= 0.85:
            return "B+"
        elif score >= 0.80:
            return "B"
        elif score >= 0.75:
            return "C+"
        elif score >= 0.70:
            return "C"
        elif score >= 0.60:
            return "D"
        else:
            return "F"

class QualityAssessmentEngine:
    """质量评估引擎"""

    def __init__(self):
        self.evaluators = {
            'completeness': CompletenessEvaluator(),
            'accuracy': AccuracyEvaluator(),
            'relevance': RelevanceEvaluator(),
            'clarity': ClarityEvaluator(),
            'practicality': PracticalityEvaluator()
        }

        self.assessment_config = AssessmentConfig()

    def assess_content_quality(self, content: str, context: Dict) -> QualityAssessment:
        """评估内容质量"""

        assessment = QualityAssessment(
            content_id=context.get('content_id', ''),
            content_type=context.get('content_type', ''),
            assessment_time=datetime.now(),
            metrics=self._evaluate_all_dimensions(content, context),
            context=context
        )

        # 生成改进建议
        assessment.improvement_suggestions = self._generate_suggestions(assessment.metrics)

        # 验证评估结果
        assessment.validation_result = self._validate_assessment(assessment)

        return assessment

    def _evaluate_all_dimensions(self, content: str, context: Dict) -> QualityMetrics:
        """评估所有质量维度"""

        metrics = {}
        details = {}

        for dimension, evaluator in self.evaluators.items():
            score, detail = evaluator.evaluate(content, context)
            metrics[dimension] = score
            details[dimension] = detail

        return QualityMetrics(
            completeness=metrics['completeness'],
            accuracy=metrics['accuracy'],
            relevance=metrics['relevance'],
            clarity=metrics['clarity'],
            practicality=metrics['practicality']
        )
```

### 维度评估器实现

#### 1. 完整性评估器

```python
class CompletenessEvaluator:
    """完整性评估器"""

    def __init__(self):
        self.required_sections = {
            'tax_guide': ['概述', '主要规定', '计算方法', '示例', '注意事项'],
            'calculation_example': ['场景描述', '给定条件', '计算过程', '结果分析'],
            'quick_reference': ['关键要点', '重要日期', '常用表格', '注意事项']
        }

        self.required_elements = {
            'tax_keywords': 3,      # 至少3个税务关键词
            'examples': 1,          # 至少1个示例
            'references': 2,        # 至少2个参考链接
            'sections': 3           # 至少3个章节
        }

    def evaluate(self, content: str, context: Dict) -> Tuple[float, Dict]:
        """评估内容完整性"""

        content_type = context.get('content_type', 'tax_guide')
        score = 0.0
        details = {}

        # 检查必需章节
        section_score, section_details = self._check_required_sections(content, content_type)
        score += section_score * 0.4
        details['sections'] = section_details

        # 检查必需元素
        element_score, element_details = self._check_required_elements(content)
        score += element_score * 0.4
        details['elements'] = element_details

        # 检查内容深度
        depth_score, depth_details = self._check_content_depth(content)
        score += depth_score * 0.2
        details['depth'] = depth_details

        return min(score, 1.0), details

    def _check_required_sections(self, content: str, content_type: str) -> Tuple[float, Dict]:
        """检查必需章节"""

        required_sections = self.required_sections.get(content_type, [])
        found_sections = []

        for section in required_sections:
            if self._find_section(content, section):
                found_sections.append(section)

        section_score = len(found_sections) / len(required_sections) if required_sections else 1.0

        details = {
            'required_sections': required_sections,
            'found_sections': found_sections,
            'missing_sections': [s for s in required_sections if s not in found_sections],
            'score': section_score
        }

        return section_score, details

    def _find_section(self, content: str, section_name: str) -> bool:
        """查找特定章节"""

        patterns = [
            rf"#+\s*{re.escape(section_name)}",
            rf"\*\*{re.escape(section_name)}\*\*",
            rf"{re.escape(section_name)}[:：]",
        ]

        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                return True

        return False
```

#### 2. 准确性评估器

```python
class AccuracyEvaluator:
    """准确性评估器"""

    def __init__(self):
        self.tax_rule_validator = TaxRuleValidator()
        self.calculation_validator = CalculationValidator()
        self.fact_checker = FactChecker()

        # 税务规则数据库
        self.tax_rules_db = TaxRulesDatabase()

    def evaluate(self, content: str, context: Dict) -> Tuple[float, Dict]:
        """评估内容准确性"""

        accuracy_score = 1.0
        details = {}

        # 1. 税务规则验证
        rule_score, rule_details = self.tax_rule_validator.validate(content)
        accuracy_score *= rule_score
        details['tax_rules'] = rule_details

        # 2. 计算验证
        calc_score, calc_details = self.calculation_validator.validate(content)
        accuracy_score *= calc_score
        details['calculations'] = calc_details

        # 3. 事实核查
        fact_score, fact_details = self.fact_checker.check(content)
        accuracy_score *= fact_score
        details['facts'] = fact_details

        # 4. 数值一致性检查
        consistency_score, consistency_details = self._check_numerical_consistency(content)
        accuracy_score *= consistency_score
        details['consistency'] = consistency_details

        return accuracy_score, details

    def _check_numerical_consistency(self, content: str) -> Tuple[float, Dict]:
        """检查数值一致性"""

        # 提取所有数值
        numbers = self._extract_numbers(content)

        if len(numbers) < 2:
            return 1.0, {'numbers_found': len(numbers)}

        # 检查百分比数值合理性
        percentages = [n for n in numbers if '%' in content[content.find(str(n))-10:content.find(str(n))+10]]
        percentage_issues = []

        for pct in percentages:
            if pct > 100 or pct < 0:
                percentage_issues.append(f"不合理的百分比: {pct}%")

        # 检查金额数值合理性
        amounts = self._extract_amounts(content)
        amount_issues = []

        for amount in amounts:
            if amount > 10000000:  # 超过1000万可能是错误
                amount_issues.append(f"异常大额: ${amount:,.2f}")

        issue_count = len(percentage_issues) + len(amount_issues)
        consistency_score = max(0, 1.0 - (issue_count / len(numbers)))

        details = {
            'total_numbers': len(numbers),
            'percentages': len(percentages),
            'amounts': len(amounts),
            'percentage_issues': percentage_issues,
            'amount_issues': amount_issues,
            'consistency_score': consistency_score
        }

        return consistency_score, details

class TaxRuleValidator:
    """税务规则验证器"""

    def __init__(self):
        self.rule_patterns = {
            'capital_gains_inclusion_rate': [
                (r'包含率\s*[:=]\s*(\d+)%', 0.5),  # 期望50%
                (r'inclusion\s*rate\s*[:=]\s*(\d+)%', 0.5),
            ],
            'rrsp_contribution_limit': [
                (r'RRSP.*限额.*\$?([\d,]+)', 30000),  # 期望30000左右
            ],
            'gst_hst_rate': [
                (r'GST.*(\d+)%', 5),  # 期望5%
                (r'HST.*(\d+)%', 13),  # 期望13%（安省）
            ]
        }

    def validate(self, content: str) -> Tuple[float, Dict]:
        """验证税务规则"""

        validation_results = []

        for rule_name, patterns in self.rule_patterns.items():
            rule_score, rule_details = self._validate_rule(content, rule_name, patterns)
            validation_results.append({
                'rule': rule_name,
                'score': rule_score,
                'details': rule_details
            })

        overall_score = sum(r['score'] for r in validation_results) / len(validation_results)

        return overall_score, {
            'rule_validations': validation_results,
            'rules_checked': len(validation_results)
        }

    def _validate_rule(self, content: str, rule_name: str, patterns: List) -> Tuple[float, Dict]:
        """验证特定规则"""

        for pattern, expected_value in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)

            if matches:
                # 检查匹配值是否合理
                for match in matches:
                    try:
                        actual_value = float(match.replace(',', ''))

                        # 允许一定的误差范围
                        tolerance = expected_value * 0.1  # 10%误差
                        if abs(actual_value - expected_value) <= tolerance:
                            return 1.0, {
                                'status': 'valid',
                                'expected': expected_value,
                                'actual': actual_value,
                                'pattern': pattern
                            }
                        else:
                            return 0.5, {
                                'status': 'questionable',
                                'expected': expected_value,
                                'actual': actual_value,
                                'difference': abs(actual_value - expected_value),
                                'pattern': pattern
                            }
                    except ValueError:
                        continue

        # 如果没有找到匹配，无法验证
        return 0.8, {
            'status': 'not_found',
            'message': f'Rule {rule_name} not found in content'
        }
```

#### 3. 清晰度评估器

```python
class ClarityEvaluator:
    """清晰度评估器"""

    def __init__(self):
        self.readability_analyzer = ReadabilityAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()

    def evaluate(self, content: str, context: Dict) -> Tuple[float, Dict]:
        """评估内容清晰度"""

        clarity_score = 0.0
        details = {}

        # 1. 可读性分析
        readability_score, readability_details = self.readability_analyzer.analyze(content)
        clarity_score += readability_score * 0.4
        details['readability'] = readability_details

        # 2. 复杂度分析
        complexity_score, complexity_details = self.complexity_analyzer.analyze(content)
        clarity_score += complexity_score * 0.3
        details['complexity'] = complexity_details

        # 3. 结构分析
        structure_score, structure_details = self._analyze_structure(content)
        clarity_score += structure_score * 0.3
        details['structure'] = structure_details

        return min(clarity_score, 1.0), details

    def _analyze_structure(self, content: str) -> Tuple[float, Dict]:
        """分析内容结构"""

        # 检查标题层次
        headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)

        if not headings:
            return 0.3, {'error': 'No headings found'}

        # 检查标题层次合理性
        level_distribution = {}
        for level, title in headings:
            level_count = len(level)
            level_distribution[level_count] = level_distribution.get(level_count, 0) + 1

        # 理想的标题分布：H1 < H2 < H3 < ...
        structure_issues = []
        if level_distribution.get(1, 0) > 1:
            structure_issues.append("Multiple H1 headings")

        if not level_distribution.get(2, 0):
            structure_issues.append("No H2 headings")

        # 检查段落长度
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        long_paragraphs = [p for p in paragraphs if len(p) > 500]

        # 检查列表使用
        lists = re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE)

        structure_score = max(0, 1.0 - (len(structure_issues) * 0.2))
        structure_score = max(0, structure_score - (len(long_paragraphs) / len(paragraphs)) * 0.1)

        details = {
            'headings_count': len(headings),
            'level_distribution': level_distribution,
            'structure_issues': structure_issues,
            'paragraphs_count': len(paragraphs),
            'long_paragraphs': len(long_paragraphs),
            'lists_count': len(lists),
            'structure_score': structure_score
        }

        return structure_score, details

class ReadabilityAnalyzer:
    """可读性分析器"""

    def analyze(self, content: str) -> Tuple[float, Dict]:
        """分析内容可读性"""

        # 移除 Markdown 格式
        clean_content = re.sub(r'[#*`\[\]()_-]', ' ', content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()

        if not clean_content:
            return 0.0, {'error': 'No content to analyze'}

        words = clean_content.split()
        sentences = re.split(r'[.!?]+', clean_content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0, {'error': 'No sentences found'}

        # 计算基本指标
        avg_words_per_sentence = len(words) / len(sentences)
        avg_chars_per_word = sum(len(word) for word in words) / len(words)

        # 计算可读性评分（简化版 Flesch Reading Ease）
        readability_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * (avg_chars_per_word / 4.7))
        readability_score = max(0, min(100, readability_score))  # 限制在 0-100 范围

        # 转换为 0-1 评分
        normalized_score = readability_score / 100

        details = {
            'words_count': len(words),
            'sentences_count': len(sentences),
            'avg_words_per_sentence': avg_words_per_sentence,
            'avg_chars_per_word': avg_chars_per_word,
            'readability_score': readability_score,
            'readability_level': self._get_readability_level(readability_score)
        }

        return normalized_score, details

    def _get_readability_level(self, score: float) -> str:
        """获取可读性等级"""
        if score >= 90:
            return "非常易读"
        elif score >= 80:
            return "易读"
        elif score >= 70:
            return "较易读"
        elif score >= 60:
            return "标准"
        elif score >= 50:
            return "较难读"
        elif score >= 30:
            return "难读"
        else:
            return "非常难读"
```

## 自动质量改进

### 智能改进引擎

```python
class IntelligentQualityImprover:
    """智能质量改进引擎"""

    def __init__(self):
        self.improvement_strategies = {
            'completeness': CompletenessImprover(),
            'accuracy': AccuracyImprover(),
            'clarity': ClarityImprover(),
            'practicality': PracticalityImprover()
        }

        self.ai_enhancer = AIContentEnhancer()
        self.max_improvement_attempts = 3

    def improve_content_quality(self, content: str, assessment: QualityAssessment) -> ImprovementResult:
        """改进内容质量"""

        improved_content = content
        improvement_log = []
        attempt_count = 0

        # 识别需要改进的维度
        dimensions_to_improve = self._identify_improvement_dimensions(assessment.metrics)

        for attempt in range(self.max_improvement_attempts):
            attempt_count += 1
            previous_score = self._calculate_current_score(improved_content, assessment.context)

            # 应用改进策略
            for dimension in dimensions_to_improve:
                if assessment.metrics.get_dimension_score(dimension) < 0.7:
                    try:
                        strategy = self.improvement_strategies.get(dimension)
                        if strategy:
                            improved_content, improvement_detail = strategy.improve(
                                improved_content, assessment.context, assessment.metrics
                            )
                            improvement_log.append({
                                'attempt': attempt_count,
                                'dimension': dimension,
                                'improvement': improvement_detail,
                                'previous_score': previous_score
                            })
                    except Exception as e:
                        improvement_log.append({
                            'attempt': attempt_count,
                            'dimension': dimension,
                            'error': str(e),
                            'status': 'failed'
                        })

            # 重新评估质量
            new_assessment = self.assess_content_quality(improved_content, assessment.context)
            new_score = new_assessment.metrics.overall_score

            # 检查是否有改进
            if new_score > previous_score + 0.05:  # 至少提升5%
                improvement_log.append({
                    'attempt': attempt_count,
                    'overall_improvement': new_score - previous_score,
                    'new_score': new_score,
                    'status': 'improved'
                })
            else:
                improvement_log.append({
                    'attempt': attempt_count,
                    'message': 'No significant improvement',
                    'status': 'no_improvement'
                })
                break

            # 检查是否达到目标质量
            if new_score >= 0.85:
                break

        # 最终评估
        final_assessment = self.assess_content_quality(improved_content, assessment.context)

        return ImprovementResult(
            original_content=content,
            improved_content=improved_content,
            original_assessment=assessment,
            final_assessment=final_assessment,
            improvement_log=improvement_log,
            overall_improvement=final_assessment.metrics.overall_score - assessment.metrics.overall_score,
            success=final_assessment.metrics.overall_score > assessment.metrics.overall_score
        )

class CompletenessImprover:
    """完整性改进策略"""

    def improve(self, content: str, context: Dict, metrics: QualityMetrics) -> Tuple[str, str]:
        """改进内容完整性"""

        if metrics.completeness < 0.7:
            # 识别缺失的章节
            missing_sections = self._identify_missing_sections(content, context)

            if missing_sections:
                # 使用 AI 生成缺失章节
                enhanced_content = self._generate_missing_sections(content, missing_sections, context)

                improvement_detail = f"添加了缺失章节: {', '.join(missing_sections)}"
                return enhanced_content, improvement_detail

        return content, "内容完整性良好"

class ClarityImprover:
    """清晰度改进策略"""

    def improve(self, content: str, context: Dict, metrics: QualityMetrics) -> Tuple[str, str]:
        """改进内容清晰度"""

        if metrics.clarity < 0.7:
            # 分析清晰度问题
            clarity_issues = self._analyze_clarity_issues(content)

            if clarity_issues:
                # 使用 AI 改进清晰度
                enhanced_content = self._improve_clarity_with_ai(content, clarity_issues, context)

                improvement_detail = f"改进了清晰度问题: {', '.join(clarity_issues)}"
                return enhanced_content, improvement_detail

        return content, "内容清晰度良好"

    def _improve_clarity_with_ai(self, content: str, issues: List[str], context: Dict) -> str:
        """使用 AI 改进清晰度"""

        improvement_prompt = f"""
请改进以下税务内容的清晰度，解决以下问题：

问题：{', '.join(issues)}

原始内容：
{content}

改进要求：
1. 简化复杂的句子结构
2. 解释专业术语
3. 改善段落组织
4. 使用更通俗的表达
5. 保持技术准确性

请返回改进后的内容，保持原有的技术信息不变。
"""

        try:
            enhanced_content = self.ai_enhancer.enhance_content(improvement_prompt)
            return enhanced_content
        except Exception as e:
            return content  # 改进失败，返回原内容
```

## 验证和测试

### 自动化验证系统

```python
class AutomatedValidationSystem:
    """自动化验证系统"""

    def __init__(self):
        self.validators = {
            'content': ContentValidator(),
            'format': FormatValidator(),
            'links': LinkValidator(),
            'calculations': CalculationValidator(),
            'consistency': ConsistencyValidator()
        }

        self.test_suite = ValidationTestSuite()

    def validate_content(self, content: str, validation_rules: Dict) -> ValidationReport:
        """验证内容"""

        validation_results = {}

        for validator_name, validator in self.validators.items():
            if validator_name in validation_rules or validation_rules.get('all', False):
                result = validator.validate(content, validation_rules.get(validator_name, {}))
                validation_results[validator_name] = result

        # 生成验证报告
        validation_report = ValidationReport(
            content_hash=self._generate_content_hash(content),
            validation_timestamp=datetime.now(),
            results=validation_results,
            overall_status=self._calculate_overall_status(validation_results),
            issues=self._collect_issues(validation_results)
        )

        return validation_report

    def run_validation_tests(self, test_data: List[Dict]) -> TestResults:
        """运行验证测试"""

        test_results = TestResults()

        for test_case in test_data:
            try:
                # 运行测试
                result = self.test_suite.run_test(test_case)
                test_results.add_result(result)

            except Exception as e:
                test_results.add_error(test_case['id'], str(e))

        return test_results

class ContentValidator:
    """内容验证器"""

    def validate(self, content: str, rules: Dict) -> ValidationResult:
        """验证内容"""

        issues = []
        warnings = []

        # 检查必需内容
        if rules.get('required_sections'):
            missing_sections = self._check_required_sections(content, rules['required_sections'])
            issues.extend([f"缺失章节: {section}" for section in missing_sections])

        # 检查禁用内容
        if rules.get('forbidden_content'):
            forbidden_found = self._check_forbidden_content(content, rules['forbidden_content'])
            issues.extend([f"包含禁用内容: {item}" for item in forbidden_found])

        # 检查内容长度
        if rules.get('min_length'):
            if len(content) < rules['min_length']:
                warnings.append(f"内容过短: {len(content)} < {rules['min_length']}")

        if rules.get('max_length'):
            if len(content) > rules['max_length']:
                warnings.append(f"内容过长: {len(content)} > {rules['max_length']}")

        # 检查语言质量
        if rules.get('language_check', True):
            language_issues = self._check_language_quality(content)
            warnings.extend(language_issues)

        return ValidationResult(
            validator_name="content",
            status="passed" if not issues else "failed",
            issues=issues,
            warnings=warnings,
            score=max(0, 1.0 - (len(issues) * 0.2))
        )

class CalculationValidator:
    """计算验证器"""

    def validate(self, content: str, rules: Dict) -> ValidationResult:
        """验证计算"""

        calculations = self._extract_calculations(content)
        issues = []
        validated_calculations = []

        for calc in calculations:
            try:
                # 验证计算逻辑
                validation_result = self._validate_calculation(calc)

                if validation_result.is_valid:
                    validated_calculations.append(validation_result)
                else:
                    issues.append(f"计算错误: {calc.expression} - {validation_result.error}")

            except Exception as e:
                issues.append(f"计算验证失败: {calc.expression} - {str(e)}")

        # 检查计算一致性
        if len(calculations) > 1:
            consistency_issues = self._check_calculation_consistency(calculations)
            issues.extend(consistency_issues)

        return ValidationResult(
            validator_name="calculations",
            status="passed" if not issues else "failed",
            issues=issues,
            validated_calculations=validated_calculations,
            score=max(0, 1.0 - (len(issues) / max(len(calculations), 1)))
        )
```

## 监控和报告

### 质量监控系统

```python
class QualityMonitoringSystem:
    """质量监控系统"""

    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.report_generator = ReportGenerator()

        self.monitoring_config = MonitoringConfig()

    def monitor_content_quality(self, content_id: str, assessment: QualityAssessment):
        """监控内容质量"""

        # 收集质量指标
        self._collect_quality_metrics(content_id, assessment)

        # 检查警报条件
        self._check_alert_conditions(content_id, assessment)

        # 更新趋势数据
        self._update_quality_trends(content_id, assessment)

    def _collect_quality_metrics(self, content_id: str, assessment: QualityAssessment):
        """收集质量指标"""

        timestamp = datetime.now()

        # 整体质量指标
        self.metrics_collector.record_metric(
            name="content_quality_overall",
            value=assessment.metrics.overall_score,
            tags={
                "content_id": content_id,
                "content_type": assessment.content_type
            },
            timestamp=timestamp
        )

        # 各维度指标
        for dimension, score in assessment.metrics.__dict__.items():
            if isinstance(score, (int, float)):
                self.metrics_collector.record_metric(
                    name=f"content_quality_{dimension}",
                    value=score,
                    tags={
                        "content_id": content_id,
                        "content_type": assessment.content_type
                    },
                    timestamp=timestamp
                )

    def _check_alert_conditions(self, content_id: str, assessment: QualityAssessment):
        """检查警报条件"""

        # 低质量警报
        if assessment.metrics.overall_score < self.monitoring_config.low_quality_threshold:
            self.alert_manager.send_alert(
                level="warning",
                title="内容质量低于阈值",
                message=f"内容 {content_id} 质量评分 {assessment.metrics.overall_score:.2f} 低于阈值 {self.monitoring_config.low_quality_threshold}",
                metadata={
                    "content_id": content_id,
                    "quality_score": assessment.metrics.overall_score,
                    "threshold": self.monitoring_config.low_quality_threshold
                }
            )

        # 严重质量问题警报
        critical_issues = [
            dimension for dimension, score in assessment.metrics.__dict__.items()
            if isinstance(score, (int, float)) and score < self.monitoring_config.critical_threshold
        ]

        if critical_issues:
            self.alert_manager.send_alert(
                level="error",
                title="严重质量问题",
                message=f"内容 {content_id} 存在严重质量问题: {', '.join(critical_issues)}",
                metadata={
                    "content_id": content_id,
                    "critical_issues": critical_issues
                }
            )

    def generate_quality_report(self, period: str = "daily") -> QualityReport:
        """生成质量报告"""

        end_time = datetime.now()

        if period == "daily":
            start_time = end_time - timedelta(days=1)
        elif period == "weekly":
            start_time = end_time - timedelta(weeks=1)
        elif period == "monthly":
            start_time = end_time - timedelta(days=30)
        else:
            start_time = end_time - timedelta(days=1)

        # 收集报告数据
        report_data = self._collect_report_data(start_time, end_time)

        # 生成报告
        report = self.report_generator.generate_report(
            period=period,
            start_time=start_time,
            end_time=end_time,
            data=report_data
        )

        return report

class ReportGenerator:
    """报告生成器"""

    def generate_report(self, period: str, start_time: datetime, end_time: datetime, data: Dict) -> QualityReport:
        """生成质量报告"""

        report = QualityReport(
            period=period,
            start_time=start_time,
            end_time=end_time,
            generated_at=datetime.now()
        )

        # 整体统计
        report.overall_statistics = {
            'total_contents_processed': data.get('total_contents', 0),
            'average_quality_score': data.get('avg_quality_score', 0.0),
            'quality_distribution': data.get('quality_distribution', {}),
            'improvement_rate': data.get('improvement_rate', 0.0)
        }

        # 维度分析
        report.dimension_analysis = self._analyze_dimensions(data)

        # 趋势分析
        report.trend_analysis = self._analyze_trends(data)

        # 问题分析
        report.issue_analysis = self._analyze_issues(data)

        # 改进建议
        report.recommendations = self._generate_recommendations(report)

        return report

    def _generate_recommendations(self, report: QualityReport) -> List[str]:
        """生成改进建议"""

        recommendations = []

        # 基于整体质量评分的建议
        if report.overall_statistics['average_quality_score'] < 0.8:
            recommendations.append("整体质量偏低，建议加强内容审核和改进流程")

        # 基于维度分析的建议
        if report.dimension_analysis.get('lowest_scoring_dimension'):
            lowest_dimension = report.dimension_analysis['lowest_scoring_dimension']
            recommendations.append(f"重点关注 {lowest_dimension} 的质量提升")

        # 基于趋势分析的建议
        if report.trend_analysis.get('quality_trend') == 'declining':
            recommendations.append("质量呈下降趋势，建议立即采取改进措施")

        # 基于问题分析的建议
        if report.issue_analysis.get('most_common_issue'):
            common_issue = report.issue_analysis['most_common_issue']
            recommendations.append(f"重点解决 {common_issue} 问题")

        return recommendations
```

## 最佳实践

### 质量控制最佳实践

1. **多层次验证**
   - 实施自动化和人工验证相结合
   - 建立分级审核机制
   - 定期进行质量审计

2. **持续改进**
   - 建立质量反馈循环
   - 定期更新质量标准
   - 优化评估算法

3. **数据驱动决策**
   - 收集详细的质量指标
   - 分析质量趋势和模式
   - 基于数据制定改进策略

### 实施建议

1. **分阶段实施**
   - 先实施基础质量评估
   - 逐步增加高级功能
   - 持续优化和改进

2. **团队培训**
   - 培训团队使用质量系统
   - 建立质量意识文化
   - 定期分享最佳实践

3. **技术投资**
   - 投资先进的 AI 技术
   - 建立完善的基础设施
   - 保障系统稳定性和性能

## 总结

质量控制和验证系统为 BlockMe CRA 税务文档处理系统提供了全方位的质量保证机制。通过多维度评估、自动改进、智能验证和持续监控，确保输出内容的高质量和可靠性。

关键优势：
1. **全面性**：五维质量评估覆盖内容质量的各个方面
2. **智能化**：AI 驱动的自动改进和验证
3. **可靠性**：多层次验证确保内容准确性
4. **可扩展性**：灵活的架构支持功能扩展
5. **数据驱动**：基于指标和趋势的决策支持

这个系统将成为 BlockMe 确保内容质量的核心基础设施，为用户提供高质量、可靠的税务知识服务。