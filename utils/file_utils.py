"""
文件工具类
"""

import os
import shutil
from typing import Optional, List, Tuple


class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def get_file_info(file_path: str) -> Optional[dict]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典，如果文件不存在则返回None
        """
        try:
            if not os.path.exists(file_path):
                return None
                
            stat_info = os.stat(file_path)
            
            return {
                "path": file_path,
                "name": os.path.basename(file_path),
                "size": stat_info.st_size,
                "size_human": FileUtils.format_file_size(stat_info.st_size),
                "created": stat_info.st_ctime,
                "modified": stat_info.st_mtime,
                "accessed": stat_info.st_atime,
                "extension": os.path.splitext(file_path)[1].lower(),
                "directory": os.path.dirname(file_path)
            }
        except Exception:
            return None
            
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        格式化文件大小
        
        Args:
            size_bytes: 文件大小（字节）
            
        Returns:
            格式化后的文件大小字符串
        """
        if size_bytes == 0:
            return "0 B"
            
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024
            i += 1
            
        return f"{size:.2f} {size_names[i]}"
        
    @staticmethod
    def is_excel_file(file_path: str) -> bool:
        """
        检查是否为Excel文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否为Excel文件
        """
        if not file_path:
            return False
            
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ['.xlsx', '.xls', '.xlsm', '.xlsb']
        
    @staticmethod
    def validate_excel_file(file_path: str) -> Tuple[bool, str]:
        """
        验证Excel文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            (是否有效, 错误信息)
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False, "文件不存在"
            
        # 检查文件大小
        try:
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return False, "文件为空"
            if file_size > 100 * 1024 * 1024:  # 100MB限制
                return False, "文件过大（超过100MB）"
        except:
            return False, "无法获取文件大小"
            
        # 检查文件扩展名
        if not FileUtils.is_excel_file(file_path):
            return False, "不是有效的Excel文件"
            
        return True, "文件有效"
        
    @staticmethod
    def create_backup(file_path: str, backup_dir: Optional[str] = None) -> Optional[str]:
        """
        创建文件备份
        
        Args:
            file_path: 原始文件路径
            backup_dir: 备份目录，如果为None则使用原始文件所在目录
            
        Returns:
            备份文件路径，如果失败则返回None
        """
        try:
            if not os.path.exists(file_path):
                return None
                
            # 确定备份目录
            if backup_dir is None:
                backup_dir = os.path.dirname(file_path)
                
            # 创建备份目录（如果不存在）
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成备份文件名
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(file_name)[0]
            ext = os.path.splitext(file_name)[1]
            backup_name = f"{name_without_ext}_backup_{timestamp}{ext}"
            backup_path = os.path.join(backup_dir, backup_name)
            
            # 复制文件
            shutil.copy2(file_path, backup_path)
            
            return backup_path
            
        except Exception:
            return None
            
    @staticmethod
    def get_unique_filename(file_path: str) -> str:
        """
        获取唯一的文件名（避免覆盖）
        
        Args:
            file_path: 原始文件路径
            
        Returns:
            唯一的文件路径
        """
        if not os.path.exists(file_path):
            return file_path
            
        directory = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(file_name)[0]
        ext = os.path.splitext(file_name)[1]
        
        counter = 1
        while True:
            new_name = f"{name_without_ext}_{counter}{ext}"
            new_path = os.path.join(directory, new_name)
            if not os.path.exists(new_path):
                return new_path
            counter += 1
            
    @staticmethod
    def safe_delete(file_path: str) -> bool:
        """
        安全删除文件（先移动到回收站或备份）
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否删除成功
        """
        try:
            if not os.path.exists(file_path):
                return True
                
            # 创建备份
            backup_dir = os.path.join(os.path.dirname(file_path), "_deleted_backups")
            backup_path = FileUtils.create_backup(file_path, backup_dir)
            
            # 删除原文件
            os.remove(file_path)
            
            return True
            
        except Exception:
            return False
            
    @staticmethod
    def get_directory_size(directory: str) -> int:
        """
        获取目录大小
        
        Args:
            directory: 目录路径
            
        Returns:
            目录大小（字节）
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
        
    @staticmethod
    def clean_directory(directory: str, max_age_days: int = 30) -> int:
        """
        清理目录中的旧文件
        
        Args:
            directory: 目录路径
            max_age_days: 最大保留天数
            
        Returns:
            删除的文件数量
        """
        if not os.path.exists(directory):
            return 0
            
        import datetime
        deleted_count = 0
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_mtime < cutoff_time:
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                    except:
                        pass
                        
        return deleted_count