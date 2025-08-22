#!/usr/bin/env python3
"""
报告生成模块 - LLM验证审核系统
Report Generator Module for LLM Validation Suite

生成详细的验证报告和统计分析
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import base64

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template

try:
    from .data_manager import ValidationRecord
except ImportError:
    from data_manager import ValidationRecord


class ReportGenerator:
    """报告生成器类"""
    
    def __init__(self, config_path: str = "scripts/05_validation/validation_config.yaml"):
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.report_settings = self.config['report_settings']
        
        # Set fonts for better compatibility
        plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
    
    def _get_template_content(self, language: str) -> Dict[str, str]:
        """获取模板内容文本"""
        if language == 'en':
            return {
                'main_title': '🔍 LLM Named Entity Extraction Validation Report',
                'overview_title': '📊 Overall Overview',
                'total_records_label': 'Total Records',
                'validated_records_label': 'Validated Records',
                'completion_rate_label': 'Completion Rate',
                'overall_accuracy_label': 'Overall Accuracy',
                'complexity_analysis_title': '📈 Accuracy Analysis by Complexity Level',
                'complexity_detail_title': '📋 Detailed Statistics by Complexity',
                'complexity_label': 'Complexity',
                'total_label': 'Total',
                'correct_label': 'Correct',
                'accuracy_label': 'Accuracy',
                'error_analysis_title': '🔍 Error Pattern Analysis',
                'most_common_errors': 'Most Common Error Types:',
                'improvement_suggestions_title': '💡 Improvement Suggestions',
                'suggestions_intro': 'Suggestions based on analysis results:',
                'low_accuracy_suggestion': 'Overall accuracy is low: Consider reviewing LLM prompts and processing logic',
                'complex_cases_suggestion': 'Complex case processing capability insufficient: Need to optimize algorithms for complex cases',
                'separation_issue_suggestion': 'Multi-author separation issues: Optimize author separation logic and delimiter recognition',
                'classification_issue_suggestion': 'Institution information classification issues: Improve name vs institution classification rules',
                'continuous_monitoring_suggestion': 'Continuous monitoring: Recommend regular validation to ensure processing quality',
                'manual_review_suggestion': 'Manual review: Suggest adding manual review process for low-confidence cases',
                'generation_time_label': 'Report Generation Time:',
                'system_name': 'LLM Named Entity Extraction Validation System - InvisibleResearch Project'
            }
        else:
            return {
                'main_title': '🔍 LLM名称提取验证报告',
                'overview_title': '📊 总体概览',
                'total_records_label': '总记录数',
                'validated_records_label': '已验证记录',
                'completion_rate_label': '完成率',
                'overall_accuracy_label': '整体准确率',
                'complexity_analysis_title': '📈 按复杂度分类的准确率分析',
                'complexity_detail_title': '📋 复杂度详细统计',
                'complexity_label': '复杂度',
                'total_label': '总数',
                'correct_label': '正确',
                'accuracy_label': '准确率',
                'error_analysis_title': '🔍 错误模式分析',
                'most_common_errors': '最常见的错误类型：',
                'improvement_suggestions_title': '💡 改进建议',
                'suggestions_intro': '基于分析结果的建议：',
                'low_accuracy_suggestion': '整体准确率偏低: 建议重新审视LLM提示词和处理逻辑',
                'complex_cases_suggestion': '复杂案例处理能力不足: 需要针对复杂案例优化算法',
                'separation_issue_suggestion': '多作者分割问题: 优化作者分割逻辑和分隔符识别',
                'classification_issue_suggestion': '机构信息分类问题: 改进姓名与机构信息的分类规则',
                'continuous_monitoring_suggestion': '持续监控: 建议定期进行验证以确保处理质量',
                'manual_review_suggestion': '人工复核: 对于低置信度案例建议增加人工复核流程',
                'generation_time_label': '报告生成时间:',
                'system_name': 'LLM验证审核系统 - InvisibleResearch项目'
            }

    def calculate_detailed_statistics(self, records: List[ValidationRecord]) -> Dict[str, Any]:
        """计算详细统计信息"""
        completed_records = [r for r in records if r.overall_status is not None]
        
        if not completed_records:
            return {
                'basic_info': {
                    'total_records': len(records),
                    'completed_records': 0,
                    'completion_rate': 0.0
                },
                'overall_accuracy': 0.0,
                'accuracy_by_complexity': {},
                'error_analysis': {}
            }
        
        # 基础信息
        basic_info = {
            'total_records': len(records),
            'completed_records': len(completed_records),
            'completion_rate': len(completed_records) / len(records) if records else 0.0
        }
        
        # 整体准确率
        correct_count = len([r for r in completed_records if r.overall_status == 'correct'])
        overall_accuracy = correct_count / len(completed_records) if completed_records else 0.0
        
        # 按复杂度分析
        complexity_stats = {}
        for record in completed_records:
            complexity = record.complexity_level
            if complexity not in complexity_stats:
                complexity_stats[complexity] = {
                    'total': 0,
                    'correct': 0,
                    'partial': 0,
                    'incorrect': 0,
                    'accuracy': 0.0
                }
            
            complexity_stats[complexity]['total'] += 1
            complexity_stats[complexity][record.overall_status] += 1
            
        # 计算各复杂度准确率
        for complexity in complexity_stats:
            stats = complexity_stats[complexity]
            stats['accuracy'] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0.0
        
        # 错误分析
        error_patterns = {}
        for record in completed_records:
            if record.overall_status in ['partial', 'incorrect']:
                # 这里可以根据具体错误类型进行更详细的分析
                if record.overall_status == 'incorrect':
                    error_patterns['incorrect_identification'] = error_patterns.get('incorrect_identification', 0) + 1
                elif record.overall_status == 'partial':
                    error_patterns['partial_errors'] = error_patterns.get('partial_errors', 0) + 1
        
        return {
            'basic_info': basic_info,
            'overall_accuracy': overall_accuracy,
            'accuracy_by_complexity': complexity_stats,
            'error_analysis': error_patterns
        }

    def create_complexity_chart(self, stats: Dict[str, Any], output_dir: Path, language: str = 'zh') -> str:
        """创建复杂度准确率图表"""
        if not stats['accuracy_by_complexity']:
            return None
        
        complexity_data = stats['accuracy_by_complexity']
        complexities = list(complexity_data.keys())
        accuracies = [complexity_data[c]['accuracy'] for c in complexities]
        
        # 设置图表
        plt.figure(figsize=(10, 6))
        bars = plt.bar(complexities, accuracies, color=['#4CAF50', '#FF9800', '#F44336'])
        
        # 根据语言设置标签
        if language == 'en':
            plt.xlabel('Complexity Level')
            plt.ylabel('Accuracy Rate')
            plt.title('Recognition Accuracy by Complexity Level')
        else:
            plt.xlabel('复杂度等级')
            plt.ylabel('准确率')
            plt.title('按复杂度分类的准确率分析')
        
        plt.ylim(0, 1)
        
        # 添加数值标签
        for bar, accuracy in zip(bars, accuracies):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{accuracy:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # 保存图表
        chart_path = output_dir / f"complexity_accuracy_{language}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(chart_path)

    def generate_csv_report(self, records: List[ValidationRecord], output_path: Path) -> str:
        """生成CSV格式报告"""
        # 准备数据
        data = []
        for record in records:
            data.append({
                'record_id': record.record_id,
                'title': record.title,
                'original_creator': record.original_creator,
                'processed_authors': record.processed_authors,
                'processed_affiliations': '; '.join(record.processed_affiliations) if record.processed_affiliations else '',
                'complexity_level': record.complexity_level,
                'author_count': record.author_count,
                'creator_length': record.creator_length,
                'author_identification_score': record.author_identification_score or '',
                'author_separation_score': record.author_separation_score or '',
                'name_affiliation_score': record.name_affiliation_score or '',
                'name_formatting_score': record.name_formatting_score or '',
                'overall_status': record.overall_status or '',
                'notes': record.notes or '',
                'validator_name': record.validator_name or '',
                'validation_timestamp': record.validation_timestamp or ''
            })
        
        # 创建DataFrame并保存
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        return str(output_path)

    def generate_json_report(self, stats: Dict[str, Any], records: List[ValidationRecord], output_path: Path) -> str:
        """生成JSON格式报告"""
        report_data = {
            'generation_time': datetime.now().isoformat(),
            'summary_statistics': stats,
            'detailed_records': []
        }
        
        # 添加记录详情
        for record in records:
            if record.overall_status is not None:  # 只包含已验证的记录
                report_data['detailed_records'].append({
                    'record_id': record.record_id,
                    'complexity_level': record.complexity_level,
                    'overall_status': record.overall_status,
                    'scores': {
                        'author_identification': record.author_identification_score,
                        'author_separation': record.author_separation_score,
                        'name_affiliation': record.name_affiliation_score,
                        'name_formatting': record.name_formatting_score
                    },
                    'validation_info': {
                        'validator_name': record.validator_name,
                        'validation_timestamp': record.validation_timestamp,
                        'notes': record.notes
                    }
                })
        
        # 保存JSON文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return str(output_path)

    def generate_html_report(self, records: List[ValidationRecord], charts_dir: Path, language: str = 'zh') -> str:
        """生成详细HTML报告"""
        # 计算统计信息
        stats = self.calculate_detailed_statistics(records)
        
        # 创建图表
        chart_files = {}
        complexity_chart = self.create_complexity_chart(stats, charts_dir, language)
        if complexity_chart:
            chart_files['complexity_accuracy'] = complexity_chart
        
        # 根据语言选择不同模板和标题
        if language == 'en':
            lang_attr = "en"
            title = "LLM Named Entity Extraction Validation Report"
        else:
            lang_attr = "zh-CN"
            title = "LLM名称提取验证报告"
        
        # 获取对应语言的模板内容
        template_content = self._get_template_content(language)
        
        # 生成详细HTML报告模板
        html_template = f"""
<!DOCTYPE html>
<html lang="{lang_attr}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; border-left: 4px solid #3498db; padding-left: 10px; }}
        .summary {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin: 20px 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; text-align: center; }}
        .metric {{ padding: 15px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; display: block; }}
        .metric-label {{ font-size: 0.9em; margin-top: 5px; opacity: 0.9; }}
        .chart {{ text-align: center; margin: 20px 0; }}
        .chart img {{ max-width: 100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f8f9fa; }}
        .status-correct {{ color: #27ae60; font-weight: bold; }}
        .status-partial {{ color: #f39c12; font-weight: bold; }}
        .status-incorrect {{ color: #e74c3c; font-weight: bold; }}
        .progress-bar {{ width: 100%; background-color: #ecf0f1; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 20px; background: linear-gradient(90deg, #2ecc71, #27ae60); text-align: center; line-height: 20px; color: white; font-size: 12px; }}
        .error-list {{ background-color: #fdf2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 15px; margin: 10px 0; }}
        .recommendation {{ background-color: #f0f9ff; border: 1px solid #7dd3fc; border-radius: 6px; padding: 15px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{template_content['main_title']}</h1>
        
        <div class="summary">
            <h2 style="color: white; border: none;">{template_content['overview_title']}</h2>
            <div class="metric">
                <span class="metric-value">{{{{ stats.basic_info.total_records }}}}</span>
                <span class="metric-label">{template_content['total_records_label']}</span>
            </div>
            <div class="metric">
                <span class="metric-value">{{{{ stats.basic_info.completed_records }}}}</span>
                <span class="metric-label">{template_content['validated_records_label']}</span>
            </div>
            <div class="metric">
                <span class="metric-value">{{{{ "%.1f%%" | format(stats.basic_info.completion_rate * 100) }}}}</span>
                <span class="metric-label">{template_content['completion_rate_label']}</span>
            </div>
            <div class="metric">
                <span class="metric-value">{{{{ "%.1f%%" | format(stats.overall_accuracy * 100) }}}}</span>
                <span class="metric-label">{template_content['overall_accuracy_label']}</span>
            </div>
        </div>

        {{% if chart_files.complexity_accuracy %}}
        <h2>{template_content['complexity_analysis_title']}</h2>
        <div class="chart">
            <img src="{{{{ chart_files.complexity_accuracy }}}}" alt="Complexity accuracy chart">
        </div>
        {{% endif %}}

        <h2>{template_content['complexity_detail_title']}</h2>
        <table>
            <thead>
                <tr>
                    <th>{template_content['complexity_label']}</th>
                    <th>{template_content['total_label']}</th>
                    <th>{template_content['correct_label']}</th>
                    <th>{template_content['accuracy_label']}</th>
                </tr>
            </thead>
            <tbody>
                {{% for complexity, data in stats.accuracy_by_complexity.items() %}}
                <tr>
                    <td>{{{{ complexity }}}}</td>
                    <td>{{{{ data.total }}}}</td>
                    <td>{{{{ data.correct }}}}</td>
                    <td>{{{{ "%.1f%%" | format(data.accuracy * 100) }}}}</td>
                </tr>
                {{% endfor %}}
            </tbody>
        </table>

        {{% if stats.error_analysis %}}
        <h2>{template_content['error_analysis_title']}</h2>
        <div class="error-list">
            <h3>{template_content['most_common_errors']}</h3>
            <ul>
                {{% for error_type, count in stats.error_analysis.items() %}}
                <li><strong>{{{{ error_type }}}}</strong>: {{{{ count }}}} cases</li>
                {{% endfor %}}
            </ul>
        </div>
        {{% endif %}}

        <h2>{template_content['improvement_suggestions_title']}</h2>
        <div class="recommendation">
            <h3>{template_content['suggestions_intro']}</h3>
            <ul>
                {{% if stats.overall_accuracy < 0.7 %}}
                <li><strong>{template_content['low_accuracy_suggestion']}</strong></li>
                {{% endif %}}
                
                {{% if stats.accuracy_by_complexity.complex and stats.accuracy_by_complexity.simple and stats.accuracy_by_complexity.complex.accuracy < stats.accuracy_by_complexity.simple.accuracy %}}
                <li><strong>{template_content['complex_cases_suggestion']}</strong></li>
                {{% endif %}}
                
                {{% if stats.error_analysis.get('incorrect_separation', 0) > 5 %}}
                <li><strong>{template_content['separation_issue_suggestion']}</strong></li>
                {{% endif %}}
                
                {{% if stats.error_analysis.get('misclassified_affiliation', 0) > 5 %}}
                <li><strong>{template_content['classification_issue_suggestion']}</strong></li>
                {{% endif %}}
                
                <li><strong>{template_content['continuous_monitoring_suggestion']}</strong></li>
                <li><strong>{template_content['manual_review_suggestion']}</strong></li>
            </ul>
        </div>

        <div style="margin-top: 30px; text-align: center; color: #7f8c8d; font-size: 0.9em;">
            <p>{template_content['generation_time_label']} {{{{ generation_time }}}}</p>
            <p>{template_content['system_name']}</p>
        </div>
    </div>
</body>
</html>
        """
        
        # 渲染模板
        template = Template(html_template)
        html_content = template.render(
            stats=stats,
            chart_files=chart_files,
            generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # 写入文件
        output_path = charts_dir.parent / f"validation_report_{language}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)

    def generate_all_reports(self, records: List[ValidationRecord], output_dir: Path, language: str = 'zh'):
        """生成所有格式的报告"""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts_dir = output_dir / "charts"
        charts_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report_files = {}
        
        # 生成详细HTML报告
        html_path = self.generate_html_report(records, charts_dir, language)
        report_files['html'] = html_path
        
        # 生成CSV数据报告
        csv_path = output_dir / f"validation_data_{language}_{timestamp}.csv"
        self.generate_csv_report(records, csv_path)
        report_files['csv'] = str(csv_path)
        
        # 生成JSON摘要报告
        stats = self.calculate_detailed_statistics(records)
        json_path = output_dir / f"validation_summary_{language}_{timestamp}.json"
        self.generate_json_report(stats, records, json_path)
        report_files['json'] = str(json_path)
        
        return report_files


def main():
    """测试报告生成功能"""
    try:
        from data_manager import DataManager
    except ImportError:
        from .data_manager import DataManager
    
    # 创建测试数据
    dm = DataManager()
    records = dm.prepare_validation_records()[:10]  # 使用前10条记录进行测试
    
    # 模拟一些验证结果
    for i, record in enumerate(records):
        record.validator_name = "test_user"
        record.validation_timestamp = datetime.now().isoformat()
        record.author_identification_score = 4 if i % 3 != 0 else 3
        record.author_separation_score = 5 if i % 2 == 0 else 4
        record.name_affiliation_score = 4
        record.name_formatting_score = 3 if i % 4 == 0 else 4
        record.overall_status = "correct" if i % 3 != 0 else "partial" if i % 5 != 0 else "incorrect"
        record.notes = f"测试验证记录 {i+1}"
    
    # 生成报告
    generator = ReportGenerator()
    output_dir = Path("data/validation/test_reports")
    
    print("📊 生成中文测试报告...")
    report_files_zh = generator.generate_all_reports(records, output_dir, 'zh')
    
    print("📊 生成英文测试报告...")
    report_files_en = generator.generate_all_reports(records, output_dir, 'en')
    
    print("✅ 报告生成完成:")
    print("中文报告:")
    for format_type, file_path in report_files_zh.items():
        print(f"  {format_type.upper()}: {file_path}")
    
    print("英文报告:")
    for format_type, file_path in report_files_en.items():
        print(f"  {format_type.upper()}: {file_path}")


if __name__ == "__main__":
    main()