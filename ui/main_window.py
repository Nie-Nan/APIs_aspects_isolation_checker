"""
主窗口类
"""

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QProgressBar,
    QFileDialog, QMessageBox, QGroupBox, QFrame, QStatusBar, QHeaderView,
    QMenu, QApplication, QComboBox, QWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QFont, QColor, QBrush, QDragEnterEvent, QDropEvent, QPainter, QPolygon

from ui.styles import get_stylesheet, COLORS
from core.excel_parser import ExcelParser
from core.http_checker import HttpChecker
from core.isolation_checker import IsolationChecker
from core.result_manager import ResultManager


class FilterableHeaderView(QHeaderView):
    """支持下拉筛选的自定义表头"""

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.table_widget = None
        self.filter_icon_size = 20
        self.filter_button_rects = {}
        self.active_filters = {}  # 记录每列的当前筛选值

    def set_table_widget(self, table_widget):
        """设置表格控件"""
        self.table_widget = table_widget

    def paintEvent(self, event):
        """重写绘制事件，绘制筛选按钮"""
        super().paintEvent(event)

        # 使用viewport作为绘画设备
        painter = QPainter(self.viewport())
        if not painter.isActive():
            return
            
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制每个列的筛选按钮
        for i in range(self.count()):
            # 使用 sectionViewportPosition + sectionSize 计算矩形
            # （PyQt5 中 QHeaderView 没有 sectionRect 方法）
            x = self.sectionViewportPosition(i)
            width = self.sectionSize(i)
            if x < 0 or width <= 0:
                continue
            rect = QRect(x, 0, width, self.height())
            if rect.isValid():
                # 在列标题右侧绘制筛选按钮
                # 检查列宽是否足够显示筛选按钮
                if width < self.filter_icon_size + 10:
                    continue
                
                # 使用更精确的位置计算，避免边界问题
                button_x = rect.left() + width - self.filter_icon_size - 5
                button_rect = QRect(
                    button_x,
                    rect.top() + (rect.height() - self.filter_icon_size) // 2,
                    self.filter_icon_size,
                    self.filter_icon_size
                )

                # 存储按钮位置
                self.filter_button_rects[i] = button_rect

                # 绘制筛选图标（简单的三角形）
                center_x = button_rect.left() + button_rect.width() // 2
                center_y = button_rect.top() + button_rect.height() // 2
                
                # 绘制深蓝色圆角矩形背景，与表头风格统一
                bg_rect = QRect(
                    button_rect.left() + 1,
                    button_rect.top() + 1,
                    button_rect.width() - 2,
                    button_rect.height() - 2
                )
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(COLORS['primary_light'])))  # 表头深蓝色系
                painter.drawRoundedRect(bg_rect, 4, 4)

                # 绘制向下三角形（白色填充，深蓝色边框）
                triangle = QPolygon([
                    QPoint(center_x - 6, center_y - 3),
                    QPoint(center_x + 6, center_y - 3),
                    QPoint(center_x, center_y + 3)
                ])
                
                # 先绘制边框（更深的蓝色）
                painter.setPen(QColor(COLORS['primary_dark']))
                painter.setBrush(Qt.NoBrush)
                painter.drawPolygon(triangle)
                
                # 再绘制填充（白色）
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(COLORS['white'])))
                painter.drawPolygon(triangle)

        painter.end()

    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            # 检查是否点击了筛选按钮
            for logical_index, button_rect in self.filter_button_rects.items():
                if button_rect.contains(event.pos()):
                    self.show_filter_menu(button_rect.topLeft(), logical_index)
                    return

        super().mousePressEvent(event)

    def show_filter_menu(self, pos, logical_index):
        """显示筛选菜单"""
        # 获取该列的所有唯一值
        unique_values = self.get_unique_values(logical_index)

        # 如果没有值，不显示筛选器
        if not unique_values:
            return

        # 创建并显示筛选菜单
        menu = QMenu(self)
        all_action = menu.addAction("显示全部")
        all_action.setCheckable(True)
        all_action.setChecked(logical_index not in self.active_filters)
        all_action.triggered.connect(lambda: self.filter_column(logical_index, None))
        menu.addSeparator()

        for value in unique_values:
            action = menu.addAction(str(value))
            action.setCheckable(True)
            is_checked = (logical_index in self.active_filters and
                          self.active_filters[logical_index] == str(value))
            action.setChecked(is_checked)
            action.triggered.connect(lambda _, v=value: self.filter_column(logical_index, v))

        # 在按钮下方显示菜单
        menu.exec_(self.mapToGlobal(pos))

    def get_unique_values(self, column):
        """获取列的所有唯一值"""
        values = set()
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, column)
            if item:
                values.add(item.text())
        return sorted(values)

    def filter_column(self, column, filter_value):
        """筛选列数据（支持多列同时筛选）"""
        if filter_value is None:
            if column in self.active_filters:
                del self.active_filters[column]
        else:
            self.active_filters[column] = str(filter_value)

        # 重新应用所有筛选条件
        for row in range(self.table_widget.rowCount()):
            should_show = True
            for col, expected_value in self.active_filters.items():
                item = self.table_widget.item(row, col)
                if not item or item.text() != expected_value:
                    should_show = False
                    break
            self.table_widget.setRowHidden(row, not should_show)


class FileUploadGroupBox(QGroupBox):
    """支持拖拽的文件上传区域"""

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAcceptDrops(True)
        self.drag_callback = None
        self.drag_enter_callback = None

    def set_drop_callback(self, callback):
        """设置拖拽释放回调"""
        self.drag_callback = callback

    def set_drag_enter_callback(self, callback):
        """设置拖拽进入回调"""
        self.drag_enter_callback = callback

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if self.drag_enter_callback:
            self.drag_enter_callback(event)
        else:
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
            else:
                event.ignore()

    def dropEvent(self, event: QDropEvent):
        """拖拽释放事件"""
        if self.drag_callback:
            self.drag_callback(event)


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化组件
        self.excel_parser = ExcelParser()
        self.http_checker = HttpChecker(delay=1.0)
        self.isolation_checker = IsolationChecker()
        self.result_manager = ResultManager()
        
        # 当前文件路径
        self.current_file_path = None
        # 检查线程
        self.check_thread = None
        
        # 初始化UI
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 设置窗口属性
        self.setWindowTitle("三切面隔离检查工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 应用样式表
        self.setStyleSheet(get_stylesheet())
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)
        
        # 1. 标题区域
        title_label = QLabel("三切面隔离检查工具")
        title_label.setObjectName("title")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # 2. 文件上传区域
        file_group = self.create_file_upload_group()
        main_layout.addWidget(file_group)
        
        # 3. 控制按钮区域
        control_group = self.create_control_buttons_group()
        main_layout.addWidget(control_group)
        
        # 4. 结果显示区域
        result_group = self.create_result_display_group()
        main_layout.addWidget(result_group, 1)  # 设置拉伸因子为1
        
        # 5. 状态区域
        status_group = self.create_status_group()
        main_layout.addWidget(status_group)
        
        # 设置状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
    def create_file_upload_group(self):
        """创建文件上传区域"""
        group = FileUploadGroupBox("文件上传")
        layout = QVBoxLayout(group)

        # 文件信息显示
        self.file_info_label = QLabel("未选择文件")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        self.file_info_label.setWordWrap(True)
        layout.addWidget(self.file_info_label)

        # 按钮布局
        button_layout = QHBoxLayout()

        # 选择文件按钮
        self.select_file_btn = QPushButton("选择Excel文件")
        self.select_file_btn.clicked.connect(self.select_file)
        button_layout.addWidget(self.select_file_btn)

        # 拖拽区域提示
        drag_label = QLabel("或拖拽文件到此区域")
        drag_label.setAlignment(Qt.AlignCenter)
        drag_label.setStyleSheet(f"color: {COLORS['gray']}; font-style: italic;")
        button_layout.addWidget(drag_label)

        layout.addLayout(button_layout)

        # 设置拖拽回调
        group.set_drag_enter_callback(self._on_drag_enter)
        group.set_drop_callback(self._on_drop)

        return group

    def _on_drag_enter(self, event):
        """拖拽进入事件处理"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def _on_drop(self, event):
        """拖拽释放事件处理"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.xlsx', '.xls')):
                self.load_file(file_path)
            else:
                QMessageBox.warning(self, "文件格式错误", "请选择Excel文件(.xlsx或.xls)")
        
    def create_control_buttons_group(self):
        """创建控制按钮区域"""
        group = QGroupBox("控制")
        layout = QHBoxLayout(group)
        
        # 开始检查按钮
        self.start_check_btn = QPushButton("开始检查")
        self.start_check_btn.clicked.connect(self.start_check)
        self.start_check_btn.setEnabled(False)
        self.start_check_btn.setObjectName("success")
        layout.addWidget(self.start_check_btn)
        
        # 停止按钮
        self.stop_check_btn = QPushButton("停止")
        self.stop_check_btn.clicked.connect(self.stop_check)
        self.stop_check_btn.setEnabled(False)
        self.stop_check_btn.setObjectName("danger")
        layout.addWidget(self.stop_check_btn)
        
        # 导出结果按钮
        self.export_result_btn = QPushButton("导出结果")
        self.export_result_btn.clicked.connect(self.export_result)
        self.export_result_btn.setEnabled(False)
        layout.addWidget(self.export_result_btn)
        
        # 清空结果按钮
        self.clear_result_btn = QPushButton("清空结果")
        self.clear_result_btn.clicked.connect(self.clear_result)
        layout.addWidget(self.clear_result_btn)
        
        layout.addStretch()
        
        return group
        
    def create_result_display_group(self):
        """创建结果显示区域"""
        group = QGroupBox("检查结果")
        layout = QVBoxLayout(group)

        # 创建表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels([
            "URL", "切面分类", "请求方式",
            "状态码", "检查结果"
        ])

        # 设置表格属性
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSortingEnabled(True)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止编辑

        # 创建自定义表头（支持下拉筛选）
        custom_header = FilterableHeaderView(Qt.Horizontal)
        custom_header.set_table_widget(self.result_table)
        self.result_table.setHorizontalHeader(custom_header)

        # 列宽自适应设置
        header = self.result_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)           # URL 自适应拉伸
        header.setSectionResizeMode(1, QHeaderView.Interactive)       # 切面分类 可手动调整
        header.setSectionResizeMode(2, QHeaderView.Interactive)       # 请求方式 可手动调整
        header.setSectionResizeMode(3, QHeaderView.Interactive)       # 状态码 可手动调整
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 检查结果 根据内容自适应
        header.setMinimumSectionSize(90)

        # 设置合理的初始列宽，避免过于紧凑
        self.result_table.setColumnWidth(1, 200)   # 切面分类
        self.result_table.setColumnWidth(2, 200)   # 请求方式
        self.result_table.setColumnWidth(3, 200)   # 状态码
        self.result_table.setColumnWidth(4, 200)   # 检查结果

        # 设置表格字体大小
        font = self.result_table.font()
        font.setPointSize(12)
        self.result_table.setFont(font)

        # 设置表头字体大小
        header_font = self.result_table.horizontalHeader().font()
        header_font.setPointSize(13)
        header_font.setBold(True)
        self.result_table.horizontalHeader().setFont(header_font)

        # 设置右键菜单策略
        self.result_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.result_table.customContextMenuRequested.connect(self.show_table_context_menu)

        layout.addWidget(self.result_table)

        return group
        
    def create_status_group(self):
        """创建状态区域"""
        group = QGroupBox("状态信息")
        layout = QGridLayout(group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(QLabel("进度:"), 0, 0)
        layout.addWidget(self.progress_bar, 0, 1, 1, 3)
        
        # 统计信息
        self.total_label = QLabel("总计: 0")
        self.success_label = QLabel("已隔离: 0")
        self.failed_label = QLabel("未隔离: 0")
        self.error_label = QLabel("错误: 0")
        
        layout.addWidget(QLabel("统计:"), 1, 0)
        layout.addWidget(self.total_label, 1, 1)
        layout.addWidget(self.success_label, 1, 2)
        layout.addWidget(self.failed_label, 1, 3)
        layout.addWidget(self.error_label, 1, 4)
        
        # 当前状态
        self.current_status_label = QLabel("状态: 就绪")
        layout.addWidget(self.current_status_label, 2, 0, 1, 5)
        
        return group

    def select_file(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        
        if file_path:
            self.load_file(file_path)
            
    def load_file(self, file_path):
        """加载文件"""
        try:
            # 解析Excel文件
            data = self.excel_parser.parse(file_path)
            
            if data:
                self.current_file_path = file_path
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path) / 1024  # KB
                
                # 更新文件信息
                self.file_info_label.setText(
                    f"已选择文件: {file_name}\n"
                    f"文件大小: {file_size:.2f} KB\n"
                    f"记录数: {len(data)}"
                )
                
                # 启用开始检查按钮
                self.start_check_btn.setEnabled(True)
                self.status_bar.showMessage(f"已加载文件: {file_name}")
                
                # 清空之前的结果
                self.clear_result_table()
                
            else:
                QMessageBox.warning(self, "文件解析错误", "无法解析Excel文件，请检查文件格式")
                
        except Exception as e:
            QMessageBox.critical(self, "文件加载错误", f"加载文件时发生错误:\n{str(e)}")
            
    def show_table_context_menu(self, position):
        """显示表格右键菜单"""
        item = self.result_table.itemAt(position)
        if not item:
            return
        
        # 仅在 URL 列显示右键菜单
        if item.column() != 0:
            return
        
        menu = QMenu(self)
        copy_action = menu.addAction("复制")
        action = menu.exec_(self.result_table.viewport().mapToGlobal(position))
        
        if action == copy_action:
            url_text = item.text()
            clipboard = QApplication.clipboard()
            clipboard.setText(url_text)
    
    def clear_result_table(self):
        """清空结果表格"""
        self.result_table.setRowCount(0)
        self.update_statistics(0, 0, 0, 0)
        
    def update_statistics(self, total, success, failed, error):
        """更新统计信息"""
        self.total_label.setText(f"总计: {total}")
        self.success_label.setText(f"已隔离: {success}")
        self.failed_label.setText(f"未隔离: {failed}")
        self.error_label.setText(f"错误: {error}")
        
    def start_check(self):
        """开始检查"""
        if not self.current_file_path:
            QMessageBox.warning(self, "警告", "请先选择Excel文件")
            return
            
        # 禁用开始按钮，启用停止按钮
        self.start_check_btn.setEnabled(False)
        self.stop_check_btn.setEnabled(True)
        self.export_result_btn.setEnabled(False)
        
        # 清空结果表格
        self.clear_result_table()
        
        # 更新状态
        self.current_status_label.setText("状态: 正在检查...")
        self.status_bar.showMessage("正在检查API隔离状态...")
        
        # 创建并启动检查线程
        self.check_thread = CheckThread(
            self.current_file_path,
            self.excel_parser,
            self.http_checker,
            self.isolation_checker
        )
        
        # 连接信号
        self.check_thread.progress_updated.connect(self.update_progress)
        self.check_thread.result_ready.connect(self.add_result_row)
        self.check_thread.statistics_updated.connect(self.update_statistics)
        self.check_thread.finished.connect(self.on_check_finished)
        self.check_thread.error_occurred.connect(self.on_check_error)
        
        # 启动线程
        self.check_thread.start()
        
    def stop_check(self):
        """停止检查"""
        if self.check_thread and self.check_thread.isRunning():
            self.check_thread.stop()
            self.stop_check_btn.setEnabled(False)
            self.current_status_label.setText("状态: 正在停止...")
            
    def on_check_finished(self):
        """检查完成"""
        self.start_check_btn.setEnabled(True)
        self.stop_check_btn.setEnabled(False)
        self.export_result_btn.setEnabled(True)
        
        self.current_status_label.setText("状态: 检查完成")
        self.status_bar.showMessage("检查完成")
        
        # 更新进度条
        self.progress_bar.setValue(100)
        
    def on_check_error(self, error_msg):
        """检查错误"""
        QMessageBox.critical(self, "检查错误", error_msg)
        self.on_check_finished()
        
    def update_progress(self, value, total):
        """更新进度"""
        if total > 0:
            progress = int((value / total) * 100)
            self.progress_bar.setValue(progress)
            self.status_bar.showMessage(f"正在检查: {value}/{total}")
            
    def add_result_row(self, row_data):
        """添加结果行到表格"""
        # 临时禁用排序，避免在设置单元格数据时触发排序导致数据错位或丢失
        sorting_enabled = self.result_table.isSortingEnabled()
        self.result_table.setSortingEnabled(False)

        row = self.result_table.rowCount()
        self.result_table.insertRow(row)

        # row_data 结构: [full_url, aspect, method, status_code_display, result, detail]
        # detail 包含响应时间信息
        full_url, aspect, method, status_code_display, result, detail = row_data

        # 创建表格项
        url_item = QTableWidgetItem(str(full_url))
        aspect_item = QTableWidgetItem(str(aspect))
        method_item = QTableWidgetItem(str(method))
        status_item = QTableWidgetItem(str(status_code_display))

        # 检查结果项 - 只显示检查结果，不显示响应时间
        result_item = QTableWidgetItem(str(result))

        # 设置结果项颜色
        if "非本应用API，请确认" in result:
            result_item.setForeground(QBrush(QColor(COLORS["warning"])))
            font = QFont()
            font.setBold(True)
            result_item.setFont(font)
        elif "已隔离" in result:
            result_item.setForeground(QBrush(QColor(COLORS["success"])))
            font = QFont()
            font.setBold(True)
            result_item.setFont(font)
        elif "未隔离" in result:
            result_item.setForeground(QBrush(QColor(COLORS["danger"])))
            font = QFont()
            font.setBold(True)
            result_item.setFont(font)

        # 设置 tooltip：鼠标悬浮时显示响应时间和响应结果
        tooltip_text = f"{detail}\n检查结果: {result}"
        result_item.setToolTip(tooltip_text)

        # 设置文本对齐
        aspect_item.setTextAlignment(Qt.AlignCenter)
        method_item.setTextAlignment(Qt.AlignCenter)
        status_item.setTextAlignment(Qt.AlignCenter)
        result_item.setTextAlignment(Qt.AlignCenter)

        # 添加到表格
        self.result_table.setItem(row, 0, url_item)
        self.result_table.setItem(row, 1, aspect_item)
        self.result_table.setItem(row, 2, method_item)
        self.result_table.setItem(row, 3, status_item)
        self.result_table.setItem(row, 4, result_item)

        # 如果有激活的筛选条件，检查新行是否应该显示
        header = self.result_table.horizontalHeader()
        if isinstance(header, FilterableHeaderView) and header.active_filters:
            should_show = True
            for col, expected_value in header.active_filters.items():
                item = self.result_table.item(row, col)
                if not item or item.text() != expected_value:
                    should_show = False
                    break
            self.result_table.setRowHidden(row, not should_show)

        # 恢复排序
        self.result_table.setSortingEnabled(sorting_enabled)

        # 滚动到最后一行
        self.result_table.scrollToBottom()

        
    def export_result(self):
        """导出结果"""
        if self.result_table.rowCount() == 0:
            QMessageBox.warning(self, "警告", "没有可导出的结果")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出结果", "", "Excel文件 (*.xlsx)"
        )
        
        if file_path:
            try:
                # 保存结果
                self.result_manager.save_results(self.result_table, file_path)
                QMessageBox.information(self, "导出成功", f"结果已导出到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "导出错误", f"导出结果时发生错误:\n{str(e)}")
                
    def clear_result(self):
        """清空结果"""
        reply = QMessageBox.question(
            self, "确认清空", "确定要清空所有结果吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.clear_result_table()
            self.progress_bar.setValue(0)
            self.current_status_label.setText("状态: 就绪")
            self.status_bar.showMessage("结果已清空")


class CheckThread(QThread):
    """检查线程"""
    
    progress_updated = pyqtSignal(int, int)  # 当前进度, 总数
    result_ready = pyqtSignal(list)  # 结果行数据
    statistics_updated = pyqtSignal(int, int, int, int)  # 总计, 成功, 失败, 错误
    error_occurred = pyqtSignal(str)  # 错误信息
    
    def __init__(self, file_path, excel_parser, http_checker, isolation_checker):
        super().__init__()
        self.file_path = file_path
        self.excel_parser = excel_parser
        self.http_checker = http_checker
        self.isolation_checker = isolation_checker
        self._is_running = True
        
    def run(self):
        """线程运行函数"""
        try:
            # 解析Excel文件
            data = self.excel_parser.parse(self.file_path)
            if not data:
                self.error_occurred.emit("无法解析Excel文件")
                return
                
            total = len(data)
            success_count = 0
            failed_count = 0
            error_count = 0
            
            # 检查每个API
            for i, row in enumerate(data):
                if not self._is_running:
                    break
                    
                try:
                    # 获取数据
                    aspect = row.get("切面分类", "")
                    domain = row.get("域名", "")
                    api = row.get("API", "")
                    method = row.get("请求方式", "GET")
                    
                    # 发送HTTP请求
                    response = self.http_checker.check(
                        domain=domain,
                        api=api,
                        method=method
                    )
                    
                    # 如果HTTP请求本身失败，直接显示错误原因
                    if not response.get("success"):
                        error_count += 1
                        result = f"检查错误: {response.get('error', '未知网络错误')}"
                        status_code_display = response.get("status_code") if response.get("status_code") is not None else "N/A"
                        detail = f"状态码: {status_code_display}\n响应时间: {response.get('response_time', 'N/A')}ms"
                    else:
                        # 判断隔离状态
                        result = self.isolation_checker.check(
                            aspect=aspect,
                            status_code=response.get("status_code"),
                            response_time=response.get("response_time")
                        )
                        status_code_display = response.get("status_code") if response.get("status_code") is not None else "N/A"
                        detail = f"状态码: {status_code_display}\n响应时间: {response.get('response_time', 'N/A')}ms"
                        
                        # 统计
                        if "已隔离" in result:
                            success_count += 1
                        elif "未隔离" in result:
                            failed_count += 1
                        else:
                            error_count += 1
                        
                    # 发射结果信号
                    # 构建完整URL
                    full_url = f"http://{domain}{api}" if not domain.startswith(("http://", "https://")) else f"{domain}{api}"
                    row_data = [
                        full_url,  # URL（域名+API）
                        aspect,  # 切面分类
                        method,  # 请求方式
                        status_code_display,  # 状态码
                        result,  # 检查结果
                        detail  # 详细信息
                    ]
                    
                    self.result_ready.emit(row_data)
                    
                except Exception as e:
                    error_count += 1
                    # 发射错误结果
                    # 构建完整URL
                    domain = row.get("域名", "")
                    api = row.get("API", "")
                    full_url = f"http://{domain}{api}" if domain and api and not domain.startswith(("http://", "https://")) else f"{domain}{api}"
                    row_data = [
                        full_url,
                        row.get("切面分类", ""),
                        row.get("请求方式", "GET"),
                        "N/A",
                        f"检查错误: {str(e)}",
                        "状态码: N/A\n响应时间: N/A"
                    ]
                    self.result_ready.emit(row_data)
                    
                # 更新进度
                self.progress_updated.emit(i + 1, total)
                self.statistics_updated.emit(i + 1, success_count, failed_count, error_count)
                
        except Exception as e:
            self.error_occurred.emit(f"检查过程中发生错误: {str(e)}")
            
    def stop(self):
        """停止线程"""
        self._is_running = False