"""
结果管理器
"""

import pandas as pd
from PyQt5.QtWidgets import QTableWidget
from datetime import datetime


class ResultManager:
    """结果管理器"""

    def save_results(self, table_widget: QTableWidget, file_path: str):
        try:
            data = []
            columns = []

            for col in range(table_widget.columnCount()):
                header_item = table_widget.horizontalHeaderItem(col)
                if header_item:
                    columns.append(header_item.text())

            for row in range(table_widget.rowCount()):
                row_data = []
                for col in range(table_widget.columnCount()):
                    item = table_widget.item(row, col)
                    if item:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
                data.append(row_data)

            df = pd.DataFrame(data, columns=columns)

            summary_df = self._create_summary_dataframe(table_widget)

            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='检查结果', index=False)
                summary_df.to_excel(writer, sheet_name='统计信息', index=False)

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
        isolated_count = 0
        not_isolated_count = 0
        error_count = 0

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
