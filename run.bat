@echo off
chcp 65001 >nul
title 三切面隔离检查工具

echo ========================================
echo   三切面隔离检查工具
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo 检查依赖包...
pip show pandas >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 依赖包安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

REM 运行程序
echo.
echo 启动三切面隔离检查工具...
python main.py

if errorlevel 1 (
    echo.
    echo 程序运行失败，请检查错误信息。
    pause
    exit /b 1
)

echo.
echo 程序已退出。
pause