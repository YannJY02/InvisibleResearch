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
        st.sidebar.title("🔍 LLM Validation System")
        
        # Validator Information
        st.sidebar.subheader("Validator Information")
        validator_name = st.sidebar.text_input("Validator Name", value=st.session_state.validator_name)
        if validator_name != st.session_state.validator_name:
            st.session_state.validator_name = validator_name
        
        st.sidebar.divider()
        
        # Navigation Control
        st.sidebar.subheader("Navigation Control")
        
        if st.session_state.records:
            total_records = len(st.session_state.records)
            current_index = st.session_state.current_index
            
            # Display Progress
            completed_count = len([r for r in st.session_state.records if r.overall_status is not None])
            progress_percentage = completed_count / total_records if total_records > 0 else 0
            
            st.sidebar.metric("Total Records", total_records)
            st.sidebar.metric("Completed", f"{completed_count} ({progress_percentage:.1%})")
            
            # Progress Bar
            st.sidebar.progress(progress_percentage)
            
            # Navigation Buttons
            st.sidebar.write("**Navigation Buttons**")
            col1, col2 = st.sidebar.columns([1, 1])
            
            with col1:
                if st.button("⬅️ Previous", disabled=current_index <= 0, key="nav_prev", use_container_width=True):
                    st.session_state.current_index = max(0, current_index - 1)
                    st.rerun()
            
            with col2:
                if st.button("➡️ Next", disabled=current_index >= total_records - 1, key="nav_next", use_container_width=True):
                    st.session_state.current_index = min(total_records - 1, current_index + 1)
                    st.rerun()
            
            # Jump to specific record
            jump_to = st.sidebar.number_input("Jump to Record", min_value=1, max_value=total_records, value=current_index + 1, key="jump_to_input")
            if st.sidebar.button("Jump", key="jump_to_btn"):
                st.session_state.current_index = jump_to - 1
                st.rerun()
            
            # Filter Options
            st.sidebar.subheader("Filter Options")
            filter_status = st.sidebar.selectbox(
                "Filter by Status",
                ["All", "Incomplete", "Completed", "Correct", "Partial", "Incorrect"],
                key="filter_status_select"
            )
            
            filter_complexity = st.sidebar.selectbox(
                "Filter by Complexity",
                ["All", "simple", "medium", "complex"],
                key="filter_complexity_select"
            )
            
            # Apply Filters
            if st.sidebar.button("Apply Filters", key="apply_filter_btn"):
                self.apply_filters(filter_status, filter_complexity)
        else:
            st.sidebar.info("Navigation controls will appear after data loading")
        
        st.sidebar.divider()
        
        # Action Buttons
        st.sidebar.subheader("Actions")
        
        if st.sidebar.button("💾 Manual Save", key="manual_save_btn"):
            if self.save_progress():
                st.sidebar.success("Saved successfully!")
        
        if st.sidebar.button("📊 Generate Report", key="generate_report_btn"):
            self.generate_report()
        
        if st.sidebar.button("🔄 Reload Data", key="reload_data_btn"):
            st.session_state.records = []
            st.session_state.validation_progress = {}
            st.rerun()
    
    def apply_filters(self, status_filter: str, complexity_filter: str):
        """Apply filter conditions"""
        filtered_records = []
        
        for record in st.session_state.records:
            # Status filtering
            if status_filter == "Incomplete" and record.overall_status is not None:
                continue
            elif status_filter == "Completed" and record.overall_status is None:
                continue
            elif status_filter == "Correct" and record.overall_status != "correct":
                continue
            elif status_filter == "Partial" and record.overall_status != "partial":
                continue
            elif status_filter == "Incorrect" and record.overall_status != "incorrect":
                continue
            
            # Complexity filtering
            if complexity_filter != "All" and record.complexity_level != complexity_filter:
                continue
            
            filtered_records.append(record)
        
        if filtered_records:
            # Find the index of the first matching record
            original_records = st.session_state.records
            for i, record in enumerate(original_records):
                if record.record_id == filtered_records[0].record_id:
                    st.session_state.current_index = i
                    break
            st.rerun()
        else:
            st.sidebar.warning("No records found matching the criteria")
    
    def render_record_display(self, record: ValidationRecord):
        """Render record display"""
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("📝 Record Information")
            
            # Basic Information
            st.write(f"**Record ID**: {record.record_id}")
            st.write(f"**Complexity**: {record.complexity_level}")
            st.write(f"**Author Count**: {record.author_count}")
            st.write(f"**Character Length**: {record.creator_length}")
            
            # Title
            st.write("**Title**:")
            st.text_area("Title content", value=record.title, height=60, disabled=True, key=f"title_{record.record_id}", label_visibility="collapsed")
            
            # Original creator
            st.write("**Original Creator Field**:")
            st.text_area("Original creator content", value=record.original_creator, height=120, disabled=True, key=f"original_{record.record_id}", label_visibility="collapsed")
            
            # Processing results
            st.write("**Processed Authors Clean**:")
            st.text_area("Processed authors content", value=record.processed_authors, height=100, disabled=True, key=f"processed_{record.record_id}", label_visibility="collapsed")
            
            # Affiliation information
            if record.processed_affiliations:
                st.write("**Extracted Affiliation Information**:")
                for i, affiliation in enumerate(record.processed_affiliations):
                    st.write(f"{i+1}. {affiliation}")
        
        with col2:
            st.subheader("🔍 External Verification")
            
            # Generate search links
            search_urls = self.external_validator.generate_search_urls(record.title, record.processed_authors)
            
            for url_info in search_urls:
                st.markdown(f"[🔗 {url_info['name']}]({url_info['url']})")
            
            # Auto validation button
            if st.button("🤖 Auto Validate", key=f"auto_validate_{record.record_id}"):
                with st.spinner("Validating..."):
                    try:
                        result = self.external_validator.comprehensive_validation(record.title, record.processed_authors)
                        record.external_verification = result
                        st.session_state.validation_progress[record.record_id] = record
                        
                        st.success(f"Validation complete! Confidence: {result['overall_confidence']:.2f}")
                        st.write(f"Recommendation: {result['recommendation']}")
                    except Exception as e:
                        st.error(f"Auto validation failed: {e}")
    
    def render_validation_form(self, record: ValidationRecord):
        """Render validation form"""
        st.subheader("✅ Manual Validation")
        
        # Quick marking buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Correct", key=f"correct_{record.record_id}", use_container_width=True):
                record.overall_status = "correct"
                record.author_identification_score = 5
                record.author_separation_score = 5
                record.name_affiliation_score = 5
                record.name_formatting_score = 5
                record.validator_name = st.session_state.validator_name
                record.validation_timestamp = pd.Timestamp.now().isoformat()
                record.notes = "Quick marked as correct"
                st.session_state.validation_progress[record.record_id] = record
                st.success("Marked as correct!")
                time.sleep(0.5)
                st.rerun()
        
        with col2:
            if st.button("⚠️ Partial", key=f"partial_{record.record_id}", use_container_width=True):
                record.overall_status = "partial"
                record.author_identification_score = 3
                record.author_separation_score = 3
                record.name_affiliation_score = 3
                record.name_formatting_score = 3
                record.validator_name = st.session_state.validator_name
                record.validation_timestamp = pd.Timestamp.now().isoformat()
                record.notes = "Quick marked as partial"
                st.session_state.validation_progress[record.record_id] = record
                st.warning("Marked as partial!")
                time.sleep(0.5)
                st.rerun()
        
        with col3:
            if st.button("❌ Incorrect", key=f"incorrect_{record.record_id}", use_container_width=True):
                record.overall_status = "incorrect"
                record.author_identification_score = 1
                record.author_separation_score = 1
                record.name_affiliation_score = 1
                record.name_formatting_score = 1
                record.validator_name = st.session_state.validator_name
                record.validation_timestamp = pd.Timestamp.now().isoformat()
                record.notes = "Quick marked as incorrect"
                st.session_state.validation_progress[record.record_id] = record
                st.error("Marked as incorrect!")
                time.sleep(0.5)
                st.rerun()
        
        st.divider()
        
        # Detailed scoring form
        with st.form(f"validation_form_{record.record_id}"):
            st.write("**Detailed Scoring** (1=Poor, 5=Excellent)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                id_score = st.slider(
                    "Author Identification Accuracy",
                    1, 5,
                    value=record.author_identification_score or 3,
                    key=f"id_score_{record.record_id}"
                )
                
                sep_score = st.slider(
                    "Multi-author Separation Accuracy",
                    1, 5,
                    value=record.author_separation_score or 3,
                    key=f"sep_score_{record.record_id}"
                )
            
            with col2:
                class_score = st.slider(
                    "Name vs Affiliation Classification",
                    1, 5,
                    value=record.name_affiliation_score or 3,
                    key=f"class_score_{record.record_id}"
                )
                
                format_score = st.slider(
                    "Name Formatting Quality",
                    1, 5,
                    value=record.name_formatting_score or 3,
                    key=f"format_score_{record.record_id}"
                )
            
            # Overall status
            overall_status = st.selectbox(
                "Overall Assessment",
                ["correct", "partial", "incorrect"],
                index=["correct", "partial", "incorrect"].index(record.overall_status) if record.overall_status else 1,
                key=f"status_{record.record_id}"
            )
            
            # Notes
            notes = st.text_area(
                "Notes/Comments",
                value=record.notes or "",
                height=80,
                key=f"notes_{record.record_id}"
            )
            
            # Submit button
            if st.form_submit_button("💾 Save Validation Results", use_container_width=True):
                # Update record
                record.author_identification_score = id_score
                record.author_separation_score = sep_score
                record.name_affiliation_score = class_score
                record.name_formatting_score = format_score
                record.overall_status = overall_status
                record.notes = notes
                record.validator_name = st.session_state.validator_name
                record.validation_timestamp = pd.Timestamp.now().isoformat()
                
                # Save to session state
                st.session_state.validation_progress[record.record_id] = record
                
                st.success("✅ Validation results saved!")
                
                # Auto navigate to next record
                if st.session_state.current_index < len(st.session_state.records) - 1:
                    st.session_state.current_index += 1
                    time.sleep(1)
                    st.rerun()
    
    def render_statistics_dashboard(self):
        """Render statistics dashboard"""
        if not st.session_state.records:
            return
        
        st.subheader("📊 Validation Statistics")
        
        records = st.session_state.records
        completed_records = [r for r in records if r.overall_status is not None]
        
        # Basic statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(records))
        
        with col2:
            st.metric("Completed", len(completed_records))
        
        with col3:
            completion_rate = len(completed_records) / len(records) if len(records) > 0 else 0
            st.metric("Completion Rate", f"{completion_rate:.1%}")
        
        with col4:
            if completed_records:
                correct_count = len([r for r in completed_records if r.overall_status == "correct"])
                accuracy = correct_count / len(completed_records)
                st.metric("Accuracy Rate", f"{accuracy:.1%}")
            else:
                st.metric("Accuracy Rate", "N/A")
        
        if completed_records:
            # Status distribution pie chart
            status_counts = {}
            for record in completed_records:
                status = record.overall_status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Validation Results Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Complexity vs accuracy
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
                    title="Accuracy Rate by Complexity Level",
                    labels={'x': 'Complexity', 'y': 'Accuracy Rate'}
                )
                fig.update_yaxis(range=[0, 1])
                st.plotly_chart(fig, use_container_width=True)
    
    def generate_report(self):
        """Generate final report"""
        if not st.session_state.records:
            st.error("No data available to generate report")
            return
        
        with st.spinner("🔄 Generating report..."):
            try:
                output_dir = Path("data/validation/reports")
                report_files = self.report_generator.generate_all_reports(
                    st.session_state.records, output_dir
                )
                
                st.success("✅ Report generation completed!")
                
                for format_type, file_path in report_files.items():
                    st.write(f"**{format_type.upper()} Report**: {file_path}")
                    
                    # Provide download links (for supported formats)
                    if format_type == 'csv':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            st.download_button(
                                f"Download {format_type.upper()} Report",
                                f.read(),
                                file_name=f"validation_report.{format_type}",
                                mime=f"text/{format_type}"
                            )
                
            except Exception as e:
                st.error(f"Report generation failed: {e}")
    
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
        
        # Main interface
        st.title("🔍 LLM Named Entity Extraction Validation System")
        st.markdown("---")
        
        # Load data
        self.load_data()
        
        # Render sidebar (after data loading)
        self.render_sidebar()
        
        if not st.session_state.records:
            st.info("Please wait for data loading...")
            return
        
        # Select view mode
        view_mode = st.selectbox(
            "Select View Mode",
            ["📝 Validation Mode", "📊 Statistics Dashboard"],
            key="view_mode"
        )
        
        if view_mode == "📝 Validation Mode":
            # Validation mode
            current_index = st.session_state.current_index
            if 0 <= current_index < len(st.session_state.records):
                current_record = st.session_state.records[current_index]
                
                st.subheader(f"Record {current_index + 1} / {len(st.session_state.records)}")
                
                # Display record
                self.render_record_display(current_record)
                
                st.markdown("---")
                
                # Validation form
                self.render_validation_form(current_record)
            else:
                st.error("Invalid record index")
        
        elif view_mode == "📊 Statistics Dashboard":
            # Statistics dashboard
            self.render_statistics_dashboard()


def main():
    """主函数"""
    app = ValidationApp()
    app.run()


if __name__ == "__main__":
    main()
