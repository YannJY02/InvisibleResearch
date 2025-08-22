#!/usr/bin/env python3
"""
数据保护模块 - LLM验证审核系统
Data Protection Module for LLM Validation Suite

防止验证数据丢失的保护机制
"""

import json
import shutil
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProtectionManager:
    """数据保护管理器"""
    
    def __init__(self, progress_file_path: str):
        """
        初始化数据保护管理器
        
        Args:
            progress_file_path: validation_progress.json文件路径
        """
        self.progress_file = Path(progress_file_path)
        self.backup_dir = self.progress_file.parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # 保护配置
        self.max_backups = 10  # 最多保留10个备份
        self.backup_interval = 300  # 5分钟自动备份间隔（秒）
        self.last_backup_time = 0
        
        logger.info(f"数据保护管理器已初始化: {self.progress_file}")
    
    def create_backup(self, reason: str = "manual") -> Optional[Path]:
        """
        创建数据备份
        
        Args:
            reason: 备份原因 ("manual", "auto", "pre_save", "pre_report")
            
        Returns:
            备份文件路径，如果备份失败返回None
        """
        if not self.progress_file.exists():
            logger.warning(f"原文件不存在，无法创建备份: {self.progress_file}")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"validation_progress_backup_{reason}_{timestamp}.json"
            backup_path = self.backup_dir / backup_filename
            
            # 复制文件
            shutil.copy2(self.progress_file, backup_path)
            
            # 更新最后备份时间
            self.last_backup_time = time.time()
            
            logger.info(f"备份已创建: {backup_path}")
            
            # 清理老旧备份
            self._cleanup_old_backups()
            
            return backup_path
        
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return None
    
    def safe_save(self, data: Dict[str, Any]) -> bool:
        """
        安全保存数据到validation_progress.json
        
        Args:
            data: 要保存的数据
            
        Returns:
            保存是否成功
        """
        try:
            # 1. 预保存备份
            backup_path = self.create_backup("pre_save")
            if backup_path:
                logger.info(f"预保存备份已创建: {backup_path}")
            
            # 2. 写入临时文件
            temp_file = self.progress_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 3. 验证临时文件
            if self._verify_file_integrity(temp_file):
                # 4. 原子性替换
                shutil.move(str(temp_file), str(self.progress_file))
                logger.info(f"数据已安全保存到: {self.progress_file}")
                return True
            else:
                # 验证失败，删除临时文件
                temp_file.unlink(missing_ok=True)
                logger.error("临时文件验证失败，保存被取消")
                return False
                
        except Exception as e:
            logger.error(f"安全保存失败: {e}")
            # 清理临时文件
            temp_file = self.progress_file.with_suffix('.tmp')
            temp_file.unlink(missing_ok=True)
            return False
    
    def auto_backup_if_needed(self) -> bool:
        """
        如果需要，执行自动备份
        
        Returns:
            是否执行了备份
        """
        current_time = time.time()
        if current_time - self.last_backup_time > self.backup_interval:
            backup_path = self.create_backup("auto")
            return backup_path is not None
        return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        列出所有备份文件
        
        Returns:
            备份文件信息列表
        """
        backups = []
        for backup_file in sorted(self.backup_dir.glob("validation_progress_backup_*.json"), reverse=True):
            try:
                stat = backup_file.stat()
                backups.append({
                    'path': str(backup_file),
                    'name': backup_file.name,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'reason': self._extract_backup_reason(backup_file.name)
                })
            except Exception as e:
                logger.warning(f"无法获取备份文件信息: {backup_file}, 错误: {e}")
        
        return backups
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        从备份恢复数据
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            恢复是否成功
        """
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            logger.error(f"备份文件不存在: {backup_path}")
            return False
        
        try:
            # 验证备份文件完整性
            if not self._verify_file_integrity(backup_file):
                logger.error(f"备份文件损坏: {backup_path}")
                return False
            
            # 创建当前文件的备份（以防恢复失败）
            current_backup = self.create_backup("pre_restore")
            if current_backup:
                logger.info(f"恢复前备份已创建: {current_backup}")
            
            # 执行恢复
            shutil.copy2(backup_file, self.progress_file)
            logger.info(f"数据已从备份恢复: {backup_path} -> {self.progress_file}")
            return True
            
        except Exception as e:
            logger.error(f"从备份恢复失败: {e}")
            return False
    
    def get_data_statistics(self) -> Dict[str, Any]:
        """
        获取数据统计信息
        
        Returns:
            数据统计字典
        """
        stats = {
            'file_exists': self.progress_file.exists(),
            'file_size': 0,
            'record_count': 0,
            'completed_records': 0,
            'last_modified': None,
            'backup_count': len(list(self.backup_dir.glob("validation_progress_backup_*.json")))
        }
        
        if self.progress_file.exists():
            try:
                file_stat = self.progress_file.stat()
                stats['file_size'] = file_stat.st_size
                stats['last_modified'] = datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                
                # 读取并分析数据
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    stats['record_count'] = len(data)
                    stats['completed_records'] = len([
                        record for record in data.values()
                        if isinstance(record, dict) and record.get('overall_status') is not None
                    ])
            except Exception as e:
                logger.warning(f"获取文件统计失败: {e}")
        
        return stats
    
    def _verify_file_integrity(self, file_path: Path) -> bool:
        """
        验证文件完整性
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件是否完整有效
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 基本完整性检查
            if not isinstance(data, dict):
                return False
            
            # 检查是否包含预期的数据结构
            for record_id, record_data in data.items():
                if not isinstance(record_data, dict):
                    return False
                if 'record_id' not in record_data:
                    return False
            
            return True
            
        except (json.JSONDecodeError, UnicodeDecodeError, KeyError):
            return False
        except Exception as e:
            logger.warning(f"文件完整性验证异常: {e}")
            return False
    
    def _cleanup_old_backups(self):
        """清理过期的备份文件"""
        try:
            backup_files = sorted(
                self.backup_dir.glob("validation_progress_backup_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # 保留最新的max_backups个文件
            for old_backup in backup_files[self.max_backups:]:
                old_backup.unlink()
                logger.info(f"已删除旧备份: {old_backup}")
                
        except Exception as e:
            logger.warning(f"清理旧备份失败: {e}")
    
    def _extract_backup_reason(self, filename: str) -> str:
        """从备份文件名提取备份原因"""
        parts = filename.split('_')
        if len(parts) >= 4:
            return parts[3]  # validation_progress_backup_{reason}_{timestamp}.json
        return "unknown"


def create_protection_manager(config_path: str = "scripts/05_validation/validation_config.yaml") -> DataProtectionManager:
    """
    创建数据保护管理器实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        DataProtectionManager实例
    """
    import yaml
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        progress_file_path = config['data_paths']['validation_progress']
        return DataProtectionManager(progress_file_path)
        
    except Exception as e:
        # 回退到默认路径
        logger.warning(f"无法加载配置文件，使用默认路径: {e}")
        return DataProtectionManager("data/validation/validation_progress.json")


if __name__ == "__main__":
    # 测试数据保护功能
    print("🔒 测试数据保护功能...")
    
    protection = create_protection_manager()
    
    # 创建手动备份
    backup_path = protection.create_backup("test")
    if backup_path:
        print(f"✅ 测试备份已创建: {backup_path}")
    
    # 显示统计信息
    stats = protection.get_data_statistics()
    print(f"📊 数据统计: {stats}")
    
    # 列出备份
    backups = protection.list_backups()
    print(f"📁 当前备份数量: {len(backups)}")
    
    print("🔒 数据保护功能测试完成")
