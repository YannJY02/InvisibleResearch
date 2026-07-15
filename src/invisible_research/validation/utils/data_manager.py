#!/usr/bin/env python3
"""
数据管理模块 - LLM验证审核系统
Data Manager Module for LLM Validation Suite

负责数据加载、分层抽样、进度管理等功能
"""

import os
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import yaml
import numpy as np

from ...data import resolve_data_root
from .. import DEFAULT_CONFIG_PATH


@dataclass
class ValidationRecord:
    """验证记录数据结构"""
    record_id: str
    title: str
    original_creator: str
    processed_authors: str
    processed_affiliations: List[str]
    complexity_level: str
    author_count: int
    creator_length: int
    
    # 验证结果
    validator_name: Optional[str] = None
    validation_timestamp: Optional[str] = None
    author_identification_score: Optional[int] = None
    author_separation_score: Optional[int] = None
    name_affiliation_score: Optional[int] = None
    name_formatting_score: Optional[int] = None
    overall_status: Optional[str] = None  # "correct", "incorrect", "partial"
    notes: Optional[str] = None
    external_verification: Optional[Dict] = None


class DataManager:
    """数据管理器类"""
    
    def __init__(self, config_path: str | Path | None = None):
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
            
        self.config = self._load_config()
        data_root = resolve_data_root()
        self.data_paths = {
            name: str(data_root.joinpath(*Path(value).parts[1:]))
            if Path(value).parts[:1] == ("data",)
            else value
            for name, value in self.config['data_paths'].items()
        }
        
        # 确保数据目录存在
        Path(self.data_paths['validation_results']).parent.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self) -> Dict:
        """加载配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def load_source_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        加载源数据
        返回: (输入数据DataFrame, 输出数据DataFrame)
        """
        input_df = pq.read_table(self.data_paths['input_file']).to_pandas()
        output_df = pq.read_table(self.data_paths['output_file']).to_pandas()
        
        return input_df, output_df
    
    def _classify_complexity(self, record: Dict) -> str:
        """根据配置标准分类复杂度"""
        criteria = self.config['complexity_criteria']
        
        # 处理可能的列名后缀
        creator_key = 'creator_input' if 'creator_input' in record else 'creator'
        count_key = 'creator_count_input' if 'creator_count_input' in record else 'creator_count'
        affil_key = 'affiliations' if 'affiliations' in record else []
        
        creator_length = len(str(record[creator_key]))
        author_count = record[count_key]
        has_affiliations = len(record.get(affil_key, [])) > 0
        
        # 检查是否为简单案例
        simple = criteria['simple']
        if (creator_length <= simple['max_length'] and 
            author_count <= simple['max_authors'] and
            has_affiliations == simple['has_affiliations']):
            return 'simple'
        
        # 检查是否为中等复杂案例
        medium = criteria['medium']
        if (creator_length <= medium['max_length'] and 
            author_count <= medium['max_authors']):
            return 'medium'
        
        return 'complex'
    
    def prepare_validation_records(self) -> List[ValidationRecord]:
        """准备验证记录列表"""
        input_df, output_df = self.load_source_data()
        
        # 合并数据
        merged_df = pd.merge(input_df, output_df, on='id', suffixes=('_input', '_output'))
        
        records = []
        for _, row in merged_df.iterrows():
            complexity = self._classify_complexity(row)
            
            # 处理可能的列名变化
            title_key = 'title_input' if 'title_input' in merged_df.columns else 'title'
            creator_input_key = 'creator_input' if 'creator_input' in merged_df.columns else 'creator'
            count_input_key = 'creator_count_input' if 'creator_count_input' in merged_df.columns else 'creator_count'
            
            record = ValidationRecord(
                record_id=str(row['id']),
                title=str(row[title_key]),
                original_creator=str(row[creator_input_key]),
                processed_authors=str(row['authors_clean']),
                processed_affiliations=row['affiliations'] if isinstance(row['affiliations'], list) else [],
                complexity_level=complexity,
                author_count=int(row[count_input_key]),
                creator_length=len(str(row[creator_input_key]))
            )
            records.append(record)
        
        return records
    
    def stratified_sampling(self, records: List[ValidationRecord]) -> List[ValidationRecord]:
        """分层抽样"""
        sampling_config = self.config['validation_modes']['stratified_sampling']
        
        if not sampling_config['enabled']:
            return records
        
        # 按复杂度分组
        groups = {'simple': [], 'medium': [], 'complex': []}
        for record in records:
            groups[record.complexity_level].append(record)
        
        # 从每组抽样
        sampled_records = []
        sample_sizes = {
            'simple': sampling_config['simple_sample_size'],
            'medium': sampling_config['medium_sample_size'],
            'complex': sampling_config['complex_sample_size']
        }
        
        for complexity, group_records in groups.items():
            sample_size = min(sample_sizes[complexity], len(group_records))
            if sample_size > 0:
                sampled = random.sample(group_records, sample_size)
                sampled_records.extend(sampled)
        
        return sampled_records
    
    def get_targeted_records(self, records: List[ValidationRecord]) -> List[ValidationRecord]:
        """获取专项审核记录"""
        targeted_config = self.config['validation_modes']['targeted_audit']
        targeted_records = []
        
        for record in records:
            # 多作者案例
            if (targeted_config['multi_author_cases'] and 
                ';' in record.processed_authors):
                targeted_records.append(record)
                continue
            
            # 包含机构信息案例
            if (targeted_config['affiliation_cases'] and 
                len(record.processed_affiliations) > 0):
                targeted_records.append(record)
                continue
            
            # 疑似错误案例（启发式规则）
            if targeted_config['error_prone_cases']:
                # 检查明显的错误模式
                if ('*' in record.processed_authors or
                    record.processed_authors.strip() == '' or
                    len(record.processed_authors.split(';')) != record.author_count):
                    targeted_records.append(record)
        
        return targeted_records
    
    def load_validation_progress(self) -> Dict[str, ValidationRecord]:
        """加载验证进度"""
        progress_file = Path(self.data_paths['validation_progress'])
        
        if not progress_file.exists():
            return {}
        
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
            
            # 转换为ValidationRecord对象
            progress = {}
            for record_id, data in progress_data.items():
                # 处理datetime字段
                if data.get('validation_timestamp'):
                    data['validation_timestamp'] = data['validation_timestamp']
                
                # 处理列表字段
                if not isinstance(data.get('processed_affiliations'), list):
                    data['processed_affiliations'] = []
                
                progress[record_id] = ValidationRecord(**data)
            
            return progress
            
        except Exception as e:
            print(f"⚠️ 加载进度文件失败: {e}")
            return {}
    
    def save_validation_progress(self, progress: Dict[str, ValidationRecord]) -> None:
        """保存验证进度（带数据保护）"""
        from .data_protection import create_protection_manager
        
        # 转换为可序列化的字典
        serializable_progress = {}
        for record_id, record in progress.items():
            serializable_progress[record_id] = asdict(record)
        
        try:
            # 使用数据保护管理器安全保存
            protection = create_protection_manager()
            success = protection.safe_save(serializable_progress)
            
            if success:
                print(f"✅ 验证进度已安全保存 (记录数: {len(serializable_progress)})")
            else:
                print(f"⚠️ 安全保存失败，尝试直接保存...")
                # 回退到直接保存
                progress_file = Path(self.data_paths['validation_progress'])
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(serializable_progress, f, ensure_ascii=False, indent=2)
                print(f"✅ 验证进度已直接保存 (记录数: {len(serializable_progress)})")
                
        except Exception as e:
            print(f"⚠️ 保存进度文件失败: {e}")
            raise
    
    def save_validation_results(self, records: List[ValidationRecord]) -> None:
        """保存最终验证结果到Parquet文件"""
        # 转换为DataFrame
        data = [asdict(record) for record in records]
        df = pd.DataFrame(data)
        
        # 保存为Parquet
        results_file = Path(self.data_paths['validation_results'])
        pq.write_table(pa.Table.from_pandas(df), results_file)
        
        print(f"✅ 验证结果已保存到: {results_file}")
    
    def get_validation_statistics(self, records: List[ValidationRecord]) -> Dict:
        """计算验证统计信息"""
        completed_records = [r for r in records if r.overall_status is not None]
        
        if not completed_records:
            return {
                'total_records': len(records),
                'completed_records': 0,
                'completion_rate': 0.0,
                'accuracy_by_complexity': {},
                'overall_accuracy': 0.0
            }
        
        # 按复杂度统计准确率
        accuracy_by_complexity = {}
        for complexity in ['simple', 'medium', 'complex']:
            complexity_records = [r for r in completed_records if r.complexity_level == complexity]
            if complexity_records:
                correct_count = len([r for r in complexity_records if r.overall_status == 'correct'])
                accuracy_by_complexity[complexity] = {
                    'total': len(complexity_records),
                    'correct': correct_count,
                    'accuracy': correct_count / len(complexity_records)
                }
        
        # 整体准确率
        total_correct = len([r for r in completed_records if r.overall_status == 'correct'])
        overall_accuracy = total_correct / len(completed_records)
        
        return {
            'total_records': len(records),
            'completed_records': len(completed_records),
            'completion_rate': len(completed_records) / len(records),
            'accuracy_by_complexity': accuracy_by_complexity,
            'overall_accuracy': overall_accuracy,
            'status_distribution': {
                'correct': len([r for r in completed_records if r.overall_status == 'correct']),
                'incorrect': len([r for r in completed_records if r.overall_status == 'incorrect']),
                'partial': len([r for r in completed_records if r.overall_status == 'partial'])
            }
        }


def main():
    """测试数据管理器功能"""
    dm = DataManager()
    
    print("🔄 加载源数据...")
    input_df, output_df = dm.load_source_data()
    print(f"✅ 输入数据: {len(input_df)} 条记录")
    print(f"✅ 输出数据: {len(output_df)} 条记录")
    
    print("\n🔄 准备验证记录...")
    records = dm.prepare_validation_records()
    print(f"✅ 准备完成: {len(records)} 条记录")
    
    # 显示复杂度分布
    complexity_dist = {}
    for record in records:
        complexity_dist[record.complexity_level] = complexity_dist.get(record.complexity_level, 0) + 1
    
    print(f"\n📊 复杂度分布:")
    for complexity, count in complexity_dist.items():
        print(f"  {complexity}: {count} 条")
    
    print("\n🔄 分层抽样测试...")
    sampled = dm.stratified_sampling(records)
    print(f"✅ 抽样结果: {len(sampled)} 条记录")
    
    print("\n🔄 专项审核测试...")
    targeted = dm.get_targeted_records(records)
    print(f"✅ 专项审核: {len(targeted)} 条记录")


if __name__ == "__main__":
    main()
