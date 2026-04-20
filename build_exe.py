#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
构建可执行文件
"""

import os
import sys
import subprocess
import shutil
import datetime

def build_executable():
    """构建可执行文件"""
    print("开始构建三切面隔离检查工具...")
    
    # 清理之前的构建
    if os.path.exists("build"):
        shutil.rmtree("build")
        print("已清理 build 目录")
        
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        print("已清理 dist 目录")
        
    # 构建命令（使用 spec 文件，避免把发布目录打包进去）
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "api_isolation_checker.spec"
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 执行构建
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("构建输出:")
        print(result.stdout)
        
        if result.stderr:
            print("构建警告/错误:")
            print(result.stderr)
            
        # 检查构建结果
        exe_path = os.path.join("dist", "三切面隔离检查工具.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"\n[OK] 构建成功!")
            print(f"可执行文件: {exe_path}")
            print(f"文件大小: {file_size:.2f} MB")
            
            # 复制到项目根目录
            shutil.copy(exe_path, "三切面隔离检查工具.exe")
            print("已复制可执行文件到项目根目录")
            
            return True
        else:
            print("\n[ERR] 构建失败: 未找到可执行文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n[ERR] 构建失败 (退出码: {e.returncode}):")
        print(e.stdout)
        print(e.stderr)
        return False
    except Exception as e:
        print(f"\n[ERR] 构建过程中发生错误: {str(e)}")
        return False

def create_standalone_package():
    """创建独立包（包含所有依赖）"""
    print("\n创建独立包...")
    
    package_dir = "三切面隔离检查工具_独立包"
    
    # 清理之前的包（如被占用则重命名）
    if os.path.exists(package_dir):
        try:
            shutil.rmtree(package_dir)
        except Exception:
            # 如果被占用，重命名旧目录
            backup_dir = f"{package_dir}_旧_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            os.rename(package_dir, backup_dir)
            print(f"[WARN] 旧目录被占用，已重命名为: {backup_dir}")
        
    # 创建目录结构
    os.makedirs(package_dir, exist_ok=True)
    
    # 复制可执行文件
    exe_src = os.path.join("dist", "三切面隔离检查工具.exe")
    if os.path.exists(exe_src):
        shutil.copy(exe_src, os.path.join(package_dir, "三切面隔离检查工具.exe"))
        print(f"[OK] 复制可执行文件到 {package_dir}")
    else:
        print("[ERR] 未找到可执行文件")
        return False
        
    # 复制测试数据
    test_data_src = "test_data.xlsx"
    if os.path.exists(test_data_src):
        shutil.copy(test_data_src, os.path.join(package_dir, "测试数据.xlsx"))
        print(f"[OK] 复制测试数据到 {package_dir}")
        
    # 创建说明文件
    readme_content = """三切面隔离检查工具 - 使用说明

一、工具功能
1. 检查API的三切面隔离状态
2. 支持Excel文件上传（支持拖拽）
3. 自动解析域名和API路径
4. 根据HTTP响应码判断隔离状态
5. 导出检查结果

二、使用步骤
1. 运行"三切面隔离检查工具.exe"
2. 点击"选择Excel文件"或拖拽Excel文件到上传区域
3. Excel文件必须包含以下列：
   - 切面分类（运行集成面/运维管理面）
   - 域名（支持多个域名，用逗号或分号分隔）
   - API（API路径）
   - 请求方式（GET/POST等）
4. 点击"开始检查"
5. 查看检查结果
6. 可点击"导出结果"保存检查结果

三、隔离判断逻辑
1. 运行集成面API：响应码403表示已隔离，其他表示未隔离
2. 运维管理面API：响应码403表示已隔离，其他表示未隔离

四、系统要求
- Windows 7/8/10/11
- 无需安装Python或其他依赖

五、注意事项
1. 确保网络连接正常
2. Excel文件大小不超过100MB
3. 检查过程中请勿关闭程序

如有问题，请联系工具开发组。
"""
    
    with open(os.path.join(package_dir, "使用说明.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"[OK] 创建使用说明文件")
    
    print(f"\n[OK] 独立包创建完成: {package_dir}")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("三切面隔离检查工具 - 构建脚本")
    print("=" * 60)
    
    # 构建可执行文件
    if build_executable():
        # 创建独立包
        create_standalone_package()
        
        print("\n" + "=" * 60)
        print("构建完成!")
        print("=" * 60)
        print("\n生成的文件:")
        print("1. dist/三切面隔离检查工具.exe - 可执行文件")
        print("2. 三切面隔离检查工具.exe - 项目根目录副本")
        print("3. 三切面隔离检查工具_独立包/ - 完整发布包")
        print("\n请将 三切面隔离检查工具_独立包 文件夹分发给用户使用。")
    else:
        print("\n构建失败，请检查错误信息。")
        sys.exit(1)