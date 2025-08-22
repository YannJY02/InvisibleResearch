#!/usr/bin/env python3
"""
LLM验证器核心模块 - LLM验证审核系统
Core LLM Validator Module for LLM Validation Suite

提供核心的验证逻辑和评估功能
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import asdict

from utils.data_manager import ValidationRecord, DataManager
from utils.search_tools import ExternalValidator


class LLMValidator:
    """LLM验证器主类"""
    
    def __init__(self, config_path: str = "scripts/05_validation/validation_config.yaml"):
        self.data_manager = DataManager(config_path)
        self.external_validator = ExternalValidator(config_path)
        self.config = self.data_manager.config
        self.evaluation_criteria = self.config['evaluation_criteria']
    
    def analyze_author_identification(self, record: ValidationRecord) -> Tuple[int, str]:
        """
        分析作者识别准确性
        返回: (评分1-5, 分析说明)
        """
        original = record.original_creator.strip()
        processed = record.processed_authors.strip()
        
        if not original:
            return 1, "原始creator字段为空"
        
        if not processed:
            return 1, "处理后authors_clean字段为空"
        
        # 检查明显的错误模式
        error_patterns = ['*', '???', 'unknown', 'anonymous']
        if any(pattern in processed.lower() for pattern in error_patterns):
            return 1, f"包含错误模式: {processed}"
        
        # 检查字符长度差异
        length_ratio = len(processed) / len(original) if len(original) > 0 else 0
        if length_ratio < 0.1:
            return 2, "处理后内容严重缺失"
        elif length_ratio > 3:
            return 2, "处理后内容异常增加"
        
        # 检查作者姓名的合理性
        authors_list = [name.strip() for name in processed.split(';') if name.strip()]
        
        # 基本姓名格式检查
        valid_name_pattern = re.compile(r'^[A-Za-zÀ-ÿ\u4e00-\u9fff\u0400-\u04ff\s,.-]+$')
        invalid_names = [name for name in authors_list if not valid_name_pattern.match(name)]
        
        if len(invalid_names) > 0:
            return 2, f"包含无效姓名格式: {invalid_names[:2]}"
        
        # 检查姓名长度合理性
        too_short_names = [name for name in authors_list if len(name) < 2]
        too_long_names = [name for name in authors_list if len(name) > 100]
        
        if too_short_names:
            return 2, f"姓名过短: {too_short_names}"
        if too_long_names:
            return 2, f"姓名过长: {too_long_names[:1]}"
        
        # 简单的相似度检查
        original_clean = re.sub(r'[^\w\s]', ' ', original.lower())
        processed_clean = re.sub(r'[^\w\s]', ' ', processed.lower())
        
        original_words = set(original_clean.split())
        processed_words = set(processed_clean.split())
        
        if original_words and processed_words:
            overlap = len(original_words.intersection(processed_words))
            similarity = overlap / len(original_words.union(processed_words))
            
            if similarity > 0.7:
                return 5, "高相似度，可能正确"
            elif similarity > 0.5:
                return 4, "中等相似度，基本合理"
            elif similarity > 0.3:
                return 3, "较低相似度，需要检查"
            else:
                return 2, "极低相似度，可能有问题"
        
        return 3, "无法确定相似度，需要人工判断"
    
    def analyze_author_separation(self, record: ValidationRecord) -> Tuple[int, str]:
        """
        分析多作者分割准确性
        返回: (评分1-5, 分析说明)
        """
        original = record.original_creator
        processed = record.processed_authors
        expected_count = record.author_count
        
        # 如果是单作者案例
        if expected_count <= 1:
            if ';' not in processed:
                return 5, "单作者案例，无需分割"
            else:
                return 2, "单作者案例不应包含分号"
        
        # 多作者案例
        actual_authors = [name.strip() for name in processed.split(';') if name.strip()]
        actual_count = len(actual_authors)
        
        # 检查分割数量准确性
        if actual_count == expected_count:
            score = 5
            note = f"分割数量正确: {actual_count} 个作者"
        elif abs(actual_count - expected_count) == 1:
            score = 4
            note = f"分割数量接近: {actual_count} vs 期望 {expected_count}"
        elif abs(actual_count - expected_count) <= 2:
            score = 3
            note = f"分割数量偏差较小: {actual_count} vs 期望 {expected_count}"
        else:
            score = 2
            note = f"分割数量偏差较大: {actual_count} vs 期望 {expected_count}"
        
        # 检查分割质量
        duplicate_names = []
        name_lengths = []
        
        for name in actual_authors:
            name_lengths.append(len(name))
            if actual_authors.count(name) > 1:
                duplicate_names.append(name)
        
        # 惩罚重复姓名
        if duplicate_names:
            score = max(1, score - 1)
            note += f"; 发现重复姓名: {duplicate_names[:2]}"
        
        # 惩罚异常短或长的姓名
        avg_length = sum(name_lengths) / len(name_lengths) if name_lengths else 0
        if avg_length < 5:
            score = max(1, score - 1)
            note += "; 平均姓名长度过短"
        elif avg_length > 50:
            score = max(1, score - 1)
            note += "; 平均姓名长度过长"
        
        return score, note
    
    def analyze_name_affiliation_classification(self, record: ValidationRecord) -> Tuple[int, str]:
        """
        分析姓名vs机构信息分类准确性
        返回: (评分1-5, 分析说明)
        """
        authors = record.processed_authors
        affiliations = record.processed_affiliations
        
        # 检查作者字段中是否包含明显的机构信息
        institution_keywords = [
            'university', 'college', 'institute', 'department', 'faculty',
            'hospital', 'center', 'centre', 'school', 'laboratory', 'lab',
            'email', '@', 'phone', 'tel', 'orcid', 'doi', 'www', 'http',
            '大学', '学院', '研究所', '医院', '中心', '实验室'
        ]
        
        authors_lower = authors.lower()
        institution_in_authors = any(keyword in authors_lower for keyword in institution_keywords)
        
        if institution_in_authors:
            return 2, "作者字段中包含机构信息，分类不准确"
        
        # 检查机构字段的合理性
        if len(affiliations) == 0:
            # 原始creator中是否包含机构信息
            original_lower = record.original_creator.lower()
            has_institution_in_original = any(keyword in original_lower for keyword in institution_keywords)
            
            if has_institution_in_original:
                return 3, "原始数据包含机构信息但未提取到affiliations中"
            else:
                return 5, "无机构信息，分类正确"
        
        # 检查提取的机构信息质量
        valid_affiliations = 0
        for affiliation in affiliations:
            if len(affiliation.strip()) > 5:  # 至少5个字符
                valid_affiliations += 1
        
        if valid_affiliations == len(affiliations):
            return 5, f"成功提取 {len(affiliations)} 个有效机构信息"
        elif valid_affiliations > len(affiliations) * 0.7:
            return 4, f"大部分机构信息有效: {valid_affiliations}/{len(affiliations)}"
        else:
            return 3, f"部分机构信息可能无效: {valid_affiliations}/{len(affiliations)}"
    
    def analyze_name_formatting(self, record: ValidationRecord) -> Tuple[int, str]:
        """
        分析姓名格式化质量
        返回: (评分1-5, 分析说明)
        """
        processed = record.processed_authors
        
        if not processed.strip():
            return 1, "处理后姓名为空"
        
        authors_list = [name.strip() for name in processed.split(';') if name.strip()]
        
        format_scores = []
        format_notes = []
        
        for name in authors_list:
            # 检查基本格式
            score = 3  # 默认中等分数
            notes = []
            
            # 检查是否包含逗号分隔（推荐格式）
            if ',' in name:
                parts = name.split(',')
                if len(parts) == 2:
                    last_name, first_name = parts
                    if last_name.strip() and first_name.strip():
                        score += 1
                        notes.append("使用推荐的 'Last, First' 格式")
                    else:
                        score -= 1
                        notes.append("逗号格式但缺少姓或名")
                else:
                    score -= 1
                    notes.append("逗号过多")
            
            # 检查大小写
            if name.isupper():
                score -= 1
                notes.append("全大写格式")
            elif name.islower():
                score -= 1
                notes.append("全小写格式")
            elif name.istitle() or any(c.isupper() for c in name):
                score += 0.5
                notes.append("适当的大小写")
            
            # 检查特殊字符
            if re.search(r'[^\w\s,.-]', name):
                score -= 0.5
                notes.append("包含特殊字符")
            
            # 检查空格
            if re.search(r'\s{2,}', name):
                score -= 0.5
                notes.append("包含多余空格")
            
            format_scores.append(max(1, min(5, score)))
            format_notes.extend(notes)
        
        avg_score = sum(format_scores) / len(format_scores)
        final_score = round(avg_score)
        
        note = f"平均格式分数: {avg_score:.1f}; {'; '.join(format_notes[:3])}"
        
        return final_score, note
    
    def calculate_overall_score(self, record: ValidationRecord) -> Tuple[str, float, str]:
        """
        计算综合评分
        返回: (状态, 权重分数, 说明)
        """
        criteria = self.evaluation_criteria
        
        # 获取各项评分
        id_score, _ = self.analyze_author_identification(record)
        sep_score, _ = self.analyze_author_separation(record)
        class_score, _ = self.analyze_name_affiliation_classification(record)
        format_score, _ = self.analyze_name_formatting(record)
        
        # 计算加权平均分
        weighted_score = (
            id_score * criteria['author_identification']['weight'] +
            sep_score * criteria['author_separation']['weight'] +
            class_score * criteria['name_affiliation_classification']['weight'] +
            format_score * criteria['name_formatting']['weight']
        )
        
        # 确定状态
        if weighted_score >= 4.5:
            status = "correct"
            explanation = "高质量处理结果"
        elif weighted_score >= 3.5:
            status = "partial"
            explanation = "中等质量，部分正确"
        else:
            status = "incorrect"
            explanation = "低质量，需要改进"
        
        return status, weighted_score, explanation
    
    def validate_record(self, record: ValidationRecord, 
                       include_external: bool = False,
                       validator_name: str = "system") -> ValidationRecord:
        """
        验证单条记录
        """
        # 执行各项分析
        id_score, id_note = self.analyze_author_identification(record)
        sep_score, sep_note = self.analyze_author_separation(record)
        class_score, class_note = self.analyze_name_affiliation_classification(record)
        format_score, format_note = self.analyze_name_formatting(record)
        
        # 计算综合评分
        status, weighted_score, explanation = self.calculate_overall_score(record)
        
        # 更新记录
        record.author_identification_score = id_score
        record.author_separation_score = sep_score
        record.name_affiliation_score = class_score
        record.name_formatting_score = format_score
        record.overall_status = status
        record.validator_name = validator_name
        record.validation_timestamp = datetime.now().isoformat()
        
        # 生成详细说明
        notes = [
            f"作者识别({id_score}/5): {id_note}",
            f"分割准确性({sep_score}/5): {sep_note}",
            f"分类准确性({class_score}/5): {class_note}",
            f"格式质量({format_score}/5): {format_note}",
            f"综合评分: {weighted_score:.2f}/5.0 - {explanation}"
        ]
        record.notes = "; ".join(notes)
        
        # 外部验证（可选）
        if include_external:
            try:
                external_result = self.external_validator.comprehensive_validation(
                    record.title, record.processed_authors
                )
                record.external_verification = external_result
            except Exception as e:
                record.external_verification = {"error": str(e)}
        
        return record
    
    def batch_validate(self, records: List[ValidationRecord], 
                      include_external: bool = False,
                      validator_name: str = "system") -> List[ValidationRecord]:
        """
        批量验证记录
        """
        validated_records = []
        
        for i, record in enumerate(records):
            print(f"🔍 验证进度: {i+1}/{len(records)} - ID: {record.record_id}")
            
            validated_record = self.validate_record(
                record, include_external, validator_name
            )
            validated_records.append(validated_record)
            
            # 如果启用外部验证，添加延迟避免API限制
            if include_external and i < len(records) - 1:
                import time
                time.sleep(1)
        
        return validated_records


def main():
    """测试LLM验证器"""
    validator = LLMValidator()
    
    print("🔍 测试LLM验证器...")
    
    # 准备测试数据
    dm = validator.data_manager
    records = dm.prepare_validation_records()
    
    # 取前3条记录进行测试
    test_records = records[:3]
    
    print(f"\n📋 测试记录数: {len(test_records)}")
    
    for i, record in enumerate(test_records, 1):
        print(f"\n--- 测试记录 {i} ---")
        print(f"ID: {record.record_id}")
        print(f"标题: {record.title[:50]}...")
        print(f"原始creator: {record.original_creator[:50]}...")
        print(f"处理后authors: {record.processed_authors}")
        
        # 执行验证
        validated = validator.validate_record(record, include_external=False)
        
        print(f"验证结果: {validated.overall_status}")
        print(f"作者识别: {validated.author_identification_score}/5")
        print(f"分割准确性: {validated.author_separation_score}/5")
        print(f"分类准确性: {validated.name_affiliation_score}/5")
        print(f"格式质量: {validated.name_formatting_score}/5")
        print(f"详细说明: {validated.notes[:100]}...")


if __name__ == "__main__":
    main()
