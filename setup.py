#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='api_isolation_checker',
    version='1.2.0',
    description='三切面隔离检查工具',
    author='Tool Dev Team',
    packages=find_packages(),
    install_requires=[
        'PyQt5==5.15.9',
        'pandas==2.1.4',
        'openpyxl==3.1.2',
        'requests==2.31.0',
        'xlrd==2.0.1',
        'xlwt==1.3.0',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'api_isolation_checker=main:main',
        ],
    },
)
