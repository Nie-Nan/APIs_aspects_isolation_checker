#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建发布包
"""

import os
import shutil
import datetime

def create_release_package():
    """创建发布包"""
    print("=" * 70)
    print("创建三切面隔离检查工具发布包")
    print("=" * 70)
    
    # 源目录和目标目录
    source_dir = r"build\exe.win-amd64-3.12"
    release_dir = "三切面隔离检查工具_发布包_v1.2"
    
    # 清理旧的发布包
    if os.path.exists(release_dir):
        print(f"清理旧的发布包: {release_dir}")
        shutil.rmtree(release_dir)
    
    # 创建发布目录
    os.makedirs(release_dir, exist_ok=True)
    print(f"创建发布目录: {release_dir}")
    
    # 复制可执行文件
    exe_source = os.path.join(source_dir, "三切面隔离检查工具.exe")
    exe_dest = os.path.join(release_dir, "三切面隔离检查工具.exe")
    
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, exe_dest)
        file_size = os.path.getsize(exe_dest) / (1024 * 1024)  # MB
        print(f"✓ 复制可执行文件: {file_size:.2f} MB")
    else:
        print(f"✗ 可执行文件不存在: {exe_source}")
        return False
    
    # 复制必要的库文件
    lib_files = [
        "libcrypto-3.dll",
        "libssl-3.dll",
        "python3.dll",
        "python312.dll",
    ]
    
    for lib_file in lib_files:
        lib_source = os.path.join(source_dir, lib_file)
        if os.path.exists(lib_source):
            shutil.copy2(lib_source, os.path.join(release_dir, lib_file))
            print(f"✓ 复制库文件: {lib_file}")
    
    # 复制lib目录
    lib_source = os.path.join(source_dir, "lib")
    lib_dest = os.path.join(release_dir, "lib")
    
    if os.path.exists(lib_source):
        shutil.copytree(lib_source, lib_dest)
        print(f"✓ 复制lib目录")
    
    # 复制文档文件
    docs_to_copy = [
        "使用说明.md",
        "更新说明.md",
        "字体调整说明.md",
        "最终优化报告.md",
        "test_data.xlsx",
    ]
    
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy2(doc, os.path.join(release_dir, doc))
            print(f"✓ 复制文档: {doc}")
    
    # 创建运行说明
    readme_content = f"""三切面隔离检查工具 - 使用说明

版本: 1.2
构建日期: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

一、工具简介
这是一个用于检查API三切面隔离状态的桌面工具，具有以下特点：
1. 现代化界面设计，大字体清晰显示
2. 支持Excel文件拖拽上传
3. 自动解析多域名和API路径
4. 根据HTTP响应码判断隔离状态
5. 彩色标识检查结果，支持结果导出

二、系统要求
- Windows 7/8/10/11 (64位)
- 无需安装Python或其他依赖
- 需要网络连接用于发送HTTP请求

三、使用方法
1. 双击运行 "三切面隔离检查工具.exe"
2. 拖拽Excel文件到上传区域或点击"选择Excel文件"
3. 点击"开始检查"按钮
4. 查看彩色标识的检查结果（绿色:已隔离，红色:未隔离）
5. 可点击"导出结果"保存检查结果为Excel文件

四、Excel文件格式要求
必需字段（列名必须完全一致）：
1. 切面分类：运行集成面 / 运维管理面
2. 域名：支持多个域名，用逗号或分号分隔
3. API：API路径，必须以"/"开头（如：/api/test）
4. 请求方式：GET / POST / PUT / DELETE等

示例：
┌──────────────┬──────────────────────┬─────────────┬──────────┐
│ 切面分类     │ 域名                 │ API         │ 请求方式 │
├──────────────┼──────────────────────┼─────────────┼──────────┤
│ 运行集成面   │ example.com,test.com │ /api/test   │ GET      │
│ 运维管理面   │ admin.example.com    │ /admin/api  │ POST     │
└──────────────┴──────────────────────┴─────────────┴──────────┘

五、隔离判断逻辑
1. 运行集成面API：响应码403=已隔离，其他=未隔离
2. 运维管理面API：响应码403=已隔离，其他=未隔离

六、界面特点
1. 大字体设计：标题28pt，全局16px，便于阅读
2. 精简表格：6列表格，域名和API合并为URL
3. 彩色标识：绿色（已隔离）、红色（未隔离）
4. 实时统计：显示检查进度和统计信息

七、测试数据
包内包含 test_data.xlsx 文件，可用于测试工具功能。

八、常见问题
1. 首次运行可能需要等待几秒钟加载
2. 确保Excel文件格式正确
3. 检查网络连接是否正常
4. 如有错误，请查看错误信息并参考文档

九、技术支持
如有问题，请参考文档或联系工具开发组。

注意：本工具为绿色软件，无需安装，可直接运行。
"""
    
    readme_path = os.path.join(release_dir, "README.txt")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"✓ 创建使用说明: README.txt")
    
    # 创建快捷运行批处理
    bat_content = """@echo off
chcp 65001 >nul
title 三切面隔离检查工具

echo ========================================
echo   三切面隔离检查工具
echo ========================================
echo.

echo 正在启动程序...
echo 首次启动可能需要几秒钟时间，请稍候...
echo.

start "" "三切面隔离检查工具.exe"

echo 程序已启动！
echo 请查看弹出的窗口...
echo.
pause
"""
    
    bat_path = os.path.join(release_dir, "运行工具.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_content)
    print(f"✓ 创建运行批处理: 运行工具.bat")
    
    # 计算发布包大小
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(release_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    
    total_size_mb = total_size / (1024 * 1024)
    
    print("\n" + "=" * 70)
    print("🎉 发布包创建完成!")
    print("=" * 70)
    print(f"发布包目录: {release_dir}")
    print(f"总大小: {total_size_mb:.2f} MB")
    print(f"包含文件:")
    print(f"  1. 三切面隔离检查工具.exe - 主程序")
    print(f"  2. 运行工具.bat - 运行脚本")
    print(f"  3. README.txt - 使用说明")
    print(f"  4. test_data.xlsx - 测试数据")
    print(f"  5. 多个文档文件 - 详细说明")
    print(f"  6. lib/ 目录 - 运行库")
    print()
    print("🚀 使用方式:")
    print("  1. 将整个文件夹复制到任意位置")
    print("  2. 双击'运行工具.bat'或直接运行'exe'文件")
    print("  3. 按照使用说明操作")
    print()
    print("💡 提示:")
    print("  - 无需安装，绿色软件")
    print("  - 首次运行可能需要等待几秒钟")
    print("  - 确保有网络连接用于HTTP检查")
    
    return True

if __name__ == "__main__":
    try:
        create_release_package()
    except Exception as e:
        print(f"\n✗ 创建发布包时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()