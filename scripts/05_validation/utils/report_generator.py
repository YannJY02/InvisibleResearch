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
        
        # 设置中文字体（如果需要）
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
    
    def calculate_detailed_statistics(self, records: List[ValidationRecord]) -> Dict[str, Any]:
        """计算详细统计信息"""
        completed_records = [r for r in records if r.overall_status is not None]
        
        if not completed_records:
            return {
                'total_records': len(records),
                'completed_records': 0,
                'completion_rate': 0.0,
                'overall_accuracy': 0.0,
                'statistics': {}
            }
        
        stats = {
            'basic_info': {
                'total_records': len(records),
                'completed_records': len(completed_records),
                'completion_rate': len(completed_records) / len(records),
                'validation_period': {
                    'start': min([r.validation_timestamp for r in completed_records if r.validation_timestamp]),
                    'end': max([r.validation_timestamp for r in completed_records if r.validation_timestamp])
                }
            },
            
            'accuracy_by_complexity': {},
            'accuracy_by_author_count': {},
            'score_distributions': {},
            'error_analysis': {},
            'validator_performance': {}
        }
        
        # 按复杂度分析
        for complexity in ['simple', 'medium', 'complex']:
            complexity_records = [r for r in completed_records if r.complexity_level == complexity]
            if complexity_records:
                correct_count = len([r for r in complexity_records if r.overall_status == 'correct'])
                partial_count = len([r for r in complexity_records if r.overall_status == 'partial'])
                incorrect_count = len([r for r in complexity_records if r.overall_status == 'incorrect'])
                
                stats['accuracy_by_complexity'][complexity] = {
                    'total': len(complexity_records),
                    'correct': correct_count,
                    'partial': partial_count,
                    'incorrect': incorrect_count,
                    'accuracy': correct_count / len(complexity_records),
                    'success_rate': (correct_count + partial_count) / len(complexity_records)
                }
        
        # 按作者数量分析
        author_count_groups = {}
        for record in completed_records:
            count = record.author_count
            group = '1' if count == 1 else '2-3' if count <= 3 else '4-5' if count <= 5 else '6+'
            if group not in author_count_groups:
                author_count_groups[group] = []
            author_count_groups[group].append(record)
        
        for group, group_records in author_count_groups.items():
            correct_count = len([r for r in group_records if r.overall_status == 'correct'])
            stats['accuracy_by_author_count'][group] = {
                'total': len(group_records),
                'correct': correct_count,
                'accuracy': correct_count / len(group_records)
            }
        
        # 评分分布
        score_fields = [
            'author_identification_score',
            'author_separation_score', 
            'name_affiliation_score',
            'name_formatting_score'
        ]
        
        for field in score_fields:
            scores = [getattr(r, field) for r in completed_records if getattr(r, field) is not None]
            if scores:
                stats['score_distributions'][field] = {
                    'mean': sum(scores) / len(scores),
                    'min': min(scores),
                    'max': max(scores),
                    'distribution': {str(i): scores.count(i) for i in range(1, 6)}
                }
        
        # 错误分析
        incorrect_records = [r for r in completed_records if r.overall_status == 'incorrect']
        error_patterns = {}
        
        for record in incorrect_records:
            if record.notes:
                # 简单的错误模式分析
                if '重复姓名' in record.notes:
                    error_patterns['duplicate_names'] = error_patterns.get('duplicate_names', 0) + 1
                if '机构信息' in record.notes:
                    error_patterns['misclassified_affiliation'] = error_patterns.get('misclassified_affiliation', 0) + 1
                if '分割数量' in record.notes:
                    error_patterns['incorrect_separation'] = error_patterns.get('incorrect_separation', 0) + 1
                if '格式' in record.notes:
                    error_patterns['formatting_issues'] = error_patterns.get('formatting_issues', 0) + 1
        
        stats['error_analysis'] = error_patterns
        
        # 验证者性能分析
        validator_groups = {}
        for record in completed_records:
            validator = record.validator_name or 'unknown'
            if validator not in validator_groups:
                validator_groups[validator] = []
            validator_groups[validator].append(record)
        
        for validator, validator_records in validator_groups.items():
            correct_count = len([r for r in validator_records if r.overall_status == 'correct'])
            stats['validator_performance'][validator] = {
                'total': len(validator_records),
                'correct': correct_count,
                'accuracy': correct_count / len(validator_records)
            }
        
        # 计算整体准确率
        total_correct = len([r for r in completed_records if r.overall_status == 'correct'])
        stats['overall_accuracy'] = total_correct / len(completed_records)
        
        return stats
    
    def generate_charts(self, stats: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        """生成图表并返回文件路径"""
        chart_files = {}
        
        if not self.report_settings.get('include_charts', True):
            return chart_files
        
        # 1. 复杂度准确率图表
        if stats['accuracy_by_complexity']:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            complexities = list(stats['accuracy_by_complexity'].keys())
            accuracies = [stats['accuracy_by_complexity'][c]['accuracy'] for c in complexities]
            totals = [stats['accuracy_by_complexity'][c]['total'] for c in complexities]
            
            bars = ax.bar(complexities, accuracies, color=['#2E8B57', '#4682B4', '#DC143C'])
            ax.set_ylabel('准确率')
            ax.set_title('按复杂度分类的准确率分析')
            ax.set_ylim(0, 1)
            
            # 添加数据标签
            for i, (bar, total) in enumerate(zip(bars, totals)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{height:.2%}\n(n={total})',
                       ha='center', va='bottom')
            
            chart_path = output_dir / 'complexity_accuracy.png'
            plt.tight_layout()
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            chart_files['complexity_accuracy'] = str(chart_path)
        
        # 2. 评分分布图表
        if stats['score_distributions']:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            axes = axes.flatten()
            
            score_fields = [
                ('author_identification_score', '作者识别'),
                ('author_separation_score', '分割准确性'),
                ('name_affiliation_score', '分类准确性'),
                ('name_formatting_score', '格式质量')
            ]
            
            for i, (field, title) in enumerate(score_fields):
                if field in stats['score_distributions']:
                    distribution = stats['score_distributions'][field]['distribution']
                    scores = list(range(1, 6))
                    counts = [int(distribution.get(str(s), 0)) for s in scores]
                    
                    axes[i].bar(scores, counts, color='skyblue', alpha=0.7)
                    axes[i].set_title(f'{title}评分分布')
                    axes[i].set_xlabel('评分')
                    axes[i].set_ylabel('记录数')
                    axes[i].set_xticks(scores)
                    
                    # 添加平均分标线
                    mean_score = stats['score_distributions'][field]['mean']
                    axes[i].axvline(mean_score, color='red', linestyle='--', 
                                   label=f'平均分: {mean_score:.2f}')
                    axes[i].legend()
            
            chart_path = output_dir / 'score_distributions.png'
            plt.tight_layout()
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            chart_files['score_distributions'] = str(chart_path)
        
        # 3. 错误类型分析
        if stats['error_analysis']:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            error_types = list(stats['error_analysis'].keys())
            error_counts = list(stats['error_analysis'].values())
            
            bars = ax.barh(error_types, error_counts, color='lightcoral')
            ax.set_xlabel('错误数量')
            ax.set_title('常见错误类型分析')
            
            # 添加数据标签
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                       f'{int(width)}',
                       ha='left', va='center')
            
            chart_path = output_dir / 'error_analysis.png'
            plt.tight_layout()
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            chart_files['error_analysis'] = str(chart_path)
        
        return chart_files
    
    def generate_html_report(self, records: List[ValidationRecord], 
                           output_path: Path) -> str:
        """生成HTML格式的详细报告"""
        
        # 计算统计信息
        stats = self.calculate_detailed_statistics(records)
        
        # 创建图表
        chart_dir = output_path.parent / 'charts'
        chart_dir.mkdir(exist_ok=True)
        chart_files = self.generate_charts(stats, chart_dir)
        
        # HTML模板
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM名称提取验证报告</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; border-left: 4px solid #3498db; padding-left: 10px; }
        .summary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .metric { display: inline-block; margin: 10px 20px; text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; display: block; }
        .metric-label { font-size: 0.9em; opacity: 0.9; }
        .chart { text-align: center; margin: 20px 0; }
        .chart img { max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 8px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #3498db; color: white; }
        tr:nth-child(even) { background-color: #f8f9fa; }
        .status-correct { color: #27ae60; font-weight: bold; }
        .status-partial { color: #f39c12; font-weight: bold; }
        .status-incorrect { color: #e74c3c; font-weight: bold; }
        .progress-bar { width: 100%; background-color: #ecf0f1; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 20px; background: linear-gradient(90deg, #2ecc71, #27ae60); text-align: center; line-height: 20px; color: white; font-size: 12px; }
        .error-list { background-color: #fdf2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 15px; margin: 10px 0; }
        .recommendation { background-color: #f0f9ff; border: 1px solid #7dd3fc; border-radius: 6px; padding: 15px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 LLM名称提取验证报告</h1>
        
        <div class="summary">
            <h2 style="color: white; border: none;">📊 总体概览</h2>
            <div class="metric">
                <span class="metric-value">{{ stats.basic_info.total_records }}</span>
                <span class="metric-label">总记录数</span>
            </div>
            <div class="metric">
                <span class="metric-value">{{ stats.basic_info.completed_records }}</span>
                <span class="metric-label">已验证记录</span>
            </div>
            <div class="metric">
                <span class="metric-value">{{ "%.1f%%" | format(stats.basic_info.completion_rate * 100) }}</span>
                <span class="metric-label">完成率</span>
            </div>
            <div class="metric">
                <span class="metric-value">{{ "%.1f%%" | format(stats.overall_accuracy * 100) }}</span>
                <span class="metric-label">整体准确率</span>
            </div>
        </div>

        {% if chart_files.complexity_accuracy %}
        <h2>📈 按复杂度分类的准确率分析</h2>
        <div class="chart">
            <img src="{{ chart_files.complexity_accuracy }}" alt="复杂度准确率图表">
        </div>
        {% endif %}

        <h2>📋 复杂度详细统计</h2>
        <table>
            <thead>
                <tr>
                    <th>复杂度</th>
                    <th>总数</th>
                    <th>正确</th>
                    <th>部分正确</th>
                    <th>错误</th>
                    <th>准确率</th>
                    <th>成功率</th>
                </tr>
            </thead>
            <tbody>
                {% for complexity, data in stats.accuracy_by_complexity.items() %}
                <tr>
                    <td>{{ complexity.title() }}</td>
                    <td>{{ data.total }}</td>
                    <td class="status-correct">{{ data.correct }}</td>
                    <td class="status-partial">{{ data.partial }}</td>
                    <td class="status-incorrect">{{ data.incorrect }}</td>
                    <td>{{ "%.1f%%" | format(data.accuracy * 100) }}</td>
                    <td>{{ "%.1f%%" | format(data.success_rate * 100) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        {% if chart_files.score_distributions %}
        <h2>📊 评分分布分析</h2>
        <div class="chart">
            <img src="{{ chart_files.score_distributions }}" alt="评分分布图表">
        </div>
        {% endif %}

        <h2>🎯 各维度评分统计</h2>
        <table>
            <thead>
                <tr>
                    <th>评估维度</th>
                    <th>平均分</th>
                    <th>最低分</th>
                    <th>最高分</th>
                    <th>分布</th>
                </tr>
            </thead>
            <tbody>
                {% for field, data in stats.score_distributions.items() %}
                <tr>
                    <td>
                        {% if field == 'author_identification_score' %}作者识别
                        {% elif field == 'author_separation_score' %}分割准确性
                        {% elif field == 'name_affiliation_score' %}分类准确性
                        {% elif field == 'name_formatting_score' %}格式质量
                        {% endif %}
                    </td>
                    <td>{{ "%.2f" | format(data.mean) }}</td>
                    <td>{{ data.min }}</td>
                    <td>{{ data.max }}</td>
                    <td>
                        {% for score in range(1, 6) %}
                            {{ score }}分:{{ data.distribution[score|string] or 0 }}{% if not loop.last %}, {% endif %}
                        {% endfor %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        {% if stats.error_analysis %}
        <h2>⚠️ 错误类型分析</h2>
        {% if chart_files.error_analysis %}
        <div class="chart">
            <img src="{{ chart_files.error_analysis }}" alt="错误分析图表">
        </div>
        {% endif %}
        <div class="error-list">
            <h3>常见错误模式:</h3>
            <ul>
                {% for error_type, count in stats.error_analysis.items() %}
                <li><strong>{{ error_type.replace('_', ' ').title() }}</strong>: {{ count }} 次</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}

        {% if stats.validator_performance %}
        <h2>👥 验证者性能</h2>
        <table>
            <thead>
                <tr>
                    <th>验证者</th>
                    <th>验证数量</th>
                    <th>正确数量</th>
                    <th>准确率</th>
                </tr>
            </thead>
            <tbody>
                {% for validator, data in stats.validator_performance.items() %}
                <tr>
                    <td>{{ validator }}</td>
                    <td>{{ data.total }}</td>
                    <td>{{ data.correct }}</td>
                    <td>{{ "%.1f%%" | format(data.accuracy * 100) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}

        <h2>💡 改进建议</h2>
        <div class="recommendation">
            <h3>基于分析结果的建议:</h3>
            <ul>
                {% if stats.overall_accuracy < 0.7 %}
                <li><strong>整体准确率偏低</strong>: 建议重新审视LLM提示词和处理逻辑</li>
                {% endif %}
                
                {% if stats.accuracy_by_complexity.complex.accuracy < stats.accuracy_by_complexity.simple.accuracy %}
                <li><strong>复杂案例处理能力不足</strong>: 需要针对复杂案例优化算法</li>
                {% endif %}
                
                {% if stats.error_analysis.get('incorrect_separation', 0) > 5 %}
                <li><strong>多作者分割问题</strong>: 优化作者分割逻辑和分隔符识别</li>
                {% endif %}
                
                {% if stats.error_analysis.get('misclassified_affiliation', 0) > 5 %}
                <li><strong>机构信息分类问题</strong>: 改进姓名与机构信息的分类规则</li>
                {% endif %}
                
                <li><strong>持续监控</strong>: 建议定期进行验证以确保处理质量</li>
                <li><strong>人工复核</strong>: 对于低置信度案例建议增加人工复核流程</li>
            </ul>
        </div>

        <div style="margin-top: 30px; text-align: center; color: #7f8c8d; font-size: 0.9em;">
            <p>报告生成时间: {{ generation_time }}</p>
            <p>LLM验证审核系统 - InvisibleResearch项目</p>
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
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)
    
    def generate_csv_report(self, records: List[ValidationRecord], 
                           output_path: Path) -> str:
        """生成CSV格式的详细数据报告"""
        
        # 准备数据
        data = []
        for record in records:
            row = {
                'record_id': record.record_id,
                'title': record.title,
                'original_creator': record.original_creator,
                'processed_authors': record.processed_authors,
                'processed_affiliations': str(record.processed_affiliations),
                'complexity_level': record.complexity_level,
                'author_count': record.author_count,
                'creator_length': record.creator_length,
                'validator_name': record.validator_name,
                'validation_timestamp': record.validation_timestamp,
                'author_identification_score': record.author_identification_score,
                'author_separation_score': record.author_separation_score,
                'name_affiliation_score': record.name_affiliation_score,
                'name_formatting_score': record.name_formatting_score,
                'overall_status': record.overall_status,
                'notes': record.notes,
                'external_verification': str(record.external_verification) if record.external_verification else ''
            }
            data.append(row)
        
        # 创建DataFrame并保存
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        return str(output_path)
    
    def generate_summary_json(self, records: List[ValidationRecord], 
                             output_path: Path) -> str:
        """生成JSON格式的汇总报告"""
        
        stats = self.calculate_detailed_statistics(records)
        
        # 添加元数据
        summary = {
            'report_metadata': {
                'generation_time': datetime.now().isoformat(),
                'total_records': len(records),
                'completed_records': len([r for r in records if r.overall_status is not None]),
                'report_version': '1.0'
            },
            'statistics': stats
        }
        
        # 写入JSON文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        return str(output_path)
    
    def generate_all_reports(self, records: List[ValidationRecord], 
                           output_dir: Path) -> Dict[str, str]:
        """生成所有格式的报告"""
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_files = {}
        
        # HTML报告
        if 'html' in self.report_settings['formats']:
            html_path = output_dir / f'validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            report_files['html'] = self.generate_html_report(records, html_path)
        
        # CSV报告
        if 'csv' in self.report_settings['formats']:
            csv_path = output_dir / f'validation_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            report_files['csv'] = self.generate_csv_report(records, csv_path)
        
        # JSON报告
        if 'json' in self.report_settings['formats']:
            json_path = output_dir / f'validation_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            report_files['json'] = self.generate_summary_json(records, json_path)
        
        return report_files


def main():
    """测试报告生成器"""
    try:
        from .data_manager import DataManager
    except ImportError:
        from data_manager import DataManager
    
    # 准备测试数据
    dm = DataManager()
    records = dm.prepare_validation_records()[:10]  # 取前10条记录
    
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
    
    print("📊 生成测试报告...")
    report_files = generator.generate_all_reports(records, output_dir)
    
    print("✅ 报告生成完成:")
    for format_type, file_path in report_files.items():
        print(f"  {format_type.upper()}: {file_path}")


if __name__ == "__main__":
    main()
