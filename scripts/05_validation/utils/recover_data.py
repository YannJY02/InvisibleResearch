#!/usr/bin/env python3
"""
数据恢复工具 - LLM验证审核系统
Data Recovery Utility for LLM Validation Suite

从最新的CSV报告中恢复 'validation_progress.json' 文件
"""

import pandas as pd
import json
from pathlib import Path
import sys

# 确保可以从项目根目录运行
# Get the absolute path of the script's directory
script_dir = Path(__file__).parent.resolve()
# Add the 'scripts/05_validation' directory to sys.path to find 'utils'
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
# Also add the scripts directory
sys.path.insert(0, str(project_root / "scripts"))


try:
    # This might be the correct import statement
    from o5_validation.utils.data_manager import DataManager, ValidationRecord
except (ModuleNotFoundError, ImportError) as e:
    print(f"Initial import failed: {e}. Adjusting path...")
    # Add the 'scripts/05_validation' directory to sys.path
    validation_script_dir = project_root / "scripts" / "05_validation"
    sys.path.insert(0, str(validation_script_dir))
    try:
         from utils.data_manager import DataManager, ValidationRecord
    except (ModuleNotFoundError, ImportError) as e2:
        print(f"Second import attempt failed: {e2}")
        print("Please run this script from the project root directory.")
        sys.exit(1)


def recover_progress():
    """从最新的CSV报告恢复验证进度"""
    print("🚀 开始数据恢复流程...")
    
    try:
        dm = DataManager()
    except FileNotFoundError:
        print("❌ 无法找到'validation_config.yaml'。请确保从项目根目录运行此脚本。")
        return

    # 1. 加载原始源数据以创建基础记录
    print("1. 加载原始数据记录...")
    try:
        base_records_list = dm.prepare_validation_records()
        base_records = {r.record_id: r for r in base_records_list}
        print(f"  ✅ 成功加载 {len(base_records)} 条原始记录。")
    except Exception as e:
        print(f"  ❌ 加载原始数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return

    # 2. 找到最新的CSV报告以从中恢复验证结果
    reports_dir = Path(dm.data_paths['reports_dir'])
    if not reports_dir.exists():
        print(f"  ❌ 报告目录不存在: {reports_dir}")
        return
        
    csv_reports = sorted(list(reports_dir.glob("validation_data_*.csv")), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not csv_reports:
        print("  ❌ 在报告目录中未找到可用于恢复的CSV文件。")
        return
        
    latest_csv = csv_reports[0]
    print(f"2. 从最新的CSV报告加载验证结果: {latest_csv}")
    
    try:
        report_df = pd.read_csv(latest_csv)
        # 处理非字符串列中可能的NaN值
        report_df = report_df.where(pd.notnull(report_df), None)
        print(f"  ✅ 成功加载 {len(report_df)} 条已验证记录。")
    except Exception as e:
        print(f"  ❌ 读取CSV报告失败: {e}")
        return

    # 3. 将验证结果合并到基础记录中
    print("3. 合并原始数据和验证结果...")
    recovered_count = 0
    progress_to_save = {}
    for index, row in report_df.iterrows():
        record_id = str(row['record_id'])
        if record_id in base_records:
            record = base_records[record_id]
            
            # 只有当记录已验证时才更新
            if row.get('overall_status') is not None:
                record.validator_name = row.get('validator_name')
                record.validation_timestamp = row.get('validation_timestamp')
                
                def safe_int(val):
                    try:
                        return int(float(val))
                    except (ValueError, TypeError):
                        return None

                record.author_identification_score = safe_int(row.get('author_identification_score'))
                record.author_separation_score = safe_int(row.get('author_separation_score'))
                record.name_affiliation_score = safe_int(row.get('name_affiliation_score'))
                record.name_formatting_score = safe_int(row.get('name_formatting_score'))
                
                record.overall_status = row.get('overall_status')
                record.notes = row.get('notes') if row.get('notes') is not None else ''
                
                ext_ver = row.get('external_verification')
                if isinstance(ext_ver, str) and ext_ver.strip() and ext_ver not in ['None', 'nan', '']:
                    try:
                        record.external_verification = json.loads(ext_ver.replace("'", '"'))
                    except json.JSONDecodeError:
                        record.external_verification = {'raw_string': ext_ver}
                else:
                    record.external_verification = None

                progress_to_save[record_id] = record
                recovered_count += 1

    print(f"  ✅ 成功合并 {recovered_count} 条记录。")

    # 4. 将完整记录保存到 validation_progress.json
    progress_file = Path(dm.data_paths['validation_progress'])
    print(f"4. 将恢复的数据写入 '{progress_file}'...")
    
    if not progress_to_save:
        print("  ⚠️ 没有找到已验证的记录来恢复。将不会写入进度文件。")
        return

    try:
        dm.save_validation_progress(progress_to_save)
        print("  ✅ 进度文件写入成功！")
    except Exception as e:
        print(f"  ❌ 写入进度文件失败: {e}")
        import traceback
        traceback.print_exc()

    print("🏁 数据恢复流程完成。")


if __name__ == "__main__":
    recover_progress()
