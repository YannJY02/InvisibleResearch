#!/usr/bin/env python3
"""
LLM验证审核系统 - Web界面
Web Interface for LLM Validation Suite

提供交互式界面进行人工验证和统计分析
"""

import sys
import time
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

# 设置路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir / "utils"))

from utils.data_manager import DataManager, ValidationRecord
from utils.search_tools import ExternalValidator
from utils.report_generator import ReportGenerator
from llm_validator import LLMValidator


class ValidationApp:
    """LLM验证审核系统主应用"""
    
    def __init__(self):
        """初始化应用"""
        self.data_manager = DataManager()
        self.external_validator = ExternalValidator()
        self.llm_validator = LLMValidator()
        self.report_generator = ReportGenerator()
        
        # 语言字典
        self.translations = {
            'zh': {
                'title': '🔍 LLM名称提取验证系统',
                'sidebar_title': '🔍 LLM验证系统',
                'validator_info': '验证者信息',
                'validator_name': '验证者姓名',
                'navigation_control': '导航控制',
                'total_records': '总记录数',
                'completed': '已完成',
                'completion_rate': '完成率',
                'accuracy_rate': '准确率',
                'progress_bar': '进度条',
                'navigation_buttons': '导航按钮',
                'previous': '⬅️ 上一条',
                'next': '➡️ 下一条',
                'jump_to_record': '跳转到记录',
                'jump': '跳转',
                'filter_options': '筛选选项',
                'filter_by_status': '筛选状态',
                'filter_by_complexity': '筛选复杂度',
                'apply_filters': '应用筛选',
                'actions': '操作',
                'manual_save': '💾 手动保存',
                'generate_report': '📊 生成报告',
                'reload_data': '🔄 重新加载',
                'saved_successfully': '保存成功!',
                'navigation_controls_loading': '数据加载完成后将显示导航控制',
                'no_records_matching': '没有找到符合条件的记录',
                'record_information': '📝 记录信息',
                'record_id': '记录ID',
                'complexity': '复杂度',
                'author_count': '作者数量',
                'character_length': '字符长度',
                'title_field': '标题',
                'original_creator': '原始Creator字段',
                'processed_authors': '处理后Authors Clean',
                'extracted_affiliations': '提取的机构信息',
                'external_verification': '🔍 外部验证',
                'auto_validate': '🤖 自动验证',
                'validating': '验证中...',
                'validation_complete': '验证完成! 置信度:',
                'recommendation': '建议:',
                'auto_validation_failed': '自动验证失败:',
                'manual_validation': '✅ 人工验证',
                'correct': '✅ 正确',
                'partial': '⚠️ 部分正确',
                'incorrect': '❌ 错误',
                'marked_as_correct': '已标记为正确!',
                'marked_as_partial': '已标记为部分正确!',
                'marked_as_incorrect': '已标记为错误!',
                'detailed_scoring': '详细评分',
                'scoring_range': '(1=很差, 5=很好)',
                'author_identification': '作者识别准确性',
                'multi_author_separation': '多作者分割准确性',
                'name_affiliation_classification': '姓名vs机构分类准确性',
                'name_formatting_quality': '姓名格式化质量',
                'overall_assessment': '总体评价',
                'notes_comments': '备注说明',
                'save_validation_results': '💾 保存验证结果',
                'validation_results_saved': '✅ 验证结果已保存!',
                'validation_statistics': '📊 验证统计',
                'validation_results_distribution': '验证结果分布',
                'accuracy_by_complexity': '按复杂度分类的准确率',
                'select_view_mode': '选择视图模式',
                'validation_mode': '📝 验证模式',
                'statistics_dashboard': '📊 统计面板',
                'record_count': '记录',
                'invalid_record_index': '无效的记录索引',
                'please_wait_loading': '请等待数据加载...',
                'no_data_for_report': '没有数据可以生成报告',
                'generating_report': '🔄 生成报告中...',
                'report_generation_completed': '✅ 报告生成完成!',
                'report_generation_failed': '报告生成失败:',
                'download_report': '下载{format}报告',
                'status_all': '全部',
                'status_incomplete': '未完成',
                'status_completed': '已完成',
                'status_correct': '正确',
                'status_partial': '部分正确',
                'status_incorrect': '错误',
                'complexity_all': '全部',
                'select_report_language': '选择报告语言'
            },
            'en': {
                'title': '🔍 LLM Named Entity Extraction Validation System',
                'sidebar_title': '🔍 LLM Validation System',
                'validator_info': 'Validator Information',
                'validator_name': 'Validator Name',
                'navigation_control': 'Navigation Control',
                'total_records': 'Total Records',
                'completed': 'Completed',
                'completion_rate': 'Completion Rate',
                'accuracy_rate': 'Accuracy Rate',
                'progress_bar': 'Progress Bar',
                'navigation_buttons': 'Navigation Buttons',
                'previous': '⬅️ Previous',
                'next': '➡️ Next',
                'jump_to_record': 'Jump to Record',
                'jump': 'Jump',
                'filter_options': 'Filter Options',
                'filter_by_status': 'Filter by Status',
                'filter_by_complexity': 'Filter by Complexity',
                'apply_filters': 'Apply Filters',
                'actions': 'Actions',
                'manual_save': '💾 Manual Save',
                'generate_report': '📊 Generate Report',
                'reload_data': '🔄 Reload Data',
                'saved_successfully': 'Saved successfully!',
                'navigation_controls_loading': 'Navigation controls will appear after data loading',
                'no_records_matching': 'No records found matching the criteria',
                'record_information': '📝 Record Information',
                'record_id': 'Record ID',
                'complexity': 'Complexity',
                'author_count': 'Author Count',
                'character_length': 'Character Length',
                'title_field': 'Title',
                'original_creator': 'Original Creator Field',
                'processed_authors': 'Processed Authors Clean',
                'extracted_affiliations': 'Extracted Affiliation Information',
                'external_verification': '🔍 External Verification',
                'auto_validate': '🤖 Auto Validate',
                'validating': 'Validating...',
                'validation_complete': 'Validation complete! Confidence:',
                'recommendation': 'Recommendation:',
                'auto_validation_failed': 'Auto validation failed:',
                'manual_validation': '✅ Manual Validation',
                'correct': '✅ Correct',
                'partial': '⚠️ Partial',
                'incorrect': '❌ Incorrect',
                'marked_as_correct': 'Marked as correct!',
                'marked_as_partial': 'Marked as partial!',
                'marked_as_incorrect': 'Marked as incorrect!',
                'detailed_scoring': 'Detailed Scoring',
                'scoring_range': '(1=Poor, 5=Excellent)',
                'author_identification': 'Author Identification Accuracy',
                'multi_author_separation': 'Multi-author Separation Accuracy',
                'name_affiliation_classification': 'Name vs Affiliation Classification',
                'name_formatting_quality': 'Name Formatting Quality',
                'overall_assessment': 'Overall Assessment',
                'notes_comments': 'Notes/Comments',
                'save_validation_results': '💾 Save Validation Results',
                'validation_results_saved': '✅ Validation results saved!',
                'validation_statistics': '📊 Validation Statistics',
                'validation_results_distribution': 'Validation Results Distribution',
                'accuracy_by_complexity': 'Accuracy Rate by Complexity Level',
                'select_view_mode': 'Select View Mode',
                'validation_mode': '📝 Validation Mode',
                'statistics_dashboard': '📊 Statistics Dashboard',
                'record_count': 'Record',
                'invalid_record_index': 'Invalid record index',
                'please_wait_loading': 'Please wait for data loading...',
                'no_data_for_report': 'No data available to generate report',
                'generating_report': '🔄 Generating report...',
                'report_generation_completed': '✅ Report generation completed!',
                'report_generation_failed': 'Report generation failed:',
                'download_report': 'Download {format} Report',
                'status_all': 'All',
                'status_incomplete': 'Incomplete',
                'status_completed': 'Completed',
                'status_correct': 'Correct',
                'status_partial': 'Partial',
                'status_incorrect': 'Incorrect',
                'complexity_all': 'All',
                'select_report_language': 'Select Report Language'
            }
        }
        
        # 初始化session state
        self.init_session_state()
    
    def init_session_state(self):
        """初始化session state"""
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
        if 'language' not in st.session_state:
            st.session_state.language = 'zh'
    
    def get_text(self, key: str) -> str:
        """获取当前语言的文本"""
        return self.translations[st.session_state.language].get(key, key)
    
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
                st.success(f"✅已加载 {len(records)} 条记录")
    
    def save_progress(self) -> bool:
        """保存进度"""
        try:
            self.data_manager.save_validation_progress(st.session_state.validation_progress)
            st.session_state.last_save_time = time.time()
            return True
        except Exception as e:
            st.error(f"保存失败: {e}")
            return False
    
    def auto_save(self):
        """自动保存（每30秒）和自动备份"""
        current_time = time.time()
        if current_time - st.session_state.last_save_time > 30:
            self.save_progress()
            
            # 执行自动备份（如果需要）
            try:
                from utils.data_protection import create_protection_manager
                protection = create_protection_manager()
                if protection.auto_backup_if_needed():
                    print("🔒 自动备份已创建")
            except Exception as e:
                print(f"⚠️ 自动备份失败: {e}")
    
    def render_sidebar(self):
        """渲染侧边栏"""
        # 语言切换按钮
        col1, col2 = st.sidebar.columns([1, 1])
        with col1:
            if st.button("🇨🇳 中文", key="lang_zh", use_container_width=True):
                st.session_state.language = 'zh'
                st.rerun()
        with col2:
            if st.button("🇺🇸 English", key="lang_en", use_container_width=True):
                st.session_state.language = 'en'
                st.rerun()
        
        st.sidebar.divider()
        
        st.sidebar.title(self.get_text('sidebar_title'))
        
        # Validator Information
        st.sidebar.subheader(self.get_text('validator_info'))
        validator_name = st.sidebar.text_input(self.get_text('validator_name'), value=st.session_state.validator_name)
        if validator_name != st.session_state.validator_name:
            st.session_state.validator_name = validator_name
        
        st.sidebar.divider()
        
        # Navigation Control
        st.sidebar.subheader(self.get_text('navigation_control'))
        
        if st.session_state.records:
            total_records = len(st.session_state.records)
            current_index = st.session_state.current_index
            
            # Display Progress
            completed_count = len([r for r in st.session_state.records if r.overall_status is not None])
            progress_percentage = completed_count / total_records if total_records > 0 else 0
            
            st.sidebar.metric(self.get_text('total_records'), total_records)
            st.sidebar.metric(self.get_text('completed'), f"{completed_count} ({progress_percentage:.1%})")
            
            # Progress Bar
            st.sidebar.progress(progress_percentage)
            
            # Navigation Buttons
            st.sidebar.write(f"**{self.get_text('navigation_buttons')}**")
            col1, col2 = st.sidebar.columns([1, 1])
            
            with col1:
                if st.button(self.get_text('previous'), disabled=current_index <= 0, key="nav_prev", use_container_width=True):
                    st.session_state.current_index = max(0, current_index - 1)
                    st.rerun()
            
            with col2:
                if st.button(self.get_text('next'), disabled=current_index >= total_records - 1, key="nav_next", use_container_width=True):
                    st.session_state.current_index = min(total_records - 1, current_index + 1)
                    st.rerun()
            
            # Jump to specific record
            jump_to = st.sidebar.number_input(self.get_text('jump_to_record'), min_value=1, max_value=total_records, value=current_index + 1, key="jump_to_input")
            if st.sidebar.button(self.get_text('jump'), key="jump_to_btn"):
                st.session_state.current_index = jump_to - 1
                st.rerun()
            
            # Filter Options
            st.sidebar.subheader(self.get_text('filter_options'))
            
            status_options = [
                self.get_text('status_all'),
                self.get_text('status_incomplete'), 
                self.get_text('status_completed'),
                self.get_text('status_correct'),
                self.get_text('status_partial'),
                self.get_text('status_incorrect')
            ]
            filter_status = st.sidebar.selectbox(
                self.get_text('filter_by_status'),
                status_options,
                key="filter_status_select"
            )
            
            complexity_options = [self.get_text('complexity_all'), "simple", "medium", "complex"]
            filter_complexity = st.sidebar.selectbox(
                self.get_text('filter_by_complexity'),
                complexity_options,
                key="filter_complexity_select"
            )
            
            # Apply Filters
            if st.sidebar.button(self.get_text('apply_filters'), key="apply_filter_btn"):
                self.apply_filters(filter_status, filter_complexity)
        else:
            st.sidebar.info(self.get_text('navigation_controls_loading'))
        
        st.sidebar.divider()
        
        # Action Buttons
        st.sidebar.subheader(self.get_text('actions'))
        
        if st.sidebar.button(self.get_text('manual_save'), key="manual_save_btn"):
            if self.save_progress():
                st.sidebar.success(self.get_text('saved_successfully'))
                # 手动保存后创建备份
                try:
                    from utils.data_protection import create_protection_manager
                    protection = create_protection_manager()
                    backup_path = protection.create_backup("manual")
                    if backup_path:
                        st.sidebar.info(f"🔒 备份已创建: {backup_path.name}")
                except Exception as e:
                    st.sidebar.warning(f"备份创建失败: {e}")
        
        # 数据保护状态显示
        try:
            from utils.data_protection import create_protection_manager
            protection = create_protection_manager()
            stats = protection.get_data_statistics()
            
            if stats['file_exists']:
                st.sidebar.write(f"📊 **数据状态**")
                st.sidebar.write(f"记录总数: {stats['record_count']}")
                st.sidebar.write(f"已完成: {stats['completed_records']}")
                st.sidebar.write(f"备份数量: {stats['backup_count']}")
                
                # 数据保护操作
                if st.sidebar.button("🔒 创建备份", key="create_backup_btn"):
                    backup_path = protection.create_backup("manual")
                    if backup_path:
                        st.sidebar.success(f"备份已创建: {backup_path.name}")
                    else:
                        st.sidebar.error("备份创建失败")
        except Exception as e:
            st.sidebar.warning(f"数据保护状态获取失败: {e}")
        
        # 报告生成区域
        st.sidebar.write(f"**{self.get_text('generate_report')}**")
        
        # 报告语言选择
        report_lang_options = {
            '🇨🇳 中文报告': 'zh',
            '🇺🇸 English Report': 'en'
        }
        selected_report_lang = st.sidebar.selectbox(
            self.get_text('select_report_language'),
            list(report_lang_options.keys()),
            key="report_language_select"
        )
        
        if st.sidebar.button("📊 " + self.get_text('generate_report').replace('📊 ', ''), key="generate_report_btn"):
            report_language = report_lang_options[selected_report_lang]
            self.generate_report(report_language)
        
        if st.sidebar.button(self.get_text('reload_data'), key="reload_data_btn"):
            st.session_state.records = []
            st.session_state.validation_progress = {}
            st.rerun()
    
    def apply_filters(self, status_filter: str, complexity_filter: str):
        """Apply filter conditions"""
        filtered_records = []
        
        for record in st.session_state.records:
            # Status filtering
            if status_filter == self.get_text('status_incomplete') and record.overall_status is not None:
                continue
            elif status_filter == self.get_text('status_completed') and record.overall_status is None:
                continue
            elif status_filter == self.get_text('status_correct') and record.overall_status != "correct":
                continue
            elif status_filter == self.get_text('status_partial') and record.overall_status != "partial":
                continue
            elif status_filter == self.get_text('status_incorrect') and record.overall_status != "incorrect":
                continue
            
            # Complexity filtering
            if complexity_filter != self.get_text('complexity_all') and record.complexity_level != complexity_filter:
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
            st.sidebar.warning(self.get_text('no_records_matching'))
    
    def render_record_display(self, record: ValidationRecord):
        """Render record display"""
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader(self.get_text('record_information'))
            
            # Basic Information
            st.write(f"**{self.get_text('record_id')}**: {record.record_id}")
            st.write(f"**{self.get_text('complexity')}**: {record.complexity_level}")
            st.write(f"**{self.get_text('author_count')}**: {record.author_count}")
            st.write(f"**{self.get_text('character_length')}**: {record.creator_length}")
            
            # Title
            st.write(f"**{self.get_text('title_field')}**:")
            st.text_area("Title content", value=record.title, height=60, disabled=True, key=f"title_{record.record_id}", label_visibility="collapsed")
            
            # Original creator
            st.write(f"**{self.get_text('original_creator')}**:")
            st.text_area("Original creator content", value=record.original_creator, height=120, disabled=True, key=f"original_{record.record_id}", label_visibility="collapsed")
            
            # Processing results
            st.write(f"**{self.get_text('processed_authors')}**:")
            st.text_area("Processed authors content", value=record.processed_authors, height=100, disabled=True, key=f"processed_{record.record_id}", label_visibility="collapsed")
            
            # Affiliation information
            if record.processed_affiliations:
                st.write(f"**{self.get_text('extracted_affiliations')}**:")
                for i, affiliation in enumerate(record.processed_affiliations):
                    st.write(f"{i+1}. {affiliation}")
        
        with col2:
            st.subheader(self.get_text('external_verification'))
            
            # Generate search links
            search_urls = self.external_validator.generate_search_urls(record.title, record.processed_authors)
            
            for url_info in search_urls:
                st.markdown(f"[🔗 {url_info['name']}]({url_info['url']})")
            
            # Auto validation button
            if st.button(self.get_text('auto_validate'), key=f"auto_validate_{record.record_id}"):
                with st.spinner(self.get_text('validating')):
                    try:
                        result = self.external_validator.comprehensive_validation(record.title, record.processed_authors)
                        record.external_verification = result
                        st.session_state.validation_progress[record.record_id] = record
                        
                        st.success(f"{self.get_text('validation_complete')} {result['overall_confidence']:.2f}")
                        st.write(f"{self.get_text('recommendation')} {result['recommendation']}")
                    except Exception as e:
                        st.error(f"{self.get_text('auto_validation_failed')} {e}")
    
    def render_validation_form(self, record: ValidationRecord):
        """Render validation form"""
        st.subheader(self.get_text('manual_validation'))
        
        # Quick marking buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(self.get_text('correct'), key=f"correct_{record.record_id}", use_container_width=True):
                record.overall_status = "correct"
                record.author_identification_score = 5
                record.author_separation_score = 5
                record.name_affiliation_score = 5
                record.name_formatting_score = 5
                record.validator_name = st.session_state.validator_name
                record.validation_timestamp = pd.Timestamp.now().isoformat()
                record.notes = "Quick marked as correct"
                st.session_state.validation_progress[record.record_id] = record
                st.success(self.get_text('marked_as_correct'))
                time.sleep(0.5)
                st.rerun()
        
        with col2:
            if st.button(self.get_text('partial'), key=f"partial_{record.record_id}", use_container_width=True):
                record.overall_status = "partial"
                record.author_identification_score = 3
                record.author_separation_score = 3
                record.name_affiliation_score = 3
                record.name_formatting_score = 3
                record.validator_name = st.session_state.validator_name
                record.validation_timestamp = pd.Timestamp.now().isoformat()
                record.notes = "Quick marked as partial"
                st.session_state.validation_progress[record.record_id] = record
                st.warning(self.get_text('marked_as_partial'))
                time.sleep(0.5)
                st.rerun()
        
        with col3:
            if st.button(self.get_text('incorrect'), key=f"incorrect_{record.record_id}", use_container_width=True):
                record.overall_status = "incorrect"
                record.author_identification_score = 1
                record.author_separation_score = 1
                record.name_affiliation_score = 1
                record.name_formatting_score = 1
                record.validator_name = st.session_state.validator_name
                record.validation_timestamp = pd.Timestamp.now().isoformat()
                record.notes = "Quick marked as incorrect"
                st.session_state.validation_progress[record.record_id] = record
                st.error(self.get_text('marked_as_incorrect'))
                time.sleep(0.5)
                st.rerun()
        
        st.divider()
        
        # Detailed scoring form
        with st.form(f"validation_form_{record.record_id}"):
            st.write(f"**{self.get_text('detailed_scoring')}** {self.get_text('scoring_range')}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                id_score = st.slider(
                    self.get_text('author_identification'),
                    1, 5,
                    value=record.author_identification_score or 3,
                    key=f"id_score_{record.record_id}"
                )
                
                sep_score = st.slider(
                    self.get_text('multi_author_separation'),
                    1, 5,
                    value=record.author_separation_score or 3,
                    key=f"sep_score_{record.record_id}"
                )
            
            with col2:
                class_score = st.slider(
                    self.get_text('name_affiliation_classification'),
                    1, 5,
                    value=record.name_affiliation_score or 3,
                    key=f"class_score_{record.record_id}"
                )
                
                format_score = st.slider(
                    self.get_text('name_formatting_quality'),
                    1, 5,
                    value=record.name_formatting_score or 3,
                    key=f"format_score_{record.record_id}"
                )
            
            # Overall status
            overall_status = st.selectbox(
                self.get_text('overall_assessment'),
                ["correct", "partial", "incorrect"],
                index=["correct", "partial", "incorrect"].index(record.overall_status) if record.overall_status else 1,
                key=f"status_{record.record_id}"
            )
            
            # Notes
            notes = st.text_area(
                self.get_text('notes_comments'),
                value=record.notes or "",
                height=80,
                key=f"notes_{record.record_id}"
            )
            
            # Submit button
            if st.form_submit_button(self.get_text('save_validation_results'), use_container_width=True):
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
                
                st.success(self.get_text('validation_results_saved'))
                
                # Auto navigate to next record
                if st.session_state.current_index < len(st.session_state.records) - 1:
                    st.session_state.current_index += 1
                    time.sleep(1)
                    st.rerun()
    
    def render_statistics_dashboard(self):
        """Render statistics dashboard"""
        if not st.session_state.records:
            return
        
        st.subheader(self.get_text('validation_statistics'))
        
        records = st.session_state.records
        completed_records = [r for r in records if r.overall_status is not None]
        
        # Basic statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(self.get_text('total_records'), len(records))
        
        with col2:
            st.metric(self.get_text('completed'), len(completed_records))
        
        with col3:
            completion_rate = len(completed_records) / len(records) if len(records) > 0 else 0
            st.metric(self.get_text('completion_rate'), f"{completion_rate:.1%}")
        
        with col4:
            if completed_records:
                correct_count = len([r for r in completed_records if r.overall_status == "correct"])
                accuracy = correct_count / len(completed_records)
                st.metric(self.get_text('accuracy_rate'), f"{accuracy:.1%}")
            else:
                st.metric(self.get_text('accuracy_rate'), "N/A")
        
        if completed_records:
            # Status distribution pie chart
            status_counts = {}
            for record in completed_records:
                status = record.overall_status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title=self.get_text('validation_results_distribution')
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
                    title=self.get_text('accuracy_by_complexity'),
                    labels={'x': 'Complexity', 'y': 'Accuracy Rate'}
                )
                fig.update_layout(yaxis=dict(range=[0, 1]))
                st.plotly_chart(fig, use_container_width=True)
    
    def generate_report(self, report_language: str = None):
        """Generate final report"""
        if not st.session_state.records:
            st.error(self.get_text('no_data_for_report'))
            return
        
        # 如果没有指定报告语言，使用当前界面语言
        if report_language is None:
            report_language = st.session_state.language
        
        # 报告生成前创建数据备份
        try:
            from utils.data_protection import create_protection_manager
            protection = create_protection_manager()
            backup_path = protection.create_backup("pre_report")
            if backup_path:
                st.info(f"🔒 报告生成前备份已创建: {backup_path.name}")
        except Exception as e:
            st.warning(f"备份创建失败: {e}")
        
        with st.spinner(self.get_text('generating_report')):
            try:
                output_dir = Path("data/validation/reports")
                report_files = self.report_generator.generate_all_reports(
                    st.session_state.records, output_dir, report_language
                )
                
                lang_name = "中文" if report_language == 'zh' else "English"
                st.success(f"{self.get_text('report_generation_completed')} ({lang_name})")
                
                for format_type, file_path in report_files.items():
                    st.write(f"**{format_type.upper()} Report ({lang_name})**: {file_path}")
                    
                    # Provide download links (for supported formats)
                    if format_type in ['csv', 'json']:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            st.download_button(
                                f"下载{format_type.upper()}报告 / Download {format_type.upper()} Report",
                                f.read(),
                                file_name=f"validation_report_{report_language}.{format_type}",
                                mime=f"text/{format_type}" if format_type == 'csv' else "application/json"
                            )
                
            except Exception as e:
                st.error(f"{self.get_text('report_generation_failed')} {e}")
    
    def run(self):
        """运行应用"""
        st.set_page_config(
            page_title=self.get_text('title'),
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # 自动保存
        self.auto_save()
        
        # Main interface
        st.title(self.get_text('title'))
        st.markdown("---")
        
        # Load data
        self.load_data()
        
        # Render sidebar (after data loading)
        self.render_sidebar()
        
        if not st.session_state.records:
            st.info(self.get_text('please_wait_loading'))
            return
        
        # Select view mode
        view_mode = st.selectbox(
            self.get_text('select_view_mode'),
            [self.get_text('validation_mode'), self.get_text('statistics_dashboard')],
            key="view_mode"
        )
        
        if view_mode == self.get_text('validation_mode'):
            # Validation mode
            current_index = st.session_state.current_index
            if 0 <= current_index < len(st.session_state.records):
                current_record = st.session_state.records[current_index]
                
                st.subheader(f"{self.get_text('record_count')} {current_index + 1} / {len(st.session_state.records)}")
                
                # Display record
                self.render_record_display(current_record)
                
                st.markdown("---")
                
                # Validation form
                self.render_validation_form(current_record)
            else:
                st.error(self.get_text('invalid_record_index'))
        
        elif view_mode == self.get_text('statistics_dashboard'):
            # Statistics dashboard
            self.render_statistics_dashboard()


def main():
    """主函数"""
    app = ValidationApp()
    app.run()


if __name__ == "__main__":
    main()