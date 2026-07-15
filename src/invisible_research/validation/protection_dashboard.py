#!/usr/bin/env python3
"""
数据保护仪表板 - LLM验证审核系统
Data Protection Dashboard for LLM Validation Suite

提供数据保护状态监控和恢复功能的独立界面
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

from invisible_research.validation.utils.data_protection import create_protection_manager


def main():
    """数据保护仪表板主函数"""
    st.set_page_config(
        page_title="🔒 数据保护仪表板",
        page_icon="🔒",
        layout="wide"
    )
    
    st.title("🔒 LLM验证系统数据保护仪表板")
    st.markdown("---")
    
    try:
        protection = create_protection_manager()
    except Exception as e:
        st.error(f"无法初始化数据保护管理器: {e}")
        return
    
    # 数据状态概览
    st.subheader("📊 数据状态概览")
    
    stats = protection.get_data_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if stats['file_exists']:
            st.metric("主文件状态", "✅ 存在", f"{stats['file_size']} 字节")
        else:
            st.metric("主文件状态", "❌ 不存在", "0 字节")
    
    with col2:
        st.metric("记录总数", stats['record_count'])
    
    with col3:
        st.metric("已完成记录", stats['completed_records'])
    
    with col4:
        st.metric("备份文件数", stats['backup_count'])
    
    if stats['last_modified']:
        st.info(f"📅 最后修改时间: {stats['last_modified']}")
    
    st.markdown("---")
    
    # 备份管理
    st.subheader("🗂️ 备份管理")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("**可用备份列表**")
        
        backups = protection.list_backups()
        
        if backups:
            backup_df = pd.DataFrame(backups)
            backup_df['size_mb'] = (backup_df['size'] / 1024 / 1024).round(2)
            backup_df['modified_time'] = pd.to_datetime(backup_df['modified']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # 显示备份表格
            display_df = backup_df[['name', 'reason', 'modified_time', 'size_mb']].copy()
            display_df.columns = ['文件名', '备份原因', '创建时间', '大小(MB)']
            
            st.dataframe(display_df, use_container_width=True)
            
            # 备份文件选择器
            selected_backup = st.selectbox(
                "选择要恢复的备份:",
                options=[backup['path'] for backup in backups],
                format_func=lambda x: Path(x).name,
                key="backup_selector"
            )
        else:
            st.warning("没有找到备份文件")
            selected_backup = None
    
    with col2:
        st.write("**备份操作**")
        
        # 创建新备份
        if st.button("🔒 创建新备份", key="create_new_backup"):
            with st.spinner("创建备份中..."):
                backup_path = protection.create_backup("dashboard_manual")
                if backup_path:
                    st.success(f"备份已创建: {backup_path.name}")
                    st.rerun()
                else:
                    st.error("备份创建失败")
        
        st.markdown("---")
        
        # 恢复操作
        if selected_backup:
            st.write(f"**选中备份:**")
            st.code(Path(selected_backup).name)
            
            if st.button("🔄 从此备份恢复", key="restore_backup", type="primary"):
                with st.spinner("恢复数据中..."):
                    success = protection.restore_from_backup(selected_backup)
                    if success:
                        st.success("数据已成功恢复!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("数据恢复失败")
        else:
            st.info("请先选择一个备份文件")
    
    st.markdown("---")
    
    # 数据完整性验证
    st.subheader("🔍 数据完整性验证")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("验证主文件完整性", key="verify_main_file"):
            with st.spinner("验证中..."):
                is_valid = protection._verify_file_integrity(protection.progress_file)
                if is_valid:
                    st.success("✅ 主文件完整性验证通过")
                else:
                    st.error("❌ 主文件完整性验证失败")
    
    with col2:
        if selected_backup and st.button("验证备份文件完整性", key="verify_backup_file"):
            with st.spinner("验证中..."):
                is_valid = protection._verify_file_integrity(Path(selected_backup))
                if is_valid:
                    st.success("✅ 备份文件完整性验证通过")
                else:
                    st.error("❌ 备份文件完整性验证失败")
    
    st.markdown("---")
    
    # 数据详情预览
    st.subheader("📄 数据详情预览")
    
    if stats['file_exists']:
        try:
            with st.spinner("加载数据预览..."):
                with open(protection.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 显示数据摘要
                st.write(f"**数据摘要** (总记录数: {len(data)})")
                
                # 按状态统计
                status_counts = {}
                complexity_counts = {}
                
                for record in data.values():
                    if isinstance(record, dict):
                        status = record.get('overall_status', 'incomplete')
                        complexity = record.get('complexity_level', 'unknown')
                        
                        status_counts[status] = status_counts.get(status, 0) + 1
                        complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**按状态统计:**")
                    for status, count in status_counts.items():
                        st.write(f"- {status}: {count}")
                
                with col2:
                    st.write("**按复杂度统计:**")
                    for complexity, count in complexity_counts.items():
                        st.write(f"- {complexity}: {count}")
                
                # 显示最近修改的记录
                st.write("**最近验证的记录:**")
                recent_records = []
                for record_id, record in data.items():
                    if isinstance(record, dict) and record.get('validation_timestamp'):
                        recent_records.append({
                            'record_id': record_id,
                            'title': record.get('title', '')[:50] + '...' if len(record.get('title', '')) > 50 else record.get('title', ''),
                            'status': record.get('overall_status', ''),
                            'timestamp': record.get('validation_timestamp', '')
                        })
                
                if recent_records:
                    # 按时间排序
                    recent_records.sort(key=lambda x: x['timestamp'], reverse=True)
                    recent_df = pd.DataFrame(recent_records[:10])  # 显示最近10条
                    st.dataframe(recent_df, use_container_width=True)
                else:
                    st.info("没有找到已验证的记录")
                
        except Exception as e:
            st.error(f"无法加载数据预览: {e}")
    else:
        st.warning("主数据文件不存在")
    
    # 页脚
    st.markdown("---")
    st.caption("🔒 数据保护仪表板 - 确保您的验证数据安全")


if __name__ == "__main__":
    main()
