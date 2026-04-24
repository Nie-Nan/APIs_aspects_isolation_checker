"""
UI样式定义
遵循设计原则：大量留白、单色调配色、精简元素、清晰排版
"""

# 颜色方案 - 单色调配色
COLORS = {
    # 主色调 - 深蓝色
    "primary": "#2c3e50",
    "primary_light": "#34495e",
    "primary_dark": "#1a252f",

    # 辅助色 - 灰色系
    "secondary": "#ecf0f1",
    "secondary_light": "#f8f9fa",
    "secondary_dark": "#bdc3c7",

    # 强调色 - 绿色（成功/已隔离）
    "success": "#27ae60",
    "success_light": "#2ecc71",

    # 强调色 - 红色（失败/未隔离）
    "danger": "#e74c3c",

    # 中性色
    "white": "#ffffff",
    "gray": "#95a5a6",
    "gray_dark": "#7f8c8d",

    # 状态色
    "warning": "#f39c12",
}

# 字体设置
FONTS = {
    "default": "Microsoft YaHei, Segoe UI, Arial, sans-serif",
}

# 尺寸设置
SIZES = {
    "border_radius": 4,
    "padding_medium": 8,
    "padding_large": 16,
    "spacing_small": 4,
    "spacing_medium": 8,
}

def get_stylesheet():
    """获取应用程序样式表"""
    return f"""
    /* 全局样式 */
    QWidget {{
        font-family: {FONTS['default']};
        font-size: 16px;
        color: {COLORS['primary']};
        background-color: {COLORS['white']};
    }}

    /* 主窗口 */
    QMainWindow {{
        background-color: {COLORS['white']};
    }}

    /* 按钮样式 */
    QPushButton {{
        background-color: {COLORS['primary']};
        color: {COLORS['white']};
        border: none;
        border-radius: {SIZES['border_radius']}px;
        padding: {SIZES['padding_medium']}px {SIZES['padding_large']}px;
        font-weight: 500;
        font-size: 15px;
    }}

    QPushButton:hover {{
        background-color: {COLORS['primary_light']};
    }}

    QPushButton:pressed {{
        background-color: {COLORS['primary_dark']};
    }}

    QPushButton:disabled {{
        background-color: {COLORS['secondary_dark']};
        color: {COLORS['gray']};
    }}

    /* 成功按钮 */
    QPushButton.success {{
        background-color: {COLORS['success']};
    }}

    QPushButton.success:hover {{
        background-color: {COLORS['success_light']};
    }}

    /* 危险按钮 */
    QPushButton.danger {{
        background-color: {COLORS['danger']};
    }}

    QPushButton.danger:hover {{
        background-color: {COLORS['danger']};
    }}

    /* 输入框 */
    QLineEdit, QTextEdit, QPlainTextEdit {{
        border: 1px solid {COLORS['secondary_dark']};
        border-radius: {SIZES['border_radius']}px;
        padding: {SIZES['padding_medium']}px;
        background-color: {COLORS['white']};
    }}

    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {COLORS['primary']};
    }}

    /* 标签 */
    QLabel {{
        color: {COLORS['primary']};
    }}

    QLabel.title {{
        font-size: 24px;
        font-weight: 600;
        color: {COLORS['primary_dark']};
    }}

    QLabel.subtitle {{
        font-size: 18px;
        font-weight: 500;
        color: {COLORS['primary']};
    }}

    /* 表格 */
    QTableWidget {{
        border: 1px solid {COLORS['secondary_dark']};
        border-radius: {SIZES['border_radius']}px;
        background-color: {COLORS['white']};
        gridline-color: {COLORS['secondary']};
        selection-background-color: {COLORS['primary_light']};
        selection-color: {COLORS['white']};
    }}

    QTableWidget::item {{
        padding: {SIZES['padding_medium']}px;
    }}

    QTableWidget::item:selected {{
        background-color: {COLORS['primary_light']};
        color: {COLORS['white']};
    }}

    QHeaderView::section {{
        background-color: {COLORS['primary']};
        color: {COLORS['white']};
        padding: {SIZES['padding_medium']}px;
        border: none;
        font-weight: 500;
    }}

    /* 进度条 */
    QProgressBar {{
        border: 1px solid {COLORS['secondary_dark']};
        border-radius: {SIZES['border_radius']}px;
        text-align: center;
        background-color: {COLORS['white']};
    }}

    QProgressBar::chunk {{
        background-color: {COLORS['primary']};
        border-radius: {SIZES['border_radius']}px;
    }}

    /* 分组框 */
    QGroupBox {{
        border: 1px solid {COLORS['secondary_dark']};
        border-radius: {SIZES['border_radius']}px;
        margin-top: {SIZES['spacing_medium']}px;
        padding-top: {SIZES['padding_medium']}px;
        font-weight: 500;
        color: {COLORS['primary']};
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        left: {SIZES['padding_medium']}px;
        padding: 0 {SIZES['padding_medium']}px 0 {SIZES['padding_medium']}px;
    }}

    /* 分隔线 */
    QFrame[frameShape="4"] {{ /* HLine */
        background-color: {COLORS['secondary_dark']};
        max-height: 1px;
        min-height: 1px;
    }}

    /* 状态栏 */
    QStatusBar {{
        background-color: {COLORS['secondary']};
        color: {COLORS['primary']};
        border-top: 1px solid {COLORS['secondary_dark']};
    }}

    /* 工具栏 */
    QToolBar {{
        background-color: {COLORS['white']};
        border-bottom: 1px solid {COLORS['secondary_dark']};
        spacing: {SIZES['spacing_small']}px;
    }}

    /* 菜单栏 */
    QMenuBar {{
        background-color: {COLORS['white']};
        border-bottom: 1px solid {COLORS['secondary_dark']};
    }}

    QMenuBar::item {{
        padding: {SIZES['padding_medium']}px {SIZES['padding_large']}px;
    }}

    QMenuBar::item:selected {{
        background-color: {COLORS['secondary']};
    }}

    /* 滚动条 */
    QScrollBar:vertical {{
        border: none;
        background-color: {COLORS['secondary']};
        width: 10px;
        margin: 0px;
    }}

    QScrollBar:handle:vertical {{
        background-color: {COLORS['gray']};
        border-radius: 5px;
        min-height: 20px;
    }}

    QScrollBar:handle:vertical:hover {{
        background-color: {COLORS['gray_dark']};
    }}

    QScrollBar:add-line:vertical, QScrollBar:sub-line:vertical {{
        border: none;
        background: none;
        height: 0px;
    }}

    /* 文件拖拽区域 */
    QFrame#drag-drop-area {{
        border: 2px dashed {COLORS['primary']};
        border-radius: {SIZES['border_radius']}px;
        background-color: {COLORS['secondary_light']};
    }}

    QFrame#drag-drop-area:hover {{
        background-color: {COLORS['secondary']};
        border-color: {COLORS['primary_light']};
    }}
    """
