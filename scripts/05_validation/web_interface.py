#!/usr/bin/env python3
"""
Streamlit Web界面 - LLM验证审核系统
Streamlit Web Interface for LLM Validation Suite

提供用户友好的Web界面进行人工审核
"""

import os
import sys
from pathlib import Path
import time
from typing import Dict, List, Optional

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir / "utils"))

from utils.data_manager import ValidationRecord, DataManager
from utils.search_tools import ExternalValidator
from llm_validator import LLMValidator
from utils.report_generator import ReportGenerator


class ValidationApp:
    """验证应用主类"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.external_validator = ExternalValidator()
        self.llm_validator = LLMValidator()
        self.report_generator = ReportGenerator()
        
        # 初始化session state
        if 'records' not in st.session_state:
            st.session_state.records = []
        if 'current_index' not in st.session_state:
            st.session_state.current_index = 0
        if 'validation_progress' not in st.session_state:
            st.session_state.validation_progress = {}
        if 'validator_name' not in st.session_state:
            st.session_state.validator_name = "anonymous"
        if 'last_save_time' not in st.session_state:
            st.session_state.last_save_time = time.time()
    
    def load_data(self):
        """加载数据"""
        if not st.session_state.records:
            with st.spinner("🔄 加载数据中..."):
                # 准备验证记录
                records = self.data_manager.prepare_validation_records()
                
                # 加载之前的进度
                progress = self.data_manager.load_validation_progress()
                
                # 更新记录状态
                for record in records:
                    if record.record_id in progress:
                        saved_record = progress[record.record_id]
                        # 复制验证结果
                        record.validator_name = saved_record.validator_name
                        record.validation_timestamp = saved_record.validation_timestamp
                        record.author_identification_score = saved_record.author_identification_score
                        record.author_separation_score = saved_record.author_separation_score
                        record.name_affiliation_score = saved_record.name_affiliation_score
                        record.name_formatting_score = saved_record.name_formatting_score
                        record.overall_status = saved_record.overall_status
                        record.notes = saved_record.notes
                        record.external_verification = saved_record.external_verification
                
                st.session_state.records = records
                st.session_state.validation_progress = {r.record_id: r for r in records}
                
                st.success(f"✅ 已加载 {len(records)} 条记录")
    
    def save_progress(self):
        """保存进度"""
        try:
            self.data_manager.save_validation_progress(st.session_state.validation_progress)
            st.session_state.last_save_time = time.time()
            return True
        except Exception as e:
            st.error(f"保存失败: {e}")
            return False
    
    def auto_save(self):
        """自动保存（每30秒）"""
        current_time = time.time()
        if current_time - st.session_state.last_save_time > 30:
            self.save_progress()
    
    def render_sidebar(self):
        """渲染侧边栏"""
        st.sidebar.title("🔍 LLM验证系统")
        
        # 验证者信息
        st.sidebar.subheader("验证者信息")
        validator_name = st.sidebar.text_input("验证者姓名", value=st.session_state.validator_name)
        if validator_name != st.session_state.validator_name:
            st.session_state.validator_name = validator_name
        
        st.sidebar.divider()
        
        # 导航控制
        st.sidebar.subheader("导航控制")
        
        if st.session_state.records:
            total_records = len(st.session_state.records)
            current_index = st.session_state.current_index
            
            # 显示进度
            completed_count = len([r for r in st.session_state.records if r.overall_status is not None])
            progress_percentage = completed_count / total_records if total_records > 0 else 0
            
            st.sidebar.metric("总记录数", total_records)
            st.sidebar.metric("已完成", f"{completed_count} ({progress_percentage:.1%})")
            
            # 进度条
            st.sidebar.progress(progress_percentage)
            
            # 导航按钮
            st.sidebar.write("**导航按钮**")
            col1, col2 = st.sidebar.columns([1, 1])
            
            with col1:
                if st.button("⬅️ 上一条", disabled=current_index <= 0, key="nav_prev", use_container_width=True):
                    st.session_state.current_index = max(0, current_index - 1)
                    st.rerun()
            
            with col2:
                if st.button("➡️ 下一条", disabled=current_index >= total_records - 1, key="nav_next", use_container_width=True):
                    st.session_state.current_index = min(total_records - 1, current_index + 1)
                    st.rerun()
            
            # 跳转到指定记录
            jump_to = st.sidebar.number_input("跳转到记录", min_value=1, max_value=total_records, value=current_index + 1, key="jump_to_input")
            if st.sidebar.button("跳转", key="jump_to_btn"):
                st.session_state.current_index = jump_to - 1
                st.rerun()
            
            # 筛选选项
            st.sidebar.subheader("筛选选项")
            filter_status = st.sidebar.selectbox(
                "筛选状态",
                ["全部", "未完成", "已完成", "正确", "部分正确", "错误"],
                key="filter_status_select"
            )
            
            filter_complexity = st.sidebar.selectbox(
                "筛选复杂度",
                ["全部", "simple", "medium", "complex"],
                key="filter_complexity_select"
            )
            
            # 应用筛选
            if st.sidebar.button("应用筛选", key="apply_filter_btn"):
                self.apply_filters(filter_status, filter_complexity)
        else:
            st.sidebar.info("数据加载完成后将显示导航控制")
        
        st.sidebar.divider()
        
        # 操作按钮
        st.sidebar.subheader("操作")
        
        if st.sidebar.button("💾 手动保存", key="manual_save_btn"):
            if self.save_progress():
                st.sidebar.success("保存成功!")
        
        if st.sidebar.button("📊 生成报告", key="generate_report_btn"):
            self.generate_report()
        
        if st.sidebar.button("🔄 重新加载", key="reload_data_btn"):
            st.session_state.records = []
            st.session_state.validation_progress = {}
            st.rerun()
    
    def apply_filters(self, status_filter: str, complexity_filter: str):
        """应用筛选条件"""
        filtered_records = []
        
        for record in st.session_state.records:
            # 状态筛选
            if status_filter == "未完成" and record.overall_status is not None:
                continue
            elif status_filter == "已完成" and record.overall_status is None:
                continue
            elif status_filter == "正确" and record.overall_status != "correct":
                continue
            elif status_filter == "部分正确" and record.overall_status != "partial":
                continue
            elif status_filter == "错误" and record.overall_status != "incorrect":
                continue
            
            # 复杂度筛选
            if complexity_filter != "全部" and record.complexity_level != complexity_filter:
                continue
            
            filtered_records.append(record)
        
        if filtered_records:
            # 找到第一个符合条件的记录的索引
            original_records = st.session_state.records
            for i, record in enumerate(original_records):
                if record.record_id == filtered_records[0].record_id:
                    st.session_state.current_index = i
                    break
            st.rerun()
        else:
            st.sidebar.warning("没有找到符合条件的记录")
    
    def render_record_display(self, record: ValidationRecord):
        """渲染记录显示"""
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("📝 记录信息")
            
            # 基本信息
            st.write(f"**记录ID**: {record.record_id}")
            st.write(f"**复杂度**: {record.complexity_level}")
            st.write(f"**作者数量**: {record.author_count}")
            st.write(f"**字符长度**: {record.creator_length}")
            
            # 标题
            st.write("**标题**:")
            st.text_area("标题内容", value=record.title, height=60, disabled=True, key=f"title_{record.record_id}", label_visibility="collapsed")
            
            # 原始creator
            st.write("**原始Creator字段**:")
            st.text_area("原始creator内容", value=record.original_creator, height=120, disabled=True, key=f"original_{record.record_id}", label_visibility="collapsed")
            
            # 处理结果
            st.write("**处理后Authors Clean**:")
            st.text_area("处理后authors内容", value=record.processed_authors, height=100, disabled=True, key=f"processed_{record.record_id}", label_visibility="collapsed")
            
            # 机构信息
            if record.processed_affiliations:
                st.write("**提取的机构信息**:")
                for i, affiliation in enumerate(record.processed_affiliations):
                    st.write(f"{i+1}. {affiliation}")
        
        with col2:
            st.subheader("🔍 外部验证")
            
            # 生成搜索链接
            search_urls = self.external_validator.generate_search_urls(record.title, record.processed_authors)
            
            for url_info in search_urls:
                st.markdown(f"[🔗 {url_info['name']}]({url_info['url']})")
            
            # 自动验证按钮
            if st.button("🤖 自动验证", key=f"auto_validate_{record.record_id}"):
                with st.spinner("验证中..."):
                    try:
                        result = self.external_validator.comprehensive_validation(record.title, record.processed_authors)
                        record.external_verification = result
                        st.session_state.validation_progress[record.record_id] = record
                        
                        st.success(f"验证完成! 置信度: {result['overall_confidence']:.2f}")
                        st.write(f"建议: {result['recommendation']}")
                    except Exception as e:
                        st.error(f"自动验证失败: {e}")
    
    def render_validation_form(self, record: ValidationRecord):
        """渲染验证表单"""
        st.subheader("✅ 人工验证")
        
        # 快速标记按钮
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ 正确", key=f"correct_{record.record_id}", use_container_width=True):
                record.overall_status = "correct"
                record.author_identification_score = 5
                record.author_separation_score = 5
                record.name_affiliation_score = 5
                record.name_formatting_score = 5
                record.validator_name = st.session_state.validator_name
                record.validation_timestamp = pd.Timestamp.now().isoformat()
                record.notes = "快速标记为正确"
                st.session_state.validation_progress[record.record_id] = record
                st.success("已标记为正确!")
                time.sleep(0.5)
                st.rerun()
        
        with col2:
            if st.button("⚠️ 部分正确", key=f"partial_{record.record_id}", use_container_width=True):
                record.overall_status = "partial"
                record.author_identification_score = 3
                record.author_separation_score = 3
                record.name_affiliation_score = 3
                record.name_formatting_score = 3
                record.validator_name = st.session_state.validator_name
                record.validation_timestamp = pd.Timestamp.now().isoformat()
                record.notes = "快速标记为部分正确"
                st.session_state.validation_progress[record.record_id] = record
                st.warning("已标记为部分正确!")
                time.sleep(0.5)
                st.rerun()
        
        with col3:
            if st.button("❌ 错误", key=f"incorrect_{record.record_id}", use_container_width=True):
                record.overall_status = "incorrect"
                record.author_identification_score = 1
                record.author_separation_score = 1
                record.name_affiliation_score = 1
                record.name_formatting_score = 1
                record.validator_name = st.session_state.validator_name
                record.validation_timestamp = pd.Timestamp.now().isoformat()
                record.notes = "快速标记为错误"
                st.session_state.validation_progress[record.record_id] = record
                st.error("已标记为错误!")
                time.sleep(0.5)
                st.rerun()
        
        st.divider()
        
        # 详细评分表单
        with st.form(f"validation_form_{record.record_id}"):
            st.write("**详细评分** (1=很差, 5=很好)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                id_score = st.slider(
                    "作者识别准确性",
                    1, 5,
                    value=record.author_identification_score or 3,
                    key=f"id_score_{record.record_id}"
                )
                
                sep_score = st.slider(
                    "多作者分割准确性",
                    1, 5,
                    value=record.author_separation_score or 3,
                    key=f"sep_score_{record.record_id}"
                )
            
            with col2:
                class_score = st.slider(
                    "姓名vs机构分类准确性",
                    1, 5,
                    value=record.name_affiliation_score or 3,
                    key=f"class_score_{record.record_id}"
                )
                
                format_score = st.slider(
                    "姓名格式化质量",
                    1, 5,
                    value=record.name_formatting_score or 3,
                    key=f"format_score_{record.record_id}"
                )
            
            # 总体状态
            overall_status = st.selectbox(
                "总体评价",
                ["correct", "partial", "incorrect"],
                index=["correct", "partial", "incorrect"].index(record.overall_status) if record.overall_status else 1,
                key=f"status_{record.record_id}"
            )
            
            # 备注
            notes = st.text_area(
                "备注说明",
                value=record.notes or "",
                height=80,
                key=f"notes_{record.record_id}"
            )
            
            # 提交按钮
            if st.form_submit_button("💾 保存验证结果", use_container_width=True):
                # 更新记录
                record.author_identification_score = id_score
                record.author_separation_score = sep_score
                record.name_affiliation_score = class_score
                record.name_formatting_score = format_score
                record.overall_status = overall_status
                record.notes = notes
                record.validator_name = st.session_state.validator_name
                record.validation_timestamp = pd.Timestamp.now().isoformat()
                
                # 保存到session state
                st.session_state.validation_progress[record.record_id] = record
                
                st.success("✅ 验证结果已保存!")
                
                # 自动跳转到下一条记录
                if st.session_state.current_index < len(st.session_state.records) - 1:
                    st.session_state.current_index += 1
                    time.sleep(1)
                    st.rerun()
    
    def render_statistics_dashboard(self):
        """渲染统计面板"""
        if not st.session_state.records:
            return
        
        st.subheader("📊 验证统计")
        
        records = st.session_state.records
        completed_records = [r for r in records if r.overall_status is not None]
        
        # 基础统计
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总记录数", len(records))
        
        with col2:
            st.metric("已完成", len(completed_records))
        
        with col3:
            completion_rate = len(completed_records) / len(records) if len(records) > 0 else 0
            st.metric("完成率", f"{completion_rate:.1%}")
        
        with col4:
            if completed_records:
                correct_count = len([r for r in completed_records if r.overall_status == "correct"])
                accuracy = correct_count / len(completed_records)
                st.metric("准确率", f"{accuracy:.1%}")
            else:
                st.metric("准确率", "N/A")
        
        if completed_records:
            # 状态分布饼图
            status_counts = {}
            for record in completed_records:
                status = record.overall_status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="验证结果分布"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 复杂度vs准确率
            complexity_stats = {}
            for record in completed_records:
                complexity = record.complexity_level
                if complexity not in complexity_stats:
                    complexity_stats[complexity] = {'total': 0, 'correct': 0}
                complexity_stats[complexity]['total'] += 1
                if record.overall_status == 'correct':
                    complexity_stats[complexity]['correct'] += 1
            
            if complexity_stats:
                complexities = list(complexity_stats.keys())
                accuracies = [complexity_stats[c]['correct'] / complexity_stats[c]['total'] for c in complexities]
                
                fig = px.bar(
                    x=complexities,
                    y=accuracies,
                    title="按复杂度分类的准确率",
                    labels={'x': '复杂度', 'y': '准确率'}
                )
                fig.update_yaxis(range=[0, 1])
                st.plotly_chart(fig, use_container_width=True)
    
    def generate_report(self):
        """生成最终报告"""
        if not st.session_state.records:
            st.error("没有数据可以生成报告")
            return
        
        with st.spinner("🔄 生成报告中..."):
            try:
                output_dir = Path("data/validation/reports")
                report_files = self.report_generator.generate_all_reports(
                    st.session_state.records, output_dir
                )
                
                st.success("✅ 报告生成完成!")
                
                for format_type, file_path in report_files.items():
                    st.write(f"**{format_type.upper()}报告**: {file_path}")
                    
                    # 提供下载链接（如果是支持的格式）
                    if format_type == 'csv':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            st.download_button(
                                f"下载{format_type.upper()}报告",
                                f.read(),
                                file_name=f"validation_report.{format_type}",
                                mime=f"text/{format_type}"
                            )
                
            except Exception as e:
                st.error(f"报告生成失败: {e}")
    
    def run(self):
        """运行应用"""
        st.set_page_config(
            page_title="LLM名称提取验证系统",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # 自动保存
        self.auto_save()
        
        # 主界面
        st.title("🔍 LLM名称提取验证系统")
        st.markdown("---")
        
        # 加载数据
        self.load_data()
        
        # 渲染侧边栏（在数据加载后）
        self.render_sidebar()
        
        if not st.session_state.records:
            st.info("请等待数据加载...")
            return
        
        # 选择视图
        view_mode = st.selectbox(
            "选择视图模式",
            ["📝 验证模式", "📊 统计面板"],
            key="view_mode"
        )
        
        if view_mode == "📝 验证模式":
            # 验证模式
            current_index = st.session_state.current_index
            if 0 <= current_index < len(st.session_state.records):
                current_record = st.session_state.records[current_index]
                
                st.subheader(f"记录 {current_index + 1} / {len(st.session_state.records)}")
                
                # 显示记录
                self.render_record_display(current_record)
                
                st.markdown("---")
                
                # 验证表单
                self.render_validation_form(current_record)
            else:
                st.error("无效的记录索引")
        
        elif view_mode == "📊 统计面板":
            # 统计面板
            self.render_statistics_dashboard()


def main():
    """主函数"""
    app = ValidationApp()
    app.run()


if __name__ == "__main__":
    main()
