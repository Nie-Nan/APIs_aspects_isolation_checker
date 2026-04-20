#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
三切面隔离检查工具 - 主程序入口
"""

import sys
import os

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    """主函数"""
    try:
        app = QApplication(sys.argv)
        
        # 设置应用程序信息
        app.setApplicationName("三切面隔离检查工具")
        app.setOrganizationName("工具开发组")
        
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        # 运行应用程序
        sys.exit(app.exec_())
    except Exception as e:
        import traceback
        print("程序启动时发生错误:")
        traceback.print_exc()
        input("按Enter键退出...")
        return 1

if __name__ == "__main__":
    main()
