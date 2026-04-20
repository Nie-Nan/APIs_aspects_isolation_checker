"""
结果管理器
"""

import pandas as pd
from PyQt5.QtWidgets import QTableWidget
from datetime import datetime
from typing import List, Dict, Any


class ResultManager:
    """结果管理器"""
    
    def __init__(self):
        self.results = []
        self.summary = {}
        
    def add_result(self, result: Dict[str, Any]):
        """
        添加检查结果
        
        Args:
            result: 检查结果字典
        """
        # 添加时间戳
        result["check_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.results.append(result)
        
    def save_results(self, table_widget: QTableWidget, file_path: str):
        """
        保存结果到Excel文件
        
        Args:
            table_widget: QTableWidget对象
            file_path: 保存文件路径
        """
        try:
            # 从表格中提取数据
            data = []
            columns = []
            
            # 获取列标题
            for col in range(table_widget.columnCount()):
                header_item = table_widget.horizontalHeaderItem(col)
                if header_item:
                    columns.append(header_item.text())
                    
            # 获取行数据
            for row in range(table_widget.rowCount()):
                row_data = []
                for col in range(table_widget.columnCount()):
                    item = table_widget.item(row, col)
                    if item:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
                data.append(row_data)
                
            # 创建DataFrame
            df = pd.DataFrame(data, columns=columns)
            
            # 添加统计信息
            summary_df = self._create_summary_dataframe(table_widget)
            
            # 保存到Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='检查结果', index=False)
                summary_df.to_excel(writer, sheet_name='统计信息', index=False)
                
                # 调整列宽
                worksheet = writer.sheets['检查结果']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                    
        except Exception as e:
            raise Exception(f"保存结果失败: {str(e)}")
            
    def _create_summary_dataframe(self, table_widget: QTableWidget) -> pd.DataFrame:
        """
        创建统计信息DataFrame
        
        Args:
            table_widget: QTableWidget对象
            
        Returns:
            统计信息DataFrame
        """
        # 统计隔离状态
        isolated_count = 0
        not_isolated_count = 0
        error_count = 0
        
        # 检查结果列索引（第5列是检查结果，表格共6列：0-5）
        result_col = 4
        
        for row in range(table_widget.rowCount()):
            item = table_widget.item(row, result_col)
            if item:
                result_text = item.text()
                if "已隔离" in result_text:
                    isolated_count += 1
                elif "未隔离" in result_text:
                    not_isolated_count += 1
                else:
                    error_count += 1
                    
        total_count = table_widget.rowCount()
        
        # 创建统计信息
        summary_data = {
            "项目": [
                "检查时间", 
                "总记录数", 
                "已隔离数量", 
                "未隔离数量", 
                "错误数量",
                "隔离成功率"
            ],
            "数值": [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                total_count,
                isolated_count,
                not_isolated_count,
                error_count,
                f"{(isolated_count/total_count*100):.2f}%" if total_count > 0 else "0.00%"
            ]
        }
        
        return pd.DataFrame(summary_data)
        
    def export_to_csv(self, table_widget: QTableWidget, file_path: str):
        """
        导出结果到CSV文件
        
        Args:
            table_widget: QTableWidget对象
            file_path: 保存文件路径
        """
        try:
            # 从表格中提取数据
            data = []
            columns = []
            
            # 获取列标题
            for col in range(table_widget.columnCount()):
                header_item = table_widget.horizontalHeaderItem(col)
                if header_item:
                    columns.append(header_item.text())
                    
            # 获取行数据
            for row in range(table_widget.rowCount()):
                row_data = []
                for col in range(table_widget.columnCount()):
                    item = table_widget.item(row, col)
                    if item:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
                data.append(row_data)
                
            # 创建DataFrame并保存
            df = pd.DataFrame(data, columns=columns)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            
        except Exception as e:
            raise Exception(f"导出CSV失败: {str(e)}")
            
    def clear_results(self):
        """清空结果"""
        self.results = []
        self.summary = {}
        
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        if not self.results:
            return {}
            
        # 计算统计信息
        total = len(self.results)
        isolated = sum(1 for r in self.results if r.get("result", "").endswith("已隔离"))
        not_isolated = sum(1 for r in self.results if r.get("result", "").endswith("未隔离"))
        errors = total - isolated - not_isolated
        
        # 按切面分类统计
        by_aspect = {}
        for result in self.results:
            aspect = result.get("aspect", "未知")
            result_str = result.get("result", "")
            
            if aspect not in by_aspect:
                by_aspect[aspect] = {
                    "total": 0,
                    "isolated": 0,
                    "not_isolated": 0,
                    "errors": 0
                }
                
            by_aspect[aspect]["total"] += 1
            
            if "已隔离" in result_str:
                by_aspect[aspect]["isolated"] += 1
            elif "未隔离" in result_str:
                by_aspect[aspect]["not_isolated"] += 1
            else:
                by_aspect[aspect]["errors"] += 1
                
        return {
            "total": total,
            "isolated": isolated,
            "not_isolated": not_isolated,
            "errors": errors,
            "by_aspect": by_aspect,
            "success_rate": (isolated / total * 100) if total > 0 else 0
        }